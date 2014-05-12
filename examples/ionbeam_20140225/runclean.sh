# Script to erase all the files that are not needed for a clean run of bout
# the files included are all the *.pbs.*, *.eps, etc


make clean
rm -f runtest~ *.eps *.o *.pbs.* *.nc *.sh~ *.py~ *.cxx~ *.out *.pbs~ makefile~
rm -f data/*.log.* data/*.restart.* data/*.dmp.* data/BOUT.inp~