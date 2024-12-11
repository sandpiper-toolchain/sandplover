lm0 = dm.mask.LandMask.from_array(
    hcirc)
em0 = dm.mask.ElevationMask.from_array(
    hcirc)
sm0 = dm.mask.ShorelineMask.from_mask(
    em0)

rgh0 = dm.plan.compute_shoreline_roughness(sm0, lm0)