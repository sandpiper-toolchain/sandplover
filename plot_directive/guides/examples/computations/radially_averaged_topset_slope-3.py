# make a copy of the elevation data
elevation = golf["eta"][-1, :, :].copy()

# compute the slope over the full topset
mean_full, std_full = spl.plan.compute_topset_slope(
    elevation, origin=origin
    )

# set up a proximal mask
proximal_mask =  spl.mask.GeometricMask(golf["eta"][-1, :, :])
proximal_mask.circular(rad1=10, rad2=30)
proximal_mask.trim_mask(length=5)

# replace the unmasked data with nan, compute
elevation.data[~proximal_mask.mask] = np.nan
mean_prox, std_prox = spl.plan.compute_topset_slope(
    elevation, origin=origin
    )

fig, ax = plt.subplots()
ax.imshow(golf["eta"][-1], vmin=-5, vmax=1, alpha=0.5)
ax.imshow(elevation, vmin=-5, vmax=1, alpha=1)
ax.set_title(
    f"total: {mean_full:.2e} $\\pm$ {std_full:.2e}\n"
    f"proximal: {mean_prox:.2e} $\\pm$ {std_prox:.2e}"
    )

plt.show()