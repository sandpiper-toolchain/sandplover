import numpy as np
import matplotlib.pyplot as plt

from netCDF4 import Dataset
import os

import deltametrics as dm

## create the model data
# some spatial information
x = np.arange(0, 6, 0.1)
y = np.arange(0, 3, 0.1)

# some temporal information
t = np.arange(1, 5)

# meshes for each to make fake data
T, Y, X = np.meshgrid(t, y, x, indexing='ij')

# make fake time by x by y data
#   hint: this would be the data from a model, experiment, or the field
eta = np.sin(T * X + Y)
velocity = np.cos(T * Y + X)
H_SL = np.linspace(0.25, 0.9, num=len(t)) # sea level