diff_time = golfcube['eta'][t_idxs[-1], :, :] - golfcube['eta'][t_idxs[-2], :, :]
max_delta = abs(diff_time).max()
fig, ax = plt.subplots(figsize=(5, 3))
im = ax.imshow(
    diff_time, cmap='RdBu',
    vmax=max_delta,
    vmin=-max_delta)
cb = dm.plot.append_colorbar(im, ax)  # a convenience function
plt.show()
