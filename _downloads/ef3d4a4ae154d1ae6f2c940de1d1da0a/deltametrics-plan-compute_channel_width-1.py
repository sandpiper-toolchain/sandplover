import matplotlib.pyplot as plt
from deltametrics.mask import ChannelMask
from deltametrics.plan import compute_channel_width
from deltametrics.sample_data.sample_data import golf
from deltametrics.section import CircularSection
#
# Set up the cube, mask, and section
#
golf = golf()
cm = ChannelMask(
    golf['eta'][-1, :, :],
    golf['velocity'][-1, :, :],
    elevation_threshold=0,
    flow_threshold=0.3)
sec = CircularSection(golf, radius_idx=40)
#
# Compute the metric
#
m, s, w = compute_channel_width(
    cm, section=sec, return_widths=True)
#
fig, ax = plt.subplots()
cm.show(ax=ax, ticks=True)
sec.show_trace('r-', ax=ax)
_ = ax.set_title(f'mean: {m:.2f}; stddev: {s:.2f}')
