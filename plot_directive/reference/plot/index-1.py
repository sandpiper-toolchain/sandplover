import matplotlib.pyplot as plt
from sandplover.plot import aerial_view
from sandplover.sample_data.sample_data import golf
#
golfcube = golf()
elevation_data = golfcube["eta"][-1, :, :]
#
fig, ax = plt.subplots()
_ = aerial_view(elevation_data, ax=ax)
