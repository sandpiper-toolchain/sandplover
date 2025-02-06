golfcube = spl.sample_data.golf()
#
OAP = spl.plan.OpeningAnglePlanform.from_elevation_data(
    golfcube["eta"][-1, :, :], elevation_threshold=0
)
#
lm = spl.mask.LandMask.from_Planform(OAP)
sm = spl.mask.ShorelineMask.from_Planform(OAP)
#
fig, ax = plt.subplots(2, 2)
golfcube.quick_show("eta", idx=-1, ax=ax[0, 0])
OAP.show(ax=ax[0, 1])
lm.show(ax=ax[1, 0])
sm.show(ax=ax[1, 1])
