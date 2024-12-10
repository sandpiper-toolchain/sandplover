import matplotlib.pyplot as plt
import numpy as np
from deltametrics.plot import _scale_lightness
#
fig, ax = plt.subplots(figsize=(5, 2))
#
# Initial color red
#
red = (1.0, 0.0, 0.0)
_ = ax.plot(-1, 1, 'o', color=red)
#
# Scale from 1 to 0.05
#
scales = np.arange(1, 0, -0.05)
#
# Loop through scales and plot
#
for s, scale in enumerate(scales):
    darker_red = _scale_lightness(red, scale)
    _ = ax.plot(s, scale, 'o', color=darker_red)
