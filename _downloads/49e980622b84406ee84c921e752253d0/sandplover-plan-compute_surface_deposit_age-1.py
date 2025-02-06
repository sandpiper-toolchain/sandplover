import matplotlib.pyplot as plt
from sandplover.plan import compute_surface_deposit_age
from sandplover.sample_data.sample_data import golf
#
golf = golf()
sfc_time = compute_surface_deposit_age(golf, surface_idx=-1)
#
fig, ax = plt.subplots()
_ = ax.imshow(sfc_time, cmap="YlGn_r")
