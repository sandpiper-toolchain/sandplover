"""Visual for WetMask."""

import sandplover as spl
from sandplover.mask import WetMask

golfcube = spl.sample_data.golf()
wet_mask = WetMask(golfcube["eta"].data[-1, :, :])
wet_mask.show()
