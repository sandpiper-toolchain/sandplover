nt = 5
t_idxs = np.linspace(0, golfcube.shape[0]-1, num=nt, dtype=int)  # linearly interpolate t_idxs
fig, ax = plt.subplots(1, nt, figsize=(12, 2))
for i, idx in enumerate(t_idxs):
    ax[i].imshow(golfcube['eta'][idx, :, :], vmin=-2, vmax=0.5)  # show the slice
    ax[i].set_title('idx = {0}'.format(idx))
    ax[i].set_xticks([])
    ax[i].set_yticks([])
ax[0].set_ylabel('dim1 \n direction')
ax[0].set_xlabel('dim2 direction')
plt.show()
