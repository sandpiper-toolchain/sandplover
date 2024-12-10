from deltametrics.mask import LandMask
from deltametrics.mask import ShorelineMask
from deltametrics.plan import compute_land_area
from deltametrics.sample_data.sample_data import golf
#
golf = golf()
#
# Early in model run
#
lm0 = LandMask(
    golf['eta'][15, :, :],
    elevation_threshold=0,
    elevation_offset=-0.5)
sm0 = ShorelineMask(
    golf['eta'][15, :, :],
    elevation_threshold=0,
    elevation_offset=-0.5)
#
# Late in model run
#
lm1 = LandMask(
    golf['eta'][-1, :, :],
    elevation_threshold=0,
    elevation_offset=-0.5)
sm1 = ShorelineMask(
    golf['eta'][-1, :, :],
    elevation_threshold=0,
    elevation_offset=-0.5)
#
# Let's take a quick peek at the masks that we have created.
#
import matplotlib.pyplot as plt
#
fig, ax = plt.subplots(1, 2, figsize=(8, 3))
lm0.show(ax=ax[0])
sm0.show(ax=ax[1])
#
# In order for these masks to work as expected in the shoreline roughness
# computation, we need to modify the mask values slightly, to remove the
# land-water boundary that is not really a part of the delta. We use the
# :meth:`~deltametrics.mask.BaseMask.trim_mask` method to trim a mask.
#
lm0.trim_mask(length=golf.meta['L0'].data+1)
sm0.trim_mask(length=golf.meta['L0'].data+1)
lm1.trim_mask(length=golf.meta['L0'].data+1)
sm1.trim_mask(length=golf.meta['L0'].data+1)
#
fig, ax = plt.subplots(1, 2, figsize=(8, 3))
lm0.show(ax=ax[0])
sm0.show(ax=ax[1])
#
# And now, we can proceed with the calculation.
#
# Compute roughnesses
#
from deltametrics.plan import compute_shoreline_roughness
#
rgh0 = compute_shoreline_roughness(sm0, lm0)
rgh1 = compute_shoreline_roughness(sm1, lm1)
#
# Make the plot
#
fig, ax = plt.subplots(1, 2, figsize=(6, 3))
golf.quick_show('eta', idx=15, ax=ax[0])
_ = ax[0].set_title('roughness = {:.2f}'.format(rgh0))
golf.quick_show('eta', idx=-1, ax=ax[1])
_ = ax[1].set_title('roughness = {:.2f}'.format(rgh1))
