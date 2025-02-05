"""Visual for LandMask."""

import sandplover as spl
from sandplover.mask import LandMask

golfcube = spl.sample_data.golf()
land_mask = LandMask(golfcube["eta"].data[-1, :, :])
land_mask.show()
