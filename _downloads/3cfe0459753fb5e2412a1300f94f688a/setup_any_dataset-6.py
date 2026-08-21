spl.plot.aerial_view(
    nc_datacube['eta'][-1, :, :],
    datum=nc_datacube.aux['H_SL'][-1],
    ticks=True)