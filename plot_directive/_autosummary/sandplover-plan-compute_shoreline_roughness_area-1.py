from sandplover.mask import LandMask
from sandplover.mask import ShorelineMask
from sandplover.sample_data.sample_data import golf
#
golf = golf()
#
lm0 = LandMask(
    golf["eta"][15, :, :], elevation_threshold=0, elevation_offset=-0.5
)
sm0 = ShorelineMask(
    golf["eta"][15, :, :], elevation_threshold=0, elevation_offset=-0.5
)
#
lm1 = LandMask(
    golf["eta"][-1, :, :], elevation_threshold=0, elevation_offset=-0.5
)
sm1 = ShorelineMask(
    golf["eta"][-1, :, :], elevation_threshold=0, elevation_offset=-0.5
)
#
# Let's take a quick peek at the masks that we have created.
#
import matplotlib.pyplot as plt
#
fig, ax = plt.subplots(1, 2, figsize=(8, 3))
lm0.show(ax=ax[0])
sm0.show(ax=ax[1])
