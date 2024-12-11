time_bins = np.linspace(0, float(golfcube.t[-1]), num=7)
(time_sedimentograph,
    time_radii,
    _) = dm.strat.compute_sedimentograph(
    golfstrat['time'],
    num_sections=50,
    last_section_radius=2750,
    sediment_bins=time_bins,
    background=background,
    origin_idx=[3, 100])

import matplotlib
cmap = matplotlib.colormaps['viridis'].resampled(6)
cycler = matplotlib.cycler('color', cmap.colors)
fig, ax = plt.subplots()
ax.set_prop_cycle(cycler)
lines = ax.plot(
    time_radii,
    time_sedimentograph,
    'o-')
ax.set_ylim(0, 1)
time_bin_labels = [f"{time_bins[b]/1e6:.1f}--{time_bins[b+1]/1e6:.1f} million seconds" for b in np.arange(len(time_bins)-1)]
ax.legend(lines, time_bin_labels)
ax.set_xlabel('radial distance from apex (m)')
ax.set_ylabel('stratigraphy fraction in time bin')
plt.show()