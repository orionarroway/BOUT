/*******************************************************************
 * Hall Thruster Model
 *
 * Sandeep and Winston,April 2013
 *******************************************************************/

#include <bout.hxx>
#include <boutmain.hxx>
#include <derivs.hxx>      // Needed to have the d2dx2
#include <cmath>
#include "invert_laplace.hxx"

// Evolving variables
Field3D n, v; //scalar quantities

// Auxiliary (derived) variables
Field3D phi;

// Other variables
BoutReal Te = 1.0;
BoutReal q = 1.0;
BoutReal m = 1.0;

// PARAMETERS

BoutReal n0;
BoutReal v0;
Field2D a;

int phi_flags;

// Group fields together for communication

FieldGroup comms;

/***************************************************************************/

int physics_init(bool restarting) //int specifies the integer output
{
  // Load quantities from grid

  GRID_LOAD(n0); 
  GRID_LOAD(v0);
  GRID_LOAD(a);
   
  // Save these quantities
  
  SAVE_ONCE2(n0, v0);
 
  // Set boundary conditions for phi
  
  phi.setBoundary("phi");

  // SET EVOLVING VARIABLES
  bout_solve(n, "n");
  bout_solve(v, "v");
  
  // Add evolved variables to communication

  comms.add(n);
  comms.add(v);
  
  // Add derived variables to communication

  comms.add(phi);
  
  // Add variables to be dumped to file (time evolved are dumped by default)
  dump.add(phi, "phi", 1);  // flag 1 means every time
  
  return 0;
}

/*********************************************************************/

int physics_run(BoutReal t)
{
  // Solve for derived varibles using laplace inversion
  // Solves \nabla^2_{\perp} x + (1/c)*\nabla_{\perp} c \cdot \nabla x + ax = b
  // Arguments are (b, bit-field, a, c)
  // Passing Null -> missing term

  phi = invert_laplace(-n, phi_flags, &a, NULL);
 
  // Apply B.C on phi
  phi.applyBoundary();
 
  // Communicate derived variables
  mesh->communicate(phi);
  
  // Communicate evolved variables
  mesh->communicate(n);
  mesh->communicate(v);
  
  // evolved equations
  
  ddt(n) = -v0*DDX(n) - DDX(v);

  ddt(v) = -v0*DDX(v) - DDX(phi);
  
  return 0;
}
