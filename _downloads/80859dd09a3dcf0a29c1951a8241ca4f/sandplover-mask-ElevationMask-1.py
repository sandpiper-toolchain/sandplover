import matplotlib.pyplot as plt
from sandplover.mask import ElevationMask
from sandplover.sample_data.sample_data import golf
#
golfcube = golf()
emsk = ElevationMask(golfcube["eta"][-1, :, :], elevation_threshold=0)
#
fig, ax = plt.subplots(1, 2, figsize=(8, 4))
golfcube.quick_show("eta", idx=-1, ax=ax[0])
emsk.show(ax=ax[1])
