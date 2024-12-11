import matplotlib.pyplot as plt
from deltametrics.sample_data.sample_data import golf
from deltametrics.section import DipSection
#
golfcube = golf()
golfcube.register_section(
    'dip', DipSection(distance=3000))
fig, ax = plt.subplots()
golfcube.quick_show('eta', idx=-1, ax=ax, ticks=True)
golfcube.sections['dip'].show_trace('r--', ax=ax)
