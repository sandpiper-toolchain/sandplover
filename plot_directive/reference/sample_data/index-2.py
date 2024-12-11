import matplotlib.pyplot as plt
import numpy as np
from deltametrics.sample_data.sample_data import xslope
#
xslope0, xslope1 = xslope()
nt = 5
ts = np.linspace(0, xslope0["eta"].shape[0] - 1, num=nt, dtype=int)
#
fig, ax = plt.subplots(2, nt, figsize=(12, 2))
for i, t in enumerate(ts):
    _ = ax[0, i].imshow(xslope0["eta"][t, :, :], vmin=-10, vmax=0.5)
    _ = ax[0, i].set_title(f"t = {t}")
    _ = ax[1, i].imshow(xslope1["eta"][t, :, :], vmin=-10, vmax=0.5)
#
_ = ax[1, 0].set_ylabel("dim1 direction")
_ = ax[1, 0].set_xlabel("dim2 direction")
#
for axi in ax.ravel():
    _ = axi.axes.get_xaxis().set_ticks([])
    _ = axi.axes.get_yaxis().set_ticks([])
