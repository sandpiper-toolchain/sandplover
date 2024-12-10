eta = np.random.uniform(0, 1, size=(51, 100, 200))

dict_datacube = dm.cube.DataCube(
    {'eta': eta})