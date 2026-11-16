golfcube = spl.sample_data.golf()
golfcube.stratigraphy_from("eta")
golfcube.register_section("demo", spl.section.StrikeSection(distance_idx=10))


fig, ax = plt.subplots(5, 1, sharex=True, sharey=True, figsize=(12, 12))
ax = ax.flatten()
for i, var in enumerate(["time", "eta", "velocity", "discharge", "sandfrac"]):
    cmap = {"eta": "cividis", "velocity": "plasma", "discharge": "Blues"}.get(var, None)
    golfcube.show_section(
        "demo",
        var,
        ax=ax[i],
        label=True,
        style="shaded",
        data="stratigraphy",
        cmap=cmap,
    )
