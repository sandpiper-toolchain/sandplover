import matplotlib.pyplot as plt
import numpy as np
from deltametrics.mask import ChannelMask
from deltametrics.mobility import channel_presence
from deltametrics.plot import append_colorbar
from deltametrics.sample_data.sample_data import golf
#
golfcube = golf()
(x, y) = np.shape(golfcube['eta'][-1, ...])
#
# Calculate channel masks/presence over final 5 timesteps
#
chmap = np.zeros((5, x, y))  # initialize channel map
for i in np.arange(-5, 0):
    chmap[i, ...] = ChannelMask(
        golfcube['eta'][i, ...], golfcube['velocity'][i, ...],
        elevation_threshold=0, flow_threshold=0).mask
fig, ax = plt.subplots(1, 2)
golfcube.quick_show('eta', ax=ax[0])  # final delta
p = ax[1].imshow(channel_presence(chmap), cmap='Blues')
_ = append_colorbar(p, ax[1], label='Channelized Time')
