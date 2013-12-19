try:
      from netCDF4 import Dataset
      import subprocess
except:
      exit()


def run_idl_grid():
      import subprocess
      
      grid_build_str="hlmk_grids,/simple,Bz0=.1,bphi0=0.0"


      subp = subprocess.Popen("gdl -e "+grid_build_str,
                              stderr = subprocess.PIPE, stdout = subprocess.PIPE, 
                              shell = True)
      

      (idl_stdout, idl_stderr) = subp.communicate()
      print(idl_stdout)


def hlmk_grid():
      import subprocess,sys,os
      from scipy.io.idl import readsav
      import numpy as np
      
      #grid_build_str="echo 'a = simple_cyl()' | gdl"
      grid_build_str='gdl -e "a = simple_cyl()"'
  
      subp = subprocess.check_output(grid_build_str,
                             shell = True)
      s = readsav('/tmp/hlmktmp.dat')
      data = s['data'] #now we'll dump this to a netcdf
      # print(type(data))
      # os._exit(0)
      f = Dataset('hlmk.nc', "w",format='NETCDF3_CLASSIC')
      x = f.createDimension('x',data['nx'])
      y = f.createDimension('y',data['ny'])
      


      for i,name in enumerate(data.dtype.names):
            #name = dtype.name
            # print(name.lower() , name.lower() == 'nx')
            print((name.lower()))
            print(((data.dtype[i])))
           # print(type(data[name]))
            # print(type('nx'))
            if not((name.lower() ==  'nx') or (name.lower() == 'ny')):
                  print(name,name.lower())
                  
                  
                  #print((data[name]).shape)
                  try:
                        status = f.createVariable(name,data.dtype[i])
                        #print((data[name][0]).shape)
                        # print(dir((data[name])))
                        # print(type((data[name])))
                  except:
                        
                        print('did nothing')
                        print(type(data[name][0]) == type(np.array([])))
                        if (type(data[name][0])) == type(np.array([])):
                              if (data[name][0].ndim)==2:
                                    status = f.createVariable(name,(data[name][0]).dtype,('x','y'))
                              elif (data[name][0].ndim)==1:
                                    status = f.createVariable(name,(data[name][0]).dtype,('x'))
                              else:
                                    status = f.createVariable(name,(data[name][0]).dtype)

                              print((data[name][0]).dtype)
      # for elem in enumerate(data.dtype):
      #       print(elem)

      print((data.dtype))
      # print((data.dtype.type))
      # print(((data.dtype[1])))
      # print((data.dtype.names))
      # print(type((data.dtype[1])))
      #)
      
      # print(data.dtype.name)
      # print(data.dtype.name)
      # print(data.dtype.name)    
 
      # print((data).shape)
      
      # print(data)
            
      f.close()
# def write_cyl_grid(gridfile='standard.nc',nx = 32,ny=3,dx=1,dy=1,
#                    ni0=1.0e17,Te0=10.0,Ti0 =1.0,
#                    Bz0=.01,bphi0=.1,
#                    rMin = 1, rMax=1.5, Zmax=2.0,
#                    ni_profile_type = 1,te_profile_type = 2,
#                    ti_profile_type = 1,phi_profile_type = 0,
#                    expr_prof = None,mxg = 2):

#       #Tempratures are in eV
#       #densities in m^-3
#       #phi in V?

#       nx = nx+2*mxg
      

#   # mesh->get(I,    "sinty");// m^-2 T^-1
#   # mesh->get(Psixy, "psixy");//get Psi             
#   # mesh->get(Psiaxis,"psi_axis");//axis flux      
#   # mesh->get(Psibndry,"psi_bndry");//edge flux 
  
#   # When iysptrx=Nr:  periodic boundary condition
#   # When iysptrx=0:   sheath plate, material wall condition
      

#       variable_list =['Jpar0','pressure','bxcv','Rxy','Bpxy','Bxy','hthe','I']
      
#       norms = ['Lbar','Bbar']
      
#       f = Dataset(gridfile, "w",format='NETCDF3_CLASSIC')
#       x = f.createDimension('x',nx)
#       y = f.createDimension('y',ny)
      
#       nxx = f.createVariable('nx','i4')
#       nyy = f.createVariable('ny','i4')
#       nxx[:] = nx
#       nyy[:] = ny
      
#       dxx = f.createVariable('dx','f8',('x','y'))
#       dyy = f.createVariable('dy','f8',('x','y'))
#       dxx[:] = dx
#       dyy[:] = dy

  

#   f.close()
