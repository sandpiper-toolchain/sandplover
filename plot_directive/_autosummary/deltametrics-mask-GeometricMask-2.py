import matplotlib.pyplot as plt
import numpy as np
from deltametrics.mask import GeometricMask
#
arr = np.random.uniform(size=(100, 200))
gmsk0 = GeometricMask(arr)
gmsk0.angular(np.pi/4, np.pi/2)
#
gmsk1 = GeometricMask(
    (100, 200), angular=dict(
        theta1=np.pi/4, theta2=np.pi/2)
    )
#
fig, ax = plt.subplots(1, 2)
gmsk0.show(ax[0])
gmsk1.show(ax[1])
plt.tight_layout()
