import matplotlib.pyplot as plt

import sandplover as spl

golfcube = spl.sample_data.golf()
golfcube.stratigraphy_from("eta")
golfcube.register_section("demo", spl.section.StrikeSection(distance=250))

fig, ax = plt.subplots(4, 1, sharex=True, figsize=(8, 6))
golfcube.sections["demo"].show("depth", data="spacetime", ax=ax[0], label="spacetime")
golfcube.sections["demo"].show("depth", data="preserved", ax=ax[1], label="preserved")
golfcube.sections["demo"].show(
    "depth", data="stratigraphy", ax=ax[2], label="quick stratigraphy"
)
golfcube.sections["demo"].show(
    "depth", style="lines", data="stratigraphy", ax=ax[3], label="quick stratigraphy"
)
