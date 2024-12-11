golfcube = dm.sample_data.golf()

fig, ax = plt.subplots()
golfcube.quick_show('eta', idx=-1, ax=ax)
ax.set_title('Final Elevation Data')
plt.show()