from deltametrics.mask import ElevationMask
from deltametrics.plan import OpeningAnglePlanform
from deltametrics.sample_data.sample_data import golf
#
golfcube = golf()
_EM = ElevationMask(
    golfcube['eta'][-1, :, :],
    elevation_threshold=0)
#
below_mask = ~(_EM.mask)
#
OAP = OpeningAnglePlanform(below_mask)
#
# The OAP stores information computed from the
# :func:`shaw_opening_angle_method`. See the two properties of the OAP
# :obj:`below_mask` and :obj:`opening_angles`.
#
import matplotlib.pyplot as plt
from deltametrics.plot import append_colorbar
#
fig, ax = plt.subplots(1, 3, figsize=(10, 4))
golfcube.quick_show('eta', idx=-1, ax=ax[0])
im1 = ax[1].imshow(OAP.below_mask, cmap='Greys_r')
im2 = ax[2].imshow(OAP.opening_angles, cmap='jet')
_ = append_colorbar(im2, ax=ax[2])
_ = ax[0].set_title('input elevation data')
_ = ax[1].set_title('OAP.below_mask')
_ = ax[2].set_title('OAP.opening_angles')
for i in range(1, 3):
    _ = ax[i].set_xticks([])
    _ = ax[i].set_yticks([])
