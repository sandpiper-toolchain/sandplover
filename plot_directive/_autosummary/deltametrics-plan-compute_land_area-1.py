import matplotlib.pyplot as plt
from deltametrics.mask import LandMask
from deltametrics.plan import compute_land_area
from deltametrics.sample_data.sample_data import golf
#
golf = golf()
#
lm = LandMask(
    golf['eta'][-1, :, :],
    elevation_threshold=golf.meta['H_SL'][-1],
    elevation_offset=-0.5)
#
lm.trim_mask(length=golf.meta['L0'].data+1)
#
land_area = compute_land_area(lm)
#
fig, ax = plt.subplots()
lm.show(ax=ax, ticks=True)
_ = ax.set_title(f'Land area is {land_area/1e6:.1f} km$^2$')
