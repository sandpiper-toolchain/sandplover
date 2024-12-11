import matplotlib.pyplot as plt
from deltametrics.cube import StratigraphyCube
from deltametrics.sample_data.sample_data import golf
from deltametrics.section import CircularSection
#
golfcube = golf()
golfcube.register_section(
    'circular', CircularSection(radius=1200))
#
fig, ax = plt.subplots(2, 1, figsize=(8, 4))
golfcube.quick_show('eta', idx=-1, ax=ax[0], ticks=True)
golfcube.sections['circular'].show_trace('r--', ax=ax[0])
golfcube.sections['circular'].show('velocity', ax=ax[1])
#
# Create a `CircularSection` that is registered to a `StratigraphyCube` with
# radius index ``=50``, and the origin against the domain edge (using the
# `origin_idx` option):
#
golfcube = golf()
golfstrat = StratigraphyCube.from_DataCube(golfcube, dz=0.1)
golfstrat.register_section(
    'circular', CircularSection(radius_idx=50, origin_idx=(0, 100))
)
#
fig, ax = plt.subplots(2, 1, figsize=(8, 4))
golfcube.quick_show('eta', idx=-1, ax=ax[0], ticks=True)
golfstrat.sections['circular'].show_trace('r--', ax=ax[0])
golfstrat.sections['circular'].show('velocity', ax=ax[1])
