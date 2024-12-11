import matplotlib.pyplot as plt
from deltametrics.sample_data.sample_data import golf
from deltametrics.section import StrikeSection
#
golfcube = golf()
golfcube.register_section('strike', StrikeSection(distance=3500))
#
fig, ax = plt.subplots(2, 1, figsize=(8, 4))
golfcube.quick_show('eta', idx=-1, ax=ax[0], ticks=True)
golfcube.sections['strike'].show_trace('r--', ax=ax[0])
golfcube.sections['strike'].show('velocity', ax=ax[1])
#
# Create a `StrikeSection` that is registered to a `DataCube` at
# specified `distance_idx` index ``=10``, and spans the entire model domain:
#
golfcube = golf()
golfcube.register_section('strike', StrikeSection(distance_idx=10))
#
fig, ax = plt.subplots(2, 1, figsize=(8, 4))
golfcube.quick_show('eta', idx=-1, ax=ax[0], ticks=True)
golfcube.sections['strike'].show_trace('r--', ax=ax[0])
golfcube.sections['strike'].show('velocity', ax=ax[1])
#
# Create a `StrikeSection` that is registered to a `StratigraphyCube` at
# specified `distance` in `dim1` coordinates, and spans only a range in the
# middle of the domain:
#
from deltametrics.cube import StratigraphyCube
#
golfcube = golf()
golfstrat = StratigraphyCube.from_DataCube(golfcube, dz=0.1)
golfstrat.register_section(
    'strike_part', StrikeSection(distance=1500, length=(2000, 5000)))
#
fig, ax = plt.subplots(2, 1, figsize=(8, 4))
golfcube.quick_show('eta', idx=-1, ax=ax[0], ticks=True)
golfstrat.sections['strike_part'].show_trace('r--', ax=ax[0])
golfstrat.sections['strike_part'].show('time', ax=ax[1])
