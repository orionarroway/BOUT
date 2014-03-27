##################################################
#            Data utilities package
#
# Generic routines, useful for all data
##################################################

print "Loading data utilities"

# Load routines from separate files
try:
    from showdata import showdata,savemovie,new_save_movie
except:
    print "No showdata"

try:
    from plotdata import plotdata
except:
    print "No plotdata"

try:
    from datafile import DataFile
except:
    print "No datafile"

try:
    from calculus import deriv, integrate
except:
    print "No calculus"

try:
    from file_import import file_import
except:
    print "no file_import"

try:
    from primitivegrd import write_grid
except:
    print 'no write grid'

try:
    from examine_nc import examine_nc
except:
    print 'no examine_grid'
