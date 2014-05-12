#!/usr/bin/env python

# Run the text example to produce output

nproc=2     # Number of processors

from boutdata import collect
import numpy as np
import matplotlib.pyplot as plt

# Collect the data

n    = collect("n", path="data")
v    = collect('v', path="data")
phi  = collect("phi", path="data")
time = collect("t_array", path="data")

nt = np.size(time)

# Make the figures

plt.figure(1)
plt.plot(time, n[:, 10, 3, 0], 'r-o', time, v[:, 10, 3, 0], 'b-x', time, phi[:, 10, 3, 0], 'm-o')
plt.xlabel('time')
plt.legend(['n','v', '$\phi$'])
plt.savefig('plasma_parameters.eps')

"""
# Plot of close-up of ni

plt.figure(2)
plt.plot(time[0:np.int(nt/2)], ni[0:np.int(nt/2), 10, 3, 10], 'r-o')
plt.xlabel('time')
plt.ylabel('ni')
plt.yscale('log')
plt.savefig('ni_close_up.eps')

# Calculate transport

flux = ni*phi

plt.figure(3)
plt.plot(time, flux[:, 10, 3, 10])
plt.xlabel('time')
plt.ylabel('flux')
plt.savefig('flux.eps')
"""
