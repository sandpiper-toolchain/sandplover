nc_datacube = dm.cube.DataCube(os.path.join(output_folder, 'model_output.nc'))

fig, ax = plt.subplots(2, len(t), figsize=(8, 3))
for i, _ in enumerate(t):
    nc_datacube.quick_show(
        'eta', idx=i,
        ticks=True, ax=ax[0, i])
    nc_datacube.quick_show(
        'velocity', idx=i,
        ticks=True, ax=ax[1, i])
plt.show()