aeolian = dm.sample_data.aeolian()

fig, ax = plt.subplots()
ax.plot([500, 500], [0, 2000], c='r', ls='--')
aeolian.quick_show('eta', ax=ax, ticks=True, colorbar_label=True)
ax.set_xlabel('dimension 2 [m]', fontsize=8)
ax.set_ylabel('dimension 1 [m]', fontsize=8)
ax.tick_params(labelsize=7)
plt.show()