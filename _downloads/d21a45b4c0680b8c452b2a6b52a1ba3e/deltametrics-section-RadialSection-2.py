import matplotlib.pyplot as plt
from deltametrics.cube import StratigraphyCube
from deltametrics.sample_data.sample_data import golf
from deltametrics.section import RadialSection
#
golfcube = golf()
golfcube.register_section(
    'radial', RadialSection(azimuth=45))
#
fig, ax = plt.subplots(2, 1, figsize=(8, 4))
golfcube.quick_show('eta', idx=-1, ax=ax[0], ticks=True)
golfcube.sections['radial'].show_trace('r--', ax=ax[0])
golfcube.sections['radial'].show('velocity', ax=ax[1])
#
# Create several `RadialSection` objects, spaced out across the domain,
# connected to a `StratigraphyCube`. Each section should be shorter than
# the full domain width.
#
golfcube = golf()
golfstrat = StratigraphyCube.from_DataCube(golfcube, dz=0.1)
#
fig, ax = plt.subplots(2, 3, figsize=(9, 3))
ax = ax.flatten()
golfcube.quick_show('eta', idx=-1, ax=ax[1], ticks=True)
ax[1].tick_params(labelsize=8)
#
azims = np.linspace(0, 180, num=5)
idxs = [2, 5, 4, 3, 0]  # indices in the order to draw to match 0-->180
for i, (azim, idx) in enumerate(zip(azims, idxs)):
    sec = RadialSection(golfstrat, azimuth=azim, length=4000)
    sec.show_trace('r--', ax=ax[1])
    # sec.show('time', ax=ax[idx], colorbar=False)
    _ = ax[idx].text(3000, 0, 'azimuth: {0}'.format(azim), ha='center', fontsize=8)
    ax[idx].tick_params(labelsize=8)
    _ = ax[idx].set_ylim(-4, 1)
