import matplotlib.pyplot as plt
from deltametrics.plot import aerial_view
from deltametrics.plot import overlay_sparse_array
from deltametrics.sample_data.sample_data import golf
#
golfcube = golf()
elevation_data = golfcube['eta'][-1, :, :]
sparse_data = golfcube['discharge'][-1, ...]
#
fig, ax = plt.subplots(1, 3, figsize=(8, 3))
for axi in ax.ravel():
    _ = aerial_view(elevation_data, ax=axi)
#
_ = overlay_sparse_array(
    sparse_data, ax=ax[0])  # default clip is (None, 90)
_ = overlay_sparse_array(
    sparse_data, alpha_clip=(None, None), ax=ax[1])
_ = overlay_sparse_array(
    sparse_data, alpha_clip=(70, 90), ax=ax[2])
#
plt.tight_layout()
#
fig, ax = plt.subplots(1, 3, figsize=(8, 3))
for axi in ax.ravel():
    _ = aerial_view(elevation_data, ax=axi)
#
_ = overlay_sparse_array(
    sparse_data, ax=ax[0],
    clip_type='value')  # default clip is (None, 90)
_ = overlay_sparse_array(
    sparse_data, ax=ax[1],
    alpha_clip=(None, 0.2), clip_type='value')
_ = overlay_sparse_array(
    sparse_data, ax=ax[2],
    alpha_clip=(0.4, 0.6), clip_type='value')
#
plt.tight_layout()
