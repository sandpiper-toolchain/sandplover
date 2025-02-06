import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation

import sandplover as spl

def update_field(i):
    im.set_data(golf['eta'][i, :, :])

golf = spl.sample_data.golf()

time_idxs = np.arange(0, golf.shape[0]-1)

cmap, norm = spl.plot.cartographic_colormap(H_SL=0.0, h=4.5, n=1.0)

fig, ax = plt.subplots()
im = ax.imshow(
    golf['eta'][0, :, :],
    extent=golf.extent,
    cmap=cmap, norm=norm
    )