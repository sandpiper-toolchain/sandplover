import matplotlib.pyplot as plt
from deltametrics.plan import Planform
from deltametrics.sample_data.sample_data import golf
#
golfcube = golf()
planform = Planform(golfcube, idx=70)
fig, ax = plt.subplots(1, 2)
_ = planform.show('eta', ax=ax[0])
_ = planform.show('velocity', ax=ax[1])
