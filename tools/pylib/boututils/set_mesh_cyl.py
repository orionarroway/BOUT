try:
      from netCDF4 import Dataset
      #from Scientific.IO.NetCDF import NetCDFFile
      #from scipy.io import netcdf
      import subprocess
      import numpy as np
      import sys
      
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


def hlmk_grid(refresh=True):
      import subprocess,sys,os
      from scipy.io.idl import readsav
      
      if refresh:
            # grid_build_str='gdl -e "a = simple_cyl()"'
            # subp = subprocess.check_output(grid_build_str,
            #                                shell = True)
            grid_build_str ='hlmk_grids,/simple,/narrow,/local_r,Bz0=.1,bphi0=0.1,gridname="Helimak_Bz"'
            subprocess.call('gdl -e '+grid_build_str,shell = True)
           
      with open('gridnames.txt') as gridnames:
            for grid in gridnames:
                  grid = (grid.rstrip('\n'))
                  print(grid)
                  s = readsav(grid.rstrip('\n'))
                  print(grid.replace('.dat','.nc'))
                  sav_to_nc(s['data'],grid.replace('.dat','.nc'))

def sav_to_nc(data,filename):
      f = Dataset(filename, "w",format='NETCDF3_CLASSIC')
      # sys.exit()

      
      x = f.createDimension('x',data['nx'])
      y = f.createDimension('y',data['ny'])

      for i,name in enumerate(data.dtype.names):
    
            if not((name.lower() == 'areadme')):
                  
                  if isinstance(data[name][0],(type(np.array([0])))):
                        #try:
                        if (data[name][0].ndim) == 2:#.shape,data[name][0].shape)
                              var = f.createVariable(name,(data[name][0]).dtype,('x','y'))
                              var[:] = np.transpose((data[name])[0]) 
                        if (data[name][0].ndim) == 1:
                              var = f.createVariable(name,(data[name][0]).dtype,('x'))
                              print(data[name][0])
                              print((data[name][0]).shape)
                              var[:] = ((data[name])[0][0:data['nx']]) 
                              print(var)
                        # except:
                        #       print('fail at: '+name.lower()
                        #      )
                              # print((data[name])[0])
                              # print(data[name][0].ndim)
                              # var = f.createVariable(name,(data[name][0]).dtype,('x'))
                        #       #sys.exit()
                           
                        # else:
                              
                        #       #var = f.createVariable(name,(data[name][0]).dtype)
                        #       print("() case")
                        #       print(name.lower())
                        #       print((data[name][0]).shape)
                  else:
                        print("not () case")
                        print(name.lower())
                        print((data[name][0]).shape)
                        print(data[name][0].dtype)
                        var = f.createVariable(name,data[name][0].dtype)
                        var[:] = ((data[name])[0]) 
      
      f.close()

def examine_grid():
      import subprocess,sys,os
      from scipy.io.idl import readsav
      from scipy.io import netcdf
      import numpy as np
      

      s = readsav('Helimak_1x32_0.06000_lam_n.dat')
      data = s['data'] #now we'll dump this to a netcdf
      
      print((data['x_array'])[0])
      print(data['NI_X'])
      f = netcdf.netcdf_file('Helimak_1x32_0.06000_lam_n.nc', 'r')
      print(f.variables['NI_X'].data)
      R = f.variables['RXY']
      print('in .nc')
      
      print(R.shape)

      print(f.variables.keys())
      bpxy = f.variables['BPXY']
      print('bpxy')
      print(bpxy.data[:,15])

      btxy = f.variables['BTXY']
      print('btxy')
      print(btxy.data[:,15])


      Teo = f.variables['TE0']
      print(Teo.data[:,15])
      
      ni_x = f.variables['NI_X']
      print(ni_x.data)
      
      n0 = f.variables['NI0']  
     
      print(n0.data.mean())
      
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

hlmk_grid()
examine_grid()  

#   f.close()
