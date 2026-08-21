from sandplover.mask import ShorelineMask
from sandplover.plan import compute_shoreline_roughness_radius
from sandplover.sample_data.sample_data import golf
#
golf = golf()
sm = ShorelineMask(
    golf["eta"][-1, :, :], elevation_threshold=0, elevation_offset=-0.5
)
sm.trim_mask(length=golf.aux["L0"].data + 1)
origin = (
    np.array([golf.aux["L0"].data, golf.aux["CTR"].data])
    * golf.aux["dx"].data
)
#
# Compute roughness
#
rough = compute_shoreline_roughness_radius(sm, origin=origin)
#
fig, ax = plt.subplots()
sm.show(ax=ax)
_ = ax.set_title("roughness = {:.2f}".format(rough))
