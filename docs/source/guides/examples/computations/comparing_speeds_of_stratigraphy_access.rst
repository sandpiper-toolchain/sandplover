Comparing speed of stratigraphy access
--------------------------------------

The access speed of a frozen volume is **much** faster than a live cube.
This is because the live cube does not store any data in memory.
Keeping data on disk is advantageous for large datasets, but slows down access considerably for computation.

.. doctest::

    >>> import time

    >>> # set up the cubes
    >>> golfcube = spl.sample_data.golf()
    >>> stratcube = spl.cube.StratigraphyCube.from_DataCube(golfcube, dz=0.05)
    >>> fs, fe = spl.strat.compute_boxy_stratigraphy_volume(
    ...     golfcube["eta"], golfcube["sandfrac"], dz=0.05
    ... )

    >>> # time extraction from the frozen cube
    >>> start1 = time.time()
    >>> for _ in range(100):
    ...     _val = fs[10:20, 31:35, -1:-30:-2]
    ...
    >>> end1 = time.time()

    >>> # time extraction from the underlying DataCube data on disk
    >>> start2 = time.time()
    >>> for _ in range(100):
    ...     _val = stratcube["sandfrac"].data[10:20, 31:35, -1:-30:-2]
    ...
    >>> end2 = time.time()

    >>> print(
    ...     "Elapsed time for frozen cube: ", end1 - start1, " seconds"
    ... )  # doctest: +SKIP
    Elapsed time for frozen cube: 0.00011587142944335938
    >>> print(
    ...     "Elapsed time for on-disk cube: ", end2 - start2, " seconds"
    ... )  # doctest: +SKIP
    Elapsed time for on-disk cube: 7.14995002746582 seconds
    >>> print(
    ...     "Speed difference: ", (end2 - start2) / (end1 - start1), " times faster"
    ... )  # doctest: +SKIP
    Speed difference: 61705.89300411523 times faster
