"""Visual for ShoreMask."""

import sandplover as dm
from sandplover.mask import ShorelineMask

golfcube = dm.sample_data.golf()
shore_mask = ShorelineMask(golfcube["eta"].data[-1, :, :])
shore_mask.show()
