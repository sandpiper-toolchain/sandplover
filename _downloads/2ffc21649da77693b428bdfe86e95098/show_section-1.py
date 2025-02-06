golfcube = spl.sample_data.golf()
golfstrat = spl.cube.StratigraphyCube.from_DataCube(golfcube, dz=0.1)
circular = spl.section.CircularSection(golfstrat, radius=2000)
