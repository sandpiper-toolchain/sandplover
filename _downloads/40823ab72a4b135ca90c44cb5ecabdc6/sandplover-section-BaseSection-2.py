from sandplover.sample_data import golf
from sandplover.section import StrikeSection

golfcube = golf()
golfcube.stratigraphy_from("eta", dz=0.1)
golfcube.register_section("test", StrikeSection(distance_idx=5))

fig, ax = plt.subplots()
# note: transpose `strata` for columns-->lines plotting in matplotlib
ax.plot(golfcube.sections["test"].strata.T)
plt.show()