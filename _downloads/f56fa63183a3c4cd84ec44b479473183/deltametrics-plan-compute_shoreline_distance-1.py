from deltametrics.mask import ShorelineMask
from deltametrics.plan import compute_shoreline_distance
from deltametrics.sample_data.sample_data import golf
#
golf = golf()
#
sm = ShorelineMask(
    golf['eta'][-1, :, :],
    elevation_threshold=0,
    elevation_offset=-0.5)
#
# Compute mean and stddev distance
#
mean, stddev = compute_shoreline_distance(
    sm, origin=[golf.meta['CTR'].data, golf.meta['L0'].data])
#
# Make the plot
#
import matplotlib.pyplot as plt
#
fig, ax = plt.subplots()
golf.quick_show('eta', idx=-1, ticks=True, ax=ax)
_ = ax.set_title('mean = {:.2f}'.format(mean))
