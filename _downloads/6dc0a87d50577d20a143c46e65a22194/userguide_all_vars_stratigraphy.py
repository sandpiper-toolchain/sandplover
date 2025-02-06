golfcube = spl.sample_data.golf()

stratcube = spl.cube.StratigraphyCube.from_DataCube(golfcube, dz=0.05)
stratcube.register_section("demo", spl.section.StrikeSection(distance_idx=10))

fig, ax = plt.subplots(5, 1, sharex=True, sharey=True, figsize=(12, 9))
ax = ax.flatten()
for i, var in enumerate(["time", "eta", "velocity", "discharge", "sandfrac"]):
    stratcube.show_section(
        "demo", var, ax=ax[i], label=True, style="shaded", data="stratigraphy"
    )
