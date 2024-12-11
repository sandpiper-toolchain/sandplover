import matplotlib.pyplot as plt
import numpy as np
from deltametrics.cube import StratigraphyCube
from deltametrics.sample_data.sample_data import golf
from deltametrics.strat import compute_sedimentograph
#
golfcube = golf()
golfstrat = StratigraphyCube.from_DataCube(golfcube, dz=0.1)
#
background = (golfstrat.Z < np.min(golfcube['eta'].data, axis=0))
#
(sedimentograph, radii, bins) = compute_sedimentograph(
    golfstrat['sandfrac'],
    num_sections=50,
    last_section_radius=2750,
    background=background,
    origin_idx=[3, 100])
#
fig, ax = plt.subplots()
_ = ax.plot(
    radii,
    sedimentograph[:, 1],
    marker='o', ls='-')
_ = ax.set_xlabel('section radius (m)')
_ = ax.set_ylabel(f'fraction > {bins[1]}')
