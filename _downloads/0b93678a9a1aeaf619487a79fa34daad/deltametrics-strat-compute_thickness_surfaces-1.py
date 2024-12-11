import matplotlib.pyplot as plt
import numpy as np
from deltametrics.plot import append_colorbar
from deltametrics.sample_data.sample_data import golf
from deltametrics.strat import compute_thickness_surfaces
#
golfcube = golf()
deposit_thickness0 = compute_thickness_surfaces(
    golfcube['eta'][-1, :, :],
    golfcube['eta'][0, :, :])
deposit_thickness1 = compute_thickness_surfaces(
    golfcube['eta'][-1, :, :],
    np.min(golfcube['eta'], axis=0))
#
fig, ax = plt.subplots(1, 2)
im = ax[0].imshow(deposit_thickness0)
_ = append_colorbar(im, ax=ax[0])
_ = ax[0].set_title('thickness above initial basin')
im = ax[1].imshow(deposit_thickness1)
_ = append_colorbar(im, ax=ax[1])
_ = ax[1].set_title('total deposit thickness')
plt.tight_layout()
