import matplotlib.pyplot as plt
from deltametrics.cube import StratigraphyCube
from deltametrics.sample_data.sample_data import golf
#
golfcube = golf()
golfstrat = StratigraphyCube.from_DataCube(
    golfcube, dz=0.1)
fig, ax = plt.subplots(2, 1)
golfcube.quick_show('eta', ax=ax[0])  # a Planform (axis=0)
golfstrat.quick_show('eta', idx=100, axis=2, ax=ax[1])  # a DipSection
