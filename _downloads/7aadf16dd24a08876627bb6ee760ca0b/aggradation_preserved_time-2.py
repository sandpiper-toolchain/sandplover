# define rates, in m/timestep
agg_rates = [0, 0.01, 0.02]

fig, ax = plt.subplots(
    len(agg_rates), 1,
    sharex=True, sharey=True)

for i, ar in enumerate(agg_rates):
    # set up the aggradation array
    agg_array = np.tile(
        np.linspace(0, aeolian.shape[0]*ar, num=aeolian.shape[0]).reshape(-1, 1, 1),
        (1, aeolian.shape[1], aeolian.shape[2]))

    # compute stratigraphy for elevation timeseries plus aggradation
    vol, elev = dm.strat.compute_boxy_stratigraphy_volume(
        aeolian['eta']+agg_array, aeolian['time'],
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
        20, 15,
        (f'aggration rate: {ar:} m/timestep\n'
         f'fraction time preserved: {fraction_preserved:}'),
        fontsize=7)

for axi in ax.ravel():
    axi.set_ylabel('elevation [m]', fontsize=8)
    axi.set_ylim(-5, 20)
    axi.tick_params(labelsize=7)

ax[i].set_xlabel('along section [m]', fontsize=8)

plt.show()