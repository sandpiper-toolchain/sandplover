import sandplover as spl

golf = spl.sample_data.golf()
origin = np.array([golf.meta["L0"].data, golf.meta["CTR"].data]) * golf.meta["dx"].data

azimuth_kwargs = {"num": 7}
shore_mask = spl.mask.ShorelineMask(golf["eta"][-1], elevation_threshold=0)

mean_radius, std_radius = spl.plan.compute_shoreline_radius(
    shore_mask, origin=origin, **azimuth_kwargs
)

# make a map to visualize the calculation
from sandplover.plan import _determine_equally_spaced_azimuths

azimuths = _determine_equally_spaced_azimuths(**azimuth_kwargs)

fig, ax = plt.subplots()
shore_mask.show(ax=ax, ticks=True)
for a, azimuth in enumerate(azimuths):
    a_section = spl.section.RadialSection(
        golf["eta"][-1, :, :],
        azimuth=azimuth,
        origin=origin,
    )
    a_section.show_trace(ax=ax)

ax.set_title(f"{mean_radius:.0f} $\pm$ {std_radius:.0f}")