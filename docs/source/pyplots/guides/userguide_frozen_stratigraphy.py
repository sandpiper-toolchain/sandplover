import matplotlib.gridspec as gs

golfcube = spl.sample_data.golf()
golfcube.stratigraphy_from("eta")
golfcube.register_section("demo", spl.section.StrikeSection(distance_idx=10))

stratcube = spl.cube.StratigraphyCube.from_DataCube(golfcube, dz=0.05)
stratcube.register_section("demo", spl.section.StrikeSection(distance_idx=10))

fs = stratcube.export_frozen_variable("sandfrac")
fe = stratcube.Z  # exported volume does not have coordinate information!

fig, ax = plt.subplots(figsize=(10, 2))
pcm = ax.pcolormesh(
    np.tile(np.arange(fs.shape[2]), (fs.shape[0], 1)),
    fe[:, 10, :],
    fs[:, 10, :],
    shading="auto",
    cmap=golfcube.varset["sandfrac"].cmap,
    vmin=golfcube.varset["sandfrac"].vmin,
    vmax=golfcube.varset["sandfrac"].vmax,
)
spl.plot.append_colorbar(pcm, ax)
