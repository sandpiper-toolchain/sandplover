"""Visual for ShoreMask."""

import sandplover as spl
from sandplover.mask import ShorelineMask

golfcube = spl.sample_data.golf()
shore_mask = ShorelineMask(golfcube["eta"].data[-1, :, :])
shore_mask.show()
