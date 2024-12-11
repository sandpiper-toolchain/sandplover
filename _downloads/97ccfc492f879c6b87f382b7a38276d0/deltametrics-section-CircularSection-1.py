import matplotlib.pyplot as plt
from deltametrics.sample_data.sample_data import golf
from deltametrics.section import CircularSection
#
golfcube = golf()
golfcube.register_section(
    'circular', CircularSection(radius=1200))
#
fig, ax = plt.subplots()
golfcube.quick_show('eta', idx=-1, ax=ax, ticks=True)
golfcube.sections['circular'].show_trace('r--', ax=ax)
