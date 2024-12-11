import matplotlib.pyplot as plt
from deltametrics.mask import ChannelMask
from deltametrics.sample_data.sample_data import golf
#
golfcube = golf()
cmsk = ChannelMask(
    golfcube['eta'][-1, :, :],
    golfcube['velocity'][-1, :, :],
    elevation_threshold=0,
    flow_threshold=0.3)
#
fig, ax = plt.subplots(1, 2, figsize=(8, 4))
golfcube.quick_show('eta', idx=-1, ax=ax[0])
cmsk.show(ax=ax[1])
