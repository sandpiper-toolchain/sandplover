golfcube = spl.sample_data.golf()
OAP = spl.plan.OpeningAnglePlanform.from_elevation_data(
  golfcube['eta'][-1, :, :], elevation_threshold=0)