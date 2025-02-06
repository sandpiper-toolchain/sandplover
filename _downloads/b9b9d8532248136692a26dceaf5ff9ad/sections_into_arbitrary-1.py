golfcube = spl.sample_data.golf()
pl = spl.plan.Planform(golfcube, idx=-1)

css = spl.section.StrikeSection(golfcube, distance=1200)
pss = spl.section.StrikeSection(pl, distance=1200)

fig, ax = plt.subplots()
golfcube.quick_show('eta', idx=-1)
css.show_trace(ax=ax)
pss.show_trace('--', ax=ax)
plt.show()