import matplotlib.pyplot as plt
from deltametrics.mask import ShorelineMask
from deltametrics.sample_data.sample_data import golf
#
golfcube = golf()
smsk = ShorelineMask(
    golfcube['eta'][-1, :, :],
    elevation_threshold=0)
#
fig, ax = plt.subplots(1, 2, figsize=(8, 4))
golfcube.quick_show('eta', idx=-1, ax=ax[0])
smsk.show(ax=ax[1])
