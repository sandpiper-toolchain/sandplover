import matplotlib.pyplot as plt
from sandplover.plot import show_one_dimensional_trajectory_to_strata
from sandplover.sample_data import golf
#
golfcube = golf()
#
ets = golfcube["eta"].data[:, 10, 85]  # a "real" slice of the model
#
fig, ax = plt.subplots(figsize=(8, 4))
show_one_dimensional_trajectory_to_strata(ets, ax=ax, dz=0.25)
