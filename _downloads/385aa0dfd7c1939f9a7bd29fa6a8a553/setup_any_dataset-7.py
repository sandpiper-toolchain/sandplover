# create the dictionary
data_dict = {'eta': eta,
             'velocity': velocity}

# make a cube from it
dict_datacube = dm.cube.DataCube(
    data_dict,
    dimensions={'time': t,
                'y': y,
                'x': x})

fig, ax = plt.subplots(2, len(t), figsize=(8, 3))
for i, _ in enumerate(t):
    dict_datacube.quick_show(
        'eta', idx=i,
        ticks=True, ax=ax[0, i])
    dict_datacube.quick_show(
        'velocity', idx=i,
        ticks=True, ax=ax[1, i])
plt.show()