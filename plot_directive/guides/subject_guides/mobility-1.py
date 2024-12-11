golfcube = dm.sample_data.golf()
channelmask_list = []
landmask_list = []
#
for i in range(50, 60):
    landmask_list.append(dm.mask.LandMask(
        golfcube['eta'][i, ...], elevation_threshold=0))
    channelmask_list.append(dm.mask.ChannelMask(
        golfcube['eta'][i, ...], golfcube['velocity'][i, ...],
        elevation_threshold=0, flow_threshold=0.3))
