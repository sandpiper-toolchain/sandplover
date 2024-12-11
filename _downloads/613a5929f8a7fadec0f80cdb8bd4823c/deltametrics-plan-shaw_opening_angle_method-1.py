import matplotlib.pyplot as plt
import numpy as np
from deltametrics.mask import ElevationMask
from deltametrics.plan import shaw_opening_angle_method
from deltametrics.sample_data.sample_data import golf
#
golfcube = golf()
EM = ElevationMask(golfcube["eta"][-1, :, :], elevation_threshold=0)
#
OAM = shaw_opening_angle_method(np.logical_not(EM.mask))
#
fig, ax = plt.subplots()
_ = ax.imshow(OAM, vmin=0, vmax=180)
