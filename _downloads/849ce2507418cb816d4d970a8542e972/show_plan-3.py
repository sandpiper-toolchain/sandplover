golfstrat = dm.cube.StratigraphyCube.from_DataCube(
    golfcube, dz=0.1)
minus1 = dm.plan.Planform(golfstrat, z=-1)
