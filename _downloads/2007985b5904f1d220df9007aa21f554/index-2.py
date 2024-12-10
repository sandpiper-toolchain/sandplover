xslope0, xslope1 = dm.sample_data.xslope()
nt = 5
ts = np.linspace(0, xslope0['eta'].shape[0]-1, num=nt, dtype=int)

fig, ax = plt.subplots(2, nt, figsize=(12, 2))
for i, t in enumerate(ts):
    ax[0, i].imshow(xslope0['eta'][t, :, :], vmin=-10, vmax=0.5)
    ax[0, i].set_title('t = ' + str(t))
    ax[1, i].imshow(xslope1['eta'][t, :, :], vmin=-10, vmax=0.5)

ax[1, 0].set_ylabel('dim1 direction')
ax[1, 0].set_xlabel('dim2 direction')

for axi in ax.ravel():
    axi.axes.get_xaxis().set_ticks([])
    axi.axes.get_yaxis().set_ticks([])

plt.show()