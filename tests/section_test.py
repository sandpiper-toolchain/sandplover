import matplotlib.pyplot as plt
import numpy as np
import pytest
import xarray as xr

from sandplover.cube import DataCube
from sandplover.cube import StratigraphyCube
from sandplover.mask import ElevationMask
from sandplover.plan import Planform
from sandplover.sample_data.sample_data import _get_golf_path
from sandplover.sample_data.sample_data import _get_rcm8_path
from sandplover.section import CircularSection
from sandplover.section import DipSection
from sandplover.section import PathSection
from sandplover.section import RadialSection
from sandplover.section import StrikeSection
from sandplover.utils import NoStratigraphyError

rcm8_path = _get_rcm8_path()
golf_path = _get_golf_path()


# Test the basics of each different section type


class TestStrikeSection:
    """Test the basic of the StrikeSection."""

    def test_StrikeSection_without_cube(self):
        ss = StrikeSection(distance_idx=5)
        assert ss.name is None
        assert ss._distance_idx is None
        assert ss._input_distance_idx == 5
        assert ss.shape is None
        assert ss._underlying is None
        assert ss._underlying_type is None
        assert ss.s is None
        assert np.all(ss.trace == np.array([[None, None]]))
        assert ss._dim1_idx is None
        assert ss._dim2_idx is None
        assert ss.variables is None
        with pytest.raises(AttributeError, match=r"No underlying data.*."):
            ss["velocity"]

    def test_StrikeSection_bad_cube(self):
        badcube = ["some", "list"]
        with pytest.raises(TypeError, match=r"Expected type is *."):
            _ = StrikeSection(badcube, distance_idx=12)
        with pytest.raises(TypeError, match=r"Expected type is *."):
            _ = StrikeSection(badcube, distance=1000)

    def test_StrikeSection_standalone_instantiation(self):
        rcm8cube = DataCube(golf_path)
        sass = StrikeSection(rcm8cube, distance_idx=12)
        assert sass.name == "strike"
        assert sass.distance_idx == 12
        assert sass._underlying == rcm8cube
        assert sass.trace.shape == (rcm8cube.shape[2], 2)
        assert len(sass.variables) > 0

    def test_StrikeSection_register_section_distance_idx(self):
        rcm8cube = DataCube(golf_path)
        rcm8cube.register_section("test", StrikeSection(distance_idx=5))
        assert rcm8cube.sections["test"].name == "test"
        assert rcm8cube.sections["test"]._input_distance is None
        assert rcm8cube.sections["test"]._input_distance_idx == 5
        assert rcm8cube.sections["test"]._input_length is None
        assert rcm8cube.sections["test"]._distance_idx == 5
        assert rcm8cube.sections["test"]._start_end == (0, rcm8cube.shape[2] - 1)
        assert (
            rcm8cube.sections["test"].length
            == rcm8cube.dim2_coords[-1] + rcm8cube.dim2_coords[1]
        )
        assert rcm8cube.sections["test"].distance == rcm8cube.dim1_coords[5]
        assert len(rcm8cube.sections["test"].variables) > 0
        assert rcm8cube.sections["test"]._underlying is rcm8cube
        with pytest.warns(UserWarning, match=r"`.x` is a deprecated .*"):
            assert rcm8cube.sections["test"].x == rcm8cube.W
        with pytest.warns(UserWarning, match=r"`.y` is a deprecated .*"):
            assert rcm8cube.sections["test"].y == 5
        # test that the name warning is raised
        with pytest.warns(UserWarning, match=r"`name` argument supplied .*"):
            rcm8cube.register_section(
                "testname", StrikeSection(distance_idx=5, name="TESTING")
            )
        assert rcm8cube.sections["testname"].name == "TESTING"
        _sect = rcm8cube.register_section(
            "test", StrikeSection(distance_idx=5), return_section=True
        )
        assert isinstance(_sect, StrikeSection)

    def test_StrikeSection_register_section_distance(self):
        rcm8cube = DataCube(golf_path)
        rcm8cube.register_section("test", StrikeSection(distance=2000))
        assert rcm8cube.sections["test"].name == "test"
        assert rcm8cube.sections["test"]._input_distance == 2000
        assert rcm8cube.sections["test"]._input_distance_idx is None
        assert rcm8cube.sections["test"]._input_length is None
        assert rcm8cube.sections["test"]._distance_idx > 0
        assert rcm8cube.sections["test"].length == rcm8cube.dim2_coords[-1]
        assert rcm8cube.sections["test"].distance == 2000
        assert len(rcm8cube.sections["test"].variables) > 0
        assert rcm8cube.sections["test"]._underlying is rcm8cube
        rcm8cube.register_section(
            "lengthtest", StrikeSection(distance=2000, length=(2000, 5000))
        )
        assert rcm8cube.sections["lengthtest"].name == "lengthtest"
        assert rcm8cube.sections["lengthtest"]._input_distance == 2000
        assert rcm8cube.sections["lengthtest"]._input_distance_idx is None
        assert rcm8cube.sections["lengthtest"]._input_length == (2000, 5000)
        assert rcm8cube.sections["lengthtest"]._distance_idx > 0
        assert rcm8cube.sections["lengthtest"]._start_end == (2000, 5000)
        assert rcm8cube.sections["lengthtest"].length == 3000
        assert rcm8cube.sections["lengthtest"].distance == 2000

    def test_StrikeSection_register_section_either_distance_distance_idx(self):
        rcm8cube = DataCube(golf_path)
        with pytest.raises(ValueError, match=r"Must specify `distance` or .*"):
            rcm8cube.register_section("test", StrikeSection())

    def test_StrikeSection_register_section_notboth_distance_distance_idx(self):
        rcm8cube = DataCube(golf_path)
        with pytest.raises(
            ValueError, match=r"Cannot specify both `distance` .*"
        ):  # noqa: E501
            rcm8cube.register_section(
                "test", StrikeSection(distance=2000, distance_idx=2)
            )

    def test_StrikeSection_register_section_deprecated(self):
        rcm8cube = DataCube(golf_path)
        with pytest.warns(UserWarning, match=r"Arguments `y` and `x` are .*"):
            rcm8cube.register_section("warn", StrikeSection(y=5))
        # the section should still work though, so check on the attrs
        assert rcm8cube.sections["warn"].name == "warn"
        assert rcm8cube.sections["warn"]._input_distance is None
        assert rcm8cube.sections["warn"]._input_distance_idx == 5
        assert rcm8cube.sections["warn"]._input_length is None
        assert rcm8cube.sections["warn"]._distance_idx == 5
        assert rcm8cube.sections["warn"]._start_end == (0, rcm8cube.shape[2] - 1)
        assert rcm8cube.sections["warn"].distance == rcm8cube.dim1_coords[5]
        assert len(rcm8cube.sections["warn"].variables) > 0
        assert rcm8cube.sections["warn"]._underlying is rcm8cube
        # test for the error with spec deprecated and new
        with pytest.raises(
            ValueError, match=r"Cannot specify `distance`, .*"
        ):  # noqa: E501
            rcm8cube.register_section(
                "fail", StrikeSection(y=2, distance=2000, distance_idx=2)
            )

    def test_StrikeSection_register_section_x_limits(self):
        rcm8cube = DataCube(golf_path)
        rcm8cube.register_section(
            "tuple", StrikeSection(distance_idx=5, length=(10, 110))
        )
        rcm8cube.register_section(
            "list", StrikeSection(distance_idx=5, length=[20, 110])
        )
        assert len(rcm8cube.sections) == 2
        assert rcm8cube.sections["tuple"]._dim2_idx.shape[0] == 101
        assert rcm8cube.sections["list"]._dim2_idx.shape[0] == 91
        assert np.all(rcm8cube.sections["list"]._dim1_idx == 5)
        assert np.all(rcm8cube.sections["tuple"]._dim1_idx == 5)


class TestPathSection:
    """Test the basic of the PathSection."""

    test_path = np.column_stack(
        (np.arange(5, 65, 20), np.arange(60, 120, 20))  # dim1 column
    )  # dim2 column
    test_path2 = np.array([[1000, 3000], [2000, 6500], [1000, 5500], [3000, 8000]])

    def test_without_cube(self):
        ps = PathSection(path_idx=self.test_path)
        assert ps.name is None
        assert ps.path is None
        assert ps.shape is None
        assert ps._underlying is None
        assert ps._underlying_type is None
        assert ps.s is None
        assert np.all(ps.trace == np.array([[None, None]]))
        assert ps._dim1_idx is None
        assert ps._dim2_idx is None
        assert ps.variables is None
        with pytest.raises(AttributeError, match=r"No underlying data connected.*."):
            ps["velocity"]
        ps2 = PathSection(path=self.test_path2)
        assert ps2.name is None
        assert ps2.path is None
        assert ps2.shape is None
        assert ps2._underlying is None
        assert ps2._underlying_type is None
        assert ps2.s is None
        assert np.all(ps2.trace == np.array([[None, None]]))
        assert ps2._dim1_idx is None
        assert ps2._dim2_idx is None
        assert ps2.variables is None

    def test_bad_cube(self):
        badcube = ["some", "list"]
        with pytest.raises(TypeError, match=r"Expected type is *."):
            _ = PathSection(badcube, path_idx=self.test_path)

    def test_standalone_instantiation(self):
        rcm8cube = DataCube(golf_path)
        saps = PathSection(rcm8cube, path_idx=self.test_path)
        assert saps.name == "path"
        assert saps._underlying == rcm8cube
        assert saps.trace.shape[0] > 20
        assert saps.trace.shape[1] == 2
        assert len(saps.variables) > 0
        saps2 = PathSection(rcm8cube, path=self.test_path2)
        assert saps2.name == "path"
        assert saps2._underlying == rcm8cube
        assert saps2.trace.shape[0] > 20
        assert saps2.trace.shape[1] == 2
        assert len(saps2.variables) > 0
        with pytest.raises(ValueError, match=r"Cannot specify .*"):
            _ = PathSection(  # both arguments
                rcm8cube, path_idx=self.test_path, path=self.test_path
            )
        with pytest.raises(ValueError, match=r"Must specify .*"):
            _ = PathSection(rcm8cube)  # no arguments

    def test_register_section(self):
        rcm8cube = DataCube(golf_path)
        rcm8cube.stratigraphy_from("eta")
        rcm8cube.register_section("test", PathSection(path_idx=self.test_path))
        assert rcm8cube.sections["test"].name == "test"
        assert len(rcm8cube.sections["test"].variables) > 0
        assert isinstance(rcm8cube.sections["test"], PathSection)
        assert rcm8cube.sections["test"].shape[0] > 20
        # test that the name warning is raised
        with pytest.warns(UserWarning, match=r"`name` argument supplied .*"):
            rcm8cube.register_section(
                "test2", PathSection(path_idx=self.test_path, name="trial")
            )
        assert rcm8cube.sections["test2"].name == "trial"
        _section = rcm8cube.register_section(
            "test", PathSection(path_idx=self.test_path), return_section=True
        )
        assert isinstance(_section, PathSection)

    def test_return_path(self):
        # test that returned path and trace are the same
        rcm8cube = DataCube(golf_path)
        saps = PathSection(rcm8cube, path_idx=self.test_path)
        _t = saps.trace
        _p = saps.path
        assert np.all(_t == _p)

    def test_path_reduced_unique(self):
        # test a first case with a straight line
        rcm8cube = DataCube(golf_path)
        xy = np.column_stack(
            (
                np.linspace(10, 90, num=4000, dtype=int),
                np.linspace(50, 150, num=4000, dtype=int),
            )
        )
        saps1 = PathSection(rcm8cube, path_idx=xy)
        assert saps1.path.shape != xy.shape
        assert np.all(saps1.trace_idx == np.unique(xy, axis=0))

        # test a second case with small line to ensure non-unique removed
        saps2 = PathSection(
            rcm8cube, path_idx=np.array([[50, 25], [50, 26], [50, 26], [50, 27]])
        )
        assert saps2.path.shape == (3, 2)


class TestCircularSection:
    """Test the basic of the CircularSection."""

    def test_without_cube(self):
        cs = CircularSection(radius_idx=30)
        assert cs.name is None
        assert cs.shape is None
        assert cs._underlying is None
        assert cs._underlying_type is None
        assert cs.s is None
        assert np.all(cs.trace == np.array([[None, None]]))
        assert cs._dim1_idx is None
        assert cs._dim2_idx is None
        assert cs.variables is None
        assert cs.radius is None
        assert cs.origin is None
        with pytest.raises(AttributeError, match=r"No underlying data connected.*."):
            cs["velocity"]

    def test_bad_cube(self):
        badcube = ["some", "list"]
        with pytest.raises(TypeError, match=r"Expected type is *."):
            _ = CircularSection(badcube, radius_idx=30)

    def test_standalone_instantiation(self):
        golfcube = DataCube(golf_path)
        sacs = CircularSection(golfcube, radius_idx=30)
        assert sacs.name == "circular"
        assert sacs._underlying == golfcube
        assert sacs.trace.shape[0] == 85
        assert sacs._input_radius_idx == 30
        assert len(sacs.variables) > 0
        assert sacs._origin_idx[0] == golfcube.meta["L0"]
        assert sacs.radius == 1500

        sacs2 = CircularSection(golfcube, radius_idx=30, origin_idx=(0, 10))
        assert sacs2.name == "circular"
        assert sacs2._underlying == golfcube
        assert sacs2.trace.shape[0] == 53
        assert len(sacs2.variables) > 0
        assert sacs2._origin_idx == (0, 10)

        sacs3 = CircularSection(golfcube, radius=2500)
        assert sacs3.name == "circular"
        assert sacs3._underlying == golfcube
        assert sacs3.trace.shape[0] == 143
        assert len(sacs3.variables) > 0
        assert sacs3._origin_idx == (int(golfcube.meta["L0"]), golfcube.shape[2] // 2)
        assert sacs3._radius_idx == 50
        assert sacs3.radius == 2500
        assert sacs3.radius == sacs3._radius

        sacs4 = CircularSection(golfcube, origin=(1200, 1500))
        assert sacs4.name == "circular"
        assert sacs4._underlying == golfcube
        assert sacs4.trace.shape[0] == 102
        assert len(sacs4.variables) > 0
        assert sacs4._origin_idx == (1200 // 50, 1500 // 50)  # 50 is dx
        assert sacs4._radius_idx == 50
        assert sacs4.radius == 2500
        assert sacs4.radius == sacs4._radius

    def test_standalone_instantiation_legacy_nometa(self):
        with pytest.warns(UserWarning, match=r'Coordinates for "time".*'):
            rcm8cube = DataCube(rcm8_path)
        # test that it guesses the origin
        with pytest.warns(UserWarning, match=r"Trying to guess.*"):
            sacs = CircularSection(rcm8cube, radius_idx=30)
        assert sacs.name == "circular"
        assert sacs._underlying == rcm8cube
        assert sacs.trace.shape[0] == 85
        assert len(sacs.variables) > 0
        # test that it uses the origin
        sacs2 = CircularSection(rcm8cube, radius_idx=30, origin_idx=(0, 10))
        assert sacs2.name == "circular"
        assert sacs2._underlying == rcm8cube
        assert sacs2.trace.shape[0] == 53
        assert len(sacs2.variables) > 0
        assert sacs2._origin_idx == (0, 10)

    def test_standalone_instantiation_both_coord_idx_inputs(self):
        golfcube = DataCube(golf_path)
        with pytest.raises(ValueError, match=r".*`radius` and `radius_idx`"):
            _ = CircularSection(golfcube, radius=2500, radius_idx=30)
        with pytest.raises(ValueError, match=r".*`origin` and `origin_idx`"):
            _ = CircularSection(golfcube, origin=(2500, 1500), origin_idx=(3, 100))

    def test_register_section(self):
        rcm8cube = DataCube(golf_path)
        rcm8cube.stratigraphy_from("eta")
        rcm8cube.register_section("test", CircularSection(radius_idx=30))
        assert len(rcm8cube.sections["test"].variables) > 0
        # test that the name warning is raised
        assert isinstance(rcm8cube.sections["test"], CircularSection)
        with pytest.warns(UserWarning):
            rcm8cube.register_section(
                "test2", CircularSection(radius_idx=31, name="diff")
            )
        assert rcm8cube.sections["test2"].name == "diff"
        rcm8cube.register_section("test3", CircularSection())
        assert rcm8cube.sections["test3"]._radius_idx == rcm8cube.shape[1] // 2
        _section = rcm8cube.register_section(
            "test3", CircularSection(), return_section=True
        )
        assert isinstance(_section, CircularSection)

    def test_all_idx_reduced_unique(self):
        # we try this for a bunch of different radii
        rcm8cube = DataCube(golf_path)
        sacs1 = CircularSection(rcm8cube, radius_idx=40)
        assert len(sacs1.trace_idx) == len(np.unique(sacs1.trace_idx, axis=0))
        sacs2 = CircularSection(rcm8cube, radius_idx=23)
        assert len(sacs2.trace_idx) == len(np.unique(sacs2.trace_idx, axis=0))
        sacs3 = CircularSection(rcm8cube, radius_idx=17)
        assert len(sacs3.trace_idx) == len(np.unique(sacs3.trace_idx, axis=0))
        sacs4 = CircularSection(rcm8cube, radius_idx=33)
        assert len(sacs4.trace_idx) == len(np.unique(sacs4.trace_idx, axis=0))


class TestRadialSection:
    """Test the basic of the RadialSection."""

    def test_without_cube(self):
        rs = RadialSection()
        assert rs.name is None
        assert rs.shape is None
        assert rs._underlying is None
        assert rs._underlying_type is None
        assert rs.s is None
        assert np.all(rs.trace == np.array([[None, None]]))
        assert rs._dim1_idx is None
        assert rs._dim2_idx is None
        assert rs.variables is None
        with pytest.raises(AttributeError, match=r"No underlying data connected.*."):
            rs["velocity"]
        rs2 = RadialSection(azimuth=30)
        assert rs2.name is None
        assert rs2.shape is None
        assert rs2._underlying is None
        assert rs2._underlying_type is None
        assert rs2.s is None
        assert np.all(rs2.trace == np.array([[None, None]]))
        assert rs2._dim1_idx is None
        assert rs2._dim2_idx is None
        assert rs2.variables is None
        with pytest.raises(AttributeError, match=r"No underlying data connected.*."):
            rs2["velocity"]

    def test_bad_cube(self):
        badcube = ["some", "list"]
        with pytest.raises(TypeError, match=r"Expected type is *."):
            _ = RadialSection(badcube, azimuth=30)

    def test_standalone_instantiation(self):
        rcm8cube = DataCube(golf_path)
        sars = RadialSection(rcm8cube)
        assert sars.name == "radial"
        assert sars._underlying == rcm8cube
        assert (
            sars.trace.shape[0] == rcm8cube.shape[1] - rcm8cube.meta["L0"]
        )  # 120 - L0 = 120 - 3
        assert len(sars.variables) > 0
        assert sars.azimuth == 90
        sars1 = RadialSection(rcm8cube, azimuth=30)
        assert sars1.name == "radial"
        assert sars1._underlying == rcm8cube
        assert sars1.trace.shape[0] == rcm8cube.shape[1]
        assert len(sars1.variables) > 0
        assert sars1.azimuth == 30
        sars2_starty = 2
        sars2 = RadialSection(rcm8cube, azimuth=103, origin_idx=(sars2_starty, 90))
        assert sars2.name == "radial"
        assert sars2._underlying == rcm8cube
        assert sars2.trace.shape[0] == rcm8cube.shape[1] - sars2_starty
        assert len(sars2.variables) > 0
        assert sars2.azimuth == 103
        assert sars2._origin_idx == (2, 90)
        sars3 = RadialSection(
            rcm8cube, azimuth=178, origin_idx=(18, 143), length=30, name="diff"
        )
        assert sars3.name == "diff"
        assert sars3._underlying == rcm8cube
        assert sars3.trace.shape[0] == 31
        assert len(sars3.variables) > 0
        assert sars3.azimuth == 178
        assert sars3._origin_idx == (18, 143)
        sars4 = RadialSection(rcm8cube, azimuth=90, origin=(200, 5000), length=2000)
        assert sars4._underlying == rcm8cube
        assert sars4.trace.shape[0] == 41  # 2000 // 50 = L // dx == 40
        assert sars4.azimuth == 90
        assert sars4._origin_idx == (4, rcm8cube.W // 2)  # 5000 is center domain
        with pytest.raises(ValueError, match=r"Cannot specify .*"):
            _ = RadialSection(  # both arguments
                rcm8cube, origin=(200, 5000), origin_idx=(2, 90)
            )

    def test_standalone_instantiation_withmeta(self):
        golfcube = DataCube(golf_path)
        sars = RadialSection(golfcube)
        assert sars._origin_idx[0] == golfcube.meta["L0"]
        sars1 = RadialSection(golfcube, azimuth=30)
        assert sars1._origin_idx[0] == golfcube.meta["L0"]
        sars2 = RadialSection(golfcube, azimuth=103, origin_idx=(90, 2))
        assert sars2._origin_idx == (90, 2)
        sars3 = RadialSection(
            golfcube, azimuth=178, origin_idx=(18, 143), length=30, name="diff"
        )
        assert sars3.name == "diff"
        assert sars3._origin_idx == (18, 143)

    def test_register_section(self):
        rcm8cube = DataCube(golf_path)
        rcm8cube.register_section("test", RadialSection(azimuth=30))
        assert len(rcm8cube.sections["test"].variables) > 0
        assert isinstance(rcm8cube.sections["test"], RadialSection)
        # test that the name warning is raised
        with pytest.warns(UserWarning, match=r"`name` argument supplied .*"):
            rcm8cube.register_section(
                "test2", RadialSection(azimuth=30, name="notthesame")
            )
        assert rcm8cube.sections["test2"].name == "notthesame"
        _section = rcm8cube.register_section(
            "test", RadialSection(azimuth=30), return_section=True
        )
        assert isinstance(_section, RadialSection)
        # with pytest.raises(ValueError):
        _section2 = rcm8cube.register_section("test", RadialSection(azimuth=30))
        assert _section2 is None

    def test_autodetect_origin_0_aziumth(self):
        rcm8cube = DataCube(golf_path)
        rcm8cube.register_section("test", RadialSection(azimuth=0))
        _cshp, L0 = rcm8cube.shape, float(rcm8cube.meta["L0"])
        assert isinstance(rcm8cube.sections["test"], RadialSection)
        assert rcm8cube.sections["test"].trace.shape[0] == _cshp[2] // 2
        assert rcm8cube.sections["test"]._dim2_idx[-1] == _cshp[2] - 1
        assert rcm8cube.sections["test"]._dim1_idx[-1] == L0
        assert rcm8cube.sections["test"]["velocity"].shape == (_cshp[0], _cshp[1])

    def test_autodetect_origin_180_aziumth(self):
        rcm8cube = DataCube(golf_path)
        rcm8cube.register_section("test", RadialSection(azimuth=180))
        _cshp, L0 = (rcm8cube.shape, float(rcm8cube.meta["L0"]))
        assert isinstance(rcm8cube.sections["test"], RadialSection)
        assert (
            rcm8cube.sections["test"].trace.shape[0] == (_cshp[2] // 2) + 1
        )  # inclusive left
        assert rcm8cube.sections["test"]._dim2_idx[-1] == 0
        assert rcm8cube.sections["test"]._dim1_idx[-1] == L0
        assert rcm8cube.sections["test"]["velocity"].shape == (_cshp[0], _cshp[1] + 1)

    def test_autodetect_origin_90_aziumth(self):
        rcm8cube = DataCube(golf_path)
        rcm8cube.register_section("test", RadialSection(azimuth=90))
        _cshp, L0 = rcm8cube.shape, float(rcm8cube.meta["L0"])
        assert isinstance(rcm8cube.sections["test"], RadialSection)
        assert rcm8cube.sections["test"].trace.shape[0] == _cshp[1] - L0
        assert rcm8cube.sections["test"]._dim2_idx[-1] == _cshp[2] // 2
        assert rcm8cube.sections["test"]._dim1_idx[-1] == _cshp[1] - 1
        assert rcm8cube.sections["test"]["velocity"].shape == (_cshp[0], _cshp[1] - L0)

    @pytest.mark.xfail(
        raises=AssertionError,
        strict=False,
        reason=(
            "Length mismatch for Ubuntu with python 3.8 and 3.10, "
            "but passing on other OS."
        ),
    )
    def test_autodetect_origin_45_aziumth(self):
        rcm8cube = DataCube(golf_path)
        rcm8cube.register_section("test2", RadialSection(azimuth=45))
        _cshp, L0 = rcm8cube.shape, float(rcm8cube.meta["L0"])

        assert isinstance(rcm8cube.sections["test2"], RadialSection)
        assert rcm8cube.sections["test2"].trace.shape[0] == _cshp[1] - L0
        assert rcm8cube.sections["test2"]._dim2_idx[-1] == _cshp[2] - 1 - L0
        assert rcm8cube.sections["test2"]._dim1_idx[-1] == _cshp[1] - 1
        assert rcm8cube.sections["test2"]["velocity"].shape == (_cshp[0], _cshp[1] - L0)

    def test_autodetect_origin_85_aziumth(self):
        rcm8cube = DataCube(golf_path)
        rcm8cube.register_section("test3", RadialSection(azimuth=85))
        _cshp, _ = rcm8cube.shape, float(rcm8cube.meta["L0"])
        assert isinstance(rcm8cube.sections["test3"], RadialSection)
        assert rcm8cube.sections["test3"].trace.shape[0] < _cshp[1]  # slight oblique
        assert (
            rcm8cube.sections["test3"]._dim2_idx[-1] > _cshp[2] // 2
        )  # slight oblique
        assert (
            rcm8cube.sections["test3"]._dim1_idx[-1] == _cshp[1] - 1
        )  # slight oblique
        assert rcm8cube.sections["test3"]["velocity"].shape[0] == _cshp[0]

    def test_autodetect_origin_115_aziumth(self):
        rcm8cube = DataCube(golf_path)
        rcm8cube.register_section("test4", RadialSection(azimuth=115))
        _cshp, _ = rcm8cube.shape, float(rcm8cube.meta["L0"])
        assert isinstance(rcm8cube.sections["test4"], RadialSection)
        assert rcm8cube.sections["test4"].trace.shape[0] < _cshp[1]  # slight oblique
        assert (
            rcm8cube.sections["test4"]._dim2_idx[-1] < _cshp[2] // 2
        )  # slight oblique
        assert (
            rcm8cube.sections["test4"]._dim1_idx[-1] == _cshp[1] - 1
        )  # slight oblique
        assert rcm8cube.sections["test4"]["velocity"].shape[0] == _cshp[0]

    def test_autodetect_origin_165_aziumth(self):
        rcm8cube = DataCube(golf_path)
        rcm8cube.register_section("test5", RadialSection(azimuth=165))
        _cshp, _ = rcm8cube.shape, float(rcm8cube.meta["L0"])
        assert isinstance(rcm8cube.sections["test5"], RadialSection)
        assert rcm8cube.sections["test5"].trace.shape[0] > _cshp[1]  # obtuse
        assert rcm8cube.sections["test5"]._dim2_idx[-1] == 0
        assert rcm8cube.sections["test5"]._dim2_idx[0] == _cshp[2] // 2
        assert rcm8cube.sections["test5"]._dim1_idx[-1] < _cshp[1] // 2  # acute
        assert rcm8cube.sections["test5"]["velocity"].shape[0] == _cshp[0]

    def test_autodetect_origin_OOB_aziumth(self):
        rcm8cube = DataCube(golf_path)
        with pytest.raises(ValueError, match=r"Azimuth must be *."):
            rcm8cube.register_section("testfail", RadialSection(azimuth=-10))
        with pytest.raises(ValueError, match=r"Azimuth must be *."):
            rcm8cube.register_section("testfail", RadialSection(azimuth=190))

    def test_specify_origin_and_azimuth(self):
        rcm8cube = DataCube(golf_path)
        rcm8cube.register_section(
            "test", RadialSection(azimuth=145, origin_idx=(3, 20))
        )
        assert isinstance(rcm8cube.sections["test"], RadialSection)
        assert rcm8cube.sections["test"].trace.shape[0] == 21
        assert rcm8cube.sections["test"]._dim2_idx[-1] == 0
        assert rcm8cube.sections["test"]._dim2_idx[0] == 20
        assert rcm8cube.sections["test"]._dim1_idx[0] == 3
        assert rcm8cube.sections["test"]._dim1_idx[-1] > 3


class TestCubesWithManySections:

    rcm8cube = DataCube(golf_path)
    sc8cube = StratigraphyCube.from_DataCube(rcm8cube, dz=0.1)
    #                     [dim1, dim2]
    test_path = np.array([[60, 120], [30, 40]])

    def test_data_equivalence(self):
        assert self.rcm8cube.dataio is self.sc8cube.dataio
        assert np.all(self.rcm8cube.dataio["time"] == self.sc8cube.dataio["time"])
        assert np.all(
            self.rcm8cube.dataio["velocity"] == self.sc8cube.dataio["velocity"]
        )

    def test_register_multiple_strikes(self):
        self.rcm8cube.register_section("test1", StrikeSection(distance_idx=5))
        self.rcm8cube.register_section("test2", StrikeSection(distance_idx=5))
        self.rcm8cube.register_section("test3", StrikeSection(distance_idx=8))
        self.rcm8cube.register_section("test4", StrikeSection(distance_idx=10))
        assert not self.rcm8cube.sections["test1"] is self.rcm8cube.sections["test2"]
        assert np.all(
            self.rcm8cube.sections["test1"]["velocity"]
            == self.rcm8cube.sections["test2"]["velocity"]
        )
        assert not self.rcm8cube.sections["test1"] is self.rcm8cube.sections["test3"]
        assert not self.rcm8cube.sections["test1"] is self.rcm8cube.sections["test4"]
        assert not np.all(
            self.rcm8cube.sections["test1"]["velocity"]
            == self.rcm8cube.sections["test3"]["velocity"]
        )

    def test_register_strike_and_path(self):
        self.rcm8cube.register_section("test1", StrikeSection(distance_idx=5))
        self.rcm8cube.register_section("test1a", StrikeSection(distance_idx=5))
        self.rcm8cube.register_section("test2", PathSection(path=self.test_path))
        assert not self.rcm8cube.sections["test1"] is self.rcm8cube.sections["test2"]
        assert (
            self.rcm8cube.sections["test1"].trace.shape
            == self.rcm8cube.sections["test1a"].trace.shape
        )
        # create alias and verify differences
        t1, t2 = self.rcm8cube.sections["test1"], self.rcm8cube.sections["test2"]
        assert not (t1 is t2)

    def test_show_trace_sections_multiple(self):
        self.rcm8cube.register_section("show_test1", StrikeSection(distance_idx=5))
        self.rcm8cube.register_section("show_test2", StrikeSection(distance_idx=50))
        fig, ax = plt.subplots(1, 2)
        self.rcm8cube.sections["show_test2"].show_trace("r--")
        self.rcm8cube.sections["show_test1"].show_trace("g--", ax=ax[0])
        plt.close()


# test the core functionality common to all section types, for different
# Cubes and strat
class TestSectionFromDataCubeNoStratigraphy:

    rcm8cube_nostrat = DataCube(golf_path)
    rcm8cube_nostrat.register_section("test", StrikeSection(distance_idx=5))

    def test_nostrat_getitem_explicit(self):
        s = self.rcm8cube_nostrat.sections["test"].__getitem__("velocity")
        assert isinstance(s, xr.core.dataarray.DataArray)

    def test_nostrat_getitem_implicit(self):
        s = self.rcm8cube_nostrat.sections["test"]["velocity"]
        assert isinstance(s, xr.core.dataarray.DataArray)

    def test_nostrat_getitem_bad_variable(self):
        with pytest.raises(AttributeError):
            self.rcm8cube_nostrat.sections["test"]["badvariablename"]

    def test_nostrat_getitem_broken_cube(self):
        sass = StrikeSection(distance_idx=5)
        with pytest.raises(AttributeError, match=r"No underlying data connected.*."):
            sass["velocity"]
        # make a good section, then switch to invalidcube inside section
        temp_rcm8cube_nostrat = DataCube(golf_path)
        temp_rcm8cube_nostrat.register_section("test", StrikeSection(distance_idx=5))
        temp_rcm8cube_nostrat.sections["test"]._underlying = "badvalue!"
        with pytest.raises(TypeError):
            _ = temp_rcm8cube_nostrat.sections["test"].__getitem__("velocity")
        with pytest.raises(TypeError):
            temp_rcm8cube_nostrat.sections["test"]["velocity"]

    def test_nostrat_not_knows_stratigraphy(self):
        assert (
            self.rcm8cube_nostrat.sections["test"]["velocity"].strat._knows_stratigraphy
            is False
        )
        assert (
            self.rcm8cube_nostrat.sections["test"]["velocity"].strat.knows_stratigraphy
            is False
        )

    def test_nostrat_nostratigraphyinfo(self):
        with pytest.raises(NoStratigraphyError):
            _ = self.rcm8cube_nostrat.sections["test"][
                "velocity"
            ].strat.as_stratigraphy()
        with pytest.raises(NoStratigraphyError):
            _ = self.rcm8cube_nostrat.sections["test"]["velocity"].strat.as_preserved()

    def test_nostrat_SectionVariable_basic_math_comparisons(self):
        s1 = self.rcm8cube_nostrat.sections["test"]["velocity"]
        s2 = self.rcm8cube_nostrat.sections["test"]["depth"]
        s3 = np.absolute(self.rcm8cube_nostrat.sections["test"]["eta"])
        assert np.all(s1 + s1 == s1 * 2)
        assert not np.any((s2 - np.random.rand(*s2.shape)) == s2)
        assert np.all(s3 + s3 > s3)
        assert type(s3) is xr.core.dataarray.DataArray

    def test_nostrat_trace(self):
        assert isinstance(self.rcm8cube_nostrat.sections["test"].trace, np.ndarray)

    def test_nostrat_s(self):
        _s = self.rcm8cube_nostrat.sections["test"].s
        assert isinstance(_s, xr.core.dataarray.DataArray)
        assert np.all(_s.data[1:] > _s.data[:-1])  # monotonic increase

    def test_nostrat_z(self):
        _z = self.rcm8cube_nostrat.sections["test"].z
        assert isinstance(_z, xr.core.dataarray.DataArray)
        assert np.all(_z.data[1:] > _z.data[:-1])  # monotonic increase

    def test_nostrat_variables(self):
        _v = self.rcm8cube_nostrat.sections["test"].variables
        assert len(_v) > 0
        assert isinstance(_v, list)

    def test_nostrat_show_shaded_spacetime(self):
        self.rcm8cube_nostrat.sections["test"].show(
            "time", style="shaded", data="spacetime"
        )

    def test_nostrat_show_shaded_spacetime_specific_ax(self):
        fig, ax = plt.subplots()
        self.rcm8cube_nostrat.sections["test"].show(
            "time", style="shaded", data="spacetime", ax=ax
        )

    def test_nostrat_show_shaded_spacetime_no_cube(self):
        sass = StrikeSection(distance_idx=5)
        with pytest.raises(AttributeError, match=r"No underlying data connected.*."):
            sass.show("time", style="shaded", data="spacetime")

    def test_nostrat_show_shaded_aspreserved(self):
        with pytest.raises(NoStratigraphyError):
            self.rcm8cube_nostrat.sections["test"].show(
                "time", style="shaded", data="preserved"
            )

    def test_nostrat_show_shaded_asstratigraphy(self):
        with pytest.raises(NoStratigraphyError):
            self.rcm8cube_nostrat.sections["test"].show(
                "time", style="shaded", data="stratigraphy"
            )

    def test_nostrat_show_lines_spacetime(self):
        self.rcm8cube_nostrat.sections["test"].show(
            "time", style="lines", data="spacetime"
        )

    def test_nostrat_show_lines_aspreserved(self):
        with pytest.raises(NoStratigraphyError):
            self.rcm8cube_nostrat.sections["test"].show(
                "time", style="lines", data="preserved"
            )

    def test_nostrat_show_lines_asstratigraphy(self):
        with pytest.raises(NoStratigraphyError):
            self.rcm8cube_nostrat.sections["test"].show(
                "time", style="lines", data="stratigraphy"
            )

    def test_nostrat_show_bad_style(self):
        with pytest.raises(ValueError, match=r'Bad style argument: "somethinginvalid"'):
            self.rcm8cube_nostrat.sections["test"].show(
                "time", style="somethinginvalid", data="spacetime", label=True
            )

    def test_nostrat_show_bad_variable(self):
        with pytest.raises(AttributeError):
            self.rcm8cube_nostrat.sections["test"].show("badvariablename")

    def test_nostrat_show_label_true(self):
        # no assertions, just functionality test
        self.rcm8cube_nostrat.sections["test"].show("time", label=True)

    def test_nostrat_show_label_given(self):
        # no assertions, just functionality test
        self.rcm8cube_nostrat.sections["test"].show("time", label="TESTLABEL!")


class TestSectionFromDataCubeWithStratigraphy:

    rcm8cube = DataCube(golf_path)
    rcm8cube.stratigraphy_from("eta", dz=0.1)
    rcm8cube.register_section("test", StrikeSection(distance_idx=5))

    def test_withstrat_getitem_explicit(self):
        s = self.rcm8cube.sections["test"].__getitem__("velocity")
        assert isinstance(s, xr.core.dataarray.DataArray)

    def test_withstrat_getitem_implicit(self):
        s = self.rcm8cube.sections["test"]["velocity"]
        assert isinstance(s, xr.core.dataarray.DataArray)

    def test_withstrat_getitem_bad_variable(self):
        with pytest.raises(AttributeError):
            self.rcm8cube.sections["test"]["badvariablename"]

    def test_withstrat_getitem_broken_cube(self):
        sass = StrikeSection(distance_idx=5)
        with pytest.raises(AttributeError, match=r"No underlying data connected.*."):
            sass["velocity"]
        # make a good section, then switch to invalidcube inside section
        temp_rcm8cube = DataCube(golf_path)
        temp_rcm8cube.register_section("test", StrikeSection(distance_idx=5))
        temp_rcm8cube.sections["test"]._underlying = "badvalue!"
        with pytest.raises(TypeError):
            _ = temp_rcm8cube.sections["test"].__getitem__("velocity")
        with pytest.raises(TypeError):
            temp_rcm8cube.sections["test"]["velocity"]

    def test_withstrat_knows_stratigraphy(self):
        assert (
            self.rcm8cube.sections["test"]["velocity"].strat._knows_stratigraphy is True
        )
        assert (
            self.rcm8cube.sections["test"]["velocity"].strat.knows_stratigraphy is True
        )

    def test_withstrat_trace(self):
        assert isinstance(self.rcm8cube.sections["test"].trace, np.ndarray)

    def test_withstrat_s(self):
        _s = self.rcm8cube.sections["test"].s
        assert isinstance(_s, xr.core.dataarray.DataArray)
        assert np.all(_s.data[1:] > _s.data[:-1])  # monotonic increase

    def test_withstrat_z(self):
        _z = self.rcm8cube.sections["test"].z
        assert isinstance(_z, xr.core.dataarray.DataArray)
        assert np.all(_z.data[1:] > _z.data[:-1])  # monotonic increase

    def test_withstrat_variables(self):
        _v = self.rcm8cube.sections["test"].variables
        assert len(_v) > 0
        assert isinstance(_v, list)

    def test_withstrat_registered_StrikeSection_attributes(self):
        assert np.all(self.rcm8cube.sections["test"].trace_idx[:, 0] == 5)
        assert self.rcm8cube.sections["test"].s.size == self.rcm8cube.shape[2]
        assert len(self.rcm8cube.sections["test"].variables) > 0
        assert self.rcm8cube.sections["test"].distance_idx == 5

    def test_withstrat_SectionVariable_basic_math(self):
        s1 = self.rcm8cube.sections["test"]["velocity"]
        assert np.all(s1 + s1 == s1 * 2)

    def test_withstrat_strat_attr_mesh_components(self):
        sa = self.rcm8cube.sections["test"]["velocity"].strat.strat_attr
        assert "strata" in sa
        assert "psvd_idx" in sa
        assert "psvd_flld" in sa
        assert "x0" in sa
        assert "x1" in sa
        assert "s" in sa
        assert "s_sp" in sa
        assert "z_sp" in sa

    def test_withstrat_strat_attr_shapes(self):
        sa = self.rcm8cube.sections["test"]["velocity"].strat.strat_attr
        assert sa["x0"].shape == (101, self.rcm8cube.shape[2])
        assert sa["x1"].shape == (101, self.rcm8cube.shape[2])
        assert sa["s"].shape == (self.rcm8cube.shape[2],)
        assert sa["s_sp"].shape == sa["z_sp"].shape

    def test_withstrat_show_shaded_spacetime(self):
        self.rcm8cube.sections["test"].show("time", style="shaded", data="spacetime")

    def test_withstrat_show_shaded_spacetime_specific_ax(self):
        fig, ax = plt.subplots()
        self.rcm8cube.sections["test"].show(
            "time", style="shaded", data="spacetime", ax=ax
        )

    def test_withstrat_show_shaded_spacetime_no_cube(self):
        sass = StrikeSection(distance_idx=5)
        with pytest.raises(AttributeError, match=r"No underlying data connected.*."):
            sass.show("time", style="shaded", data="spacetime")

    def test_withstrat_show_shaded_aspreserved(self):
        self.rcm8cube.sections["test"].show("time", style="shaded", data="preserved")

    def test_withstrat_show_shaded_asstratigraphy(self):
        self.rcm8cube.sections["test"].show("time", style="shaded", data="stratigraphy")

    def test_withstrat_show_lines_spacetime(self):
        self.rcm8cube.sections["test"].show("time", style="lines", data="spacetime")

    def test_withstrat_show_lines_aspreserved(self):
        self.rcm8cube.sections["test"].show("time", style="lines", data="preserved")

    def test_withstrat_show_lines_asstratigraphy(self):
        self.rcm8cube.sections["test"].show("time", style="lines", data="stratigraphy")

    def test_withstrat_show_bad_style(self):
        with pytest.raises(ValueError, match=r'Bad style argument: "somethinginvalid"'):
            self.rcm8cube.sections["test"].show(
                "time", style="somethinginvalid", data="spacetime", label=True
            )

    def test_withstrat_show_bad_variable(self):
        with pytest.raises(AttributeError):
            self.rcm8cube.sections["test"].show("badvariablename")

    def test_withstrat_show_label_true(self):
        # no assertions, just functionality test
        self.rcm8cube.sections["test"].show("time", label=True)

    def test_withstrat_show_label_given(self):
        # no assertions, just functionality test
        self.rcm8cube.sections["test"].show("time", label="TESTLABEL!")


class TestSectionFromStratigraphyCube:

    rcm8cube = DataCube(golf_path)
    sc8cube = StratigraphyCube.from_DataCube(rcm8cube, dz=0.1)
    rcm8cube.register_section("test", StrikeSection(distance_idx=5))
    sc8cube.register_section("test", StrikeSection(distance_idx=5))

    def test_strat_getitem_explicit(self):
        s = self.sc8cube.sections["test"].__getitem__("velocity")
        assert isinstance(s, xr.core.dataarray.DataArray)

    def test_strat_getitem_implicit(self):
        s = self.sc8cube.sections["test"]["velocity"]
        assert isinstance(s, xr.core.dataarray.DataArray)

    def test_strat_getitem_bad_variable(self):
        with pytest.raises(AttributeError):
            self.sc8cube.sections["test"]["badvariablename"]

    def test_strat_getitem_broken_cube(self):
        sass = StrikeSection(distance_idx=5)
        with pytest.raises(AttributeError, match=r"No underlying data connected.*."):
            sass["velocity"]
        # make a good section, then switch to invalidcube inside section
        temp_rcm8cube = DataCube(golf_path)
        temp_rcm8cube.register_section("test", StrikeSection(distance_idx=5))
        temp_rcm8cube.sections["test"]._underlying = "badvalue!"
        with pytest.raises(TypeError):
            _ = temp_rcm8cube.sections["test"].__getitem__("velocity")
        with pytest.raises(TypeError):
            temp_rcm8cube.sections["test"]["velocity"]

    def test_nonequal_sections(self):
        assert not self.rcm8cube.sections["test"] is self.sc8cube.sections["test"]

    def test_trace(self):
        assert isinstance(self.rcm8cube.sections["test"].trace, np.ndarray)
        assert isinstance(self.sc8cube.sections["test"].trace, np.ndarray)

    def test_idx_trace(self):
        assert isinstance(self.rcm8cube.sections["test"].trace_idx, np.ndarray)
        assert isinstance(self.sc8cube.sections["test"].trace_idx, np.ndarray)

    def test_s(self):
        assert isinstance(self.rcm8cube.sections["test"].s, xr.core.dataarray.DataArray)
        assert isinstance(self.sc8cube.sections["test"].s, xr.core.dataarray.DataArray)

    def test_z(self):
        assert isinstance(self.rcm8cube.sections["test"].z, xr.core.dataarray.DataArray)
        assert isinstance(self.sc8cube.sections["test"].z, xr.core.dataarray.DataArray)

    def test_variables(self):
        assert isinstance(self.rcm8cube.sections["test"].variables, list)
        assert isinstance(self.sc8cube.sections["test"].variables, list)

    def test_strat_show_noargs(self):
        self.sc8cube.sections["test"].show("time")

    def test_strat_show_shaded_spacetime(self):
        with pytest.raises(AttributeError, match=r'No "spacetime" or "preserved"*.'):
            self.sc8cube.sections["test"].show("time", style="shaded", data="spacetime")

    def test_strat_show_shaded_spacetime_no_cube(self):
        sass = StrikeSection(distance_idx=5)
        with pytest.raises(AttributeError, match=r"No underlying data connected.*."):
            sass.show("time", style="shaded", data="spacetime")

    def test_strat_show_shaded_aspreserved(self):
        with pytest.raises(AttributeError, match=r'No "spacetime" or "preserved"*.'):
            self.sc8cube.sections["test"].show("time", style="shaded", data="preserved")

    def test_strat_show_shaded_asstratigraphy(self):
        self.sc8cube.sections["test"].show("time", style="shaded", data="stratigraphy")

    def test_strat_show_shaded_asstratigraphy_specific_ax(self):
        fig, ax = plt.subplots()
        self.sc8cube.sections["test"].show(
            "time", style="shaded", data="stratigraphy", ax=ax
        )

    def test_strat_show_lines_spacetime(self):
        with pytest.raises(AttributeError, match=r'No "spacetime" or "preserved"*.'):
            self.sc8cube.sections["test"].show("time", style="lines", data="spacetime")

    def test_strat_show_lines_aspreserved(self):
        with pytest.raises(AttributeError, match=r'No "spacetime" or "preserved"*.'):
            self.sc8cube.sections["test"].show("time", style="lines", data="preserved")

    def test_strat_show_lines_asstratigraphy(self):
        # reason='not yet decided best way to implement'
        with pytest.raises(NotImplementedError):
            self.sc8cube.sections["test"].show(
                "time", style="lines", data="stratigraphy"
            )

    def test_strat_show_bad_style(self):
        with pytest.raises(ValueError, match=r'Bad style argument: "somethinginvalid"'):
            self.sc8cube.sections["test"].show(
                "time", style="somethinginvalid", data="spacetime", label=True
            )

    def test_strat_show_bad_variable(self):
        with pytest.raises(AttributeError):
            self.sc8cube.sections["test"].show("badvariablename")

    def test_strat_show_label_true(self):
        # no assertions, just functionality test
        self.sc8cube.sections["test"].show("time", label=True)

    def test_strat_show_label_given(self):
        # no assertions, just functionality test
        self.sc8cube.sections["test"].show("time", label="TESTLABEL!")


class TestSectionVariableNoStratigraphy:

    rcm8cube = DataCube(golf_path)
    rcm8cube.register_section("test", StrikeSection(distance_idx=5))
    dsv = rcm8cube.sections["test"]["velocity"]

    def test_dsv_view_from(self):
        _arr = self.dsv + 5  # takes a view from
        assert not (_arr is self.dsv)
        _arr2 = _arr - 5
        assert np.all(_arr2 == pytest.approx(self.dsv.values, abs=1e-6))

    def test_dsv_knows_stratigraphy(self):
        assert self.dsv.strat._knows_stratigraphy is False
        assert self.dsv.strat.knows_stratigraphy is False
        assert self.dsv.strat.knows_stratigraphy == self.dsv.strat._knows_stratigraphy

    def test_dsv__check_knows_stratigraphy(self):
        with pytest.raises(NoStratigraphyError):
            self.dsv.strat._check_knows_stratigraphy()

    def test_dsv_as_preserved(self):
        with pytest.raises(NoStratigraphyError):
            self.dsv.strat.as_preserved()

    def test_dsv_as_stratigraphy(self):
        with pytest.raises(NoStratigraphyError):
            self.dsv.strat.as_stratigraphy()


class TestSectionVariableWithStratigraphy:

    rcm8cube = DataCube(golf_path)
    rcm8cube.stratigraphy_from("eta", dz=0.1)
    rcm8cube.register_section("test", StrikeSection(distance_idx=5))
    dsv = rcm8cube.sections["test"]["velocity"]

    def test_dsv_knows_stratigraphy(self):
        assert self.dsv.strat._knows_stratigraphy is True
        assert self.dsv.strat.knows_stratigraphy is True
        assert self.dsv.strat.knows_stratigraphy == self.dsv.strat._knows_stratigraphy

    def test_dsv__check_knows_stratigraphy(self):
        assert self.dsv.strat._check_knows_stratigraphy()

    def test_dsv_as_preserved(self):
        _arr = self.dsv.strat.as_preserved()
        assert _arr.shape == self.dsv.shape
        assert isinstance(_arr, xr.core.dataarray.DataArray)

    def test_dsv_as_stratigraphy(self):
        _arr = self.dsv.strat.as_stratigraphy()
        assert _arr.shape == (
            np.max(self.dsv.strat.strat_attr["z_sp"]) + 1,
            self.dsv.shape[1],
        )


class TestSectionVariableStratigraphyCube:

    rcm8cube = DataCube(golf_path)
    sc8cube = StratigraphyCube.from_DataCube(rcm8cube, dz=0.1)
    sc8cube.register_section("test", StrikeSection(distance_idx=5))
    ssv = sc8cube.sections["test"]["velocity"]

    def test_ssv_view_from(self):
        _arr = self.ssv + 5  # takes a view from
        assert not (_arr is self.ssv)
        assert np.all(np.isnan(_arr) == np.isnan(self.ssv))
        _arr2 = _arr - 5
        assert np.all(
            _arr2.data[~np.isnan(_arr2)].flatten()
            == pytest.approx(self.ssv.data[~np.isnan(self.ssv)].flatten())
        )

    def test_ssv_knows_spacetime(self):
        assert self.ssv.strat._knows_spacetime is False
        assert self.ssv.strat.knows_spacetime is False
        assert self.ssv.strat.knows_spacetime == self.ssv.strat._knows_spacetime

    def test_ssv__check_knows_spacetime(self):
        with pytest.raises(AttributeError, match=r'No "spacetime" or "preserved"*.'):
            self.ssv.strat._check_knows_spacetime()


class TestDipSection:
    """Test the basic of the DipSection."""

    def test_DipSection_without_cube(self):
        ss = DipSection(distance_idx=5)
        assert ss.name is None
        assert ss._input_distance_idx == 5
        assert ss.shape is None
        assert ss._underlying is None
        assert ss._underlying_type is None
        assert ss.s is None
        assert np.all(ss.trace == np.array([[None, None]]))
        assert ss._dim1_idx is None
        assert ss._dim2_idx is None
        assert ss.variables is None
        with pytest.raises(AttributeError, match=r"No underlying data connected.*."):
            ss["velocity"]

    def test_DipSection_bad_cube(self):
        badcube = ["some", "list"]
        with pytest.raises(TypeError, match=r"Expected type is *."):
            _ = DipSection(badcube, distance_idx=12)
        with pytest.raises(TypeError, match=r"Expected type is *."):
            _ = StrikeSection(badcube, distance=1000)

    def test_DipSection_standalone_instantiation(self):
        rcm8cube = DataCube(golf_path)
        sass = DipSection(rcm8cube, distance_idx=120)
        assert sass.name == "dip"
        assert sass.distance_idx == 120
        with pytest.warns(UserWarning, match=r"`.x` is a deprecated .*"):
            assert sass.x == 120
        assert sass._underlying is rcm8cube
        assert sass.trace.shape == (rcm8cube.shape[1], 2)
        assert len(sass.variables) > 0
        sass = DipSection(rcm8cube, distance_idx=12, name="named")
        assert sass.name == "named"
        with pytest.warns(UserWarning, match=r"`.x` is a deprecated .*"):
            assert sass.x == 12

    def test_DipSection_register_section_distance_idx(self):
        rcm8cube = DataCube(golf_path)
        rcm8cube.register_section("test", DipSection(distance_idx=150))
        assert rcm8cube.sections["test"].name == "test"
        assert len(rcm8cube.sections["test"].variables) > 0
        assert rcm8cube.sections["test"]._underlying is rcm8cube
        with pytest.warns(UserWarning, match=r"`.x` is a deprecated .*"):
            assert rcm8cube.sections["test"].x == 150
        with pytest.warns(UserWarning, match=r"`.y` is a deprecated .*"):
            assert rcm8cube.sections["test"].y == rcm8cube.L
        # test that the name warning is raised when creating
        with pytest.warns(UserWarning, match=r"`name` argument supplied .*"):
            rcm8cube.register_section(
                "testname", DipSection(distance_idx=150, name="TESTING")
            )
        assert rcm8cube.sections["testname"].name == "TESTING"
        _sect = rcm8cube.register_section(
            "test", DipSection(distance_idx=150), return_section=True
        )
        assert isinstance(_sect, DipSection)

    def test_DipSection_register_section_distance(self):
        rcm8cube = DataCube(golf_path)
        rcm8cube.register_section("test", DipSection(distance=4000))
        assert rcm8cube.sections["test"].name == "test"
        assert rcm8cube.sections["test"]._input_distance == 4000
        assert rcm8cube.sections["test"]._input_distance_idx is None
        assert rcm8cube.sections["test"]._input_length is None
        assert rcm8cube.sections["test"]._distance_idx > 0
        assert (
            rcm8cube.sections["test"].length
            == rcm8cube.dim1_coords[-1] + rcm8cube.dim1_coords[1]
        )
        assert rcm8cube.sections["test"].distance == 4000
        assert len(rcm8cube.sections["test"].variables) > 0
        assert rcm8cube.sections["test"]._underlying is rcm8cube
        with pytest.warns(UserWarning, match=r"`.x` is a deprecated .*"):
            assert (
                rcm8cube.sections["test"].x == rcm8cube.sections["test"]._distance_idx
            )
        rcm8cube.register_section(
            "lengthtest", DipSection(distance=7000, length=(500, 2000))
        )
        assert rcm8cube.sections["lengthtest"].name == "lengthtest"
        assert rcm8cube.sections["lengthtest"]._input_distance == 7000
        assert rcm8cube.sections["lengthtest"]._input_distance_idx is None
        assert rcm8cube.sections["lengthtest"]._input_length == (500, 2000)
        assert rcm8cube.sections["lengthtest"]._distance_idx > 0
        assert rcm8cube.sections["lengthtest"].length == pytest.approx(1500, 50)
        assert rcm8cube.sections["lengthtest"].distance == 7000

    def test_DipSection_register_section_notboth_distance_distance_idx(self):
        rcm8cube = DataCube(golf_path)
        with pytest.raises(
            ValueError, match=r"Cannot specify both `distance` .*"
        ):  # noqa: E501
            rcm8cube.register_section("test", DipSection(distance=2000, distance_idx=2))

    def test_DipSection_register_section_deprecated(self):
        rcm8cube = DataCube(golf_path)
        with pytest.warns(UserWarning, match=r"Arguments `y` and `x` are .*"):
            rcm8cube.register_section("warn", DipSection(x=5))
        # the section should still work though, so check on the attrs
        assert rcm8cube.sections["warn"].name == "warn"
        assert rcm8cube.sections["warn"]._input_distance is None
        assert rcm8cube.sections["warn"]._input_distance_idx == 5
        assert rcm8cube.sections["warn"]._input_length is None
        assert rcm8cube.sections["warn"]._distance_idx == 5
        assert rcm8cube.sections["warn"].length == (
            rcm8cube.dim1_coords[-1] + rcm8cube.dim1_coords[1]
        )
        assert rcm8cube.sections["warn"].distance == rcm8cube.dim2_coords[5]
        assert len(rcm8cube.sections["warn"].variables) > 0
        assert rcm8cube.sections["warn"]._underlying is rcm8cube
        # test for the error with spec deprecated and new
        with pytest.raises(
            ValueError, match=r"Cannot specify `distance`, .*"
        ):  # noqa: E501
            rcm8cube.register_section(
                "fail", DipSection(y=2, distance=2000, distance_idx=2)
            )

    def test_DipSection_register_section_length_limits(self):
        rcm8cube = DataCube(golf_path)
        rcm8cube.register_section(
            "tuple", DipSection(distance_idx=150, length=(10, 50))
        )
        rcm8cube.register_section("list", DipSection(distance_idx=150, length=(10, 40)))
        assert len(rcm8cube.sections) == 2
        assert rcm8cube.sections["tuple"]._dim1_idx.shape[0] == 41
        assert rcm8cube.sections["list"]._dim1_idx.shape[0] == 31
        assert np.all(rcm8cube.sections["list"]._dim2_idx == 150)
        assert np.all(rcm8cube.sections["tuple"]._dim2_idx == 150)


class TestSectionsIntoMasks:

    golfcube = DataCube(golf_path)
    EM = ElevationMask(golfcube["eta"][-1], elevation_threshold=0)

    def test_section_types(self):
        mcs = CircularSection(self.EM, radius=500)
        _got = mcs["mask"]
        assert _got.ndim == 1
        assert np.all(np.logical_or(_got == 1, _got == 0))
        mrs = RadialSection(self.EM, azimuth=50)
        _got = mrs["mask"]
        assert _got.ndim == 1
        assert np.all(np.logical_or(_got == 1, _got == 0))
        mss = StrikeSection(self.EM, distance=500)
        _got = mss["mask"]
        assert _got.ndim == 1
        assert np.all(np.logical_or(_got == 1, _got == 0))

    def test_show(self):
        mss = StrikeSection(self.EM, distance=500)
        fig, ax = plt.subplots()
        mss.show("mask", ax=ax)
        plt.close()

    def test_show_trace(self):
        mss = StrikeSection(self.EM, distance=500)
        fig, ax = plt.subplots()
        mss.show_trace(ax=ax)
        plt.close()


class TestSectionsIntoPlans:

    golfcube = DataCube(golf_path)
    pl = Planform(golfcube, idx=-1)

    def test_section_types(self):
        mcs = CircularSection(self.pl, radius=500)
        _got = mcs["eta"]
        assert _got.ndim == 1
        assert np.all(np.isfinite(_got))
        mrs = RadialSection(self.pl, azimuth=50)
        _got = mrs["eta"]
        assert _got.ndim == 1
        assert np.all(np.isfinite(_got))
        mss = StrikeSection(self.pl, distance=500)
        _got = mss["eta"]
        assert _got.ndim == 1
        assert np.all(np.isfinite(_got))

    def test_show(self):
        mss = StrikeSection(self.pl, distance=500)
        fig, ax = plt.subplots()
        mss.show("eta", ax=ax)
        plt.close()

    def test_show_trace(self):
        mss = StrikeSection(self.pl, distance=500)
        fig, ax = plt.subplots()
        mss.show_trace(ax=ax)
        plt.close()


class TestSectionsIntoArrays:

    arr = np.random.uniform(size=(100, 200))

    def test_section_types(self):
        mcs = CircularSection(self.arr, radius=500)
        _got = mcs[None]
        assert _got.ndim == 1
        assert np.all(np.logical_or(_got <= 1, _got >= 0))
        mrs = RadialSection(self.arr, azimuth=50)
        _got = mrs[None]
        assert _got.ndim == 1
        assert np.all(np.logical_or(_got <= 1, _got >= 0))
        mss = StrikeSection(self.arr, distance=500)
        _got = mss[None]
        assert _got.ndim == 1
        assert np.all(np.logical_or(_got <= 1, _got >= 0))

    def test_show(self):
        mss = StrikeSection(self.arr, distance=500)
        fig, ax = plt.subplots()
        mss.show("mask", ax=ax)
        plt.close()

    def test_show_trace(self):
        mss = StrikeSection(self.arr, distance=500)
        fig, ax = plt.subplots()
        mss.show_trace(ax=ax)
        plt.close()
