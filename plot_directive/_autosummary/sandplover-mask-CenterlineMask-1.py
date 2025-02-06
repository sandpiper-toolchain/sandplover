import matplotlib.pyplot as plt
from sandplover.mask import CenterlineMask
from sandplover.sample_data.sample_data import golf
#
golfcube = golf()
cntmsk = CenterlineMask(
    golfcube["eta"][-1, :, :],
    golfcube["velocity"][-1, :, :],
    elevation_threshold=0,
    flow_threshold=0.3,
)
#
fig, ax = plt.subplots(1, 2, figsize=(8, 4))
golfcube.quick_show("eta", idx=-1, ax=ax[0])
cntmsk.show(ax=ax[1])
