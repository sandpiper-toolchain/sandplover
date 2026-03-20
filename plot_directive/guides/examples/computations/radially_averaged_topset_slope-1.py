golf = spl.sample_data.golf()
origin = (
    np.array([golf.meta["L0"].data, golf.meta["CTR"].data]) * golf.meta["dx"].data
)

# make a map with just five sections to see how this would look
from sandplover.plan import _determine_equally_spaced_azimuths
azimuths = _determine_equally_spaced_azimuths(num=5)

fig, ax = plt.subplots()
golf.quick_show("eta", idx=-1)
for a, azimuth in enumerate(azimuths):
    a_section = spl.section.RadialSection(
        golf["eta"][-1, :, :],
        azimuth=azimuth,
        origin=origin,
    )
    a_section.show_trace(ax=ax)

plt.show()