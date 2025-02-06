"""Visual for ChannelMask."""

import sandplover as spl
from sandplover.mask import ChannelMask

golfcube = spl.sample_data.golf()
channel_mask = ChannelMask(
    golfcube["velocity"].data[-1, :, :], golfcube["eta"].data[-1, :, :]
)
channel_mask.show()
