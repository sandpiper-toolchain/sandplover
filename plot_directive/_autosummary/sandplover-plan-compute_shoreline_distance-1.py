from sandplover.mask import ShorelineMask
from sandplover.plan import compute_shoreline_distance
from sandplover.sample_data.sample_data import golf
#
golf = golf()
#
sm = ShorelineMask(
    golf["eta"][-1, :, :], elevation_threshold=0, elevation_offset=-0.5
)
#
# Compute mean and stddev distance
#
mean, stddev = compute_shoreline_distance(
    sm, origin=[golf.aux["L0"].data, golf.aux["CTR"].data]
)
#
# Make the plot
#
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
golf.quick_show("eta", idx=-1, ticks=True, ax=ax)
dx = golf.aux["dx"].data
origin_x = golf.aux["CTR"].data * dx
origin_y = golf.aux["L0"].data * dx
_ = ax.plot(origin_x, origin_y, "ro")
_ = ax.set_title("mean = {:.2f}".format(mean))
