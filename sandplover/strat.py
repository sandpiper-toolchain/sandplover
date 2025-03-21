import abc
import warnings

import numpy as np
import xarray as xr

from sandplover.section import CircularSection


def compute_compensation(line1, line2):
    """Compute compensation statistic betwen two lines.

    .. warning::

        Not Implemented.

    Parameters
    ----------
    line1 : ndarray
        First surface to use (two-dimensional matrix with x-z coordinates of
        line).

    line2 : ndarray
        Second surface to use (two-dimensional matrix with x-z coordinates of
        line).

    Returns
    -------
    CV : float
        Compensation statistic.

    """
    raise NotImplementedError()


def _determine_deposit_from_background(sediment_volume, background):
    """Helper for stratigraphic functions.

    Determine the boolean mask of the deposit, i.e., excluding the
    pre-deposition basin topography.

    Parameters
    ----------
    sediment_volume : :obj:`xarray` or `ndarray`
        The deposit voxel array. First dimension is vertical spatial
        dimension. In this function, the data here is used only when
        `background` is specified as a constant, or for shape if no input is
        given.

    background : `xarray`, `ndarray`, or `float`, optional
        Value indicating the background or basin voxels that should be
        excluded from computation. If an array matching the size
        of :obj:`sediment_volume` is supplied, this array is assumed to be a
        binary array indicating the voxels to be excluded (i.e., the
        `deposit` is the inverse of `background`). If a float is passed, this
        is treated as a "no-data" value, and used to determine the background
        voxels. If no value is supplied, no voxels are excluded.

    Returns
    -------
    deposit : :obj:`ndarray` or :obj:`DataArray`
        Boolean, with same shape as `background`, indicating where the volume
        is deposit (`True`).

    Examples
    --------
    This example shows how choice of background affect the background used for
    stratigraphic computations.

    The first background calculation simply uses the initial basin topography
    to determine the background voxels, but this ignores erosion and
    subsequent infilling.

    The second background calculation considers this infilling of erosional
    channels by including the inflill in the deposit, and not in the
    background.

    The third background shows the effect of using a constant value as the
    background value; hint: this is generally a bad idea unless your data has
    a background value encoded into it (like ``-1`` or `9999`).

    .. plot::

        >>> import matplotlib.pyplot as plt
        >>> from sandplover.cube import StratigraphyCube
        >>> from sandplover.sample_data.sample_data import golf
        >>> from sandplover.strat import _determine_deposit_from_background

        >>> golfcube = golf()
        >>> golfstrat = StratigraphyCube.from_DataCube(golfcube, dz=0.05)

        Background determined from initial basin topography

        >>> background0 = _determine_deposit_from_background(
        ...     golfcube["sandfrac"], background=golfstrat.Z < golfcube["eta"][0].data
        ... )

        Background determined from min of bed elevation timeseries

        >>> background1 = _determine_deposit_from_background(
        ...     golfcube["sandfrac"],
        ...     background=(golfstrat.Z < np.min(golfcube["eta"].data, axis=0)),
        ... )

        Background determined from a fixed sandfrac value

        >>> background2 = _determine_deposit_from_background(
        ...     golfcube["sandfrac"], background=0
        ... )

        >>> fig, ax = plt.subplots(2, 2, figsize=(6, 4))

        Just below initial basin depth

        >>> _ = ax[0, 0].imshow(background0[59], cmap="Greys_r")

        Just above initial basin depth

        >>> _ = ax[0, 1].imshow(background0[60], cmap="Greys_r")

        Just below initial basin depth

        >>> _ = ax[1, 0].imshow(background1[59], cmap="Greys_r")

        Just below initial basin depth

        >>> _ = ax[1, 1].imshow(background2[59], cmap="Greys_r")
        >>> plt.tight_layout()
    """
    if background is None:
        deposit = np.ones(sediment_volume.shape, dtype=bool)
    elif isinstance(background, (float, int)):
        deposit = sediment_volume != background
    elif isinstance(background, np.ndarray):
        deposit = ~background.astype(bool)  # ensure boolean
    else:
        raise TypeError("Invalid type for `background`.")

    return deposit


def compute_net_to_gross(sediment_volume, net_threshold=None, background=None):
    """Compute net-to-gross for stratigraphy.

    Computes a spatially-resolved net-to-gross for a deposit. This computation
    is based on thresholding some data to indicate what volume is "net"
    (usually grain size or sand fraction data). The first axis of the data is
    assumed to be the vertical elevation dimension.

    Parameters
    ----------
    sediment_volume : :obj:`xarray` or `ndarray`
        The deposit voxel array. First dimension is vertical spatial dimension.

    net_threshold : `float`, optional
        Threshold to use for splitting out the "net". Voxels with value
        greater than or equal to `net_threshold` will be included in the net.
        If no value is supplied, the unweighted midpoint of the :obj:`sediment_volume`
        distribution (i.e., ``(max + min)/2``) will be used as the
        threshold.

    background : `xarray`, `ndarray`, or `float`, optional
        Value indicating the background or basin voxels that should be
        excluded from computation. If an array matching the size
        of :obj:`sediment_volume` is supplied, this array is assumed to be a
        binary array indicating the voxels to be excluded (i.e., the
        `deposit` is the inverse of `background`). If a float is passed, this
        is treated as a "no-data" value, and used to determine the background
        voxels. If no value is supplied, no voxels are excluded.

    Returns
    -------
    net_to_gross : :obj:`ndarray` or :obj:`DataArray`
        A spatially-resolved net-to-gross "map".

    Examples
    --------

    .. plot::

        >>> import matplotlib.pyplot as plt
        >>> import numpy as np
        >>> from sandplover.cube import StratigraphyCube
        >>> from sandplover.plot import append_colorbar
        >>> from sandplover.sample_data.sample_data import golf
        >>> from sandplover.strat import compute_net_to_gross

        >>> golfcube = golf()
        >>> golfstrat = StratigraphyCube.from_DataCube(golfcube, dz=0.1)
        >>> background = golfstrat.Z < np.min(golfcube["eta"].data, axis=0)

        >>> net_to_gross = compute_net_to_gross(
        ...     golfstrat["sandfrac"], net_threshold=0.5, background=background
        ... )

        >>> fig, ax = plt.subplots(1, 2)
        >>> im0 = ax[0].imshow(net_to_gross, extent=golfstrat.extent)
        >>> _ = append_colorbar(im0, ax=ax[0])
        >>> im1 = ax[1].imshow(
        ...     net_to_gross,
        ...     cmap=golfstrat.varset["net_to_gross"].cmap,
        ...     norm=golfstrat.varset["net_to_gross"].norm,
        ...     extent=golfstrat.extent,
        ... )
        >>> _ = append_colorbar(im1, ax=ax[1])
        >>> plt.tight_layout()
    """
    # process the optional inputs
    if net_threshold is None:
        net_threshold = (np.nanmin(sediment_volume) + np.nanmax(sediment_volume)) / 2

    deposit = _determine_deposit_from_background(sediment_volume, background)

    # determine the net and gross
    net = sediment_volume >= net_threshold
    gross = sediment_volume >= np.nanmin(sediment_volume)  # use ~np.isnan()

    net = np.nansum(np.logical_and(net, deposit), axis=0).astype(float)
    gross = np.nansum(np.logical_and(gross, deposit), axis=0).astype(float)
    gross[gross == 0] = np.nan

    return net / gross


def compute_thickness_surfaces(top_surface, bottom_surface):
    """Compute deposit thickness.

    This computation determines the deposit thickness, based on two bounding
    surfaces. It is a calculation of ``(top_surface - bottom_surface)``, with
    corrections to invalidate areas of no-deposition or net erosion, i.e.,
    hightlighting only where net deposition has occurred.

    .. note::

        This function does not operate directly on :obj:`StratigraphyCube`,
        but on two surfaces of interest (which could be extracted from a
        :obj:`StratigraphyCube`). See example.

    Parameters
    ----------
    top_surface
        Elevation of top-bounding surface for computation. This is often the
        air-sediment surface, or an isochron surface in stratigraphy.

    bottom_surface
        Elevation of bottom-bounding surface for computation. This is often
        the pre-deposition basin surface.

    Returns
    -------
    difference : :obj:`ndarray` or :obj:`DataArray`
        Difference in elevation between :obj:`top_surface`
        and :obj:`bottom_surface`.

    Examples
    --------
    .. plot::

        >>> import matplotlib.pyplot as plt
        >>> import numpy as np
        >>> from sandplover.plot import append_colorbar
        >>> from sandplover.sample_data.sample_data import golf
        >>> from sandplover.strat import compute_thickness_surfaces

        >>> golfcube = golf()
        >>> deposit_thickness0 = compute_thickness_surfaces(
        ...     golfcube["eta"][-1, :, :], golfcube["eta"][0, :, :]
        ... )
        >>> deposit_thickness1 = compute_thickness_surfaces(
        ...     golfcube["eta"][-1, :, :], np.min(golfcube["eta"], axis=0)
        ... )

        >>> fig, ax = plt.subplots(1, 2)
        >>> im = ax[0].imshow(deposit_thickness0)
        >>> _ = append_colorbar(im, ax=ax[0])
        >>> _ = ax[0].set_title("thickness above initial basin")
        >>> im = ax[1].imshow(deposit_thickness1)
        >>> _ = append_colorbar(im, ax=ax[1])
        >>> _ = ax[1].set_title("total deposit thickness")
        >>> plt.tight_layout()
    """
    difference = top_surface - bottom_surface
    whr = difference <= 0
    if isinstance(difference, xr.DataArray):
        difference.data[whr] = np.nan
    else:
        difference[whr] = np.nan
    return difference


def compute_sedimentograph(
    sediment_volume,
    sediment_bins=None,
    num_sections=10,
    last_section_radius=None,
    background=None,
    **kwargs,
):
    """Compute the sedimentograph.

    The sedimentograph [1]_ is a measure of sand fraction of delta
    stratigraphy. In this implementation, a series of concentric
    `CircularSection` are drawn with increasing radius, so the sedimentograph
    is a function of space.

    .. hint::

        To compute the sedimentograph as a function of time and space, loop
        over stratigraphic volumes computed from a subset of the timeseries,
        and apply this metric.

    Parameters
    ----------
    sediment_volume : :obj:`xarray` or `ndarray`
        The deposit voxel array. First dimension is vertical spatial dimension.

    sediment_bins : :obj:`ndarray`
        Threshold values to use for splitting out the sediment grain size or
        sand fraction bins. Lower bound is inclusive for all bins, and upper
        bound is inclusive (but not unbounded) for last bin. If no value is
        supplied, the unweighted midpoint of the :obj:`sediment_volume`
        distribution will divide two bins (i.e., ``[min, (max + min)/2,
        max]``).

    num_sections : :obj:`int`, optional
        Number of sections to calculate for the sedimentograph. Default is
        10.

    last_section_radius : :obj:`float`, optional
        Radius of the last section for the sedimentograph. If no value is
        supplied, last section will be placed at the half the maximum
        coordinate of the `dim1` axis (first spatial coordinate) of the
        `sediment_volume` volume.

    background : `xarray`, `ndarray`, or `float`, optional
        Value indicating the background or basin voxels that should be
        excluded from computation. If an array matching the size
        of :obj:`sediment_volume` is supplied, this array is assumed to be a
        binary array indicating the voxels to be excluded (i.e., the
        `deposit` is the inverse of `background`). If a float is passed, this
        is treated as a "no-data" value, and used to determine the background
        voxels. If no value is supplied, no voxels are excluded.

    **kwargs
        Passed to `CircularSection` instantiation. Hint: You likely want to
        supply the `origin` parameter.

    Returns
    -------
    sedimentograph : :obj:`ndarray`
        A `num` x `len(sediment_bins)` array of sediment volume fraction in each bin
        (columns) for each `CircularSection` with increasing distance from
        the origin.

    section_radii : :obj:`ndarray`
        Radii where the :obj:`CircularSection` for the sedimentograph were
        located.

    sediment_bins : :obj:`ndarray`
        Bins used to classify values in `sediment_volume`.

    Examples
    --------
    Compute the sedimentograph for the `golf` data `sandfrac`, using the
    default bins. Note that this yields two bins, which are simply `
    (1-other)`, so we only plot the second bin --- indicating the sandy
    fraction of the deposit for the `golf` `sandfrac` data.

    .. plot::

        >>> import matplotlib.pyplot as plt
        >>> import numpy as np
        >>> from sandplover.cube import StratigraphyCube
        >>> from sandplover.sample_data.sample_data import golf
        >>> from sandplover.strat import compute_sedimentograph

        >>> golfcube = golf()
        >>> golfstrat = StratigraphyCube.from_DataCube(golfcube, dz=0.1)

        >>> background = golfstrat.Z < np.min(golfcube["eta"].data, axis=0)

        >>> (sedimentograph, radii, bins) = compute_sedimentograph(
        ...     golfstrat["sandfrac"],
        ...     num_sections=50,
        ...     last_section_radius=2750,
        ...     background=background,
        ...     origin_idx=[3, 100],
        ... )

        >>> fig, ax = plt.subplots()
        >>> _ = ax.plot(radii, sedimentograph[:, 1], marker="o", ls="-")
        >>> _ = ax.set_xlabel("section radius (m)")
        >>> _ = ax.set_ylabel(f"fraction > {bins[1]}")

    .. [1] Liang, M., Van Dyk, C., and Passalacqua, P. (2016), Quantifying
           the patterns and dynamics of river deltas under conditions of
           steady forcing and relative sea level rise, J. Geophys. Res.
           Earth Surf., 121, 465– 496, doi:10.1002/2015JF003653.
    """
    # implementation note: this could be refactored to take advantage of numpy
    # histogram/bin counting, rather than manually searching.

    # get the deposit only
    deposit = _determine_deposit_from_background(sediment_volume, background)

    # figure out the sediment_bins
    if sediment_bins is None:
        # two bins, midpoint of dataset is break
        sediment_bins = np.array(
            [
                np.nanmin(sediment_volume),
                (np.nanmin(sediment_volume) + np.nanmax(sediment_volume)) / 2,
                np.nanmax(sediment_volume),
            ]
        )

    # figure out the last section radius
    if last_section_radius is None:
        # figure it out somehow?
        last_section_radius = float(sediment_volume[sediment_volume.dims[1]][-1]) / 2

    # make a list of sections to draw out
    section_radii = np.linspace(0, last_section_radius, num=num_sections + 1)[1:]
    sedimentograph = np.zeros(shape=(len(section_radii), len(sediment_bins) - 1))

    # loop through the sections and compute the sediment vols
    for i, sect_rad in enumerate(section_radii):
        sect = CircularSection(
            sediment_volume[0, :, :],  # must be a 2d slice to make section
            radius=sect_rad,
            **kwargs,
        )
        # manually slice, because not set up for sections into arbitrary 3d volume
        sect_slice = sediment_volume.data[:, sect._dim1_idx, sect._dim2_idx]
        sect_deposit = deposit[:, sect._dim1_idx, sect._dim2_idx]
        # manually loop bins
        for b in np.arange(len(sediment_bins) - 1):
            low_bin = sediment_bins[b]
            high_bin = sediment_bins[b + 1]

            if b < (len(sediment_bins) - 2):
                in_bin = np.logical_and(sect_slice >= low_bin, sect_slice < high_bin)
            else:
                in_bin = np.logical_and(sect_slice >= low_bin, sect_slice <= high_bin)
            in_bin_count = np.sum(np.logical_and(in_bin, sect_deposit))
            total_count = np.sum(np.logical_and(~np.isnan(sect_slice), sect_deposit))

            if total_count > 0:
                frac = in_bin_count / total_count
            else:
                frac = np.nan
            sedimentograph[i, b] = frac

    return sedimentograph, section_radii, sediment_bins


def compute_boxy_stratigraphy_volume(
    elev, prop, sigma_dist=None, z=None, dz=None, nz=None, return_cube=False
):
    """Process t-x-y data volume to boxy stratigraphy volume.

    This function returns a "frozen" cube of stratigraphy
    with values of the supplied property/variable (:obj:`prop`) placed into a
    three-dimensional real-valued 3D array.

    By default, the data are returned as a numpy `ndarray`, however, specify
    :obj:`return_Cube` as `True` to return a
    :obj:`~sandplover.cube.FrozenStratigraphyCube`. If `False`, function
    :additionally returns an `ndarray` of elevations corresponding to the
    :stratigraphy positions.

    Parameters
    ----------
    elev : :obj:`ndarray`
        The `t-x-y` ndarray of elevation data to determine stratigraphy.

    prop : :obj:`ndarray`
        The `t-x-y` ndarray of property data to process into the stratigraphy.

    sigma_dist : :obj:`ndarray`, :obj:`float`, :obj:`int`, optional
        Optional subsidence distance argument used to adjust the elevation
        data to account for subsidence when computing stratigraphy. See
        :obj:`_adjust_elevation_by_subsidence` for a complete description.

    z : :obj:`ndarray`, optional
        Vertical coordinates for stratigraphy, in meters. Optional, and
        mutually exclusive with :obj:`dz` and :obj:`nz`,
        see :obj:`_determine_strat_coordinates` for complete description.

    dz : :obj:`float`, optional
        Vertical resolution of stratigraphy, in meters. Optional, and mutually
        exclusive with :obj:`z` and :obj:`nz`,
        see :obj:`_determine_strat_coordinates` for complete description.

    nz : :obj:`int`, optional
        Number of intervals for vertical coordinates of stratigraphy.
        Optional, and mutually exclusive with :obj:`z` and :obj:`dz`,
        see :obj:`_determine_strat_coordinates` for complete description.

    return_cube : :obj:`boolean`, optional
        Whether to return the stratigraphy as a
        :obj:`~sandplover.cube.FrozenStratigraphyCube` instance. Default is
        to return an `ndarray` and :obj:`elevations` `ndarray`.

        .. warning:: not implemented!

    Returns
    -------
    stratigraphy_cube : :obj:`~sandplover.cube.StratigraphyCube`
        Not Implemented.

    stratigraphy : :obj:`ndarray`
        A `z-x-y` `ndarray` with data from `prop` placed into voxels to fill
        stratigraphy.

    elevations : :obj:`ndarray`
        A `z-x-y` `ndarray` with elevations for each voxel in the stratigraphy
        array.
    """
    # verify dimensions
    if elev.shape != prop.shape:
        raise ValueError('Mismatched input shapes "elev" and "prop".')
    if elev.ndim != 3:
        raise ValueError("Input arrays must be three-dimensional.")

    # compute preservation from low-level funcs
    if sigma_dist is not None:
        # convert elevations
        elev = _adjust_elevation_by_subsidence(elev, sigma_dist)
    strata, _ = _compute_elevation_to_preservation(elev)
    z = _determine_strat_coordinates(elev, z=z, dz=dz, nz=nz)
    strata_coords, data_coords = _compute_preservation_to_cube(strata, z=z)

    # copy data out and into the stratigraphy based on coordinates
    nx, ny = strata.shape[1:]
    stratigraphy = np.full((len(z), nx, ny), np.nan)  # preallocate nans
    _cut = prop.values[data_coords[:, 0], data_coords[:, 1], data_coords[:, 2]]
    stratigraphy[strata_coords[:, 0], strata_coords[:, 1], strata_coords[:, 2]] = _cut

    elevations = np.tile(z, (ny, nx, 1)).T

    if return_cube:
        raise NotImplementedError
    else:
        return stratigraphy, elevations


def compute_boxy_stratigraphy_coordinates(
    elev,
    sigma_dist=None,
    z=None,
    dz=None,
    nz=None,
    return_cube=False,
    return_strata=False,
):
    """Process t-x-y data volume to boxy stratigraphy coordinates.

    This function computes the corresponding preservation of `t-x-y`
    coordinates in a dense 3D volume of stratigraphy, as `z-x-y` coordinates.
    This "mapping" is able to be computed only once, and used many times to
    synthesize a cube of preserved stratigraphy from an arbitrary `t-x-y`
    dataset.

    Parameters
    ----------
    elev : :obj:`ndarray`
        The `t-x-y` ndarray of elevation data to determine stratigraphy.

    sigma_dist : :obj:`ndarray`, :obj:`float`, :obj:`int`, optional
        Optional subsidence distance argument used to adjust the elevation
        data to account for subsidence when computing stratigraphy. See
        :obj:`_adjust_elevation_by_subsidence` for a complete description.

    z : :obj:`ndarray`, optional
        Vertical coordinates for stratigraphy, in meters. Optional, and
        mutually exclusive with :obj:`dz` and :obj:`nz`,
        see :obj:`_determine_strat_coordinates` for complete description.

    dz : :obj:`float`, optional
        Vertical resolution of stratigraphy, in meters. Optional, and mutually
        exclusive with :obj:`z` and :obj:`nz`,
        see :obj:`_determine_strat_coordinates` for complete description.

    nz : :obj:`int`, optional
        Number of intervals for vertical coordinates of stratigraphy.
        Optional, and mutually exclusive with :obj:`z` and :obj:`dz`,
        see :obj:`_determine_strat_coordinates` for complete description.

    return_cube : :obj:`boolean`, optional
        Whether to return the stratigraphy as a
        :obj:`~sandplover.cube.FrozenStratigraphyCube` instance. Default is
        `False`, do not return a cube.

        .. warning:: not implemented!

    return_strata : :obj:`boolean`, optional
        Whether to return the stratigraphy elevations, as returned from
        internal computations in :obj:`_compute_elevation_to_preservation`.
        Default is `False`, do not return strata.

    Returns
    -------
    stratigraphy_cube : :obj:`~sandplover.cube.StratigraphyCube`
        Not Implemented.

    strata_coords : :obj:`ndarray`
        An `N x 3` array of `z-x-y` coordinates where information is preserved
        in the boxy stratigraphy. Rows in `strat_coords` correspond with rows
        in `data_coords`. See :obj:`_compute_preservation_to_cube` for
        computation implementation.

    data_coords : :obj:`ndarray`
        An `N x 3` array of `t-x-y` coordinates where information is to be
        extracted from the data array. Rows in `data_coords` correspond with
        rows in `strat_coords`.  See :obj:`_compute_preservation_to_cube` for
        computation implementation.

    strata : :obj:`ndarray`
        A `t-x-y` `ndarray` of stratal surface elevations. Returned as third
        argument only if `return_strata=True`.
    """
    # compute preservation from low-level funcs
    if sigma_dist is not None:
        # adjust elevation by subsidence rates if present
        elev = _adjust_elevation_by_subsidence(elev, sigma_dist)
    strata, _ = _compute_elevation_to_preservation(elev)
    z = _determine_strat_coordinates(elev, z=z, dz=dz, nz=nz)
    strata_coords, data_coords = _compute_preservation_to_cube(strata, z=z)

    if return_cube:
        raise NotImplementedError
    elif return_strata:
        return strata_coords, data_coords, strata
    else:
        return strata_coords, data_coords


class BaseStratigraphyAttributes:

    def __init__(self, style):
        self._style = style

    @abc.abstractmethod
    def __call__(self):
        """Slicing operation to get sections and planforms.

        Must be implemented by subclasses.
        """
        ...

    def __getitem__(self, *unused_args, **unused_kwargs):
        raise NotImplementedError('Use "__call__" to slice.')

    @property
    def style(self):
        return self._style

    @property
    def display_arrays(self):
        return self.data, self.X, self.Y

    @property
    @abc.abstractmethod
    def data(self):
        return ...

    @property
    @abc.abstractmethod
    def X(self):
        return ...

    @property
    @abc.abstractmethod
    def Y(self):
        return ...

    @property
    @abc.abstractmethod
    def preserved_index(self):
        """:obj:`ndarray` : Boolean array indicating preservation.

        True where data is preserved in final stratigraphy.
        """
        return ...

    @property
    @abc.abstractmethod
    def preserved_voxel_count(self):
        """:obj:`ndarray` : Nmber of preserved voxels per x-y.

        X-Y array indicating number of preserved voxels per x-y pair.
        """
        return ...


class BoxyStratigraphyAttributes:
    """Attribute set for boxy stratigraphy information, emebdded into a DataCube."""

    def __init__(self):
        super().__init__("boxy")
        raise NotImplementedError(
            "Implementation should match MeshStratigraphyAttributes"
        )


class MeshStratigraphyAttributes(BaseStratigraphyAttributes):
    """Attribute set for mesh stratigraphy information, emebdded into a DataCube.

    This object stores attributes of stratigraphy as a "mesh", only retaining
    the minimal necessary information to represent the stratigraphy. Contrast
    this with Boxy stratigraphy.

    Notes
    -----
    Some descriptions regarding implementation.

    _psvd_idx : :obj:`ndarray` of `bool`
        Preserved index into the section array.

    _psvd_flld : :obj:`ndarray`
        Elevation of preserved voxels, filled to vertical extent with the
        final elevation of the bed (i.e., to make it displayable by
        pcolormesh).

    _i : :obj:`ndarray`
        Row index for sparse matrix of preserved strata. I.e., which row
        in the stratigraphy matrix each voxel "winds up as".

    _j : :obj:`ndarray`
        Column index for sparse matrix of preserved strata. I.e., which
        column in the stratigraphy matrix each voxel "winds up as". This
        is kind of just a dummy to make the api consistent with ``_i``,
        because the column cannot change with preservation.
    """

    def __init__(self, elev, **kwargs):
        """
        We can precompute several attributes of the stratigraphy, including
        which voxels are preserved, what their row indicies in the sparse
        stratigraphy matrix are, and what the elevation of each elevation
        entry in the final stratigraphy are. *This allows placing of any t-x-y
        stored variable into the section.*

        Parameters
        ---------
        elev :
            elevation t-x-y array to compute from

        Keyword arguments
        -----------------
        load : :obj:`bool`, optional
            Whether to load the eta array into memory before computation. For
            especially large data files, `load` should be `False` to keep the
            file on disk; note on-disk computation is considerably slower.

        sigma_dist : :obj:`ndarray`, :obj:`float`, :obj:`int`, optional
            Optional subsidence distance argument that is used to adjust the
            elevation data to account for subsidence when computing
            stratigraphy. See :obj:`_adjust_elevation_by_subsidence` for a
            complete description.
        """
        super().__init__("mesh")

        # load or read eta field
        load = kwargs.pop("load", True)
        if load:
            _eta = np.array(elev)
        else:
            _eta = elev

        # rate of subsidence
        sigma_dist = kwargs.pop("sigma_dist", None)
        if sigma_dist is not None:
            _eta = _adjust_elevation_by_subsidence(_eta, sigma_dist)

        # make computation
        _strata, _psvd = _compute_elevation_to_preservation(_eta)
        _psvd[0, ...] = True
        self.strata = _strata

        self.psvd_vxl_cnt = _psvd.sum(axis=0, dtype=int)
        self.psvd_vxl_idx = _psvd.cumsum(axis=0, dtype=int)
        self.psvd_vxl_cnt_max = int(self.psvd_vxl_cnt.max())
        self.psvd_idx = _psvd.astype(bool)  # guarantee bool

        # Determine the elevation of any voxel that is preserved.
        # These are matrices that are size n_preserved-x-y.
        #    psvd_vxl_eta : records eta for each entry in the preserved matrix.
        #    psvd_flld    : fills above with final eta entry (for pcolormesh).
        self.psvd_vxl_eta = np.full((self.psvd_vxl_cnt_max, *_eta.shape[1:]), np.nan)
        self.psvd_flld = np.full((self.psvd_vxl_cnt_max, *_eta.shape[1:]), np.nan)
        for i in np.arange(_eta.shape[1]):
            for j in np.arange(_eta.shape[2]):
                self.psvd_vxl_eta[0 : self.psvd_vxl_cnt[i, j], i, j] = _eta[
                    self.psvd_idx[:, i, j], i, j
                ].copy()
                self.psvd_flld[0 : self.psvd_vxl_cnt[i, j], i, j] = _eta[
                    self.psvd_idx[:, i, j], i, j
                ].copy()
                self.psvd_flld[self.psvd_vxl_cnt[i, j] :, i, j] = self.psvd_flld[
                    self.psvd_vxl_cnt[i, j] - 1, i, j
                ]  # noqa: E501

    def __call__(self, _dir, _x0, _x1):
        """Get a slice out of the stratigraphy attributes.

        Used for building section variables.

        Parameters
        ----------
        _dir : :obj:`str`
            Which direction to slice. If 'section', then _x0 is the
            _coordinates to slice in the domain length, and _x1 is the
            coordinates _to slice in the domain width direction.

        _x0, _x1

        Returns
        -------
        strat_attr : :obj:`dict`
            Dictionary containing useful information for sections and plans
            derived from the call.
        """
        strat_attr = {}
        if _dir == "section":
            strat_attr["strata"] = self.strata[:, _x0, _x1]
            strat_attr["psvd_idx"] = _psvd_idx = self.psvd_idx[:, _x0, _x1]
            strat_attr["psvd_flld"] = self.psvd_flld[:, _x0, _x1]
            strat_attr["x0"] = _i = self.psvd_vxl_idx[:, _x0, _x1]
            strat_attr["x1"] = _j = np.tile(np.arange(_i.shape[1]), (_i.shape[0], 1))
            strat_attr["s"] = _j[0, :]  # along-sect coord
            strat_attr["s_sp"] = _j[_psvd_idx]  # along-sect coord, sparse
            strat_attr["z_sp"] = _i[_psvd_idx]  # vert coord, sparse

        elif (_dir == "plan") or (_dir == "planform"):
            pass
            # cannot be done without interpolation for mesh strata.
            # should be possible for boxy stratigraphy?
        else:
            raise ValueError('Bad "_dir" argument: %s' % str(_dir))
        return strat_attr

    @property
    def data(self):
        return self._data

    @property
    def X(self):
        return self._X

    @property
    def Y(self):
        return self._Y

    @property
    def preserved_index(self):
        """:obj:`ndarray` : Boolean array indicating preservation.

        True where data is preserved in final stratigraphy.
        """
        return self._psvd_idx

    @property
    def preserved_voxel_count(self):
        """:obj:`ndarray` : Nmber of preserved voxels per x-y.

        X-Y array indicating number of preserved voxels per x-y pair.
        """
        return self._psvd_vxl_cnt


def _compute_elevation_to_preservation(elev):
    """Compute the preserved elevations of stratigraphy.

    Given elevation data alone, we can compute the preserved stratal surfaces.
    These surfaces depend on the timeseries of bed elevation at any spatial
    location. We determine preservation by marching backward in time,
    determining when was the most recent time that the bed elevation was equal
    to a given elevation.

    This function is declared as private and not part of the public API,
    however some users may find it helpful. The function is heavily utlized
    internally. Function inputs and outputs are standard numpy `ndarray`, so
    that these functions can accept data from an arbitrary source.

    Parameters
    ----------
    elev : :obj:`ndarray` or :obj:`xr.core.dataarray.DataArray`
        The `t-x-y` volume of elevation data to determine stratigraphy.

    Returns
    -------
    strata : :obj:`ndarray`
        A `t-x-y` `ndarry` of stratal surface elevations.

    psvd : :obj:`ndarray`
        A `t-x-y` boolean `ndarry` of whether a `(t,x,y)` point of
        instantaneous time is preserved in any of the final stratal surfaces.
        To determine whether time from a given *timestep* is preserved, use
        ``psvd.nonzero()[0] - 1``.
    """
    psvd = np.zeros_like(elev.data, dtype=bool)  # bool, if retained
    strata = np.zeros_like(elev.data)  # elev of surface at each t

    nt = strata.shape[0]
    if isinstance(elev, np.ndarray) is True:
        _elev = elev
    elif isinstance(elev, xr.core.dataarray.DataArray) is True:
        _elev = elev.values
    else:  # case where elev is a CubeVariable
        _elev = elev.data.values

    strata[-1, ...] = _elev[-1, ...]
    for j in np.arange(nt - 2, -1, -1):
        strata[j, ...] = np.minimum(_elev[j, ...], strata[j + 1, ...])
        psvd[j + 1, ...] = np.less(strata[j, ...], strata[j + 1, ...])
    if nt > 1:  # allows a single-time elevation-series to return
        psvd[0, ...] = np.less(strata[0, ...], strata[1, ...])

    return strata, psvd


def _compute_preservation_to_time_intervals(psvd):
    """Compute the preserved timesteps.

    The output from :obj:`_compute_elevation_to_preservation` records whether
    an instance of time, defined exactly at the data interval, is recorded in
    the stratigraphy (here, "recorded" does not include stasis). This differs
    from determining which *time-intervals* are preserved in the stratigraphy,
    because the deposits reflect the conditions *between* the save intervals.

    While this computation is simply an offset-by-one indexing (``psvd[1:,
    ...]``), the function is implemented explicitly and utilized internally
    for consistency.

    .. note::

        `True` in the preserved time-interval array does not necessarily
        indicate that an entire timestep was preserved, but rather that some
        portion of this time-interval (up to the entire interval) is recorded.

    Parameters
    ----------
    psvd : :obj:`ndarray`
        Boolean `ndarray` indicating the preservation of instances of time.
        Time is expected to be the 0th axis.

    Returns
    -------
    psvd_intervals : :obj:`ndarray`
        Boolean `ndarray` indicating the preservation of time-intervals,
        including partial intervals.
    """
    return psvd[1:, ...]


def _compute_preservation_to_cube(strata, z):
    """Compute the cube-data coordinates to strata coordinates.

    Given elevation preservation data (e.g., data from
    :obj:`~sandplover.strat._compute_elevation_to_preservation`), compute
    the coordinate mapping from `t-x-y` data to `z-x-y` preserved
    stratigraphy.

    While stratigraphy is time-dependent, preservation at any spatial x-y
    location is independent of any other location. Thus, the computation is
    vectorized to sweep through all "stratigraphic columns" simultaneously.
    The operation works by beginning at the highest elevation of the
    stratigraphic volume, and sweeping down though all elevations with an
    `x-y` "plate". The plate indicates whether sediments are preserved below
    the current iteration elevation, at each x-y location.

    Once the iteration elevation is less than the strata surface at any x-y
    location, there will *always* be sediments preserved below it, at every
    elevation. We simply need to determine which time interval these sediments
    record. Then we store this time indicator into the sparse array.

    So, in the end, coordinates in resultant boxy stratigraphy are linked to
    `t-x-y` coordinates in the data source, by building a mapping that can be
    utilized repeatedly from a single stratigraphy computation.

    This function is declared as private and not part of the public API,
    however some users may find it helpful. The function is heavily utlized
    internally. Function inputs and outputs are standard numpy `ndarray`, so
    that these functions can accept data from an arbitrary source.

    Parameters
    ----------
    strata : :obj:`ndarray`
        A `t-x-y` `ndarry` of stratal surface elevations. Can be computed by
        :obj:`~sandplover.strat._compute_elevation_to_preservation`.

    z :
        Vertical coordinates of stratigraphy. Note that `z` does not need to
        have regular intervals.

    Returns
    -------
    strat_coords : :obj:`ndarray`
        An `N x 3` array of `z-x-y` coordinates where information is preserved
        in the boxy stratigraphy. Rows in `strat_coords` correspond with
        rows in `data_coords`.

    data_coords : :obj:`ndarray`
        An `N x 3` array of `t-x-y` coordinates where information is to be
        extracted from the data array. Rows in `data_coords` correspond
        with rows in `strat_coords`.
    """
    # preallocate boxy arrays and helpers
    plate = np.atleast_1d(np.zeros(strata.shape[1:], dtype=int))
    strat_coords, data_coords = [], []  # preallocate sparse idx lists
    _zero = np.array([0])

    # the main loop through the elevations
    seek_elev = strata[-1, ...]  # the first seek is the last surface
    for k in np.arange(len(z) - 1, -1, -1):  # for every z, from the top
        e = z[k]  # which elevation for this iteration
        whr = e < seek_elev  # where elev is below strat surface
        t = np.maximum(_zero, (np.argmin(strata[:, ...] <= e, axis=0)))
        plate[whr] = int(1)  # track locations in the plate

        xy = plate.nonzero()
        ks = np.full((np.count_nonzero(plate)), k)  # might be faster way
        idxs = t[xy]  # must happen before incrementing counter

        strat_ks = np.column_stack((ks, *xy))
        data_idxs = np.column_stack((idxs, *xy))
        strat_coords.append(strat_ks)  # list of numpy arrays
        data_coords.append(data_idxs)

    strat_coords = np.vstack(strat_coords)  # to single (N x 3) array
    data_coords = np.vstack(data_coords)
    return strat_coords, data_coords


def _determine_strat_coordinates(elev, z=None, dz=None, nz=None):
    """Return a valid Z array for stratigraphy based on inputs.

    This helper function enables support for user specified `dz`, `nz`, or `z`
    in many functions. The logic for determining how to handle these mutually
    exclusive inputs is placed in this function, to ensure consistent behavior
    across all classes/methods internally.

    .. note::

        If none of the optional parameters is supplied, then a default value
        is used of `dz=0.1`.

    .. important::

        Precedence when multiple arguments are supplied is `z`, `dz`, `nz`.

    Parameters
    ----------
    elev : :obj:`ndarray`
        An up-to-three-dimensional array with timeseries of elevation values,
        where elevation is expected to along the zeroth axis.

    z : :obj:`ndarray`, optional
        Array of Z values to use for bounding intervals (i.e., points in `z`),
        returned unchanged if supplied.

    dz : :obj:`float`, optional
        Interval in created Z array. Z array is created as
        ``np.arange(np.min(elev), np.max(elev)+dz, step=dz)``.

    nz : :obj:`int`, optional
        Number of *intervals* in `z`, that is, the number of points in `z` is
        `nz+1`. Z array is created as ``np.linspace(np.min(elev), np.max
        (elev), num=nz, endpoint=True)``.
    """
    # if nothing is supplied
    if (dz is None) and (z is None) and (nz is None):
        warnings.warn(
            UserWarning(
                "No specification for stratigraphy spacing"
                " was supplied. Default is to use `dz=0.1`"
            ),
            stacklevel=2,
        )
        # set the default option when nothing is supplied
        dz = 0.1

    # set up an error message to use in a few places
    _valerr = ValueError('"dz" or "nz" cannot be zero or negative.')

    # process to find the option to set up z
    if not (z is None):
        if np.isscalar(z):
            raise ValueError('"z" must be a numpy array.')
        return z
    elif not (dz is None):
        if dz <= 0:
            raise _valerr
        max_dos = np.max(elev.data) + dz  # max depth of section, meters
        min_dos = np.min(elev.data)  # min dos, meters
        return np.arange(min_dos, max_dos, step=dz)
    elif not (nz is None):
        if nz <= 0:
            raise _valerr
        max_dos = np.max(elev.data)
        min_dos = np.min(elev.data)
        return np.linspace(min_dos, max_dos, num=nz + 1, endpoint=True)
    else:
        raise RuntimeError("No coordinates determined. Check inputs.")


def _adjust_elevation_by_subsidence(elev, sigma_dist):
    """Adjust elevation array by subsidence rates.
    Given the elevation information and information about the distance
    subsided, the true sedimentation and erosion pattern can be unraveled.
    The function is written flexibly to handle subsidence distance information
    provided as either a single constant value, a constant value over a 2-D
    spatial pattern, a 1-D temporal vector when the distance changes but
    is applied to the entire domain, and finally a full t-x-y 3-D array with
    subsidence information for each x-y position in the domain at each
    instance in time.
    Critically, when temporal information is provided (either 1-D vector or
    full 3-D array) values are assumed to be cumulative subsidence distances
    at each index in time. Alternatively, when constant information is given
    (1-D float/int, or 2-D x-y array) it is assumed that the constant values
    reported represent the distance subsided per temporal index.
    This function is declared as a private function and is not part of the
    public API. Higher level functions make a call internally to adjust the
    elevation data based on subsidence rate information when the optional
    argument `sigma_dist` is provided.

    Parameters
    ----------
    elev : :obj:`ndarray` or :obj:`xr.core.dataarray.DataArray`
        The `t-x-y` volume of elevation data to determine stratigraphy.

    sigma_dist : :obj:`ndarray`, :obj:`xr.core.dataarray.DataArray`,
                 :obj:`float`, :obj:`int`
        The subsidence information. If a single float or int is provided,
        that value is assumed to apply across the entire domain for all times.
        If a 2-D array is provided, the distances are assumed for each
        x-y location and are applied across all times. If a 1-D vector is
        provided, it is assumed that each value applies to all locations in
        the domain for a given time. If a full 3-D array is provided, it is
        assumed to follow the same `t-x-y` convention as the elevation data.
        Positive distances indicate subsidence, negative distances are uplift.

    Returns
    -------
    elev_adjusted : :obj:`ndarray`
        A `t-x-y` `ndarray` of the same shape as the input `elev` array, but
        the values have all been adjusted by the subsidence information
        provided by the input `sigma_dist`.
    """
    # single value assumed to be constant displacement over all time
    if isinstance(sigma_dist, (int, float)):
        s_arr = np.ones_like(elev) * sigma_dist
        s_arr[0] = 0.0  # no subsidence at time 0
        # assume dist subsided each timestep
        s_arr = np.flip(np.cumsum(s_arr, axis=0), axis=0)
    # 1-D array renaming when topo is 1-D too
    elif len(sigma_dist.shape) == 1 and len(elev.shape) == 1:
        s_arr = sigma_dist
        # convert to base of preserved strat at each time based on subs
        s_arr = np.max(s_arr) - s_arr
    # 2-D array gets cast into the shape of the 3-d elevation array
    elif len(sigma_dist.shape) == 2 and len(elev.shape) == 3:
        s_arr = np.tile(sigma_dist, (elev.shape[0], 1, 1))
        s_arr[0, ...] = 0.0  # no subsidence at time 0
        s_arr = np.flip(np.cumsum(s_arr, axis=0), axis=0)  # sum up over time
    elif (
        len(sigma_dist.shape) == 1
        and len(sigma_dist) == elev.shape[0]
        and len(elev.shape) == 3
    ):
        # proper 1-D timeseries; flip and rename to s_arr
        s_arr = sigma_dist
        # convert to base of preserved strat at each time based on subs
        s_arr = np.max(s_arr) - s_arr
        # casting for a 1-D vector of sigma that matches elev time dimension
        s_arr = np.tile(
            sigma_dist.reshape(len(sigma_dist), 1, 1), (1, elev.shape[1], elev.shape[2])
        )
    else:
        # else shapes of arrays must be the same
        if np.shape(elev) != np.shape(sigma_dist):
            raise ValueError("Shapes of input arrays elev and sigma_dist do not match.")
        else:
            # have to change name of input sigma_dist to s_arr
            s_arr = sigma_dist
            # convert to base of preserved strat at each time based on subs
            s_arr = np.max(s_arr, axis=0) - s_arr
    # adjust and return elevation
    elev_adjusted = np.zeros_like(elev).astype(float)  # init adjusted array
    # do elevation adjustment - first dimension assumed to be time
    elev_adjusted = elev - s_arr
    # return the subsidence-adjusted elevation values
    return elev_adjusted
