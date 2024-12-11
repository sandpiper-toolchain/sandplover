import matplotlib.pyplot as plt
import numpy as np
import deltametrics as dm
#
img, scans = dm.sample_data.savi2020()
nt = 5
ts_i = np.linspace(0, img["red"].shape[0] - 1, num=nt, dtype=int)
ts_s = np.linspace(0, scans["eta"].shape[0] - 1, num=nt, dtype=int)
#
fig, ax = plt.subplots(2, nt, figsize=(9, 6))
for i in range(nt):
    _ = ax[0, i].imshow(img["red"][ts_i[i], :, :], vmin=0, vmax=1)
    _ = ax[0, i].set_title(f"t = {ts_i[i]}")
    _ = ax[1, i].imshow(scans["eta"][ts_s[i], :, :])
    _ = ax[1, i].set_title(f"t = {ts_s[i]}")
#
_ = ax[1, 0].set_ylabel("dim1 direction")
_ = ax[1, 0].set_xlabel("dim2 direction")
