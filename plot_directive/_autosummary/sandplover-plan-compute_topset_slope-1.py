from sandplover.sample_data.sample_data import golf
from sandplover.section import RadialSection
from sandplover.plan import compute_topset_slope
#
golf = golf()
azimuth_kwargs = {"num": 5, "start": 90, "end": 180}
origin = (
    np.array([golf.meta["L0"].data, golf.meta["CTR"].data])
    * golf.meta["dx"].data
)
mean_slope, std_slope = compute_topset_slope(
    golf["eta"][-1, :, :], origin=origin, **azimuth_kwargs
)
#
from sandplover.plan import _determine_equally_spaced_azimuths
azimuths = _determine_equally_spaced_azimuths(**azimuth_kwargs)
fig, ax = plt.subplots()
golf.quick_show("eta", -1)
for a, azimuth in enumerate(azimuths):
    a_section = RadialSection(
        golf["eta"][-1, :, :],
        azimuth=azimuth,
        origin=origin,
    )

    a_section.show_trace(ax=ax)
_ = ax.set_title(f"{mean_slope:.2e} $\pm$ {std_slope:.2e}")
