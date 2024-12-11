import matplotlib.pyplot as plt
import numpy as np
from deltametrics.cube import StratigraphyCube
from deltametrics.plot import append_colorbar
from deltametrics.sample_data.sample_data import golf
from deltametrics.strat import compute_net_to_gross
#
golfcube = golf()
golfstrat = StratigraphyCube.from_DataCube(golfcube, dz=0.1)
background = (golfstrat.Z < np.min(golfcube['eta'].data, axis=0))
#
net_to_gross = compute_net_to_gross(
    golfstrat['sandfrac'],
    net_threshold=0.5,
    background=background)
#
fig, ax = plt.subplots(1, 2)
im0 = ax[0].imshow(
    net_to_gross,
    extent=golfstrat.extent)
_ = append_colorbar(im0, ax=ax[0])
im1 = ax[1].imshow(
    net_to_gross,
    cmap=golfstrat.varset['net_to_gross'].cmap,
    norm=golfstrat.varset['net_to_gross'].norm,
    extent=golfstrat.extent)
_ = append_colorbar(im1, ax=ax[1])
plt.tight_layout()
