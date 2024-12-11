import matplotlib.pyplot as plt
import numpy as np
from deltametrics.sample_data.sample_data import golf
#
golf = golf()
nt = 5
ts = np.linspace(0, golf["eta"].shape[0] - 1, num=nt, dtype=int)
#
fig, ax = plt.subplots(1, nt, figsize=(12, 2))
for i, t in enumerate(ts):
    _ = ax[i].imshow(golf["eta"][t, :, :], vmin=-2, vmax=0.5)
    _ = ax[i].set_title(f"t = {t}")
    _ = ax[i].axes.get_xaxis().set_ticks([])
    _ = ax[i].axes.get_yaxis().set_ticks([])
_ = ax[0].set_ylabel("dim1 direction")
_ = ax[0].set_xlabel("dim2 direction")
