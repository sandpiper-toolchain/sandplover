EM = dm.mask.ElevationMask(
    golfcube["eta"][-1],
    elevation_threshold=0)
mss = dm.section.StrikeSection(EM, distance=1200)

ax.plot(mss.s, mss['mask'], ':')

plt.show()