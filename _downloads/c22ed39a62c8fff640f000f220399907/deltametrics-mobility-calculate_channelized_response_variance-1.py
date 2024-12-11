import matplotlib.pyplot as plt
import numpy as np
from deltametrics.mobility import calculate_channelized_response_variance
from deltametrics.plot import append_colorbar
from deltametrics.sample_data.sample_data import savi2020
#
# Load overhead imagery sample data from Savi et al 2020
#
img, _ = savi2020()
#
# Calculate the CRV on the "Red" band
#
crv_mag, slopes, crv = calculate_channelized_response_variance(
   img['red'].data, threshold=0.0,
   normalize_input=True, normalize_output=True)
#
# Plot the results
#
fig, ax = plt.subplots(1, 3, figsize=(13, 5))
i0 = ax[0].imshow(crv_mag, vmin=0, vmax=1)
_ = ax[0].set_title('CRV Magnitude')
_ = append_colorbar(i0, ax=ax[0], size=10)
s_ex = np.max([np.abs(slopes.min()), slopes.max()])
i1 = ax[1].imshow(slopes, vmin=-1*s_ex, vmax=s_ex, cmap='PuOr')
_ = ax[1].set_title('CRV Slopes')
_ = append_colorbar(i1, ax=ax[1], size=10)
i2 = ax[2].imshow(crv, vmin=-1, vmax=1, cmap='seismic')
_ = ax[2].set_title('Directional CRV')
_ = append_colorbar(i2, ax=ax[2], size=10)
_ = fig.suptitle('CRV of Red band from imagery from Savi et al 2020')
