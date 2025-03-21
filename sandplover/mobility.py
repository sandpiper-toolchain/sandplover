"""Functions for channel mobility metrics.

Current available mobility metrics include:
- Dry fraction decay from [Cazanacli et al 2002]_
- Planform overlap from [Wickert et al 2013]_
- Reworking index from [Wickert et al 2013]_
- Channel abandonment from [Liang et al 2016]_
- Channelized response variance from [Jarriel et al 2019]_

Also included are functions to fit curves to the output from the mobility
functions, allowing for decay constants and timescales to be quantified.

.. [Cazanacli et al 2002] Cazanacli, Dan, Chris Paola, and Gary Parker.
   "Experimental steep, braided flow: application to flooding risk on fans."
   Journal of Hydraulic Engineering 128, no. 3 (2002): 322-330.
.. [Wickert et al 2013] Wickert, Andrew D., John M. Martin, Michal Tal,
   Wonsuck Kim, Ben Sheets, and Chris Paola. "River channel lateral mobility:
   Metrics, time scales, and controls." Journal of Geophysical Research:
   Earth Surface 118, no. 2 (2013): 396-412.
.. [Liang et al 2016] Liang, Man, Corey Van Dyk, and Paola Passalacqua.
   "Quantifying the patterns and dynamics of river deltas under conditions of
   steady forcing and relative sea level rise." Journal of Geophysical Research:
   Earth Surface 121, no. 2 (2016): 465-496.
.. [Jarriel et al 2019] Jarriel, Teresa, Leo F. Isikdogan, Alan Bovik, and Paola
   Passalacqua. "Characterization of deltaic channel morphodynamics from imagery
   time series using the channelized response variance." Journal of Geophysical
   Research: Earth Surface 124, no. 12 (2019): 3022-3042.
"""

import numpy as np
import xarray as xr

from sandplover import mask


def check_inputs(
    chmap,
    basevalues=None,
    basevalues_idx=None,
    window=None,
    window_idx=None,
    landmap=None,
):
    """
    Check the input variable values.

    Ensures compatibility with mobility functions. Tries to convert from some
    potential input types (xarray data arrays, sandplover masks) if possible.

    Parameters
    ----------
    chmap : list, xarray.DataArray, numpy.ndarray
        Either a list of 2-D sandplover.mask, xarray.DataArray, or
        numpy.ndarray objects, or a t-x-y 3-D xarray.DataArray or numpy.ndarray
        with channel mask values.

    basevalues : list, int, float, optional
        List of time values to use as the base channel map. (or single value)

    basevalues_idx : list, optional
        List of time indices to use as the base channel map. (or single value)

    window : int, float, optional
        Duration of time to use as the time lag (aka how far from the basemap
        will be analyzed).

    window_idx : int, float, optional
        Duration of time in terms of indices (# of save states) to use as the
        time lag.

    landmap : list, xarray.DataArray, numpy.ndarray, optional
        Either a list of 2-D sandplover.mask, xarray.DataArray, or
        numpy.ndarray objects, or a t-x-y 3-D xarray.DataArray or numpy.ndarray
        with land mask values.

    Returns
    -------
    Same as input, but with some type sanitization.

    """
    # handle input maps - try to convert some expected types
    in_maps = {"chmap": chmap, "landmap": landmap}
    out_maps = {"chmap": None, "landmap": None}
    _skip = False
    for key in in_maps.keys():
        if in_maps[key] is None:
            _skip = True
        else:
            inmap = in_maps[key]
            _skip = False
        # first expect a list of objects and coerce them into xarray.dataarrays
        if (isinstance(inmap, list)) and (_skip is False):
            # depending on type convert to xarray.dataarray
            if isinstance(inmap[0], np.ndarray) is True:
                dims = ("time", "x", "y")  # assumes an ultimate t-x-y shape
                if len(np.shape(inmap[0])) != 2:
                    raise ValueError("Expected list to be of 2-D ndarrays.")
                coords = {
                    "time": np.arange(1),
                    "x": np.arange(inmap[0].shape[0]),
                    "y": np.arange(inmap[0].shape[1]),
                }
                _converted = [
                    xr.DataArray(
                        data=np.reshape(
                            inmap[i], (1, inmap[i].shape[0], inmap[i].shape[1])
                        ),
                        coords=coords,
                        dims=dims,
                    )
                    for i in range(len(inmap))
                ]
            elif issubclass(type(inmap[0]), mask.BaseMask) is True:
                _converted = [i.mask for i in inmap]
            elif isinstance(inmap[0], xr.DataArray) is True:
                _converted = inmap
            else:
                raise TypeError(
                    "Type of objects in the input list is not " "a recognized type."
                )
            # convert the list of xr.DataArrays into a single 3-D one
            out_maps[key] = _converted[0]  # init the final 3-D DataArray
            for j in range(1, len(_converted)):
                # stack them up along the time array into a 3-D dataarray
                out_maps[key] = xr.concat(
                    (out_maps[key], _converted[j]), dim="time"
                ).astype(float)

        elif (
            (isinstance(inmap, np.ndarray) is True)
            and (len(inmap.shape) == 3)
            and (_skip is False)
        ):
            dims = ("time", "x", "y")  # assumes t-x-y orientation of array
            coords = {
                "time": np.arange(inmap.shape[0]),
                "x": np.arange(inmap.shape[1]),
                "y": np.arange(inmap.shape[2]),
            }
            out_maps[key] = xr.DataArray(data=inmap, coords=coords, dims=dims).astype(
                float
            )

        elif (issubclass(type(inmap), mask.BaseMask) is True) and (_skip is False):
            raise TypeError(
                "Cannot input a Mask directly to mobility metrics. "
                "Use a list-of-masks instead."
            )

        elif (
            (isinstance(inmap, xr.core.dataarray.DataArray) is True)
            and (len(inmap.shape) == 3)
            and (_skip is False)
        ):
            out_maps[key] = inmap.astype(float)

        elif _skip is False:
            raise TypeError("Input mask data type or format not understood.")

    # can't do this binary check for a list
    # if ((chmap == 0) | (chmap == 1)).all():
    #     pass
    # else:
    #     raise ValueError('chmap was not binary')

    # check basevalues and time_window types
    if basevalues is not None:
        try:
            baselist = list(basevalues)
            # convert to indices of the time dimension
            basevalues = [
                np.argmin(np.abs(out_maps["chmap"].time.data - i)) for i in baselist
            ]
        except Exception as err:
            raise TypeError("basevalues was not a list or list-able obj.") from err

    if basevalues_idx is not None:
        try:
            basevalues_idx = list(basevalues_idx)
        except Exception as err:
            raise TypeError("basevalues_idx was not a list or list-able obj.") from err

    if (basevalues is not None) and (basevalues_idx is not None):
        raise Warning("basevalues and basevalues_idx supplied, using `basevalues`.")
        base_out = basevalues
    elif (basevalues is None) and (basevalues_idx is not None):
        base_out = basevalues_idx
    elif (basevalues is not None) and (basevalues_idx is None):
        base_out = basevalues
    else:
        raise ValueError("No basevalue or basevalue_idx supplied!")

    if (
        (window is not None)
        and (isinstance(window, int) is False)
        and (isinstance(window, float) is False)
    ):
        raise TypeError("Input window type was not an integer or float.")
    elif window is not None:
        # convert to index of the time dimension
        _basetime = np.min(out_maps["chmap"].time.data)  # baseline time
        _reltime = out_maps["chmap"].time.data - _basetime  # relative time
        window = int(np.argmin(np.abs(_reltime - window)) + 1)

    if (
        (window_idx is not None)
        and (isinstance(window_idx, int) is False)
        and (isinstance(window_idx, float) is False)
    ):
        raise TypeError("Input window_idx type was not an integer or float.")

    if (window is not None) and (window_idx is not None):
        raise Warning("window and window_idx supplied, using `window`.")
        win_out = window
    elif (window is None) and (window_idx is not None):
        win_out = window_idx
    elif (window is not None) and (window_idx is None):
        win_out = window
    else:
        raise ValueError("No window or window_idx supplied!")

    # check map shapes align
    if (out_maps["landmap"] is not None) and (
        np.shape(out_maps["chmap"]) != np.shape(out_maps["landmap"])
    ):
        raise ValueError("Shapes of chmap and landmap do not match.")

    # check that the combined basemap + timewindow does not exceed max t-index
    Kmax = np.max(base_out) + win_out
    if Kmax > out_maps["chmap"].shape[0]:
        raise ValueError("Largest basevalue + time_window exceeds max time.")

    # collect name of the first dimension (should be time assuming t-x-y)
    dim0 = out_maps["chmap"].dims[0]

    # return the sanitized variables
    return out_maps["chmap"], out_maps["landmap"], base_out, win_out, dim0


def calculate_channel_decay(
    chmap, landmap, basevalues=None, basevalues_idx=None, window=None, window_idx=None
):
    """
    Calculate channel decay (reduction in dry fraction).

    Uses a method similar to that in Cazanacli et al 2002 [1]_ to measure the
    dry fraction of a delta over time. This requires providing an input channel
    map, an input land map, choosing a set of base maps to use, and a time
    lag/time window over which to do the analysis.

    The dry fraction is calculated as the fraction of the land map that is
    not channelized (per the channel map) at a given time. The dry fraction
    is calculated as it changes relative to a base time. Multiple base times
    can be used, and the resulting 2-D array provides the decay of the dry
    fraction relative to each base time along each row of the array. Each
    column of the array represents the decay of the dry fraction at a given
    time lag relative to the base time. Consistent with Cazanacli et al 2002,
    the dry fraction is *not* normalized, and thus the initial dry fraction
    at the base time is not fixed at 1.0 (and likely should not be 1.0 unless
    starting with an entirely dry surface).

    .. [1] Cazanacli, Dan, Chris Paola, and Gary Parker. "Experimental steep,
           braided flow: application to flooding risk on fans." Journal of
           Hydraulic Engineering 128, no. 3 (2002): 322-330.

    Parameters
    ----------
    chmap : list, xarray.DataArray, numpy.ndarray
        Either a list of 2-D sandplover.mask, xarray.DataArray, or
        numpy.ndarray objects, or a t-x-y 3-D xarray.DataArray or numpy.ndarray
        with channel mask values.

    landmap : list, xarray.DataArray, numpy.ndarray
        Either a list of 2-D sandplover.mask, xarray.DataArray, or
        numpy.ndarray objects, or a t-x-y 3-D xarray.DataArray or numpy.ndarray
        with land mask values.

    basevalues : list, int, float, optional
        List of time values to use as the base channel map. (or single value)

    basevalues_idx : list, optional
        List of time indices to use as the base channel map. (or single value)

    window : int, float, optional
        Duration of time to use as the time lag (aka how far from the basemap
        will be analyzed).

    window_idx : int, float, optional
        Duration of time in terms of indices (# of save states) to use as the
        time lag.

    Returns
    -------
    dryfrac : ndarray
        len(basevalues) x time_window 2-D array with each row representing
        the dry fraction (aka number of pixels not visited by a channel) in
        reference to a given base value at a certain time lag (column)

    """
    # sanitize the inputs first
    chmap, landmap, basevalues, time_window, dim0 = check_inputs(
        chmap, basevalues, basevalues_idx, window, window_idx, landmap
    )

    # initialize dry fraction array
    dims = ("base", dim0)  # base and time-lag dimensions
    coords = {
        "base": np.arange(len(basevalues)),
        dim0: chmap[dim0][:time_window].values,
    }
    dryfrac = xr.DataArray(
        data=np.zeros((len(basevalues), time_window)), coords=coords, dims=dims
    )

    # loop through basevalues
    for i in range(0, len(basevalues)):
        # pull the corresponding time index for the base value
        Nbase = basevalues[i]
        # first get the dry map (non-channelized locations)
        base_dry = np.abs(chmap[Nbase, :, :] - landmap[Nbase, :, :])

        # define base landmap
        base_map = landmap[Nbase, :, :]

        # set first dry fraction at t=0
        dryfrac[i, 0] = np.sum(base_dry) / np.sum(base_map)

        # loop through the other maps to see how the dry area declines
        for Nstep in range(1, time_window):
            # get the incremental map
            chA_step = chmap[Nbase + Nstep, :, :]
            # subtract incremental map from dry map to get the new dry fraction
            base_dry -= chA_step
            # just want binary (1 = never channlized, 0 = channel visited)
            base_dry.values[base_dry.values < 0] = 0  # no need to have negative values
            # store remaining dry fraction
            dryfrac[i, Nstep] = np.sum(base_dry) / np.sum(base_map)

    return dryfrac


def calculate_planform_overlap(
    chmap, landmap, basevalues=None, basevalues_idx=None, window=None, window_idx=None
):
    """
    Calculate channel planform overlap.

    This metric is calculated per Wickert et al 2013 [1]_ and measures
    the loss of channel system overlap with previous channel patterns.
    This requires an input channel map, land map, as well as defining the base
    maps to use and the time window over which you want to look.

    The normalized overlap is calculated as:

    .. math::

        O_\\Phi = 1 - \\left( \\frac{D}{A \\cdot \\Phi} \\right)

    where :math:`D` is the number of chaneged pixels between the base and
    target maps, :math:`A` is the total number of pixels in a single map,
    and :math:`\\Phi` is a random scatter parameter.

    :math:`D` is calculated as:

    .. math::

        D(B, T) = \\sum\\limits^{m_r}_{i=1} \\sum\\limits^{n_c}_{j=1}
                  \\left| K_B - K_T \\right|

    where :math:`K_B` and :math:`K_T` are the channel mask values at the base
    and target maps, respectively.

    :math:`\\Phi` is calculated as:

    .. math::

        \\Phi = f_{w,B} \\cdot f_{d,T} + f_{d,B} \\cdot f_{w,T}

    where :math:`f_{w,B}` is the fraction of water pixels in the base map,
    :math:`f_{d,B}` is the fraction of dry pixels in the base map,
    :math:`f_{w,T}` is the fraction of water pixels in the target map, and
    :math:`f_{d,T}` is the fraction of dry pixels in the target map.

    The calculation of :math:`O_\\Phi` is conducted between the base map(s) and
    channel maps (target maps) at each time lag for the duration of the
    time window specified. When multiple base maps are used, this calculation
    is conducted for each base map and its corresponding target maps, and
    the results are returned as an array in which each row represents the
    overlap results for a given base map. Each column represents the overlap
    results for a given time lag relative to the base map.

    .. [1] Wickert, Andrew D., John M. Martin, Michal Tal, Wonsuck Kim,
           Ben Sheets, and Chris Paola. "River channel lateral mobility:
           Metrics, time scales, and controls." Journal of Geophysical
           Research: Earth Surface 118, no. 2 (2013): 396-412.

    Parameters
    ----------
    chmap : list, xarray.DataArray, numpy.ndarray
        Either a list of 2-D sandplover.mask, xarray.DataArray, or
        numpy.ndarray objects, or a t-x-y 3-D xarray.DataArray or numpy.ndarray
        with channel mask values.

    landmap : list, xarray.DataArray, numpy.ndarray
        Either a list of 2-D sandplover.mask, xarray.DataArray, or
        numpy.ndarray objects, or a t-x-y 3-D xarray.DataArray or numpy.ndarray
        with land mask values.

    basevalues : list, int, float, optional
        List of time values to use as the base channel map. (or single value)

    basevalues_idx : list, optional
        List of time indices to use as the base channel map. (or single value)

    window : int, float, optional
        Duration of time to use as the time lag (aka how far from the basemap
        will be analyzed).

    window_idx : int, float, optional
        Duration of time in terms of indices (# of save states) to use as the
        time lag.

    Returns
    -------
    Ophi : ndarray
        A 2-D array of the normalized overlap values, array is of shape
        len(basevalues) x time_window so each row in the array represents
        the overlap values associated with a given base value and the
        columns are associated with each time lag.

    """
    # sanitize the inputs first
    chmap, landmap, basevalues, time_window, dim0 = check_inputs(
        chmap, basevalues, basevalues_idx, window, window_idx, landmap
    )

    # initialize D, phi and Ophi
    dims = ("base", dim0)  # base and time-lag dimensions
    coords = {
        "base": np.arange(len(basevalues)),
        dim0: chmap[dim0][:time_window].values,
    }
    D = xr.DataArray(
        data=np.zeros((len(basevalues), time_window)), coords=coords, dims=dims
    )
    phi = xr.zeros_like(D)
    Ophi = xr.zeros_like(D)

    # loop through the base maps
    for j in range(0, len(basevalues)):
        # define variables associated with the base map
        fdrybase = 1 - (
            np.sum(chmap[basevalues[j], :, :]) / np.sum(landmap[basevalues[j], :, :])
        )
        fwetbase = np.sum(chmap[basevalues[j], :, :]) / np.sum(
            landmap[basevalues[j], :, :]
        )
        # transient maps compared over the fluvial surface present in base map
        mask_map = landmap[basevalues[j], :, :]

        # loop through the transient maps associated with this base map
        for i in range(0, time_window):
            D[j, i] = np.sum(
                np.abs(
                    chmap[basevalues[j], :, :] * mask_map
                    - chmap[basevalues[j] + i, :, :] * mask_map
                )
            )
            fdrystep = 1 - (
                np.sum(chmap[basevalues[j] + i, :, :] * mask_map) / np.sum(mask_map)
            )
            fwetstep = np.sum(chmap[basevalues[j] + i, :, :] * mask_map) / np.sum(
                mask_map
            )
            phi[j, i] = fwetbase * fdrystep + fdrybase * fwetstep
            # for Ophi use a standard area in denominator, we use base area
            Ophi[j, i] = 1 - D[j, i] / (np.sum(mask_map) * phi[j, i])
    # just return the Ophi
    return Ophi


def calculate_reworking_fraction(
    chmap, landmap, basevalues=None, basevalues_idx=None, window=None, window_idx=None
):
    """
    Calculate the reworking fraction.

    Uses a method similar to that described in Wickert et al 2013 [1]_ to
    measure the reworking of the fluvial surface with time. This requires an
    input channel map, land map, as well as defining the base maps to use and
    the time window over which you want to look.

    The reworking fraction is calculated as:

    .. math::

        f_{R} = 1 - \\frac{N'_{B,T}}{A \\cdot f_{d,B}}

    where :math:`f_{R}` is the reworking fraction, :math:`N'_{B,T}` is the
    number of unreworked cells in the transient map, :math:`A` is the area of
    fluvial surface, and :math:`f_{d,B}` is the dry fraction of the base map.

    :math:`N'_{B,T}` is calculated as:

    .. math::

        N'_{B,T} = \\sum_{i=1}^{m_r} \\sum_{j=1}^{n_c} \\left[
                       \\left(
                           \\sum_{\\beta = B+1}^{T} K'_{\\beta}
                       \\right) \\equiv 0
                   \\right]


    where :math:`m_r` and :math:`n_c` are the number of rows and columns in the
    base map, :math:`K'_{\\beta}` is the channel mask at time :math:`\\beta` when
    :math:`\\beta` is used for each time step after the baseline time. This
    results in :math:`N'_{B,T}` being the number of cells that are not
    reworked at some transient time :math:`T` relative to the base time
    :math:`B`.

    .. [1] Wickert, Andrew D., John M. Martin, Michal Tal, Wonsuck Kim,
           Ben Sheets, and Chris Paola. "River channel lateral mobility:
           Metrics, time scales, and controls." Journal of Geophysical
           Research: Earth Surface 118, no. 2 (2013): 396-412.

    Parameters
    ----------
    chmap : list, xarray.DataArray, numpy.ndarray
        Either a list of 2-D sandplover.mask, xarray.DataArray, or
        numpy.ndarray objects, or a t-x-y 3-D xarray.DataArray or numpy.ndarray
        with channel mask values.

    landmap : list, xarray.DataArray, numpy.ndarray
        Either a list of 2-D sandplover.mask, xarray.DataArray, or
        numpy.ndarray objects, or a t-x-y 3-D xarray.DataArray or numpy.ndarray
        with land mask values.

    basevalues : list, int, float, optional
        List of time values to use as the base channel map. (or single value)

    basevalues_idx : list, optional
        List of time indices to use as the base channel map. (or single value)

    window : int, float, optional
        Duration of time to use as the time lag (aka how far from the basemap
        will be analyzed).

    window_idx : int, float, optional
        Duration of time in terms of indices (# of save states) to use as the
        time lag.

    Returns
    -------
    fr : ndarray
        A 2-D array of the reworked fraction values, array is of shape
        len(basevalues) x time_window so each row in the array represents
        the overlap values associated with a given base value and the
        columns are associated with each time lag.

    """
    # sanitize the inputs first
    chmap, landmap, basevalues, time_window, dim0 = check_inputs(
        chmap, basevalues, basevalues_idx, window, window_idx, landmap
    )

    # initialize unreworked pixels (Nbt) and reworked fraction (fr)
    dims = ("base", dim0)  # base and time-lag dimensions
    coords = {
        "base": np.arange(len(basevalues)),
        dim0: chmap[dim0][:time_window].values,
    }
    Nbt = xr.DataArray(
        data=np.zeros((len(basevalues), time_window)), coords=coords, dims=dims
    )
    fr = xr.zeros_like(Nbt)

    # loop through the base maps
    for j in range(0, len(basevalues)):
        # define variables associated with the base map
        base = basevalues[j]
        # fluvial surface is considered to be the one present in base map
        basemask = landmap[base, :, :]
        notland = len(np.where(basemask == 0)[0])  # number of not-land pixels
        basechannels = chmap[base, :, :]
        fbase = basemask - basechannels
        fdrybase = np.sum(fbase) / np.sum(basemask)

        # initialize channelmap series through time (kb) using initial chmap
        kb = np.copy(basechannels)

        # loop through the transient maps associated with this base map
        for i in range(0, time_window):
            # if i == 0 no reworking has happened yet
            if i == 0:
                Nbt[j, i] = fdrybase * np.sum(basemask)
                fr[j, i] = 0
            else:
                # otherwise situation is different

                # transient channel map withint base fluvial surface
                tmap = chmap[base + i, :, :] * basemask

                # add to kb
                kb += tmap

                # unreworked pixels are those channels have not visited
                # get this by finding all 0s left in kb and subtracting
                # the number of non-land pixels from base fluvial surface
                unvisited = len(np.where(kb == 0)[0])
                Nbt[j, i] = unvisited - notland
                fr[j, i] = 1 - (Nbt[j, i] / (np.sum(basemask) * fdrybase))

    # just return the reworked fraction
    return fr


def calculate_channel_abandonment(
    chmap, basevalues=None, basevalues_idx=None, window=None, window_idx=None
):
    """
    Calculate channel abandonment.

    Measure the number of channelized pixels that are no longer channelized as
    a signature of channel mobility based on method in Liang et al 2016 [1]_.
    This requires providing an input channel map, and setting parameters for
    the min/max values to compare to, and the time window over which the
    evaluation can be done.

    This calculation is performed by first identifying the number of channel
    pixels at some base time. Then, for each time step after the base time,
    we measure the number of pixels that are no longer channelized. This
    measurement is used to calculate the fraction of channel pixels that are
    abandoned relative to the base channel map for each time step. Multiple
    base times can be provided. The results are returned as a 2-D array in
    which each row represents the abandonment values associated with a given
    base value and the columns are associated with each time lag.

    .. [1] Liang, Man, Wonsuck Kim, and Paola Passalacqua. "How much subsidence
           is enough to change the morphology of river deltas?." Geophysical
           Research Letters 43, no. 19 (2016): 10-266.

    Parameters
    ----------
    chmap : list, xarray.DataArray, numpy.ndarray
        Either a list of 2-D sandplover.mask, xarray.DataArray, or
        numpy.ndarray objects, or a t-x-y 3-D xarray.DataArray or numpy.ndarray
        with channel mask values.

    basevalues : list, int, float, optional
        List of time values to use as the base channel map. (or single value)

    basevalues_idx : list, optional
        List of time indices to use as the base channel map. (or single value)

    window : int, float, optional
        Duration of time to use as the time lag (aka how far from the basemap
        will be analyzed).

    window_idx : int, float, optional
        Duration of time in terms of indices (# of save states) to use as the
        time lag.

    Returns
    -------
    PwetA : ndarray
        A 2-D array of the abandoned fraction of the channel over the window of
        time. It is of shape len(basevalues) x time_window so each row
        represents the fraction of the channel that has been abandonded, and
        the columns are associated with each time lag.

    """
    # sanitize the inputs first
    chmap, landmap, basevalues, time_window, dim0 = check_inputs(
        chmap, basevalues, basevalues_idx, window, window_idx
    )
    # initialize values
    dims = ("base", dim0)  # base and time-lag dimensions
    coords = {
        "base": np.arange(len(basevalues)),
        dim0: chmap[dim0][:time_window].values,
    }
    PwetA = xr.DataArray(
        data=np.zeros((len(basevalues), time_window)), coords=coords, dims=dims
    )
    chA_base = xr.zeros_like(chmap[0, :, :])
    chA_step = xr.zeros_like(chmap[0, :, :])

    # loop through the basevalues
    for i in range(0, len(basevalues)):
        # first get the 'base' channel map that is being compared to
        Nbase = basevalues[i]
        chA_base = chmap[Nbase, :, :]
        # get total number of channel pixels in that map
        baseA = np.sum(chA_base)
        # loop through the other maps to be compared against the base map
        for Nstep in range(1, time_window):
            # get the incremental map
            chA_step = chmap[Nbase + Nstep, :, :]
            # get the number of pixels that were abandonded
            stepA = len(
                np.where(chA_base.values.flatten() > chA_step.values.flatten())[0]
            )
            # store this number in the PwetA array for each transient map
            PwetA[i, Nstep] = stepA / baseA

    return PwetA


def channel_presence(chmap):
    """
    Calculate the normalized channel presence at each pixel location.

    Measure the normalized fraction of time a given pixel is channelized,
    based on method in Liang et al 2016 [1]_. This requires providing a 3-D input
    channel map (t-x-y).

    .. [1] Liang, Man, Corey Van Dyk, and Paola Passalacqua. "Quantifying the
           patterns and dynamics of river deltas under conditions of steady
           forcing and relative sea level rise." Journal of Geophysical
           Research: Earth Surface 121, no. 2 (2016): 465-496.

    Parameters
    ----------
    chmap : ndarray
        A t-x-y shaped array with binary channel maps

    Returns
    -------
    channel_presence : ndarray
        A x-y shaped array with the normalized channel presence values.

    Examples
    --------

    .. plot::

        >>> import matplotlib.pyplot as plt
        >>> import numpy as np
        >>> from sandplover.mask import ChannelMask
        >>> from sandplover.mobility import channel_presence
        >>> from sandplover.plot import append_colorbar
        >>> from sandplover.sample_data.sample_data import golf

        >>> golfcube = golf()
        >>> (x, y) = np.shape(golfcube["eta"][-1, ...])

        Calculate channel masks/presence over final 5 timesteps

        >>> chmap = np.zeros((5, x, y))  # initialize channel map
        >>> for i in np.arange(-5, 0):
        ...     chmap[i, ...] = ChannelMask(
        ...         golfcube["eta"][i, ...],
        ...         golfcube["velocity"][i, ...],
        ...         elevation_threshold=0,
        ...         flow_threshold=0,
        ...     ).mask
        ...
        >>>
        >>> fig, ax = plt.subplots(1, 2)
        >>> golfcube.quick_show("eta", ax=ax[0])  # final delta
        >>> p = ax[1].imshow(channel_presence(chmap), cmap="Blues")
        >>> _ = append_colorbar(p, ax[1], label="Channelized Time")
    """
    tmp_chans = None  # instantiate
    if isinstance(chmap, mask.ChannelMask) is True:
        chans = chmap._mask
    elif isinstance(chmap, np.ndarray) is True:
        tmp_chans = chmap
    elif isinstance(chmap, xr.DataArray) is True:
        chans = chmap
    elif isinstance(chmap, list) is True:
        # convert to numpy.ndarray if possible
        if (isinstance(chmap[0], np.ndarray) is True) or (
            isinstance(chmap[0], xr.DataArray) is True
        ):
            # init empty array
            tmp_chans = np.zeros(
                (len(chmap), chmap[0].squeeze().shape[0], chmap[0].squeeze().shape[1])
            )
            # populate it
            for i in range(len(chmap)):
                if isinstance(chmap[0], xr.DataArray) is True:
                    tmp_chans[i, ...] = chmap[i].data.squeeze()
                else:
                    tmp_chans[i, ...] = chmap[i].squeeze()
        elif issubclass(type(chmap[0]), mask.BaseMask) is True:
            tmp_chans = [i.mask for i in chmap]
            # convert list to ndarray
            chans = np.zeros(
                (len(tmp_chans), tmp_chans[0].shape[1], tmp_chans[0].shape[2])
            )
            for i in range(chans.shape[0]):
                chans[i, ...] = tmp_chans[i]
        else:
            raise ValueError("Invalid values in the supplied list.")
    else:
        raise TypeError("chmap data type not understood.")
    # if tmp_chans is a numpy.ndarray, dimensions are not known
    if isinstance(tmp_chans, np.ndarray):
        dims = ("time", "x", "y")  # assumes an ultimate t-x-y shape
        coords = {
            "time": np.arange(tmp_chans.shape[0]),
            "x": np.arange(tmp_chans.shape[1]),
            "y": np.arange(tmp_chans.shape[2]),
        }
        chans = xr.DataArray(data=tmp_chans, coords=coords, dims=dims)
    # calculation of channel presence is actually very simple
    channel_presence = np.sum(chans, axis=0) / chans.shape[0]
    return channel_presence


def calculate_channelized_response_variance(
    arr, threshold=0.2, normalize_input=False, normalize_output=False
):
    """
    Calculate the Channelized Response Variance (CRV).

    This function takes a t-x-y array and calculates its directional CRV [1]_.
    In short, the function does the following:

    1. Normalizes the array at each time slice if desired.
    2. Calculates the CRV magnitude (aka variance along time-axis) and
       normalizes this array if desired.
    3. Does linear regressions through time for each pixel and returns
       the slopes.
    4. Calculates the directional CRV using a slope threshold value.
    5. Returns the CRV magnitude, slopes, and directional CRV
       values

    .. [1] Jarriel, Teresa, Leo F. Isikdogan, Alan Bovik, and Paola
           Passalacqua. "Characterization of deltaic channel morphodynamics
           from imagery time series using the channelized response variance."
           Journal of Geophysical Research: Earth Surface 124, no. 12 (2019):
           3022-3042.

    Parameters
    ----------
    arr : numpy.ndarray
        A t-x-y 3-D array to calculate the CRV on.

    threshold : float, optional
        Threshold for CRV calculation. The default is 0.2.

    normalize_input : bool, optional
        Whether to normalize the input images pixel values to 0-1.
        The default is False.

    normalize_output : bool, optional
        Whether to normalize the output image pixel values to 0-1.
        The default is False.

    Returns
    -------
    crv_magnitude : numpy.ndarray
        A t-x-y 3-D array with the CRV magnitude.

    slopes : numpy.ndarray
        A t-x-y 3-D array with the slopes of the linear regressions.

    directional_crv : numpy.ndarray
        A t-x-y 3-D array with the directional CRV.

    Examples
    --------

    .. plot::

        >>> import matplotlib.pyplot as plt
        >>> import numpy as np
        >>> from sandplover.mobility import calculate_channelized_response_variance
        >>> from sandplover.plot import append_colorbar
        >>> from sandplover.sample_data.sample_data import savi2020

        Load overhead imagery sample data from Savi et al 2020

        >>> img, _ = savi2020()

        Calculate the CRV on the "Red" band

        >>> crv_mag, slopes, crv = calculate_channelized_response_variance(
        ...     img["red"].data,
        ...     threshold=0.0,
        ...     normalize_input=True,
        ...     normalize_output=True,
        ... )

        Plot the results

        >>> fig, ax = plt.subplots(1, 3, figsize=(13, 5))
        >>> i0 = ax[0].imshow(crv_mag, vmin=0, vmax=1)
        >>> _ = ax[0].set_title("CRV Magnitude")
        >>> _ = append_colorbar(i0, ax=ax[0], size=10)
        >>> s_ex = np.max([np.abs(slopes.min()), slopes.max()])
        >>> i1 = ax[1].imshow(slopes, vmin=-1 * s_ex, vmax=s_ex, cmap="PuOr")
        >>> _ = ax[1].set_title("CRV Slopes")
        >>> _ = append_colorbar(i1, ax=ax[1], size=10)
        >>> i2 = ax[2].imshow(crv, vmin=-1, vmax=1, cmap="seismic")
        >>> _ = ax[2].set_title("Directional CRV")
        >>> _ = append_colorbar(i2, ax=ax[2], size=10)
        >>> _ = fig.suptitle("CRV of Red band from imagery from Savi et al 2020")
    """
    # normalize the input array if desired
    if normalize_input is True:
        for t in range(arr.shape[0]):
            arr[t, ...] = arr[t, ...] / np.max(arr[t, ...])

    # calculate the CRV magnitude
    crv_magnitude = np.var(arr, axis=0)  # calculate variance
    # normalize if desired
    if normalize_output is True:
        crv_magnitude = crv_magnitude / crv_magnitude.max()

    # calculate the slopes of the linear regressions
    slopes = _calculate_temporal_linear_slope(arr)

    # calculate the directional CRV
    # threshold the slopes array
    # first determine which slopes are below the threshold
    slopes_abs = np.abs(slopes)
    slopes_abs[slopes_abs < threshold] = 0
    slopes_abs[slopes_abs >= threshold] = 1
    # zero out the CRV values where the slope is below the threshold
    slopes_thresholded = slopes * slopes_abs
    # then assign -1 and 1 values where they belong
    slopes_thresholded[slopes_thresholded <= -1 * threshold] = -1
    slopes_thresholded[slopes_thresholded >= threshold] = 1
    # final calculation of directional CRV
    directional_crv = slopes_thresholded * crv_magnitude

    # return the CRV magnitude, slopes, and directional CRV
    return crv_magnitude, slopes, directional_crv


def _calculate_temporal_linear_slope(stack):
    """
    Fits linear regressions and calculates slopes.

    This function calculates the slopes of the linear regressions for each
    pixel through time (axis 0). The slopes are the slope of the
    linear regression through time for each pixel.

    Parameters
    ----------
    stack : numpy array
        Stack of images as a t-x-y numpy array.

    Returns
    -------
    slopes : numpy array
        Slopes as a t-x-y numpy array.

    """
    # define x and y for linear regression
    x = np.arange(0, stack.shape[0])  # simple 0-n vector
    # convert stack from size [t,x,y] to [t, x*y]
    y = np.reshape(stack, [stack.shape[0], stack.shape[1] * stack.shape[2]])

    # do least squares regression
    # based on stackoverflow: https://stackoverflow.com/a/20344897
    slopes, _ = np.linalg.lstsq(np.c_[x, np.ones_like(x)], y, rcond=None)[0]

    # reshape
    slopes = np.reshape(slopes, [stack.shape[1], stack.shape[2]])

    return slopes
