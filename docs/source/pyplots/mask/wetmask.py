"""Visual for WetMask."""

import sandplover as dm
from sandplover.mask import WetMask

golfcube = dm.sample_data.golf()
wet_mask = WetMask(golfcube["eta"].data[-1, :, :])
wet_mask.show()
