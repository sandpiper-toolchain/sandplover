golfcube = dm.sample_data.golf()
stratcube = dm.cube.StratigraphyCube.from_DataCube(
    golfcube, dz=0.05)
