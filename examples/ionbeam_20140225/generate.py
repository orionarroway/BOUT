#!/usr/bin/env python
# Generate an input mesh for 1D ion beam problem
# Winston Frias Pombo
# January 15, 2014

from boututils import DataFile # wrapper around Netcdf4 libraries
import numpy as np

# === Size of domain === #

nx  = 64    # minimum is 5: 2 boundaries and 1 evolved
ny  = 5   # minimum 5. Should be power of 2 

# === Normalized quantities === #

v0 = 2    # velocity [au]
n0 = 1    # density  [au]

# === Domain boundaries ===== #

# == range of BOUT X

Xmin = 0.0                # bottom boundary [au]
Xmax = 35.0                # top boundary [au]

dX = (Xmax - Xmin)/(nx - 1)

# == Set geometry on the grid == #

dx = np.zeros((nx, ny), float)

for ix in range(nx):
    for jy in range(ny):
        dx[ix, jy]  = dX

a = np.zeros((nx, ny), float)

for ix in range(nx):
    for jy in range(ny):
        a[ix, jy] = -1.0

        

# === Print normalization information === #
print '=============================='
print ' n0 = ', n0
print ' v0 = ', v0
print '=============================='

# ============== Write to grid file ============ #

f=DataFile() 
f.open("slab.grd.nc",create=True)
                                    
f.write("nx" ,nx)         #write the value of nx to the element of name "nx" in f
f.write("ny", ny)

# == auxiliary quantities == #

f.write("dx", dx)
f.write("a", a)

# == normalization quantities == #

f.write("n0", n0)
f.write("v0", v0)


f.close()		   
		   
		   
		   

		
		
