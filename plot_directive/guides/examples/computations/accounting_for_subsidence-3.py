aeolian = dm.sample_data.aeolian()

# define rates, in m/timestep
subs_rates = [0, 0.01, 0.02]

fig, ax = plt.subplots(
    len(subs_rates), 1,
    sharex=True, sharey=True)

for i, su in enumerate(subs_rates):
    # compute stratigraphy for elevation timeseries with subsidence
    vol, elev = dm.strat.compute_boxy_stratigraphy_volume(
        aeolian['eta'], aeolian['time'], sigma_dist=su,
        dz=0.1)

    # section index and calculation for preservation
    sec_idx = aeolian.shape[2] // 2
    sec_data = vol[:, :, sec_idx]
    sec_data_flat = sec_data[~np.isnan(sec_data)]
    fraction_preserved = (len(np.unique(sec_data_flat)) / aeolian.shape[0])

    # show a slice through the section
    im = ax[i].imshow(
        vol[:, :, sec_idx],
        extent=[0, aeolian.dim1_coords[-1], elev.min(), elev.max()],
        aspect='auto', origin='lower')
    cb = dm.plot.append_colorbar(im, ax=ax[i])
    cb.ax.set_ylabel(aeolian['time']['time'].units, fontsize=8)

    # label
    ax[i].text(
        0.02, 0.98,
        (f'subsidence rate: {su:} m/timestep\n'
        f'fraction time preserved: {fraction_preserved:}'),
        fontsize=7, transform=ax[i].transAxes,
        ha='left', va='top')

for axi in ax.ravel():
    axi.set_ylabel('elevation', fontsize=8)
    axi.set_ylim(-15, 10)
    axi.tick_params(labelsize=7)

ax[i].set_xlabel('along section', fontsize=8)

plt.show()