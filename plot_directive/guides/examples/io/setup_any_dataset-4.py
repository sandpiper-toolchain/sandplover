## create and fill the netcdf file
output_netcdf = Dataset(file_path, 'w',
                        format='NETCDF4')

# add some description information (see netCDF docs for more)
output_netcdf.description = 'Output from MyFakeModel'
output_netcdf.source = 'MyFakeModel v0.1'

# create time and spatial netCDF dimensions
output_netcdf.createDimension('time', T.shape[0])
output_netcdf.createDimension('y', T.shape[1])
output_netcdf.createDimension('x', T.shape[2])

# create time and spatial netCDF variables
v_time = output_netcdf.createVariable(
    'time', 'f4', ('time',))
v_time.units = 'second'
v_x = output_netcdf.createVariable(
    'x', 'f4', ('x'))
v_x.units = 'meter'
v_y = output_netcdf.createVariable(
    'y', 'f4', ('y'))
v_y.units = 'meter'

# fill the variables with the coordinate information
v_time[:] = t
v_x[:] = x
v_y[:] = y

# set up variables for output data grids
v_eta = output_netcdf.createVariable(
    'eta', 'f4', ('time', 'y', 'x'))
v_eta.units = 'meter'
v_velocity = output_netcdf.createVariable(
    'velocity', 'f4', ('time', 'y', 'x'))
v_velocity.units = 'meter/second'
v_eta[:] = eta
v_velocity[:] = velocity

# set up metadata group and populate variables
output_netcdf.createGroup('meta')
v_L0 = output_netcdf.createVariable(  # a scalar, the inlet length
    'meta/L0', 'f4', ())  # no dims for scalar
v_L0.units = 'cell'
v_L0[:] = 5
v_H_SL = output_netcdf.createVariable( # an array, the sea level
    'meta/H_SL', 'f4', ('time',))  # only has time dimensions
v_H_SL.units = 'meters'
v_H_SL[:] = H_SL

# close the netcdf file
output_netcdf.close()