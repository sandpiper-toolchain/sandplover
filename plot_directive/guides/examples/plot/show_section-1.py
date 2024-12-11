golfcube = dm.sample_data.golf()
golfstrat = dm.cube.StratigraphyCube.from_DataCube(
    golfcube, dz=0.1)
circular = dm.section.CircularSection(golfstrat, radius=2000)
