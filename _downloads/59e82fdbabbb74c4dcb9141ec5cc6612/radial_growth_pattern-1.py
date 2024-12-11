golf = dm.sample_data.golf()

# measure the delta shoreline distance at five differet times
time_idxs = np.linspace(15, golf.shape[0]-1, num=5, dtype=int)

shoredist_mean = np.zeros(time_idxs.shape)
shoredist_std = np.zeros(time_idxs.shape)
for i, time_idx in enumerate(time_idxs):
    # compute the shoreline mask
    SM_mpm = dm.mask.ShorelineMask(
        golf['eta'][time_idx, :, :],
        elevation_threshold=0,
        method='MPM',
        contour_threshold=0.75,
        max_disk=8)
    SM_mpm.trim_mask(length=3)

    # compute the mean shoreline distance
    shoredist_mean[i], shoredist_std[i] = dm.plan.compute_shoreline_distance(
        SM_mpm, origin=(golf.meta['CTR'].data, golf.meta['L0'].data))