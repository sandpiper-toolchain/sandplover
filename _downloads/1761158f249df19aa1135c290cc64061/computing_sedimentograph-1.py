# set up the data source
golfcube = dm.sample_data.golf()
golfstrat = dm.cube.StratigraphyCube.from_DataCube(golfcube, dz=0.05)

background = (golfstrat.Z < np.min(golfcube['eta'].data, axis=0))
frozen_sand = golfstrat.export_frozen_variable('sandfrac')

(sedimentograph,
    section_radii,
    sediment_bins) = dm.strat.compute_sedimentograph(
    frozen_sand,
    num_sections=50,
    last_section_radius=2750,
    background=background,
    origin_idx=[golfcube.meta['L0'], golfcube.meta['CTR']])

fig, ax = plt.subplots()
ax.plot(
    section_radii,
    sedimentograph[:, 1],  # plot only the second bin (sandfrac > 0.5)
    'o-')
ax.set_xlabel('radial distance from apex (m)')
ax.set_ylabel('stratigraphy "sandfrac" fraction > 0.5')
plt.show()