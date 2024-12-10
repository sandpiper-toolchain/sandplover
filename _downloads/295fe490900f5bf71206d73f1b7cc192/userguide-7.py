minus2_slice = dm.plan.Planform(stratcube, z=-2)
#
fig, ax = plt.subplots()
minus2_slice.show('sandfrac', ticks=True, ax=ax)
plt.show()
