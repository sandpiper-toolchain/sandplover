import matplotlib.pyplot as plt
import numpy as np
import deltametrics as dm
#
aeolian = dm.sample_data.aeolian()
nt = 5
ts = np.linspace(0, aeolian["eta"].shape[0] - 1, num=nt, dtype=int)
#
fig, ax = plt.subplots(1, nt, figsize=(8, 4))
for i, t in enumerate(ts):
    _ = ax[i].imshow(aeolian["eta"][t, :, :], vmin=-5, vmax=7)
    _ = ax[i].set_title(f"t = {t}")
    _ = ax[i].axes.get_xaxis().set_ticks([])
    _ = ax[i].axes.get_yaxis().set_ticks([])
_ = ax[0].set_ylabel("northing")
_ = ax[0].set_xlabel("easting")
