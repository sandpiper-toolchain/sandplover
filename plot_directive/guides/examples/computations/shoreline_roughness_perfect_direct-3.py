lm0 = spl.mask.LandMask.from_array(
    hcirc)
em0 = spl.mask.ElevationMask.from_array(
    hcirc)
sm0 = spl.mask.ShorelineMask.from_mask(
    em0)

rgh0 = spl.plan.compute_shoreline_roughness(sm0, lm0)