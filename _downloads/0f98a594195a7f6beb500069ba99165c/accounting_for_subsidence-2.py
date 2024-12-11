elevation = np.array([0, 1, 5, 6, 9])

# plot 1-D trajectory w/ constant subsidence
fig, ax = plt.subplots(figsize=(5, 4))
dm.plot.show_one_dimensional_trajectory_to_strata(
    elevation, sigma_dist=np.array([1, 2, 5, 5, 6]),
    ax=ax, dz=0.5)
ax.set_xlim(-0.25, 4.5)
ax.set_ylim(-6.5, 9.5)
ax.set_ylabel('Elevation')
ax.set_xlabel('Time')
plt.show()