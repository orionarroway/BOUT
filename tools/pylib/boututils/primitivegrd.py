def write_gridXZ(gridfile='primitive.nc',nx=5,nz=33,dx=1,dz=1):
   print 'ok'

def write_grid(gridfile='primitive.nc',nx=5,ny=32,dx=1,dy=1):
   try :
      from netCDF4 import Dataset
    #from Scientific.IO.Netcdf . .  a less 
    #  complete module than netCDF4, no Dataset support
   except ImportError:
      print "ERROR: netcdf4-python module not found"
      raise
   
   
   
   print gridfile
   f = Dataset(gridfile, "w",format='NETCDF3_CLASSIC')
   x = f.createDimension('x',nx)
   y = f.createDimension('y',ny)

   nxx = f.createVariable('nx','i4')
   nyy = f.createVariable('ny','i4')
   nxx[:] = nx
   nyy[:] = ny

   dxx = f.createVariable('dx','f8',('x','y'))
   dyy = f.createVariable('dy','f8',('x','y'))
   dxx[:] = dx
   dyy[:] = dy
   print dx,dy
   
   f.close()

#from primitivegrd import write_grid as wg
