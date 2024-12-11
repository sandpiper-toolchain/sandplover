import matplotlib.pyplot as plt
import numpy as np
import warnings
import deltametrics as dm
#
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    rcm8 = dm.sample_data.rcm8()
nt = 5
ts = np.linspace(0, rcm8["eta"].shape[0] - 1, num=nt, dtype=int)
#
fig, ax = plt.subplots(1, nt, figsize=(12, 2))
for i, t in enumerate(ts):
    _ = ax[i].imshow(rcm8["eta"][t, :, :], vmin=-2, vmax=0.5)
    _ = ax[i].set_title(f"t = {t}")
    _ = ax[i].axes.get_xaxis().set_ticks([])
    _ = ax[i].axes.get_yaxis().set_ticks([])
_ = ax[0].set_ylabel("y-direction")
_ = ax[0].set_xlabel("x-direction")
