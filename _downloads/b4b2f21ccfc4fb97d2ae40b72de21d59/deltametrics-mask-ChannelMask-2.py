import matplotlib.pyplot as plt
from deltametrics.mask import ChannelMask
from deltametrics.mask import ElevationMask
from deltametrics.mask import FlowMask
from deltametrics.sample_data.sample_data import golf
#
golfcube = golf()
#
# Create the ElevationMask
#
emsk = ElevationMask(
    golfcube['eta'][-1, :, :],
    elevation_threshold=0)
#
# Create the FlowMask
#
fmsk = FlowMask(
    golfcube['velocity'][-1, :, :],
    flow_threshold=0.3)
#
# Make the ChannelMask from the ElevationMask and FlowMask
#
cmsk = ChannelMask.from_mask(emsk, fmsk)
#
fig, ax = plt.subplots(1, 2, figsize=(8, 4))
golfcube.quick_show('eta', idx=-1, ax=ax[0])
cmsk.show(ax=ax[1])
