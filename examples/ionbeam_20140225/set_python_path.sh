#!/bin/bash
# Script to load the version of python that has numpy & NetCDF4py
# Script to be used in Nestor machine
# First line loads the python version that has numpy & NetCDF4py
# Second line gives the path to the boututils and boutdata modules
# September 12 2012 

module load python/2.7.2 # It loads the python version we need

export PYTHONPATH=/home/kamuss/BOUT/tools/pylib # Path to bout modules