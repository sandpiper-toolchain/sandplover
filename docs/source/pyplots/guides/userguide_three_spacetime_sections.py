golfcube = spl.sample_data.golf()
golfcube.register_section("demo", spl.section.StrikeSection(distance_idx=10))

fig, ax = plt.subplots(3, 1, sharex=True, figsize=(12, 6))
golfcube.show_section("demo", "eta", ax=ax[0], cmap="cividis")
golfcube.show_section("demo", "velocity", ax=ax[1], cmap="plasma")
golfcube.show_section("demo", "sandfrac", ax=ax[2])
