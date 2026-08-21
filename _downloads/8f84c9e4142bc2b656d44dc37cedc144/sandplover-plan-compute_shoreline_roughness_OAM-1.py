from sandplover.plan import compute_shoreline_roughness_OAM

golf = spl.sample_data.golf()
origin = (
    np.array([golf.aux["L0"].data, golf.aux["CTR"].data])
    * golf.aux["dx"].data
)

em = spl.mask.ElevationMask(
    golf["eta"][30, :, :], elevation_threshold=0, elevation_offset=-0.1
)
em.trim_mask(length=golf.aux["L0"].data + 1, value=1)
oam = spl.plan.OpeningAnglePlanform.from_mask(em)

sm45 = spl.mask.ShorelineMask.from_Planform(oam, contour_threshold=45)
sm120 = spl.mask.ShorelineMask.from_Planform(oam, contour_threshold=120)

fig, ax = plt.subplots(1, 2)
sm45.show(ax=ax[0])
sm120.show(ax=ax[1])
plt.show(block=False)

roughness_oam = compute_shoreline_roughness_OAM(sm45, sm120)

fig, ax = plt.subplots()
oam.show(ax=ax)
ax.contour(
    oam.opening_angles.y,
    oam.opening_angles.x,
    oam.opening_angles,
    levels=[45, 120],
    colors=["w"],
)
ax.set_title(f"roughness: {roughness_oam:.1f}")
plt.show()