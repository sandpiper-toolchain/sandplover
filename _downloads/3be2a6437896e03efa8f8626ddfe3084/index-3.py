aeolian = dm.sample_data.aeolian()
nt = 5
ts = np.linspace(0, aeolian['eta'].shape[0]-1, num=nt, dtype=int)

fig, ax = plt.subplots(1, nt, figsize=(8, 4))
for i, t in enumerate(ts):
    ax[i].imshow(aeolian['eta'][t, :, :], vmin=-5, vmax=7)
    ax[i].set_title('t = ' + str(t))
    ax[i].axes.get_xaxis().set_ticks([])
    ax[i].axes.get_yaxis().set_ticks([])
ax[0].set_ylabel('northing')
ax[0].set_xlabel('easting')
plt.show()