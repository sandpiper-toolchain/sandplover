elevation = np.zeros((5,))  # elevation array of 0s

# plot 1-D trajectory w/ constant subsidence
fig, ax = plt.subplots(figsize=(5, 4))
dm.plot.show_one_dimensional_trajectory_to_strata(
    elevation, sigma_dist=1.0, ax=ax, dz=0.5)
ax.set_xlim(-0.25, 4.5)
ax.set_ylim(-4.5, 0.5)
ax.set_ylabel('Elevation')
ax.set_xlabel('Time')
plt.show()