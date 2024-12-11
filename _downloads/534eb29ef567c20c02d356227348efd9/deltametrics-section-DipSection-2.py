import matplotlib.pyplot as plt
from deltametrics.sample_data.sample_data import golf
from deltametrics.section import DipSection
#
golfcube = golf()
golfcube.register_section('dip', DipSection(distance=3500))
#
fig, ax = plt.subplots(2, 1, figsize=(8, 4))
golfcube.quick_show('eta', idx=-1, ax=ax[0], ticks=True)
golfcube.sections['dip'].show_trace('r--', ax=ax[0])
golfcube.sections['dip'].show('sandfrac', ax=ax[1])
#
# Create a `DipSection` that is registered to a `DataCube` at
# specified `distance_idx` index ``=75``, and spans the entire model domain:
#
golfcube = golf()
golfcube.register_section('dip75', DipSection(distance_idx=75))
#
fig, ax = plt.subplots(2, 1, figsize=(8, 4))
golfcube.quick_show('eta', idx=-1, ax=ax[0], ticks=True)
golfcube.sections['dip75'].show_trace('r--', ax=ax[0])
golfcube.sections['dip75'].show('sandfrac', ax=ax[1])
#
# Create a `DipSection` that is registered to a `StratigraphyCube` at
# specified `distance` in `dim2` coordinates, and spans only a range in the
# middle of the domain:
#
from deltametrics.cube import StratigraphyCube
#
golfcube = golf()
golfstrat = StratigraphyCube.from_DataCube(golfcube, dz=0.1)
golfstrat.register_section(
    'dip_part', DipSection(distance=4000, length=(500, 1500)))
#
fig, ax = plt.subplots(2, 1, figsize=(8, 4))
golfcube.quick_show('eta', idx=-1, ax=ax[0], ticks=True)
golfstrat.sections['dip_part'].show_trace('r--', ax=ax[0])
golfstrat.sections['dip_part'].show('velocity', ax=ax[1])
