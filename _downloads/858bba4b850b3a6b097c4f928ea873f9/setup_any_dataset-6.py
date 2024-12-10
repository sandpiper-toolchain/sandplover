dm.plot.aerial_view(
    nc_datacube['eta'][-1, :, :],
    datum=nc_datacube.meta['H_SL'][-1],
    ticks=True)