import matplotlib.pyplot as plt
from deltametrics.plan import compute_surface_deposit_time
from deltametrics.plot import append_colorbar
from deltametrics.sample_data.sample_data import golf
#
golf = golf()
sfc_time = compute_surface_deposit_time(golf, surface_idx=-1)
#
fig, ax = plt.subplots()
im = ax.imshow(sfc_time)
_ = append_colorbar(im, ax=ax)
#
# The keyword argument `stasis_tol` is an important control on the resultant
# calculation.
#
fig, ax = plt.subplots(1, 3, figsize=(10, 3))
for i, tol in enumerate([1e-16, 0.01, 0.1]):
    i_sfc_date = compute_surface_deposit_time(
        golf, surface_idx=-1, stasis_tol=tol)
    im = ax[i].imshow(i_sfc_date)
    _ = plt.colorbar(im, ax=ax[i], shrink=0.4)
    _ = ax[i].set_title(f'stasis_tol={tol}')
