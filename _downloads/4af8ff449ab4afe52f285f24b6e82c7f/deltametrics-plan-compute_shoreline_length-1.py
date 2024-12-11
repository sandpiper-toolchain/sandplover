from deltametrics.mask import ShorelineMask
from deltametrics.plan import compute_shoreline_length
from deltametrics.sample_data.sample_data import golf
#
golf = golf()
#
# Early in model run
#
sm0 = ShorelineMask(
golf['eta'][15, :, :],
elevation_threshold=0,
elevation_offset=-0.5)
#
# Late in model run
#
sm1 = ShorelineMask(
golf['eta'][-1, :, :],
elevation_threshold=0,
elevation_offset=-0.5)
#
# Compute lengths
#
len0 = compute_shoreline_length(sm0)
len1, line1 = compute_shoreline_length(sm1, return_line=True)
#
# Make the plot
#
import matplotlib.pyplot as plt
#
fig, ax = plt.subplots(1, 2, figsize=(6, 3))
golf.quick_show('eta', idx=15, ax=ax[0])
_ = ax[0].set_title('length = {:.2f}'.format(len0))
golf.quick_show('eta', idx=-1, ax=ax[1])
_ = ax[1].plot(line1[:, 0], line1[:, 1], 'r-')
_ = ax[1].set_title('length = {:.2f}'.format(len1))
