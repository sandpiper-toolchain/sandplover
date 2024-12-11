import matplotlib.pyplot as plt
from deltametrics.sample_data.sample_data import golf
from deltametrics.section import PathSection
#
golfcube = golf()
golfcube.register_section('path', PathSection(
    path_idx=np.array([[3, 50], [17, 65], [10, 130]])))
fig, ax = plt.subplots()
golfcube.quick_show('eta', idx=-1, ax=ax, ticks=True)
golfcube.sections['path'].show_trace('r--', ax=ax)
