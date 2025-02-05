"""Visual for ChannelMask."""

import sandplover as dm
from sandplover.mask import ChannelMask

golfcube = dm.sample_data.golf()
channel_mask = ChannelMask(
    golfcube["velocity"].data[-1, :, :], golfcube["eta"].data[-1, :, :]
)
channel_mask.show()
