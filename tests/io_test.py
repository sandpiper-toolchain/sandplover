import sys

import netCDF4
import numpy as np
import pytest
import xarray as xr

from sandplover.io import DictionaryIO
from sandplover.io import NetCDFIO
from sandplover.sample_data.sample_data import _get_golf_path
from sandplover.sample_data.sample_data import _get_landsat_path
from sandplover.sample_data.sample_data import _get_rcm8_path

rcm8_path = _get_rcm8_path()
golf_path = _get_golf_path()
hdf_path = _get_landsat_path()


@pytest.fixture
def empty_netcdf_file(tmp_path):
    """Create blank NetCDF4 file."""
    p = tmp_path / "dummy.nc"
    f = netCDF4.Dataset(p, "w", format="NETCDF4")
    f.createVariable("test", "f4")
    f.close()
    return p


@pytest.fixture
def empty_txt_file(tmp_path):
    """Create a dummy text file."""
    p = tmp_path / "dummy.txt"
    p.touch()
    return p


def test_netcdf_io_init():
    netcdf_io = NetCDFIO(golf_path, "netcdf")
    assert netcdf_io.io_type == "netcdf"
    assert len(netcdf_io._in_memory_data) == 0


def test_netcdf_io_init_legacy():
    # should raise two warnings
    with pytest.warns(UserWarning, match=r"Coordinates for .*"):
        netcdf_io = NetCDFIO(rcm8_path, "netcdf")
    with pytest.warns(UserWarning, match=r"No associated .*"):
        netcdf_io = NetCDFIO(rcm8_path, "netcdf")
    assert netcdf_io.io_type == "netcdf"
    assert len(netcdf_io._in_memory_data) == 0


def test_netcdf_io_keys():
    netcdf_io = NetCDFIO(golf_path, "netcdf")
    assert len(netcdf_io.keys) > 3


def test_netcdf_io_nomemory():
    netcdf_io = NetCDFIO(golf_path, "netcdf")
    dataset_size = sys.getsizeof(netcdf_io.dataset)
    inmemory_size = sys.getsizeof(netcdf_io._in_memory_data)

    var = "velocity"
    # slice the dataset directly
    velocity_arr = netcdf_io.dataset[var].data[:, 10, :]
    assert len(velocity_arr.shape) == 2
    assert type(velocity_arr) is np.ndarray

    dataset_size_after = sys.getsizeof(netcdf_io.dataset)
    inmemory_size_after = sys.getsizeof(netcdf_io._in_memory_data)

    assert dataset_size == dataset_size_after
    assert inmemory_size == inmemory_size_after


@pytest.mark.xfail()
def test_netcdf_io_intomemory_direct():
    netcdf_io = NetCDFIO(golf_path, "netcdf")
    dataset_size = sys.getsizeof(netcdf_io.dataset)
    inmemory_size = sys.getsizeof(netcdf_io._in_memory_data)

    var = "velocity"
    assert len(netcdf_io._in_memory_data) == 0
    netcdf_io._in_memory_data[var] = np.array(netcdf_io.dataset.variables[var])
    assert len(netcdf_io._in_memory_data) == 1
    _arr = netcdf_io._in_memory_data[var]

    dataset_size_after = sys.getsizeof(netcdf_io.dataset)
    inmemory_size_after = sys.getsizeof(netcdf_io._in_memory_data)

    assert dataset_size == dataset_size_after
    assert inmemory_size < inmemory_size_after
    assert sys.getsizeof(_arr) > 1000


@pytest.mark.xfail()
def test_netcdf_io_intomemory_read():
    netcdf_io = NetCDFIO(golf_path, "netcdf")
    dataset_size = sys.getsizeof(netcdf_io.dataset)
    inmemory_size = sys.getsizeof(netcdf_io._in_memory_data)

    var = "velocity"
    assert len(netcdf_io._in_memory_data) == 0
    netcdf_io.read(var)
    assert len(netcdf_io._in_memory_data) == 1
    _arr = netcdf_io._in_memory_data[var]

    assert isinstance(_arr, xr.core.dataarray.DataArray)

    dataset_size_after = sys.getsizeof(netcdf_io.dataset)
    inmemory_size_after = sys.getsizeof(netcdf_io._in_memory_data)

    assert dataset_size == dataset_size_after
    assert inmemory_size < inmemory_size_after


def test_hdf5_io_init():
    with pytest.warns(UserWarning, match=r"No associated .*"):
        netcdf_io = NetCDFIO(hdf_path, "hdf5")
    assert netcdf_io.io_type == "hdf5"
    assert len(netcdf_io._in_memory_data) == 0


def test_hdf5_io_keys():
    with pytest.warns(UserWarning, match=r"No associated .*"):
        hdf5_io = NetCDFIO(hdf_path, "hdf5")
    assert len(hdf5_io.keys) == 7


def test_nofile():
    with pytest.raises(FileNotFoundError):
        NetCDFIO("badpath", "netcdf")


def test_empty_file(empty_netcdf_file):
    assert empty_netcdf_file.is_file()
    with pytest.raises(NotImplementedError):
        NetCDFIO(empty_netcdf_file, "netcdf")


def test_invalid_file(empty_txt_file):
    assert empty_txt_file.is_file()
    with pytest.raises(TypeError):
        NetCDFIO(empty_txt_file, "netcdf")


def test_readvar_intomemory():
    netcdf_io = NetCDFIO(golf_path, "netcdf")
    assert netcdf_io._in_memory_data == {}

    netcdf_io.read("eta")
    assert ("eta" in netcdf_io._in_memory_data) is True


def test_readvar_intomemory_error():
    netcdf_io = NetCDFIO(golf_path, "netcdf")
    assert netcdf_io._in_memory_data == {}

    with pytest.raises(KeyError):
        netcdf_io.read("nonexistant")


def test_netcdf_no_metadata():
    # works fine, because there is no `connect` call in io init
    netcdf_io = NetCDFIO(golf_path, "netcdf")
    assert len(netcdf_io._in_memory_data) == 0


class TestDictionaryIO:

    _shape = (50, 100, 200)
    dict_xr = {"eta": xr.DataArray(np.random.normal(size=_shape))}
    dict_np = {
        "eta": np.random.normal(size=_shape),
        "velocity": np.random.normal(size=_shape),
    }

    def test_create_from_xarray_data(self):
        dict_io = DictionaryIO(self.dict_xr)
        assert ("eta" in dict_io._in_memory_data) is True
        assert isinstance(dict_io["eta"], xr.core.dataarray.DataArray)

    def test_dimensions_ignored_if_xarray(self):
        dict_io = DictionaryIO(self.dict_xr, dimensions=(3, 4, 5))
        assert ("eta" in dict_io._in_memory_data) is True
        assert isinstance(dict_io["eta"], xr.core.dataarray.DataArray)

    def test_create_from_numpy_data_nodims(self):
        dict_io = DictionaryIO(self.dict_np)
        assert ("eta" in dict_io._in_memory_data) is True
        assert ("velocity" in dict_io._in_memory_data) is True
        assert isinstance(dict_io["eta"], np.ndarray)
        assert isinstance(dict_io["dim0"], np.ndarray)

    def test_create_from_numpy_data_dimensions(self):
        dict_io = DictionaryIO(
            self.dict_np,
            dimensions={
                "time": np.arange(self._shape[0]),
                "x": np.arange(self._shape[1]),
                "y": np.arange(self._shape[2]),
            },
        )
        assert ("eta" in dict_io._in_memory_data) is True
        assert ("velocity" in dict_io._in_memory_data) is True
        assert isinstance(dict_io["eta"], np.ndarray)
        assert isinstance(dict_io["time"], np.ndarray)
        assert isinstance(dict_io["x"], np.ndarray)
        assert isinstance(dict_io["y"], np.ndarray)
        assert np.all(dict_io["eta"] == self.dict_np["eta"])

    def test_bad_dimensions_types(self):
        with pytest.raises(TypeError, match=r".* type for `dimensions` .*"):
            _ = DictionaryIO(self.dict_np, dimensions=(3, 4, 5))
        with pytest.raises(TypeError, match=r".* type for `dimensions` .*"):
            _ = DictionaryIO(self.dict_np, dimensions=1)
        with pytest.raises(TypeError, match=r".* type for `dimensions` .*"):
            _ = DictionaryIO(self.dict_np, dimensions="string")
        with pytest.raises(TypeError, match=r".* type for `dimensions` .*"):
            _ = DictionaryIO(self.dict_np, dimensions=["list", "string"])

    def test_bad_dimensions_length(self):
        with pytest.raises(ValueError, match=r"`dimensions` must .*"):
            _ = DictionaryIO(self.dict_np, dimensions={})

    def test_bad_dimensions_shape_mismatch(self):
        with pytest.raises(ValueError, match=r"Shape of `dimensions` .*"):
            # note dim2 and dim1 are switchd below!
            DictionaryIO(
                self.dict_np,
                dimensions={
                    "time": np.arange(self._shape[0]),
                    "x": np.arange(self._shape[2]),
                    "y": np.arange(self._shape[1]),
                },
            )

    def test_not_implemented_methods(self):
        dict_io = DictionaryIO(self.dict_xr)
        with pytest.raises(NotImplementedError):
            dict_io.connect()
        with pytest.raises(NotImplementedError):
            dict_io.read()
        with pytest.raises(NotImplementedError):
            dict_io.write()
