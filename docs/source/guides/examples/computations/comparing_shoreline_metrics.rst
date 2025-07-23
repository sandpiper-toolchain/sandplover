Comparing shoreline metrics
===========================


.. plot::
    :include-source:
    :context: close-figs

    from sandplover.plan import compute_shoreline_roughness
    from sandplover.plan import compute_shoreline_rugosity
    
    golf = spl.sample_data.golf()

    origin = np.array([golf.meta["L0"].data, golf.meta["CTR"].data]) * golf.meta["dx"].data


    times_idxs = np.linspace(10, golf.shape[0]-1, num=20, dtype=int)

    roughness = np.zeros(len(times_idxs))
    rugosity = np.zeros(len(times_idxs))
    deviation = np.zeros(len(times_idxs))
    for t, time_idx in enumerate(times_idxs):

        # make masks
        em = spl.mask.ElevationMask(golf["eta"][time_idx, :, :], elevation_threshold=0)
        mp = spl.plan.MorphologicalPlanform(em, 10)

        sm = spl.mask.ShorelineMask.from_Planform(mp, contour_threshold=0.75)
        lm = spl.mask.LandMask.from_Planform(mp, contour_threshold=0.75)

        sm.trim_mask(length=golf.meta["L0"].data)
        lm.trim_mask(length=golf.meta["L0"].data)

        # compute roughness
        roughness[t] = compute_shoreline_roughness(sm, lm)

        # compute rugosity
        rugosity[t] = compute_shoreline_rugosity(sm)

        # compute Liang roughness
        def compute_shoreline_deviation(_sm):
            """
            shoreline roughness here is measured by the ratio between (i) the number
            of cells in the domain that contain a piece of shoreline of the simulated
            delta, and (ii) the average radius of the delta toposet in number of
            cells.

            Liang et al., 2015 DeltaRCM paper
            """
            r_bar, _ = compute_shoreline_distance(
                _sm, origin=origin)
            return np.sum(_sm) / r_bar
        deviation[t] = compute_shoreline_deviation(sm)

    fig, ax = plt.subplots()
    ax.plot(time, roughness, label="roughness")
    ax.plot(time, roughness, label="rugosity")
    ax.plot(time, roughness, label="deviation")
    ax.legend()
    plt.show()
