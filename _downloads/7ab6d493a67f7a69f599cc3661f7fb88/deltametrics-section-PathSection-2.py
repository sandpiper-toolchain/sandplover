import matplotlib.pyplot as plt
from deltametrics.sample_data.sample_data import golf
from deltametrics.section import PathSection
#
golfcube = golf()
golfcube.register_section('path', PathSection(
    path=np.array([[2000, 2000], [2000, 6000], [600, 7500]])))
fig, ax = plt.subplots(2, 1, figsize=(8, 4))
golfcube.quick_show('eta', idx=-1, ax=ax[0], ticks=True)
golfcube.sections['path'].show_trace('r--', ax=ax[0])
golfcube.sections['path'].show('velocity', ax=ax[1])
#
# Create a `PathSection` that is registered to a `DataCube` at
# specified indices:
#
golfcube = golf()
golfcube.register_section('path', PathSection(
    path_idx=np.array([[3, 50], [17, 65], [10, 130]])))
fig, ax = plt.subplots(2, 1, figsize=(8, 4))
golfcube.quick_show('eta', idx=-1, ax=ax[0], ticks=True)
golfcube.sections['path'].show_trace('r--', ax=ax[0])
golfcube.sections['path'].show('velocity', ax=ax[1])
