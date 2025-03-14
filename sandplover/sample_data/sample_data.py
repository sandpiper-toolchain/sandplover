import os
import sys
import warnings

import pooch

if sys.version_info >= (3, 12):  # pragma: no cover (PY12+)
    import importlib.resources as importlib_resources
else:  # pragma: no cover (<PY312)
    import importlib_resources

from sandplover.cube import DataCube

# enusre DeprecationWarning is shown
warnings.simplefilter("default")


# configure the data registry
REGISTRY = pooch.create(
    path=pooch.os_cache("sandplover"),
    base_url=(
        "https://github.com/sandpiper-toolchain/sandplover/raw/develop/"
        "sandplover/sample_data/files/"
    ),
    env="DELTAMETRICS_DATA_DIR",
)
path_to_registry = importlib_resources.files("sandplover.sample_data").joinpath(
    "registry.txt"
)
with open(path_to_registry, "rb") as registry_file:
    REGISTRY.load_registry(registry_file)


def _get_golf_path():
    unpack = pooch.Unzip()
    fnames = REGISTRY.fetch("golf.zip", processor=unpack)
    nc_bool = [os.path.splitext(fname)[1] == ".nc" for fname in fnames]
    nc_idx = [i for i, b in enumerate(nc_bool) if b]
    golf_path = fnames[nc_idx[0]]
    return golf_path


def golf():
    """Golf Delta dataset.

    This is a synthetic delta dataset generated from the pyDeltaRCM numerical
    model. This model run was created to generate sample data. Model was run
    on 10/14/2021, at the University of Texas at Austin.

    Run was computed with pyDeltaRCM v2.1.0. See log file for complete
    information on system and model configuration.

    Data available at Zenodo, https://doi.org/10.5281/zenodo.4456143.

    Version history:
      * v1.1: 10.5281/zenodo.5570962
      * v1.0: 10.5281/zenodo.4456144

    .. plot::

        >>> import matplotlib.pyplot as plt
        >>> import numpy as np
        >>> from sandplover.sample_data.sample_data import golf

        >>> golf = golf()
        >>> nt = 5
        >>> ts = np.linspace(0, golf["eta"].shape[0] - 1, num=nt, dtype=int)

        >>> fig, ax = plt.subplots(1, nt, figsize=(12, 2))
        >>> for i, t in enumerate(ts):
        ...     _ = ax[i].imshow(golf["eta"][t, :, :], vmin=-2, vmax=0.5)
        ...     _ = ax[i].set_title(f"t = {t}")
        ...     _ = ax[i].axes.get_xaxis().set_ticks([])
        ...     _ = ax[i].axes.get_yaxis().set_ticks([])
        ...
        >>> _ = ax[0].set_ylabel("dim1 direction")
        >>> _ = ax[0].set_xlabel("dim2 direction")
    """
    golf_path = _get_golf_path()
    return DataCube(golf_path)


def _get_xslope_path():
    unpack = pooch.Unzip()
    fnames = REGISTRY.fetch("xslope.zip", processor=unpack)
    nc_bool = [os.path.splitext(fname)[1] == ".nc" for fname in fnames]
    # nc_idx = [i for i, b in enumerate(nc_bool) if b]
    fnames_idx = [fnames[i] for i, b in enumerate(nc_bool) if b]
    fnames_idx.sort()
    # xslope_path = fnames[nc_idx[0]]
    xslope_job_003_path = fnames_idx[0]
    xslope_job_013_path = fnames_idx[1]
    return xslope_job_003_path, xslope_job_013_path


def xslope():
    """xslope delta dataset.

    The delta model runs in this dataset were executed in support of a
    demonstration and teaching clinic. The set of simualtions examines the
    effect of a basin with cross-stream slope on the progradation of a delta
    system.

    .. important::

        This sample data provides **two** datasets. Calling this function
        returns two :obj:`~spl.cube.DataCube`.

    Models were run on 02/21/2022, at the University of Texas at Austin.

    Runs were computed with pyDeltaRCM v2.1.2. See log files for complete
    information on system and model configuration.

    Data available at Zenodo, version 1.1: https://doi.org/10.5281/zenodo.6301362

    Version history:
      * v1.0: 10.5281/zenodo.6226448
      * v1.1: 10.5281/zenodo.6301362

    .. plot::

        >>> import matplotlib.pyplot as plt
        >>> import numpy as np
        >>> from sandplover.sample_data.sample_data import xslope

        >>> xslope0, xslope1 = xslope()
        >>> nt = 5
        >>> ts = np.linspace(0, xslope0["eta"].shape[0] - 1, num=nt, dtype=int)

        >>> fig, ax = plt.subplots(2, nt, figsize=(12, 2))
        >>> for i, t in enumerate(ts):
        ...     _ = ax[0, i].imshow(xslope0["eta"][t, :, :], vmin=-10, vmax=0.5)
        ...     _ = ax[0, i].set_title(f"t = {t}")
        ...     _ = ax[1, i].imshow(xslope1["eta"][t, :, :], vmin=-10, vmax=0.5)
        ...

        >>> _ = ax[1, 0].set_ylabel("dim1 direction")
        >>> _ = ax[1, 0].set_xlabel("dim2 direction")

        >>> for axi in ax.ravel():
        ...     _ = axi.axes.get_xaxis().set_ticks([])
        ...     _ = axi.axes.get_yaxis().set_ticks([])
        ...

    Parameters
    ----------

    Returns
    -------
    xslope0
        First return, a :obj:`~spl.cube.DataCube` with flat basin.

    xslope1
        Second return, a :obj:`~spl.cube.DataCube` with sloped basin in the
        cross-stream direction. Slope is 0.001 m/m, with elevation centered
        at channel inlet.
    """
    xslope_path0, xslope_path1 = _get_xslope_path()
    return DataCube(xslope_path0), DataCube(xslope_path1)


def tdb12():
    raise NotImplementedError


def _get_aeolian_path():
    aeolian_path = REGISTRY.fetch("swanson_aeolian_expt1.nc")
    return aeolian_path


def aeolian():
    """An aeolian dune field dataset.

    This is a synthetic delta dataset generated from the Swanson et al.,
    2017 "A Surface Model for Aeolian Dune Topography" numerical model. The
    data have been subsetted, only keeping the first 500 saved timesteps, and
    formatted into a netCDF file.

    Swanson, T., Mohrig, D., Kocurek, G. et al. A Surface Model for Aeolian
    Dune Topography. Math Geosci 49, 635–655
    (2017). https://doi.org/10.1007/s11004-016-9654-x

    Dataset reference: https://doi.org/10.6084/m9.figshare.17118827.v1

    Details:
      * default simualtion parameters were used.
      * only the first 500 timesteps of the simulation were recorded into
        the netcdf file.
      * the *ordering* for "easting" and "northing" coordinates in the
        netCDF file is opposite from the paper---that is the source region
        is along the second axis, i.e., ``dim1[source_regiom]==0``. The
        display of this dataset is thus different from the original
        paper, *but the data are the same*.
      * simulation used the model code included as a supplement to the paper
        found here:
        https://static-content.springer.com/esm/art%3A10.1007%2Fs11004-016-9654-x/MediaObjects/11004_2016_9654_MOESM5_ESM.txt
      * simulation was executed on 12/02/2021 with Matlab R2021a on Ubuntu
        20.04.

    .. plot::

        >>> import matplotlib.pyplot as plt
        >>> import numpy as np
        >>> import sandplover as spl

        >>> aeolian = spl.sample_data.aeolian()
        >>> nt = 5
        >>> ts = np.linspace(0, aeolian["eta"].shape[0] - 1, num=nt, dtype=int)

        >>> fig, ax = plt.subplots(1, nt, figsize=(8, 4))
        >>> for i, t in enumerate(ts):
        ...     _ = ax[i].imshow(aeolian["eta"][t, :, :], vmin=-5, vmax=7)
        ...     _ = ax[i].set_title(f"t = {t}")
        ...     _ = ax[i].axes.get_xaxis().set_ticks([])
        ...     _ = ax[i].axes.get_yaxis().set_ticks([])
        ...
        >>> _ = ax[0].set_ylabel("northing")
        >>> _ = ax[0].set_xlabel("easting")
    """
    aeolian_path = _get_aeolian_path()
    return DataCube(aeolian_path)


def _get_rcm8_path():
    rcm8_path = REGISTRY.fetch("pyDeltaRCM_Output_8.nc")
    return rcm8_path


def rcm8():
    """Rcm8 Delta dataset.

    This is a synthetic delta dataset generated from the pyDeltaRCM numerical
    model. Unfortunately, we do not know the specific version of pyDeltaRCM
    the model run was executed with. Moreover, many new coupling features have
    been added to pyDeltaRCM and sandplover since this run. As a result,
    this dataset is slated to be deprecated at some point, in favor of the
    :obj:`golf` dataset.

    .. important::

        If you are learning to use sandplover or developing new codes or
        documentation, please use the :obj:`golf` delta dataset.

    .. warning:: This cube may be removed in future releases.

    .. plot::

        >>> import matplotlib.pyplot as plt
        >>> import numpy as np
        >>> import warnings
        >>> import sandplover as spl

        >>> with warnings.catch_warnings():
        ...     warnings.simplefilter("ignore")
        ...     rcm8 = spl.sample_data.rcm8()
        ...
        >>> nt = 5
        >>> ts = np.linspace(0, rcm8["eta"].shape[0] - 1, num=nt, dtype=int)

        >>> fig, ax = plt.subplots(1, nt, figsize=(12, 2))
        >>> for i, t in enumerate(ts):
        ...     _ = ax[i].imshow(rcm8["eta"][t, :, :], vmin=-2, vmax=0.5)
        ...     _ = ax[i].set_title(f"t = {t}")
        ...     _ = ax[i].axes.get_xaxis().set_ticks([])
        ...     _ = ax[i].axes.get_yaxis().set_ticks([])
        ...
        >>> _ = ax[0].set_ylabel("y-direction")
        >>> _ = ax[0].set_xlabel("x-direction")
    """
    rcm8_path = _get_rcm8_path()
    return DataCube(rcm8_path)


def _get_landsat_path():
    landsat_path = REGISTRY.fetch("LandsatEx.hdf5")
    return landsat_path


def landsat():
    """Landsat image dataset.

    This is a set of satellite images from the Landsat 5 satellite, collected
    over the Krishna River delta, India. The dataset includes annual-composite
    scenes from four different years (`[1995, 2000, 2005, 2010]`) and includes
    data collected from four bands (`['Red', 'Green', 'Blue', 'NIR']`).

    .. plot::

        >>> import matplotlib.pyplot as plt
        >>> import numpy as np
        >>> import sandplover as spl

        >>> landsat = spl.sample_data.landsat()
        >>> nt = landsat.shape[0]

        >>> maxr = np.max(landsat["Red"][:])
        >>> maxg = np.max(landsat["Green"][:])
        >>> maxb = np.max(landsat["Blue"][:])

        >>> fig, ax = plt.subplots(1, nt, figsize=(12, 2))
        >>> for i in np.arange(nt):
        ...     _arr = np.dstack(
        ...         (
        ...             landsat["Red"][i, :, :] / maxr,
        ...             landsat["Green"][i, :, :] / maxg,
        ...             landsat["Blue"][i, :, :] / maxb,
        ...         )
        ...     )
        ...     _ = ax[i].imshow(_arr)
        ...     _ = ax[i].set_title(f"year = {landsat.t[i]}")
        ...     _ = ax[i].axes.get_xaxis().set_ticks([])
        ...     _ = ax[i].axes.get_yaxis().set_ticks([])
        ...
    """
    landsat_path = _get_landsat_path()
    return DataCube(landsat_path)


def _get_savi2020_path():
    unpack = pooch.Unzip()
    fnames = REGISTRY.fetch("savi2020.zip", processor=unpack)
    nc_bool = [os.path.splitext(fname)[1] == ".nc" for fname in fnames]
    fnames_idx = [fnames[i] for i, b in enumerate(nc_bool) if b]
    fnames_idx.sort()
    savi2020_img_path = fnames_idx[0]
    savi2020_scan_path = fnames_idx[1]
    return savi2020_img_path, savi2020_scan_path


def savi2020():
    """Dataset from No Change 2 experiment in Savi et al., 2020.

    This is a dataset from one of the physical experiments conducted as part of
    the work presented in Savi et al., 2020. Specifically, these data are from
    the No Change 2 (NC2) experiment. Two netCDF files have been prepared, one
    containing a subset of the overhead imagery collected during the experiment
    at a temporal resolution of roughly one image a minute (the full dataset
    is closer to an image every 20 seconds). The second file contains the
    topographic scan data which was taken once every 30 minutes.

    Savi, Sara, et al. "Interactions between main channels and tributary
    alluvial fans: channel adjustments and sediment-signal propagation."
    Earth Surface Dynamics 8.2 (2020): 303-322.
    https://doi.org/10.5194/esurf-8-303-2020

    Physical experiments on interactions between main-channels and
    tributary alluvial fans. S. Savi, Tofelde, A. Wickert, A. Bufe,
    T. Schildgen, and M. Strecker. https://doi.org/10.26009/s0ZOQ0S6

    .. important::

        This sample data provides **two** datasets. Calling this function
        returns two :obj:`~spl.cube.DataCube` objects.

    Data available at Zenodo, version 1.1: https://doi.org/10.5281/zenodo.7080126

    Version history:
      * v1.1: 10.5281/zenodo.7080126
      * v1.0: 10.5281/zenodo.7047109

    .. plot::

        >>> import matplotlib.pyplot as plt
        >>> import numpy as np
        >>> import sandplover as spl

        >>> img, scans = spl.sample_data.savi2020()
        >>> nt = 5
        >>> ts_i = np.linspace(0, img["red"].shape[0] - 1, num=nt, dtype=int)
        >>> ts_s = np.linspace(0, scans["eta"].shape[0] - 1, num=nt, dtype=int)

        >>> fig, ax = plt.subplots(2, nt, figsize=(9, 6))
        >>> for i in range(nt):
        ...     _ = ax[0, i].imshow(img["red"][ts_i[i], :, :], vmin=0, vmax=1)
        ...     _ = ax[0, i].set_title(f"t = {ts_i[i]}")
        ...     _ = ax[1, i].imshow(scans["eta"][ts_s[i], :, :])
        ...     _ = ax[1, i].set_title(f"t = {ts_s[i]}")
        ...

        >>> _ = ax[1, 0].set_ylabel("dim1 direction")
        >>> _ = ax[1, 0].set_xlabel("dim2 direction")

    Parameters
    ----------

    Returns
    -------
    img
        First return, a :obj:`~spl.cube.DataCube` with subset overhead imagery.

    scans
        Second return, a :obj:`~spl.cube.DataCube` with topographic scan data.

    """
    savi2020_img_path, savi2020_scan_path = _get_savi2020_path()
    return DataCube(savi2020_img_path), DataCube(savi2020_scan_path)
