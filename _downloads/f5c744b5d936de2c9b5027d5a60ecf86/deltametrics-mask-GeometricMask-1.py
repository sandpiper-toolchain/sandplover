import matplotlib.pyplot as plt
from deltametrics.mask import GeometricMask
from deltametrics.sample_data.sample_data import golf
#
golfcube = golf()
arr = golfcube['eta'][-1, :, :]
gmsk = GeometricMask(arr)
#
# Define an angular mask to cover part of the domain from pi/4 to pi/2.
#
gmsk.angular(np.pi/4, np.pi/2)
#
# Further mask this region by defining bounds in the radial direction.
#
gmsk.circular(rad1=10, rad2=50)
#
# Visualize the mask:
#
fig, ax = plt.subplots(1, 2, figsize=(8, 4))
gmsk.show(ax=ax[0])
_ = ax[1].imshow(golfcube['eta'][-1, :, :]*gmsk.mask)
_ = ax[1].set_xticks([])
_ = ax[1].set_yticks([])
