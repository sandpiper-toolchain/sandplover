import matplotlib.pyplot as plt
from deltametrics.mask import GeometricMask
from deltametrics.sample_data.sample_data import golf
#
golfcube = golf()
arr = golfcube['eta'][-1, :, :]
gmsk = GeometricMask(arr)
#
# Define a mask that isolates the region 20-50 pixels from the inlet
#
gmsk.strike(20, 50)
#
# Visualize the mask:
#
fig, ax = plt.subplots(1, 2, figsize=(8, 4))
gmsk.show(ax=ax[0], title='Binary Mask')
_ = ax[1].imshow(golfcube['eta'][-1, :, :] * gmsk.mask)
_ = ax[1].set_xticks([])
_ = ax[1].set_yticks([])
_ = ax[1].set_title('Mask * Topography')
