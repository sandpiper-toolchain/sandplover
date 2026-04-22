import numpy as np
import matplotlib.pyplot as plt

import sandplover as spl

import matplotlib.animation as animation
from matplotlib.gridspec import GridSpec

import matplotlib
import pandas as pd
import xarray as xr

golfcube = spl.sample_data.golf()
golfstrat = spl.cube.StratigraphyCube.from_DataCube(golfcube, dz=0.05)

# do a single demonstration that it works for simple section
strike_section = spl.section.StrikeSection(golfstrat, distance=3000)
strike_section_stratal_surfaces = golfstrat.strata[:, 40, :]

# show the section
cmap = matplotlib.colormaps["viridis"].resampled(91)
fig, ax = plt.subplots(figsize=(5, 2))
for i in range(91):
    ax.plot(golfstrat.strata[i, 40, :], color=cmap(i))
plt.show()