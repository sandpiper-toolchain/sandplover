import matplotlib.pyplot as plt
from deltametrics.mask import DepositMask
from deltametrics.sample_data.sample_data import golf
#
golfcube = golf()
deposit_mask = DepositMask(
    golfcube['eta'][-1, :, :],
    background_value=golfcube['eta'][0, :, :])
fig, ax = plt.subplots(1, 2)
golfcube.quick_show('eta', ax=ax[0])
deposit_mask.show(ax=ax[1])
