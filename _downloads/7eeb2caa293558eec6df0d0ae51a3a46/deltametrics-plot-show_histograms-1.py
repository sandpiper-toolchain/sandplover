import matplotlib.pyplot as plt
import numpy as np
from deltametrics.plot import show_histograms
#
locs = [0.25, 1, 0.5, 4, 2]
scales = [0.1, 0.25, 0.4, 0.5, 0.1]
bins = np.linspace(0, 6, num=40)
#
hist_bin_sets = [np.histogram(np.random.normal(l, s, size=500), bins=bins, density=True) for l, s in zip(locs, scales)]
#
fig, ax = plt.subplots()
show_histograms(*hist_bin_sets, sets=[0, 1, 0, 1, 2], ax=ax)
_ = ax.set_xlim((0, 6))
_ = ax.set_ylabel('density')
