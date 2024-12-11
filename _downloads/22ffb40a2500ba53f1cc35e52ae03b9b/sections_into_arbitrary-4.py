ccs = dm.section.CircularSection(golfcube, radius=1000)
pcs = dm.section.CircularSection(pl, radius=1000)

fig, ax = plt.subplots()
golfcube.quick_show('eta', idx=-1)
ccs.show_trace(ax=ax)
pcs.show_trace('--', ax=ax)
plt.tight_layout()
plt.show()