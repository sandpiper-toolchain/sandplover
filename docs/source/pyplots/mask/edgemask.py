"""Visual for EdgeMask."""

import sandplover as spl
from sandplover.mask import EdgeMask

golfcube = spl.sample_data.golf()
edge_mask = EdgeMask(golfcube["eta"].data[-1, :, :])
edge_mask.show()
