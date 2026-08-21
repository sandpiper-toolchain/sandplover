# In order for these masks to work as expected in the shoreline rugosity
# computation, we need to modify the mask values slightly, to remove the
# land-water boundary that is not really a part of the delta. We use the
# :meth:`~sandplover.mask.BaseMask.trim_mask` method to trim a mask.
#
lm0.trim_mask(length=golf.aux["L0"].data + 1)
sm0.trim_mask(length=golf.aux["L0"].data + 1)
lm1.trim_mask(length=golf.aux["L0"].data + 1)
sm1.trim_mask(length=golf.aux["L0"].data + 1)
#
fig, ax = plt.subplots(1, 2, figsize=(8, 3))
lm0.show(ax=ax[0])
sm0.show(ax=ax[1])
