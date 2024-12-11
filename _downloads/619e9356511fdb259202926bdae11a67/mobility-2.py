dryfrac = dm.mobility.calculate_channel_decay(
    channelmask_list, landmask_list,
    basevalues_idx=[0, 1, 2], window_idx=5)
Ophi = dm.mobility.calculate_planform_overlap(
    channelmask_list, landmask_list,
    basevalues_idx=[0, 1, 2], window_idx=5)
fr = dm.mobility.calculate_reworking_fraction(
    channelmask_list, landmask_list,
    basevalues_idx=[0, 1, 2], window_idx=5)
PwetA = dm.mobility.calculate_channel_abandonment(
    channelmask_list,
    basevalues_idx=[0, 1, 2], window_idx=5)
