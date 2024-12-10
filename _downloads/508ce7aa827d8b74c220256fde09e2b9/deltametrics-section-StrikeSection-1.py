import matplotlib.pyplot as plt
from deltametrics.sample_data.sample_data import golf
from deltametrics.section import StrikeSection
#
golfcube = golf()
golfcube.register_section(
    'strike', StrikeSection(distance=1500))
fig, ax = plt.subplots()
golfcube.quick_show('eta', idx=-1, ax=ax, ticks=True)
golfcube.sections['strike'].show_trace('r--', ax=ax)
