"""Visual for CenterlineMask."""
import deltametrics as dm
from deltametrics.mask import CenterlineMask
from deltametrics.mask import ChannelMask

golfcube = dm.sample_data.golf()
channel_mask = ChannelMask(golfcube['velocity'].data[-1, :, :],
                           golfcube['eta'].data[-1, :, :])
centerline_mask = CenterlineMask(channel_mask)
centerline_mask.show()
