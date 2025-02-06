# use a new cube
maskcube = spl.sample_data.golf()

# create the masks from variables in the cube
land_mask = spl.mask.LandMask(
    maskcube['eta'][-1, :, :],
    elevation_threshold=0)

wet_mask = spl.mask.WetMask(
    maskcube['eta'][-1, :, :],
    elevation_threshold=0)

channel_mask = spl.mask.ChannelMask(
    maskcube['eta'][-1, :, :],
    maskcube['velocity'][-1, :, :],
    elevation_threshold=0,
    flow_threshold=0.3)

centerline_mask = spl.mask.CenterlineMask(
    maskcube['eta'][-1, :, :],
    maskcube['velocity'][-1, :, :],
    elevation_threshold=0,
    flow_threshold=0.3)

edge_mask = spl.mask.EdgeMask(
    maskcube['eta'][-1, :, :],
    elevation_threshold=0)

shore_mask = spl.mask.ShorelineMask(
    maskcube['eta'][-1, :, :],
    elevation_threshold=0)