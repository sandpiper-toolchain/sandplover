import matplotlib.pyplot as plt
from deltametrics.mask import FlowMask
from deltametrics.sample_data.sample_data import golf
#
golfcube = golf()
fvmsk = FlowMask(
    golfcube['velocity'][-1, :, :],
    flow_threshold=0.3)
fdmsk = FlowMask(
    golfcube['discharge'][-1, :, :],
    flow_threshold=4)
#
fig, ax = plt.subplots(1, 2)
fvmsk.show(ax=ax[0])
fdmsk.show(ax=ax[1])
