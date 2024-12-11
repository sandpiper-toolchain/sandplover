import matplotlib.pyplot as plt
import numpy as np
from deltametrics.mask import GeometricMask
from deltametrics.sample_data.sample_data import golf
#
golfcube = golf()
arr = golfcube['eta'][-1, :, :]
gmsk = GeometricMask(arr)
#
# Define an angular mask to cover part of the domain from 0 to pi/3
#
gmsk.angular(0, np.pi/3)
#
# Visualize the mask:
#
fig, ax = plt.subplots(1, 2, figsize=(8, 4))
gmsk.show(ax=ax[0], title='Binary Mask')
_ = ax[1].imshow(golfcube['eta'][-1, :, :] * gmsk.mask)
_ = ax[1].set_xticks([])
_ = ax[1].set_yticks([])
_ = ax[1].set_title('Mask * Topography')
