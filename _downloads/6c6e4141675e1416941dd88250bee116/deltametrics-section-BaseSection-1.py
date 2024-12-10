from deltametrics.sample_data.sample_data import golf
from deltametrics.section import StrikeSection
#
golfcube = golf()
golfcube.register_section(
    'demo', StrikeSection(distance_idx=5))
golfcube.sections['demo'].show('velocity')
#
# Note that the last line above is functionally equivalent to
# ``golfcube.show_section('demo', 'velocity')``.
#
# *Example 2:* Display a section, with "quick" stratigraphy, as the
# `depth` attribute, displaying several different section styles.
#
import matplotlib.pyplot as plt
#
golfcube.stratigraphy_from('eta')
golfcube.register_section(
    'demo', StrikeSection(distance=250))
#
fig, ax = plt.subplots(4, 1, sharex=True, figsize=(6, 9))
golfcube.sections['demo'].show('depth', data='spacetime',
                                ax=ax[0], label='spacetime')
golfcube.sections['demo'].show('depth', data='preserved',
                               ax=ax[1], label='preserved')
golfcube.sections['demo'].show('depth', data='stratigraphy',
                               ax=ax[2], label='quick stratigraphy')
golfcube.sections['demo'].show('depth', style='lines', data='stratigraphy',
                               ax=ax[3], label='quick stratigraphy')          # noqa: E501
