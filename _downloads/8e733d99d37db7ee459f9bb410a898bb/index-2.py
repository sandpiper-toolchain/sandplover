import matplotlib.pyplot as plt
import numpy as np
import sandplover as spl
#
tdb12 = spl.sample_data.tdb12()
nt = 5
ts = np.linspace(0, tdb12["bed_elevation"].shape[0] - 1, num=nt, dtype=int)
#
fig, ax = plt.subplots(1, nt, figsize=(12, 4))
for i, t in enumerate(ts):
    im = ax[i].imshow(tdb12["bed_elevation"][t, :, :])
    _ = fig.colorbar(im, ax=ax[i], shrink=0.25)
    _ = ax[i].set_title(f"t = {t}")
    _ = ax[i].axes.get_xaxis().set_ticks([])
    _ = ax[i].axes.get_yaxis().set_ticks([])
_ = ax[0].set_ylabel("dim0")
_ = ax[0].set_xlabel("dim1")
plt.tight_layout()
