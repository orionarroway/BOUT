/**************************************************************************
 * Interface to SUNDIALS CVODE
 * 
 * NOTE: Only one solver can currently be compiled in
 *
 **************************************************************************
 * Copyright 2010 B.D.Dudson, S.Farley, M.V.Umansky, X.Q.Xu
 *
 * Contact: Ben Dudson, bd512@york.ac.uk
 * 
 * This file is part of BOUT++.
 *
 * BOUT++ is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * BOUT++ is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with BOUT++.  If not, see <http://www.gnu.org/licenses/>.
 *
 **************************************************************************/

#include "cvode.hxx"

#ifdef BOUT_HAS_CVODE

#include <boutcomm.hxx>
#include <interpolation.hxx> // Cell interpolation
#include <boutexception.hxx>
#include <msg_stack.hxx>

#include <cvode/cvode.h>
#include <cvode/cvode_bbdpre.h>
#include <nvector/nvector_parallel.h>
#include <sundials/sundials_types.h>
#include <sundials/sundials_math.h>

#include <output.hxx>

#define ZERO        RCONST(0.)
#define ONE         RCONST(1.0)

typedef long CVINT;

static int cvode_rhs(BoutReal t, N_Vector u, N_Vector du, void *user_data);
static int cvode_bbd_rhs(CVINT Nlocal, BoutReal t, N_Vector u, N_Vector du, 
			 void *user_data);

static int cvode_pre(BoutReal t, N_Vector yy, N_Vector yp,
		     N_Vector rvec, N_Vector zvec,
		     BoutReal gamma, BoutReal delta, int lr,
		     void *user_data, N_Vector tmp);

static int cvode_jac(N_Vector v, N_Vector Jv,
		     realtype t, N_Vector y, N_Vector fy,
		     void *user_data, N_Vector tmp);

CvodeSolver::CvodeSolver() : Solver() {
  has_constraints = false; ///< This solver doesn't have constraints

  prefunc = NULL;
  jacfunc = NULL;
}

CvodeSolver::~CvodeSolver() {
  if(initialised) {
    N_VDestroy_Parallel(uvec);
    CVodeFree(&cvode_mem);
  }
}

/**************************************************************************
 * Initialise
 **************************************************************************/

int CvodeSolver::init(rhsfunc f, bool restarting, int nout, BoutReal tstep) {
  int msg_point = msg_stack.push("Initialising CVODE solver");

  /// Call the generic initialisation first
  if(Solver::init(f, restarting, nout, tstep))
    return 1;

  // Save nout and tstep for use in run
  NOUT = nout;
  TIMESTEP = tstep;

  output.write("Initialising SUNDIALS' CVODE solver\n");

  // Set the rhs solver function
  func = f;

  // Calculate number of variables (in generic_solver)
  int local_N = getLocalN();

  // Get total problem size
  msg_stack.push("Allreduce localN -> GlobalN");
  int neq;
  if(MPI_Allreduce(&local_N, &neq, 1, MPI_INT, MPI_SUM, BoutComm::get())) {
    output.write("\tERROR: MPI_Allreduce failed!\n");
    return 1;
  }
  msg_stack.pop();

  output.write("\t3d fields = %d, 2d fields = %d neq=%d, local_N=%d\n",
                n3Dvars(), n2Dvars(), neq, local_N);

  // Allocate memory

  msg_stack.push("Allocating memory with N_VNew_Parallel");
  if((uvec = N_VNew_Parallel(BoutComm::get(), local_N, neq)) == NULL)
    throw BoutException("ERROR: SUNDIALS memory allocation failed\n");
  msg_stack.pop();

  // Put the variables into uvec
  msg_stack.push("Saving variables into uvec");
  if(save_vars(NV_DATA_P(uvec)))
    throw BoutException("\tERROR: Initial variable value not set\n");
  msg_stack.pop();

  /// Get options

  msg_stack.push("Getting options");
  BoutReal abstol, reltol;
  int maxl;
  int mudq, mldq;
  int mukeep, mlkeep;
  bool use_precon, use_jacobian;
  BoutReal start_timestep, max_timestep;
  bool adams_moulton, func_iter; // Time-integration method
  int MXSUB = mesh->xend - mesh->xstart + 1;

  Options *options = Options::getRoot();
  options = options->getSection("solver");
  options->get("mudq", mudq, n3Dvars()*(MXSUB+2));
  options->get("mldq", mldq, n3Dvars()*(MXSUB+2));
  options->get("mukeep", mukeep, n3Dvars()+n2Dvars());
  options->get("mlkeep", mlkeep, n3Dvars()+n2Dvars());
  options->get("ATOL", abstol, 1.0e-12);
  options->get("RTOL", reltol, 1.0e-5);
  options->get("maxl", maxl, 5);
  OPTION(options, use_precon,   false);
  OPTION(options, use_jacobian, false);
  OPTION(options, max_timestep, -1.);
  OPTION(options, start_timestep, -1);
  OPTION(options, diagnose,     false);

  int mxsteps; // Maximum number of steps to take between outputs
  options->get("mxstep", mxsteps, 500);

  int mxorder; // Maximum lmm order to be used by the solver
  options->get("mxorder", mxorder, -1);

  options->get("adams_moulton", adams_moulton, false);

  int lmm = CV_BDF;
  if(adams_moulton) {
    // By default use functional iteration for Adams-Moulton
    lmm = CV_ADAMS;
    output.write("\tUsing Adams-Moulton implicit multistep method\n");
    options->get("func_iter", func_iter, true); 
  }else {
    output.write("\tUsing BDF method\n");
    // Use Newton iteration for BDF
    options->get("func_iter", func_iter, false); 
  }

  int iter = CV_NEWTON;
  if(func_iter)
    iter = CV_FUNCTIONAL;
  msg_stack.pop();

  // Call CVodeCreate
  msg_stack.push("Calling CVodeCreate");
  if((cvode_mem = CVodeCreate(lmm, iter)) == NULL)
    throw BoutException("CVodeCreate failed\n");
  msg_stack.pop();

  msg_stack.push("Calling CVodeSetUserData");
  if( CVodeSetUserData(cvode_mem, this) < 0 ) // For callbacks, need pointer to solver object
    throw BoutException("CVodeSetUserData failed\n");
  msg_stack.pop();

  msg_stack.push("Calling CVodeInit");
  if( CVodeInit(cvode_mem, cvode_rhs, simtime, uvec) < 0 )
    throw BoutException("CVodeInit failed\n");
  msg_stack.pop();

  msg_stack.push("Calling CVodeSStolerances");
  if( CVodeSStolerances(cvode_mem, reltol, abstol) < 0 )
    throw BoutException("CVodeSStolerances failed\n");
  msg_stack.pop();

  CVodeSetMaxNumSteps(cvode_mem, mxsteps);

  if(max_timestep > 0.0) {
    // Setting a maximum timestep
    CVodeSetMaxStep(cvode_mem, max_timestep);
  }
  
  if(start_timestep > 0.0) {
    CVodeSetInitStep(cvode_mem, start_timestep);
  }

  if(mxorder > 0) {
    // Setting the maximum solver order
    CVodeSetMaxOrd(cvode_mem, mxorder);
  }

  /// Newton method can include Preconditioners and Jacobian function
  if(!func_iter) {
    output.write("\tUsing Newton iteration\n");
    /// Set Preconditioner
    msg_stack.push("Setting preconditioner");
    if(use_precon) {

      int prectype = PREC_LEFT;
      bool rightprec;
      options->get("rightprec", rightprec, false);
      if(rightprec)
        prectype = PREC_RIGHT;
      
      if( CVSpgmr(cvode_mem, prectype, maxl) != CVSPILS_SUCCESS )
        bout_error("ERROR: CVSpgmr failed\n");

      if(prefunc == NULL) {
        output.write("\tUsing BBD preconditioner\n");

        if( CVBBDPrecInit(cvode_mem, local_N, mudq, mldq, 
              mukeep, mlkeep, ZERO, cvode_bbd_rhs, NULL) )
          bout_error("ERROR: CVBBDPrecInit failed\n");

      } else {
        output.write("\tUsing user-supplied preconditioner\n");

        if( CVSpilsSetPreconditioner(cvode_mem, NULL, cvode_pre) )
          bout_error("ERROR: CVSpilsSetPreconditioner failed\n");
      }
    }else {
      // Not using preconditioning

      output.write("\tNo preconditioning\n");

      if( CVSpgmr(cvode_mem, PREC_NONE, maxl) != CVSPILS_SUCCESS )
        bout_error("ERROR: CVSpgmr failed\n");
    }
    msg_stack.pop();

    /// Set Jacobian-vector multiplication function

    if((use_jacobian) && (jacfunc != NULL)) {
      output.write("\tUsing user-supplied Jacobian function\n");

      msg_stack.push("Setting Jacobian-vector multiply");
      if( CVSpilsSetJacTimesVecFn(cvode_mem, cvode_jac) != CVSPILS_SUCCESS )
        bout_error("ERROR: CVSpilsSetJacTimesVecFn failed\n");

      msg_stack.pop();
    }else
      output.write("\tUsing difference quotient approximation for Jacobian\n");
  }else {
    output.write("\tUsing Functional iteration\n");
  }

#ifdef CHECK
  msg_stack.pop(msg_point);
#endif

  return 0;
}


/**************************************************************************
 * Run - Advance time
 **************************************************************************/

int CvodeSolver::run(MonitorFunc monitor) {
#ifdef CHECK
  int msg_point = msg_stack.push("CvodeSolver::run()");
#endif

  if(!initialised)
    throw BoutException("CvodeSolver not initialised\n");

  for(int i=0;i<NOUT;i++) {

    /// Run the solver for one output timestep
    simtime = run(simtime + TIMESTEP); //actually call the solver here
    iteration++;

    /// Check if the run succeeded
    if(simtime < 0.0) {
      // Step failed
      output.write("Timestep failed. Aborting\n");

      // Write restart to a different file
      restart.write("%s/BOUT.final.%s", restartdir.c_str(), restartext.c_str());

      throw BoutException("SUNDIALS timestep failed\n");
    }

    /// Write the restart file
    restart.write();

    if((archive_restart > 0) && (iteration % archive_restart == 0)) {
      restart.write("%s/BOUT.restart_%04d.%s", restartdir.c_str(), iteration, restartext.c_str());
    }

    if(diagnose) {
      // Print additional diagnostics
      long int nsteps, nfevals, nniters, npevals, nliters;
      
      CVodeGetNumSteps(cvode_mem, &nsteps);
      CVodeGetNumRhsEvals(cvode_mem, &nfevals);
      CVodeGetNumNonlinSolvIters(cvode_mem, &nniters);
      CVSpilsGetNumPrecEvals(cvode_mem, &npevals);
      CVSpilsGetNumLinIters(cvode_mem, &nliters);

      output.write("\nCVODE: nsteps %ld, nfevals %ld, nniters %ld, npevals %ld, nliters %ld\n", 
                   nsteps, nfevals, nniters, npevals, nliters);
      
      output.write("    -> Newton iterations per step: %e\n", 
                   ((double) nniters) / ((double) nsteps));
      output.write("    -> Linear iterations per Newton iteration: %e\n",
                   ((double) nliters) / ((double) nniters));
      output.write("    -> Preconditioner evaluations per Newton: %e\n",
                   ((double) npevals) / ((double) nniters));
    }

    /// Call the monitor function

    if(monitor(this, simtime, i, NOUT)) {
      // User signalled to quit

      // Write restart to a different file
      restart.write("%s/BOUT.final.%s", restartdir.c_str(), restartext.c_str());

      output.write("Monitor signalled to quit. Returning\n");
      break;
    }
  }

#ifdef CHECK
  msg_stack.pop(msg_point);
#endif

  return 0;
}

BoutReal CvodeSolver::run(BoutReal tout) {
#ifdef CHECK
  int msg_point = msg_stack.push("Running solver: solver::run(%e)", tout);
#endif

  MPI_Barrier(BoutComm::get());
  
  rhs_ncalls = 0;

  pre_Wtime = 0.0;
  pre_ncalls = 0.0;

  int flag = CVode(cvode_mem, tout, uvec, &simtime, CV_NORMAL);

  // Copy variables
  load_vars(NV_DATA_P(uvec));

  // Call rhs function to get extra variables at this time
  run_rhs(simtime);

  if(flag < 0) {
    output.write("ERROR CVODE solve failed at t = %e, flag = %d\n", simtime, flag);
    return -1.0;
  }

#ifdef CHECK
  msg_stack.pop(msg_point);
#endif

  return simtime;
}

/**************************************************************************
 * RHS function du = F(t, u)
 **************************************************************************/

void CvodeSolver::rhs(BoutReal t, BoutReal *udata, BoutReal *dudata) {
#ifdef CHECK
  int msg_point = msg_stack.push("Running RHS: CvodeSolver::res(%e)", t);
#endif

  // Load state from udata
  load_vars(udata);

  // Get the current timestep
  // Note: CVodeGetCurrentStep updated too late in older versions
  CVodeGetLastStep(cvode_mem, &hcur);
  
  // Call RHS function
  run_rhs(t);

  // Save derivatives to dudata
  save_derivs(dudata);

#ifdef CHECK
  msg_stack.pop(msg_point);
#endif
}

/**************************************************************************
 * Preconditioner function
 **************************************************************************/

void CvodeSolver::pre(BoutReal t, BoutReal gamma, BoutReal delta, BoutReal *udata, BoutReal *rvec, BoutReal *zvec)
{
#ifdef CHECK
  int msg_point = msg_stack.push("Running preconditioner: CvodeSolver::pre(%e)", t);
#endif

  BoutReal tstart = MPI_Wtime();

  int N = NV_LOCLENGTH_P(uvec);
  
  if(prefunc == NULL) {
    // Identity (but should never happen)
    for(int i=0;i<N;i++)
      zvec[i] = rvec[i];
    return;
  }

  // Load state from udata (as with res function)
  load_vars(udata);

  // Load vector to be inverted into F_vars
  load_derivs(rvec);
  
  (*prefunc)(t, gamma, delta);

  // Save the solution from vars
  save_vars(zvec);

  pre_Wtime += MPI_Wtime() - tstart;
  pre_ncalls++;

#ifdef CHECK
  msg_stack.pop(msg_point);
#endif
}

/**************************************************************************
 * Jacobian-vector multiplication function
 **************************************************************************/

void CvodeSolver::jac(BoutReal t, BoutReal *ydata, BoutReal *vdata, BoutReal *Jvdata)
{
#ifdef CHECK
  int msg_point = msg_stack.push("Running Jacobian: CvodeSolver::jac(%e)", t);
#endif
  
  if(jacfunc == NULL)
    bout_error("ERROR: No jacobian function supplied!\n");
  
  // Load state from ydate
  load_vars(ydata);
  
  // Load vector to be multiplied into F_vars
  load_derivs(vdata);
  
  // Call function
  (*jacfunc)(t);

  // Save Jv from vars
  save_vars(Jvdata);

#ifdef CHECK
  msg_stack.pop(msg_point);
#endif
}

/**************************************************************************
 * CVODE RHS functions
 **************************************************************************/

static int cvode_rhs(BoutReal t, 
		     N_Vector u, N_Vector du, 
		     void *user_data) {
  
  BoutReal *udata = NV_DATA_P(u);
  BoutReal *dudata = NV_DATA_P(du);
  
  CvodeSolver *s = (CvodeSolver*) user_data;
  
  // Calculate RHS function
  s->rhs(t, udata, dudata);

  return 0;
}

/// RHS function for BBD preconditioner
static int cvode_bbd_rhs(CVINT Nlocal, BoutReal t, 
			 N_Vector u, N_Vector du, 
			 void *user_data)
{
  return cvode_rhs(t, u, du, user_data);
}

/// Preconditioner function
static int cvode_pre(BoutReal t, N_Vector yy, N_Vector yp,
		     N_Vector rvec, N_Vector zvec,
		     BoutReal gamma, BoutReal delta, int lr,
		     void *user_data, N_Vector tmp)
{
  BoutReal *udata = NV_DATA_P(yy);
  BoutReal *rdata = NV_DATA_P(rvec);
  BoutReal *zdata = NV_DATA_P(zvec);
  
  CvodeSolver *s = (CvodeSolver*) user_data;

  // Calculate residuals
  s->pre(t, gamma, delta, udata, rdata, zdata);

  return 0;
}

/// Jacobian-vector multiplication function
static int cvode_jac(N_Vector v, N_Vector Jv,
		     realtype t, N_Vector y, N_Vector fy,
		     void *user_data, N_Vector tmp)
{
  BoutReal *ydata = NV_DATA_P(y);   ///< System state
  BoutReal *vdata = NV_DATA_P(v);   ///< Input vector
  BoutReal *Jvdata = NV_DATA_P(Jv);  ///< Jacobian*vector output
  
  CvodeSolver *s = (CvodeSolver*) user_data;
  
  s->jac(t, ydata, vdata, Jvdata);
  
  return 0;
}

#endif
