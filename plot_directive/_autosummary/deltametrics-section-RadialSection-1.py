import matplotlib.pyplot as plt
from deltametrics.sample_data.sample_data import golf
from deltametrics.section import RadialSection
#
golfcube = golf()
golfcube.register_section(
    'radial', RadialSection(azimuth=65))
#
fig, ax = plt.subplots()
golfcube.quick_show('eta', idx=-1, ax=ax, ticks=True)
golfcube.sections['radial'].show_trace('r--', ax=ax)
