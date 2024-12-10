from deltametrics.mask import ElevationMask
from deltametrics.plan import MorphologicalPlanform
from deltametrics.sample_data.sample_data import golf
#
golfcube = golf()
EM = ElevationMask(
    golfcube['eta'][-1, :, :],
    elevation_threshold=0)
#
MP = MorphologicalPlanform(EM, 10)
#
# The MP stores information computed from the
# :func:`morphological_closing_method`. See the property of the MP,
# the computed :obj:`mean_image` below.
#
import matplotlib.pyplot as plt
from deltametrics.plot import append_colorbar
#
fig, ax = plt.subplots(1, 2, figsize=(7.5, 4))
golfcube.quick_show('eta', idx=-1, ax=ax[0])
im1 = ax[1].imshow(MP.mean_image,
                   cmap='cividis')
_ = append_colorbar(im1, ax=ax[1])
_ = ax[0].set_title('input elevation data')
_ = ax[1].set_title('MP.mean_image')
for i in range(1, 2):
    _ = ax[i].set_xticks([])
    _ = ax[i].set_yticks([])
