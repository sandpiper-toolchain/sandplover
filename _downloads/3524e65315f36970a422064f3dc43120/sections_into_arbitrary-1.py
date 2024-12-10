golfcube = dm.sample_data.golf()
pl = dm.plan.Planform(golfcube, idx=-1)

css = dm.section.StrikeSection(golfcube, distance=1200)
pss = dm.section.StrikeSection(pl, distance=1200)

fig, ax = plt.subplots()
golfcube.quick_show('eta', idx=-1)
css.show_trace(ax=ax)
pss.show_trace('--', ax=ax)
plt.show()