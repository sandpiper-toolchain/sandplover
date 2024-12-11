import matplotlib.pyplot as plt
from deltametrics.cube import StratigraphyCube
from deltametrics.sample_data.sample_data import golf
from deltametrics.strat import _determine_deposit_from_background
#
golfcube = golf()
golfstrat = StratigraphyCube.from_DataCube(golfcube, dz=0.05)
#
# Background determined from initial basin topography
#
background0 = _determine_deposit_from_background(
    golfcube['sandfrac'],
    background=golfstrat.Z < golfcube['eta'][0].data)
#
# Background determined from min of bed elevation timeseries
#
background1 = _determine_deposit_from_background(
    golfcube['sandfrac'],
    background=(golfstrat.Z < np.min(golfcube['eta'].data, axis=0)))
#
# Background determined from a fixed sandfrac value
#
background2 = _determine_deposit_from_background(
    golfcube['sandfrac'],
    background=0)
#
fig, ax = plt.subplots(2, 2, figsize=(6, 4))
_ = ax[0, 0].imshow(background0[59], cmap='Greys_r')  # just below initial basin depth
_ = ax[0, 1].imshow(background0[60], cmap='Greys_r')  # just above initial basin depth
_ = ax[1, 0].imshow(background1[59], cmap='Greys_r')  # just below initial basin depth
_ = ax[1, 1].imshow(background2[59], cmap='Greys_r')  # just below initial basin depth
plt.tight_layout()
