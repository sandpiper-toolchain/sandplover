"""Tests for the mask.py script."""

import unittest.mock as mock

import matplotlib.pyplot as plt
import numpy as np
import pytest
import xarray as xr

from deltametrics.cube import DataCube
from deltametrics.mask import BaseMask
from deltametrics.mask import CenterlineMask
from deltametrics.mask import ChannelMask
from deltametrics.mask import DepositMask
from deltametrics.mask import EdgeMask
from deltametrics.mask import ElevationMask
from deltametrics.mask import FlowMask
from deltametrics.mask import GeometricMask
from deltametrics.mask import LandMask
from deltametrics.mask import ShorelineMask
from deltametrics.mask import WetMask
from deltametrics.plan import MorphologicalPlanform
from deltametrics.plan import OpeningAnglePlanform
from deltametrics.sample_data.sample_data import _get_golf_path
from deltametrics.sample_data.sample_data import _get_rcm8_path

rcm8_path = _get_rcm8_path()
with pytest.warns(UserWarning):
    rcm8cube = DataCube(rcm8_path)

golf_path = _get_golf_path()
golfcube = DataCube(golf_path)

_OAP_0 = OpeningAnglePlanform.from_elevation_data(
    golfcube["eta"][-1, :, :], elevation_threshold=0
)
_OAP_05 = OpeningAnglePlanform.from_elevation_data(
    golfcube["eta"][-1, :, :], elevation_threshold=0.5
)
_MPM_0 = MorphologicalPlanform.from_elevation_data(
    golfcube["eta"][-1, :, :], elevation_threshold=0, max_disk=12
)


@mock.patch.multiple(BaseMask, __abstractmethods__=set())
class TestBaseMask:
    """
    To test the BaseMask, we patch the base job with a filled abstract method
    `.run()`.

    .. note:: This patch is handled at the class level above!!
    """

    fake_input = np.ones((100, 200))

    @mock.patch("deltametrics.mask.BaseMask._set_shape_mask")
    def test_name_setter(self, patched):
        basemask = BaseMask("somename", self.fake_input)
        assert basemask.mask_type == "somename"
        patched.assert_called()  # this would change the shape
        assert basemask.shape is None  # so shape is not set
        assert basemask._mask is None  # so mask is not set

    def test_simple_example(self):
        basemask = BaseMask("field", self.fake_input)

        # make a bunch of assertions
        assert not np.any(basemask._mask)
        assert np.all(basemask.integer_mask == 0)
        assert basemask._mask is basemask.mask
        assert basemask.shape == self.fake_input.shape

    def test_trim_mask_length(self):
        basemask = BaseMask("field", self.fake_input)
        # mock as though the mask were made
        basemask._mask = self.fake_input.astype(bool)

        assert np.all(basemask.integer_mask == 1)

        _l = 5
        basemask.trim_mask(length=_l)

        assert basemask._mask.dtype == bool
        assert np.all(basemask.integer_mask[:_l, :] == 0)
        assert np.all(basemask.integer_mask[_l:, :] == 1)

    @pytest.mark.xfail(
        raises=NotImplementedError, strict=True, reason="Have not implemented pathway."
    )
    def test_trim_mask_cube(self):
        basemask = BaseMask("field", self.fake_input)
        # mock as though the mask were made
        basemask._mask = self.fake_input.astype(bool)

        assert np.all(basemask.integer_mask == 1)

        basemask.trim_mask(golfcube)
        # assert np.all(basemask.integer_mask[:5, :] == 0)
        # assert np.all(basemask.integer_mask[5:, :] == 1)

    @pytest.mark.xfail(
        raises=NotImplementedError, strict=True, reason="Have not implemented pathway."
    )
    def test_trim_mask_noargs(self):
        basemask = BaseMask("field", self.fake_input)
        # mock as though the mask were made
        basemask._mask = self.fake_input.astype(bool)

        assert np.all(basemask.integer_mask == 1)

        basemask.trim_mask()
        # assert np.all(basemask.integer_mask[:5, :] == 0)
        # assert np.all(basemask.integer_mask[5:, :] == 1)

    def test_trim_mask_axis1_withlength(self):
        basemask = BaseMask("field", self.fake_input)
        # mock as though the mask were made
        basemask._mask = self.fake_input.astype(bool)

        assert np.all(basemask.integer_mask == 1)

        _l = 5
        basemask.trim_mask(axis=0, length=_l)
        assert basemask._mask.dtype == bool
        assert np.all(basemask.integer_mask[:, :_l] == 0)
        assert np.all(basemask.integer_mask[:, _l:] == 1)

    def test_trim_mask_diff_True(self):
        basemask = BaseMask("field", self.fake_input)

        # everything is False (0)
        assert np.all(basemask.integer_mask == 0)

        _l = 5
        basemask.trim_mask(value=True, length=_l)

        assert basemask._mask.dtype == bool
        assert np.all(basemask.integer_mask[:_l, :] == 1)
        assert np.all(basemask.integer_mask[_l:, :] == 0)

    def test_trim_mask_diff_ints(self):
        basemask = BaseMask("field", self.fake_input)

        # everything is False (0)
        assert np.all(basemask.integer_mask == 0)

        _l = 5
        basemask.trim_mask(value=1, length=_l)
        assert basemask._mask.dtype == bool
        assert np.all(basemask.integer_mask[:_l, :] == 1)

        basemask.trim_mask(value=0, length=_l)
        assert basemask._mask.dtype == bool
        assert np.all(basemask.integer_mask[:_l, :] == 0)

        basemask.trim_mask(value=5, length=_l)
        assert basemask._mask.dtype == bool
        assert np.all(basemask.integer_mask[:_l, :] == 1)

        basemask.trim_mask(value=5.534, length=_l)
        assert basemask._mask.dtype == bool
        assert np.all(basemask.integer_mask[:_l, :] == 1)

    def test_trim_mask_toomanyargs(self):
        basemask = BaseMask("field", self.fake_input)

        with pytest.raises(ValueError):
            basemask.trim_mask("arg1", "arg2", value=1, length=1)

    def test_show(self):
        """
        Here, we just test whether it works, and whether it takes a
        specific axis.
        """
        basemask = BaseMask("field", self.fake_input)

        # test show with nothing
        basemask.show()
        plt.close()

        # test show with colorbar
        basemask.show(colorbar=True)
        plt.close()

        # test show with title
        basemask.show(title="a title")
        plt.close()

        # test show with axes, bad values
        fig, ax = plt.subplots()
        basemask.show(ax=ax)
        plt.close()

    def test_show_error_nomask(self):
        """
        Here, we just test whether it works, and whether it takes a
        specific axis.
        """
        basemask = BaseMask("field", self.fake_input)

        # mock as though something went wrong
        basemask._mask = None

        with pytest.raises(RuntimeError):
            basemask.show()

    def test_no_data(self):
        """Test when no data input raises error."""
        with pytest.raises(ValueError, match=r"Expected 1 input, got 0."):
            _ = BaseMask("field")

    def test_invalid_data(self):
        """Test invalid data input."""
        with pytest.raises(TypeError, match=r"Unexpected type was input: .*"):
            _ = BaseMask("field", "a string!!")

    def test_invalid_second_data(self):
        """Test invalid data input."""
        with pytest.raises(TypeError, match=r"First input to mask .*"):
            _ = BaseMask("field", np.zeros((100, 200)), "a string!!")

    def test_return_empty(self):
        """Test when no data input, but allow empty, returns empty."""
        empty_basemask = BaseMask("field", allow_empty=True)
        assert empty_basemask.mask_type == "field"
        assert empty_basemask.shape is None
        assert empty_basemask._mask is None
        assert empty_basemask._mask is empty_basemask.mask

    def test_is_mask_deprecationwarning(self):
        """Test that TypeError is raised if is_mask is invalid."""
        with pytest.warns(DeprecationWarning):
            _ = BaseMask("field", self.fake_input, is_mask="invalid")
        with pytest.warns(DeprecationWarning):
            _ = BaseMask("field", self.fake_input, is_mask=True)

    def test_3dinput_deprecationerror(self):
        """Test that TypeError is raised if is_mask is invalid."""
        with pytest.raises(ValueError, match=r"Creating a `Mask` .*"):
            _ = BaseMask("field", np.random.uniform(size=(10, 100, 200)))


class TestShorelineMask:
    """Tests associated with the ShorelineMask class."""

    # define an input mask for the mask instantiation pathway
    _ElevationMask = ElevationMask(golfcube["eta"][-1, :, :], elevation_threshold=0)

    def test_default_vals_array(self):
        """Test that instantiation works for an array."""
        # define the mask
        shoremask = ShorelineMask(rcm8cube["eta"][-1, :, :], elevation_threshold=0)
        # make assertions
        assert shoremask._input_flag == "array"
        assert shoremask.mask_type == "shoreline"
        assert shoremask.contour_threshold > 0
        assert shoremask._mask.dtype == bool
        assert isinstance(shoremask._mask, xr.core.dataarray.DataArray)

    @pytest.mark.xfail(
        raises=NotImplementedError, strict=True, reason="Have not implemented pathway."
    )
    def test_default_vals_cube(self):
        """Test that instantiation works for an array."""
        # define the mask
        shoremask = ShorelineMask(rcm8cube, t=-1)
        # make assertions
        assert shoremask._input_flag == "cube"
        assert shoremask.mask_type == "shoreline"
        assert shoremask.contour_threshold > 0
        assert shoremask._mask.dtype == bool

    @pytest.mark.xfail(
        raises=NotImplementedError, strict=True, reason="Have not implemented pathway."
    )
    def test_default_vals_cubewithmeta(self):
        """Test that instantiation works for an array."""
        # define the mask
        shoremask = ShorelineMask(golfcube, t=-1)
        # make assertions
        assert shoremask._input_flag == "cube"
        assert shoremask.mask_type == "shoreline"
        assert shoremask.contour_threshold > 0
        assert shoremask._mask.dtype == bool

    @pytest.mark.xfail(
        raises=NotImplementedError, strict=True, reason="Have not implemented pathway."
    )
    def test_default_vals_mask(self):
        """Test that instantiation works for an array."""
        # define the mask
        shoremask = ShorelineMask(self._ElevationMask)
        # make assertions
        assert shoremask._input_flag == "mask"
        assert shoremask.mask_type == "shoreline"
        assert shoremask.contour_threshold > 0
        assert shoremask._mask.dtype == bool

    def test_angle_threshold(self):
        """Test that instantiation works for an array."""
        # define the mask
        shoremask_default = ShorelineMask(
            rcm8cube["eta"][-1, :, :], elevation_threshold=0
        )
        shoremask = ShorelineMask(
            rcm8cube["eta"][-1, :, :], elevation_threshold=0, contour_threshold=45
        )
        # make assertions
        assert shoremask.contour_threshold == 45
        assert not np.all(shoremask_default == shoremask)

    def test_submergedLand(self):
        """Check what happens when there is no (non-initial) land above water."""
        # define the mask
        shoremask = ShorelineMask(rcm8cube["eta"][0, :, :], elevation_threshold=0)
        # assert - expect all True values should be in one row
        _whr_edge = np.where(shoremask._mask[:, 0])
        assert _whr_edge[0].size > 0  # if fails, no shoreline found!
        _row = int(_whr_edge[0][0])
        _third = shoremask.shape[1] // 3  # limit to left of inlet
        assert np.all(shoremask._mask[_row, :_third] == 1)
        assert np.all(shoremask._mask[_row + 1 :, :] == 0)

    def test_static_from_OAP(self):
        shoremask = ShorelineMask(golfcube["eta"][-1, :, :], elevation_threshold=0)
        mfOAP = ShorelineMask.from_Planform(_OAP_0)

        shoremask_05 = ShorelineMask(golfcube["eta"][-1, :, :], elevation_threshold=0.5)
        mfOAP_05 = ShorelineMask.from_Planform(_OAP_05)

        assert np.all(shoremask._mask == mfOAP._mask)
        assert np.all(shoremask_05._mask == mfOAP_05._mask)

    def test_static_from_MPM(self):
        shoremask = ShorelineMask(
            golfcube["eta"][-1, :, :],
            elevation_threshold=0,
            method="MPM",
            max_disk=12,
            contour_threshold=0.5,
        )
        mfMPM = ShorelineMask.from_Planform(_MPM_0, contour_threshold=0.5)

        assert np.all(shoremask._mask == mfMPM._mask)

    def test_static_from_mask_ElevationMask(self):
        shoremask = ShorelineMask(golfcube["eta"][-1, :, :], elevation_threshold=0)
        mfem = ShorelineMask.from_mask(self._ElevationMask)

        shoremask_05 = ShorelineMask(golfcube["eta"][-1, :, :], elevation_threshold=0.5)

        assert np.all(shoremask._mask == mfem._mask)
        assert np.sum(shoremask_05.integer_mask) < np.sum(shoremask.integer_mask)

    def test_static_from_masks_EM_MPM(self):
        shoremask = ShorelineMask(
            golfcube["eta"][-1, :, :],
            elevation_threshold=0,
            contour_threshold=0.5,
            method="MPM",
            max_disk=12,
        )
        mfem = ShorelineMask.from_masks(
            self._ElevationMask, method="MPM", contour_threshold=0.5, max_disk=12
        )

        assert np.all(shoremask._mask == mfem._mask)

    def test_static_from_array(self):
        """Test that instantiation works for an array."""
        # define the mask
        _arr = np.ones((100, 200))
        _arr[50:55, :] = 0

        shoremask = ShorelineMask.from_array(_arr)
        # make assertions
        assert shoremask.mask_type == "shoreline"
        assert shoremask._input_flag is None
        assert np.all(shoremask._mask == _arr)

        _arr2 = np.random.uniform(size=(100, 200))
        _arr2_bool = _arr2.astype(bool)

        assert _arr2.dtype == float

        shoremask2 = ShorelineMask.from_array(_arr2)
        # make assertions
        assert shoremask2.mask_type == "shoreline"
        assert shoremask2._input_flag is None
        assert np.all(shoremask2._mask == _arr2_bool)


class TestElevationMask:
    """Tests associated with the LandMask class."""

    def test_default_vals_array(self):
        """Test that instantiation works for an array."""
        # define the mask
        elevationmask = ElevationMask(golfcube["eta"][-1, :, :], elevation_threshold=0)
        # make assertions
        assert elevationmask._input_flag == "array"
        assert elevationmask.mask_type == "elevation"
        assert elevationmask.elevation_threshold == 0
        assert elevationmask.threshold == 0
        assert elevationmask.elevation_threshold is elevationmask.threshold
        assert elevationmask._mask.dtype == bool

    def test_all_below_threshold(self):
        elevationmask = ElevationMask(golfcube["eta"][-1, :, :], elevation_threshold=10)
        # make assertions
        assert elevationmask._input_flag == "array"
        assert elevationmask.mask_type == "elevation"
        assert elevationmask.elevation_threshold == 10
        assert elevationmask.threshold == 10
        assert elevationmask.elevation_threshold is elevationmask.threshold
        assert elevationmask._mask.dtype == bool
        assert np.all(elevationmask.mask == 0)

    def test_all_above_threshold(self):
        elevationmask = ElevationMask(
            golfcube["eta"][-1, :, :], elevation_threshold=-10
        )
        # make assertions
        assert elevationmask._input_flag == "array"
        assert elevationmask.mask_type == "elevation"
        assert elevationmask.elevation_threshold == -10
        assert elevationmask.threshold == -10
        assert elevationmask.elevation_threshold is elevationmask.threshold
        assert elevationmask._mask.dtype == bool
        assert np.all(elevationmask.mask == 1)

    def test_default_vals_array_needs_elevation_threshold(self):
        """Test that instantiation works for an array."""
        # define the mask
        with pytest.raises(TypeError, match=r".* missing"):
            _ = ElevationMask(rcm8cube["eta"][-1, :, :])

    def test_default_vals_cube(self):
        """Test that instantiation works for an array."""
        # define the mask
        elevationmask = ElevationMask(rcm8cube, t=-1, elevation_threshold=0)
        # make assertions
        assert elevationmask._input_flag == "cube"
        assert elevationmask.mask_type == "elevation"
        assert elevationmask._mask.dtype == bool

    def test_default_vals_cubewithmeta(self):
        """Test that instantiation works for an array."""
        # define the mask
        elevationmask = ElevationMask(golfcube, t=-1, elevation_threshold=0)
        # make assertions
        assert elevationmask._input_flag == "cube"
        assert elevationmask.mask_type == "elevation"
        assert elevationmask._mask.dtype == bool

        # compare with another instantiated from array
        elevationmask_comp = ElevationMask(
            golfcube["eta"][-1, :, :], elevation_threshold=0
        )

        assert np.all(elevationmask_comp.mask == elevationmask.mask)

        # try with a different elevation_threshold (higher)
        elevationmask_higher = ElevationMask(golfcube, t=-1, elevation_threshold=0.5)

        assert np.sum(elevationmask_higher.integer_mask) < np.sum(
            elevationmask.integer_mask
        )

    def test_default_vals_cube_needs_elevation_threshold(self):
        """Test that instantiation works for an array."""
        # define the mask
        with pytest.raises(TypeError, match=r".* missing"):
            _ = ElevationMask(rcm8cube, t=-1)

        with pytest.raises(TypeError, match=r".* missing"):
            _ = ElevationMask(golfcube, t=-1)

    def test_default_vals_mask_notimplemented(self):
        """Test that instantiation works for an array."""
        # define the mask
        _ElevationMask = ElevationMask(golfcube["eta"][-1, :, :], elevation_threshold=0)
        with pytest.raises(NotImplementedError, match=r"Cannot instantiate .*"):
            _ = ElevationMask(_ElevationMask, elevation_threshold=0)

    def test_submergedLand(self):
        """Check what happens when there is no land above water."""
        # define the mask
        elevationmask = ElevationMask(rcm8cube["eta"][0, :, :], elevation_threshold=0)
        # assert - expect all True values should be up to a point
        _whr_land = np.where(elevationmask._mask[:, 0])
        assert _whr_land[0].size > 0  # if fails, no land found!
        _row = int(_whr_land[0][-1]) + 1  # last index
        _third = elevationmask.shape[1] // 3  # limit to left of inlet
        assert np.all(elevationmask._mask[:_row, :_third] == 1)
        assert np.all(elevationmask._mask[_row:, :] == 0)

    def test_static_from_array(self):
        """Test that instantiation works for an array."""
        # define the mask
        _arr = np.ones((100, 200))
        _arr[50:55, :] = 0

        elevmask = ElevationMask.from_array(_arr)
        # make assertions
        assert elevmask.mask_type == "elevation"
        assert elevmask._input_flag is None
        assert np.all(elevmask._mask == _arr)

        _arr2 = np.random.uniform(size=(100, 200))
        _arr2_bool = _arr2.astype(bool)

        assert _arr2.dtype == float

        elevmask2 = ElevationMask.from_array(_arr2)
        # make assertions
        assert elevmask2.mask_type == "elevation"
        assert elevmask2._input_flag is None
        assert np.all(elevmask2._mask == _arr2_bool)


class TestFlowMask:
    """Tests associated with the LandMask class."""

    def test_default_vals_array(self):
        """Test that instantiation works for an array."""
        # define the mask
        flowmask = FlowMask(golfcube["velocity"][-1, :, :], flow_threshold=0.3)
        # make assertions
        assert flowmask._input_flag == "array"
        assert flowmask.mask_type == "flow"
        assert flowmask.flow_threshold == 0.3
        assert flowmask.threshold == 0.3
        assert flowmask.flow_threshold is flowmask.threshold
        assert flowmask._mask.dtype == bool

        # note that, the mask will take any array though...
        # define the mask
        flowmask_any = FlowMask(golfcube["eta"][-1, :, :], flow_threshold=0)

        assert flowmask_any._input_flag == "array"
        assert flowmask_any.mask_type == "flow"
        assert flowmask_any.flow_threshold == 0
        assert flowmask_any.threshold == 0
        assert flowmask_any.flow_threshold is flowmask_any.threshold

    def test_all_below_threshold(self):
        flowmask = FlowMask(golfcube["velocity"][-1, :, :], flow_threshold=20)
        # make assertions
        assert flowmask._input_flag == "array"
        assert flowmask.mask_type == "flow"
        assert flowmask.flow_threshold == 20
        assert flowmask.threshold == 20
        assert flowmask.flow_threshold is flowmask.threshold
        assert flowmask._mask.dtype == bool
        assert np.all(flowmask.mask == 0)

    def test_all_above_threshold(self):
        flowmask = FlowMask(golfcube["velocity"][-1, :, :], flow_threshold=-5)
        # make assertions
        assert flowmask._input_flag == "array"
        assert flowmask.mask_type == "flow"
        assert flowmask.flow_threshold == -5
        assert flowmask.threshold == -5
        assert flowmask.flow_threshold is flowmask.threshold
        assert flowmask._mask.dtype == bool
        assert np.all(flowmask.mask == 1)

    def test_default_vals_array_needs_flow_threshold(self):
        """Test that instantiation works for an array."""
        # define the mask
        with pytest.raises(TypeError, match=r".* missing"):
            _ = FlowMask(rcm8cube["velocity"][-1, :, :])

    def test_default_vals_cube(self):
        """Test that instantiation works for an array."""
        # define the mask
        flowmask = FlowMask(rcm8cube, t=-1, flow_threshold=0.3)
        # make assertions
        assert flowmask._input_flag == "cube"
        assert flowmask.mask_type == "flow"
        assert flowmask._mask.dtype == bool

    def test_vals_cube_different_fields(self):
        """Test that instantiation works for an array."""
        # define the mask
        velmask = FlowMask(rcm8cube, t=-1, cube_key="velocity", flow_threshold=0.3)
        # make assertions
        assert velmask._input_flag == "cube"
        assert velmask.mask_type == "flow"
        assert velmask._mask.dtype == bool

        dismask = FlowMask(rcm8cube, t=-1, cube_key="discharge", flow_threshold=0.3)
        # make assertions
        assert dismask._input_flag == "cube"
        assert dismask.mask_type == "flow"
        assert dismask._mask.dtype == bool

        assert not np.all(velmask.mask == dismask.mask)

    def test_default_vals_cubewithmeta(self):
        """Test that instantiation works
        For a cube with metadata.
        """
        # define the mask
        flowmask = FlowMask(golfcube, t=-1, flow_threshold=0.3)
        # make assertions
        assert flowmask._input_flag == "cube"
        assert flowmask.mask_type == "flow"
        assert flowmask._mask.dtype == bool

        # compare with another instantiated from array
        flowmask_comp = FlowMask(golfcube["velocity"][-1, :, :], flow_threshold=0.3)

        assert np.all(flowmask_comp.mask == flowmask.mask)

    def test_flowthresh_vals_cubewithmeta(self):
        # make default
        flowmask = FlowMask(golfcube, t=-1, flow_threshold=0.3)

        # try with a different flow_threshold (higher)
        flowmask_higher = FlowMask(golfcube, t=-1, flow_threshold=0.5)

        assert np.sum(flowmask_higher.integer_mask) < np.sum(flowmask.integer_mask)

    def test_default_vals_cube_needs_flow_threshold(self):
        """Test that instantiation works for an array."""
        # define the mask
        with pytest.raises(TypeError, match=r".* missing"):
            _ = FlowMask(rcm8cube, t=-1)

        with pytest.raises(TypeError, match=r".* missing"):
            _ = FlowMask(golfcube, t=-1)

    def test_default_vals_mask_notimplemented(self):
        """Test that instantiation works for an array."""
        # define the mask
        _ElevationMask = ElevationMask(golfcube["eta"][-1, :, :], elevation_threshold=0)
        with pytest.raises(NotImplementedError, match=r"Cannot instantiate .*"):
            _ = FlowMask(_ElevationMask, flow_threshold=0.3)

    def test_submergedLand(self):
        """Check what happens when there is no land above water."""
        # define the mask
        flowmask = FlowMask(rcm8cube["velocity"][0, :, :], flow_threshold=0.3)
        # assert - expect doesnt care about land
        assert (
            np.any(flowmask._mask[0, :]) > 0
        )  # some high flow in first row, because of inlet
        assert flowmask.mask_type == "flow"

    def test_static_from_array(self):
        """Test that instantiation works for an array."""
        # define the mask
        _arr = np.ones((100, 200))
        _arr[50:55, :] = 0

        flowmask = FlowMask.from_array(_arr)
        # make assertions
        assert flowmask.mask_type == "flow"
        assert flowmask._input_flag is None
        assert np.all(flowmask._mask == _arr)

        _arr2 = np.random.uniform(size=(100, 200))
        _arr2_bool = _arr2.astype(bool)

        assert _arr2.dtype == float

        flowmask2 = FlowMask.from_array(_arr2)
        # make assertions
        assert flowmask2.mask_type == "flow"
        assert flowmask2._input_flag is None
        assert np.all(flowmask2._mask == _arr2_bool)


class TestLandMask:
    """Tests associated with the LandMask class."""

    # define an input mask for the mask instantiation pathway
    _ElevationMask = ElevationMask(golfcube["eta"][-1, :, :], elevation_threshold=0)

    _OAP_0 = OpeningAnglePlanform.from_elevation_data(
        golfcube["eta"][-1, :, :], elevation_threshold=0
    )
    _OAP_05 = OpeningAnglePlanform.from_elevation_data(
        golfcube["eta"][-1, :, :], elevation_threshold=0.5
    )

    def test_default_vals_array(self):
        """Test that instantiation works for an array."""
        # define the mask
        landmask = LandMask(rcm8cube["eta"][-1, :, :], elevation_threshold=0)
        # make assertions
        assert landmask._input_flag == "array"
        assert landmask.mask_type == "land"
        assert landmask.contour_threshold > 0
        assert landmask._mask.dtype == bool

    def test_default_vals_array_needs_elevation_threshold(self):
        """Test that instantiation works for an array."""
        # define the mask
        with pytest.raises(TypeError, match=r".* missing"):
            _ = LandMask(rcm8cube["eta"][-1, :, :])

    @pytest.mark.xfail(
        raises=NotImplementedError, strict=True, reason="Have not implemented pathway."
    )
    def test_default_vals_cube(self):
        """Test that instantiation works for an array."""
        # define the mask
        landmask = LandMask(rcm8cube, t=-1)
        # make assertions
        assert landmask._input_flag == "cube"
        assert landmask.mask_type == "land"
        assert landmask.contour_threshold > 0
        assert landmask._mask.dtype == bool

    @pytest.mark.xfail(
        raises=NotImplementedError, strict=True, reason="Have not implemented pathway."
    )
    def test_default_vals_cubewithmeta(self):
        """Test that instantiation works for an array."""
        # define the mask
        landmask = LandMask(golfcube, t=-1)
        # make assertions
        assert landmask._input_flag == "cube"
        assert landmask.mask_type == "land"
        assert landmask.contour_threshold > 0
        assert landmask._mask.dtype == bool

    @pytest.mark.xfail(
        raises=NotImplementedError, strict=True, reason="Have not implemented pathway."
    )
    def test_default_vals_mask(self):
        """Test that instantiation works for an array."""
        # define the mask
        landmask = LandMask(self._ElevationMask)
        # make assertions
        assert landmask._input_flag == "mask"
        assert landmask.mask_type == "land"
        assert landmask.contour_threshold > 0
        assert landmask._mask.dtype == bool

    def test_angle_threshold(self):
        """
        Test that the angle threshold argument is used by the LandMask
        when instantiated.
        """
        # define the mask
        landmask_default = LandMask(rcm8cube["eta"][-1, :, :], elevation_threshold=0)
        landmask = LandMask(
            rcm8cube["eta"][-1, :, :], elevation_threshold=0, contour_threshold=45
        )
        # make assertions
        assert landmask.contour_threshold == 45
        assert not np.all(landmask_default == landmask)

    @pytest.mark.xfail(
        strict=True,
        reason=(
            "Breaking change to OAP leads to inlet not being classified as"
            " land. (v0.4.3)."
        ),
    )
    def test_submergedLand(self):
        """Check what happens when there is no land above water."""
        # define the mask
        landmask = LandMask(rcm8cube["eta"][0, :, :], elevation_threshold=0)
        # assert - expect all True values should be in one row
        _whr_land = np.where(landmask._mask[:, 0])
        assert _whr_land[0].size > 0  # if fails, no land found!
        _row = int(_whr_land[0][-1]) + 1  # last index
        _third = landmask.shape[1] // 3  # limit to left of inlet
        assert np.all(landmask._mask[_row, :_third] == 1)
        assert np.all(landmask._mask[_row + 1 :, :] == 0)

    def test_static_from_OAP(self):
        landmask = LandMask(golfcube["eta"][-1, :, :], elevation_threshold=0)
        mfOAP = LandMask.from_Planform(_OAP_0)

        landmask_05 = LandMask(golfcube["eta"][-1, :, :], elevation_threshold=0.5)
        mfOAP_05 = LandMask.from_Planform(_OAP_05)

        assert np.all(landmask._mask == mfOAP._mask)
        assert np.all(landmask_05._mask == mfOAP_05._mask)

    def test_static_from_mask_ElevationMask(self):
        landmask = LandMask(golfcube["eta"][-1, :, :], elevation_threshold=0)
        mfem = LandMask.from_mask(self._ElevationMask)

        landmask_05 = LandMask(golfcube["eta"][-1, :, :], elevation_threshold=0.5)

        assert np.all(landmask._mask == mfem._mask)
        assert np.sum(landmask_05.integer_mask) < np.sum(landmask.integer_mask)

    def test_static_from_masks_ElevationMask(self):
        landmask = LandMask(golfcube["eta"][-1, :, :], elevation_threshold=0)
        mfem = LandMask.from_masks(self._ElevationMask)

        landmask_05 = LandMask(golfcube["eta"][-1, :, :], elevation_threshold=0.5)

        assert np.all(landmask._mask == mfem._mask)
        assert np.sum(landmask_05.integer_mask) < np.sum(landmask.integer_mask)

    def test_static_from_mask_TypeError(self):
        with pytest.raises(TypeError):
            LandMask.from_mask("invalid input")

    def test_static_from_mask_MPM(self):
        """Check that the two methods give similar results."""
        # a landmask with MPM
        mfem = LandMask.from_mask(
            self._ElevationMask, method="MPM", max_disk=12, contour_threshold=0.5
        )
        # a landmask with OAM
        landmask = LandMask(golfcube["eta"][-1, :, :], elevation_threshold=0.0)

        # some comparisons to check that things are similar (loose checks!)
        assert mfem.shape == self._ElevationMask.shape
        assert float(mfem._mask.sum()) == pytest.approx(
            float(landmask._mask.sum()), rel=1
        )
        assert float(mfem._mask.sum() / mfem._mask.size) == pytest.approx(
            float(landmask._mask.sum() / landmask._mask.size), abs=1
        )
        assert float(mfem._mask.sum()) > float(self._ElevationMask._mask.sum())

    def test_method_MPM(self):
        mfem = LandMask(
            golfcube["eta"][-1, :, :],
            elevation_threshold=0.0,
            contour_threshold=0.5,
            method="MPM",
            max_disk=12,
        )
        assert mfem.shape == self._ElevationMask.shape
        assert mfem._mask.sum() > self._ElevationMask._mask.sum()

    def test_invalid_method(self):
        with pytest.raises(TypeError):
            LandMask(
                golfcube["eta"][-1, :, :], elevation_threshold=0.0, method="invalid"
            )

    def test_static_from_array(self):
        """Test that instantiation works for an array."""
        _arr = np.ones((100, 200))
        _arr[50:55, :] = 0

        landmask = LandMask.from_array(_arr)
        # make assertions
        assert landmask.mask_type == "land"
        assert landmask._input_flag is None
        assert np.all(landmask._mask == _arr)

        _arr2 = np.random.uniform(size=(100, 200))
        _arr2_bool = _arr2.astype(bool)

        assert _arr2.dtype == float

        landmask2 = LandMask.from_array(_arr2)
        # make assertions
        assert landmask2.mask_type == "land"
        assert landmask2._input_flag is None
        assert np.all(landmask2._mask == _arr2_bool)


class TestWetMask:
    """Tests associated with the WetMask class."""

    # define an input mask for the mask instantiation pathway
    _ElevationMask = ElevationMask(golfcube["eta"][-1, :, :], elevation_threshold=0)

    def test_default_vals_array(self):
        """Test that instantiation works for an array."""
        # define the mask
        wetmask = WetMask(rcm8cube["eta"][-1, :, :], elevation_threshold=0)
        # make assertions
        assert wetmask._input_flag == "array"
        assert wetmask.mask_type == "wet"
        assert wetmask._mask.dtype == bool

    def test_default_vals_array_needs_elevation_threshold(self):
        """Test that instantiation works for an array."""
        # define the mask
        with pytest.raises(TypeError, match=r".* missing 1 .*"):
            _ = WetMask(rcm8cube["eta"][-1, :, :])

    @pytest.mark.xfail(
        raises=NotImplementedError, strict=True, reason="Have not implemented pathway."
    )
    def test_default_vals_cube(self):
        """Test that instantiation works for an array."""
        # define the mask
        wetmask = WetMask(rcm8cube, t=-1)
        # make assertions
        assert wetmask._input_flag == "cube"
        assert wetmask.mask_type == "wet"
        assert wetmask._mask.dtype == bool

    @pytest.mark.xfail(
        raises=NotImplementedError, strict=True, reason="Have not implemented pathway."
    )
    def test_default_vals_cubewithmeta(self):
        """Test that instantiation works for an array."""
        # define the mask
        wetmask = WetMask(golfcube, t=-1)
        # make assertions
        assert wetmask._input_flag == "cube"
        assert wetmask.mask_type == "wet"
        assert wetmask._mask.dtype == bool

    @pytest.mark.xfail(
        raises=NotImplementedError, strict=True, reason="Have not implemented pathway."
    )
    def test_default_vals_mask(self):
        """Test that instantiation works for an array."""
        # define the mask
        wetmask = WetMask(self._ElevationMask)
        # make assertions
        assert wetmask._input_flag == "mask"
        assert wetmask.mask_type == "wet"
        assert wetmask._mask.dtype == bool

    def test_angle_threshold(self):
        """
        Test that the angle threshold argument is passed along to the LandMask
        when instantiated.
        """
        # define the mask
        wetmask_default = WetMask(rcm8cube["eta"][-1, :, :], elevation_threshold=0)
        wetmask = WetMask(
            rcm8cube["eta"][-1, :, :], elevation_threshold=0, contour_threshold=45
        )
        # make assertions
        assert not np.all(wetmask_default == wetmask)
        assert np.sum(wetmask.integer_mask) < np.sum(wetmask_default.integer_mask)

    @pytest.mark.xfail(
        strict=True,
        reason=(
            "Breaking change to OAP leads to inlet not being classified as"
            " land. (v0.4.3)."
        ),
    )
    def test_submergedLand(self):
        """Check what happens when there is no land above water."""
        # define the mask
        wetmask = WetMask(golfcube["eta"][0, :, :], elevation_threshold=0)
        # assert - expect all False, because there is no landmass, so no wet area
        _whr_edge = np.where(wetmask._mask[:, 0])
        assert _whr_edge[0].size > 0  # if fails, no shoreline found!
        _row = int(_whr_edge[0][0])
        assert np.all(wetmask._mask[_row, :] == 1)
        assert np.all(wetmask._mask[_row + 1 :, :] == 0)

    def test_static_from_OAP(self):
        # create two with sea level = 0
        wetmask = WetMask(golfcube["eta"][-1, :, :], elevation_threshold=0)
        mfOAP = WetMask.from_Planform(_OAP_0)

        # create two with diff elevation threshold
        wetmask_05 = WetMask(golfcube["eta"][-1, :, :], elevation_threshold=0.5)
        mfOAP_05 = WetMask.from_Planform(_OAP_05)

        assert np.all(wetmask._mask == mfOAP._mask)
        assert np.all(wetmask_05._mask == mfOAP_05._mask)

    def test_static_from_MP(self):
        # this test covers the broken pathway from issue #93
        # make mask from a morphological planform
        mfMP = WetMask.from_Planform(_MPM_0)
        # assertions about it existing
        assert isinstance(mfMP, WetMask) is True

    def test_static_from_mask_ElevationMask(self):
        wetmask = WetMask(golfcube["eta"][-1, :, :], elevation_threshold=0)
        mfem = WetMask.from_mask(self._ElevationMask)

        wetmask_05 = WetMask(golfcube["eta"][-1, :, :], elevation_threshold=0.5)

        assert np.all(wetmask._mask == mfem._mask)
        assert np.sum(wetmask_05.integer_mask) < np.sum(wetmask.integer_mask)

    def test_static_from_masks_ElevationMask_LandMask(self):
        landmask = LandMask(golfcube["eta"][-1, :, :], elevation_threshold=0)
        mfem = WetMask.from_masks(self._ElevationMask, landmask)

        wetmask_0 = WetMask(golfcube["eta"][-1, :, :], elevation_threshold=0)

        assert np.all(wetmask_0._mask == mfem._mask)
        assert np.sum(wetmask_0.integer_mask) == np.sum(mfem.integer_mask)

    def test_static_from_array(self):
        """Test that instantiation works for an array."""
        # define the mask
        _arr = np.ones((100, 200))
        _arr[50:55, :] = 0

        wetmask = WetMask.from_array(_arr)
        # make assertions
        assert wetmask.mask_type == "wet"
        assert wetmask._input_flag is None
        assert np.all(wetmask._mask == _arr)

        _arr2 = np.random.uniform(size=(100, 200))
        _arr2_bool = _arr2.astype(bool)

        assert _arr2.dtype == float
        assert _arr2_bool.dtype == bool

        wetmask2 = WetMask.from_array(_arr2)
        # make assertions
        assert wetmask2.mask_type == "wet"
        assert wetmask2._input_flag is None
        assert np.all(wetmask2._mask == _arr2_bool)


class TestChannelMask:
    """Tests associated with the ChannelMask class."""

    # define an input mask for the mask instantiation pathway
    _ElevationMask = ElevationMask(golfcube["eta"][-1, :, :], elevation_threshold=0)

    def test_default_vals_array(self):
        """Test that instantiation works for an array."""
        # define the mask
        channelmask = ChannelMask(
            rcm8cube["eta"][-1, :, :],
            rcm8cube["velocity"][-1, :, :],
            elevation_threshold=0,
            flow_threshold=0.5,
        )
        # make assertions
        assert channelmask._input_flag == "array"
        assert channelmask.mask_type == "channel"
        assert channelmask._mask.dtype == bool

    def test_default_vals_array_needs_elevation_threshold(self):
        """Test that instantiation works for an array."""
        # define the mask
        with pytest.raises(TypeError, match=r".* missing 1 .*"):
            _ = ChannelMask(
                rcm8cube["eta"][-1, :, :],
                rcm8cube["velocity"][-1, :, :],
                flow_threshold=10,
            )

    def test_default_vals_array_needs_flow_threshold(self):
        """Test that instantiation works for an array."""
        # define the mask
        with pytest.raises(TypeError, match=r".* missing 1 .*"):
            _ = ChannelMask(
                rcm8cube["eta"][-1, :, :],
                rcm8cube["velocity"][-1, :, :],
                elevation_threshold=10,
            )

    @pytest.mark.xfail(
        raises=NotImplementedError, strict=True, reason="Have not implemented pathway."
    )
    def test_default_vals_cube(self):
        """Test that instantiation works for an array."""
        # define the mask
        channelmask = ChannelMask(rcm8cube, t=-1)
        # make assertions
        assert channelmask._input_flag == "cube"
        assert channelmask.mask_type == "channel"
        assert channelmask._mask.dtype == bool

    @pytest.mark.xfail(
        raises=NotImplementedError, strict=True, reason="Have not implemented pathway."
    )
    def test_default_vals_cubewithmeta(self):
        """Test that instantiation works for an array."""
        # define the mask
        channelmask = ChannelMask(golfcube, t=-1)
        # make assertions
        assert channelmask._input_flag == "cube"
        assert channelmask.mask_type == "channel"
        assert channelmask._mask.dtype == bool

    @pytest.mark.xfail(
        raises=NotImplementedError, strict=True, reason="Have not implemented pathway."
    )
    def test_default_vals_mask(self):
        """Test that instantiation works for an array."""
        # define the mask
        channelmask = ChannelMask(self._ElevationMask)
        # make assertions
        assert channelmask._input_flag == "mask"
        assert channelmask.mask_type == "channel"
        assert channelmask._mask.dtype == bool

    def test_angle_threshold(self):
        """
        Test that the angle threshold argument is passed along to the
        when instantiated.
        """
        # define the mask
        channelmask_default = ChannelMask(
            rcm8cube["eta"][-1, :, :],
            rcm8cube["velocity"][-1, :, :],
            elevation_threshold=0,
            flow_threshold=0.5,
        )
        channelmask = ChannelMask(
            rcm8cube["eta"][-1, :, :],
            rcm8cube["velocity"][-1, :, :],
            elevation_threshold=0,
            flow_threshold=0.5,
            contour_threshold=45,
        )
        # make assertions
        assert not np.all(channelmask_default == channelmask)
        assert np.sum(channelmask.integer_mask) < np.sum(
            channelmask_default.integer_mask
        )

    @pytest.mark.xfail(
        strict=True,
        reason=(
            "Breaking change to OAP leads to inlet not being classified as"
            " land. (v0.4.3)."
        ),
    )
    def test_submergedLand(self):
        """Check what happens when there is no land above water."""
        # define the mask
        channelmask = ChannelMask(
            rcm8cube["eta"][0, :, :],
            rcm8cube["velocity"][-1, :, :],
            elevation_threshold=0,
            flow_threshold=0.5,
        )
        # assert - expect all True values should be in center and first rows
        _cntr_frst = channelmask.mask[:3, rcm8cube.shape[2] // 2]
        assert np.all(_cntr_frst == 1)

    def test_static_from_OAP_not_implemented(self):
        with pytest.raises(
            NotImplementedError, match=r"`from_Planform` is not defined .*"
        ):
            _ = ChannelMask.from_Planform(_OAP_0)

    def test_static_from_OAP_and_FlowMask(self):
        """
        Test combinations to ensure that arguments passed to array instant
        match the arguments passed to the independ FlowMask and OAP
        objects.
        """
        channelmask_03 = ChannelMask(
            golfcube["eta"][-1, :, :],
            golfcube["velocity"][-1, :, :],
            elevation_threshold=0,
            flow_threshold=0.3,
        )
        flowmask_03 = FlowMask(golfcube["velocity"][-1, :, :], flow_threshold=0.3)
        mfOAP_03 = ChannelMask.from_Planform_and_FlowMask(_OAP_0, flowmask_03)

        channelmask_06 = ChannelMask(
            golfcube["eta"][-1, :, :],
            golfcube["velocity"][-1, :, :],
            elevation_threshold=0.5,
            flow_threshold=0.6,
        )
        flowmask_06 = FlowMask(golfcube["velocity"][-1, :, :], flow_threshold=0.6)
        mfOAP_06 = ChannelMask.from_Planform_and_FlowMask(_OAP_05, flowmask_06)

        assert np.all(channelmask_03._mask == mfOAP_03._mask)
        assert np.all(channelmask_06._mask == mfOAP_06._mask)
        assert not np.all(channelmask_03._mask == mfOAP_06._mask)
        assert not np.all(channelmask_03._mask == channelmask_06._mask)
        assert np.sum(mfOAP_06.integer_mask) < np.sum(mfOAP_03.integer_mask)

    def test_static_from_mask_ElevationMask_FlowMask(self):
        channelmask_comp = ChannelMask(
            golfcube["eta"][-1, :, :],
            golfcube["velocity"][-1, :, :],
            elevation_threshold=0,
            flow_threshold=0.3,
        )
        flowmask = FlowMask(golfcube["velocity"][-1, :, :], flow_threshold=0.3)
        mfem = ChannelMask.from_mask(self._ElevationMask, flowmask)
        mfem2 = ChannelMask.from_mask(flowmask, self._ElevationMask)

        assert np.all(channelmask_comp._mask == mfem2._mask)
        assert np.all(mfem._mask == mfem2._mask)

    def test_static_from_mask_LandMask_FlowMask(self):
        channelmask_comp = ChannelMask(
            golfcube["eta"][-1, :, :],
            golfcube["velocity"][-1, :, :],
            elevation_threshold=0,
            flow_threshold=0.3,
        )
        flowmask = FlowMask(golfcube["velocity"][-1, :, :], flow_threshold=0.3)
        landmask = LandMask.from_Planform(_OAP_0)

        mfem = ChannelMask.from_mask(landmask, flowmask)
        mfem2 = ChannelMask.from_mask(flowmask, landmask)

        assert np.all(channelmask_comp._mask == mfem2._mask)
        assert np.all(mfem._mask == mfem2._mask)
        assert isinstance(channelmask_comp._mask, xr.core.dataarray.DataArray)

    def test_static_from_masks_LandMask_FlowMask(self):
        channelmask_comp = ChannelMask(
            golfcube["eta"][-1, :, :],
            golfcube["velocity"][-1, :, :],
            elevation_threshold=0,
            flow_threshold=0.3,
        )
        flowmask = FlowMask(golfcube["velocity"][-1, :, :], flow_threshold=0.3)
        landmask = LandMask.from_Planform(_OAP_0)

        mfem = ChannelMask.from_masks(landmask, flowmask)
        mfem2 = ChannelMask.from_masks(flowmask, landmask)

        assert np.all(channelmask_comp._mask == mfem2._mask)
        assert np.all(mfem._mask == mfem2._mask)

    def test_static_from_mask_ValueError(self):
        with pytest.raises(ValueError):
            ChannelMask.from_mask("single arg")

    def test_static_from_mask_TypeError(self):
        wetmask = WetMask(golfcube["eta"][-1, :, :], elevation_threshold=0.0)
        landmask = LandMask.from_Planform(_OAP_0)
        with pytest.raises(TypeError):
            ChannelMask.from_mask(wetmask, landmask)

    def test_static_from_array(self):
        """Test that instantiation works for an array."""
        # define the mask
        _arr = np.ones((100, 200))
        _arr[50:55, :] = 0

        channelmask = ChannelMask.from_array(_arr)
        # make assertions
        assert channelmask.mask_type == "channel"
        assert channelmask._input_flag is None
        assert np.all(channelmask._mask == _arr)

        _arr2 = np.random.uniform(size=(100, 200))
        _arr2_bool = _arr2.astype(bool)

        assert _arr2.dtype == float

        channelmask2 = ChannelMask.from_array(_arr2)
        # make assertions
        assert channelmask2.mask_type == "channel"
        assert channelmask2._input_flag is None
        assert np.all(channelmask2._mask == _arr2_bool)


class TestEdgeMask:
    """Tests associated with the EdgeMask class."""

    # define an input mask for the mask instantiation pathway
    _ElevationMask = ElevationMask(golfcube["eta"][-1, :, :], elevation_threshold=0)

    def test_default_vals_array(self):
        """Test that instantiation works for an array."""
        # define the mask
        edgemask = EdgeMask(rcm8cube["eta"][-1, :, :], elevation_threshold=0)
        # make assertions
        assert edgemask._input_flag == "array"
        assert edgemask.mask_type == "edge"
        assert edgemask._mask.dtype == bool

    @pytest.mark.xfail(
        raises=NotImplementedError, strict=True, reason="Have not implemented pathway."
    )
    def test_default_vals_cube(self):
        """Test that instantiation works for an array."""
        # define the mask
        edgemask = EdgeMask(rcm8cube, t=-1)
        # make assertions
        assert edgemask._input_flag == "cube"
        assert edgemask.mask_type == "edge"
        assert edgemask._mask.dtype == bool

    @pytest.mark.xfail(
        raises=NotImplementedError, strict=True, reason="Have not implemented pathway."
    )
    def test_default_vals_cubewithmeta(self):
        """Test that instantiation works for an array."""
        # define the mask
        edgemask = EdgeMask(golfcube, t=-1)
        # make assertions
        assert edgemask._input_flag == "cube"
        assert edgemask.mask_type == "edge"
        assert edgemask._mask.dtype == bool

    @pytest.mark.xfail(
        raises=NotImplementedError, strict=True, reason="Have not implemented pathway."
    )
    def test_default_vals_mask(self):
        """Test that instantiation works for an array."""
        # define the mask
        edgemask = EdgeMask(self._ElevationMask)
        # make assertions
        assert edgemask._input_flag == "mask"
        assert edgemask.mask_type == "edge"
        assert edgemask._mask.dtype == bool

    def test_angle_threshold(self):
        """
        Test that the angle threshold argument is passed along to the
        when instantiated.
        """
        # define the mask
        edgemask_default = EdgeMask(rcm8cube["eta"][-1, :, :], elevation_threshold=0)
        edgemask = EdgeMask(
            rcm8cube["eta"][-1, :, :], elevation_threshold=0, contour_threshold=45
        )
        # make assertions
        assert not np.all(edgemask_default == edgemask)
        assert np.sum(edgemask.integer_mask) != np.sum(edgemask_default.integer_mask)

    @pytest.mark.xfail(
        strict=True,
        reason=(
            "Breaking change to OAP leads to inlet not being classified as"
            " land. (v0.4.3)."
        ),
    )
    def test_submergedLand(self):
        """Check what happens when there is no land above water."""
        # define the mask from rcm8
        edgemask = EdgeMask(rcm8cube["eta"][0, :, :], elevation_threshold=0)
        # assert - all zeros because no single pixel edges found
        assert np.any(edgemask._mask == 1)
        assert np.all(edgemask._mask == 0)
        assert np.median(edgemask.integer_mask) == 0

        # assert - expect some values to be true and most false
        edgemask = EdgeMask(golfcube["eta"][0, :, :], elevation_threshold=0)
        assert np.any(edgemask._mask == 1)
        assert np.any(edgemask._mask == 0)
        assert np.median(edgemask.integer_mask) == 0

    def test_static_from_OAP(self):
        edgemask_0 = EdgeMask(golfcube["eta"][-1, :, :], elevation_threshold=0)
        mfOAP_0 = EdgeMask.from_Planform(_OAP_0)

        edgemask_05 = EdgeMask(golfcube["eta"][-1, :, :], elevation_threshold=0.5)
        mfOAP_05 = EdgeMask.from_Planform(_OAP_05)

        assert np.all(edgemask_0._mask == mfOAP_0._mask)
        assert np.all(edgemask_05._mask == mfOAP_05._mask)
        assert not np.all(mfOAP_0._mask == mfOAP_05._mask)

    def test_static_from_OAP_and_WetMask(self):
        """
        Test combinations to ensure that arguments passed to array instant
        match the arguments passed to the independ FlowMask and OAP
        objects.
        """
        edgemask_0 = EdgeMask(golfcube["eta"][-1, :, :], elevation_threshold=0)
        wetmask_0 = WetMask(golfcube["eta"][-1, :, :], elevation_threshold=0)
        mfOAP_0 = EdgeMask.from_Planform_and_WetMask(_OAP_0, wetmask_0)

        assert np.all(edgemask_0._mask == mfOAP_0._mask)

    def test_static_from_mask_LandMask_WetMask(self):
        edgemask_comp = EdgeMask(golfcube["eta"][-1, :, :], elevation_threshold=0)
        landmask = LandMask.from_Planform(_OAP_0)
        wetmask = WetMask.from_Planform(_OAP_0)

        mfem = EdgeMask.from_mask(landmask, wetmask)
        mfem2 = EdgeMask.from_mask(wetmask, landmask)

        assert np.all(edgemask_comp._mask == mfem2._mask)
        assert np.all(mfem._mask == mfem2._mask)

    def test_static_from_array(self):
        """Test that instantiation works for an array."""
        # define the mask
        _arr = np.ones((100, 200))
        _arr[50:55, :] = 0

        edgemask = EdgeMask.from_array(_arr)
        # make assertions
        assert edgemask.mask_type == "edge"
        assert edgemask._input_flag is None
        assert np.all(edgemask._mask == _arr)

        _arr2 = np.random.uniform(size=(100, 200))
        _arr2_bool = _arr2.astype(bool)

        assert _arr2.dtype == float

        edgemask2 = EdgeMask.from_array(_arr2)
        # make assertions
        assert edgemask2.mask_type == "edge"
        assert edgemask2._input_flag is None
        assert np.all(edgemask2._mask == _arr2_bool)


class TestCenterlineMask:
    """Tests associated with the CenterlineMask class."""

    # define an input mask for the mask instantiation pathway
    _ElevationMask = ElevationMask(golfcube["eta"][-1, :, :], elevation_threshold=0)

    def test_default_vals_array(self):
        """Test that instantiation works for an array."""
        # define the mask
        centerlinemask = CenterlineMask(
            rcm8cube["eta"][-1, :, :],
            rcm8cube["velocity"][-1, :, :],
            elevation_threshold=0,
            flow_threshold=0.5,
        )
        # make assertions
        assert centerlinemask._input_flag == "array"
        assert centerlinemask.mask_type == "centerline"
        assert centerlinemask._mask.dtype == bool

    @pytest.mark.xfail(
        raises=NotImplementedError, strict=True, reason="Have not implemented pathway."
    )
    def test_default_vals_cube(self):
        """Test that instantiation works for an array."""
        # define the mask
        centerlinemask = CenterlineMask(rcm8cube, t=-1)
        # make assertions
        assert centerlinemask._input_flag == "cube"
        assert centerlinemask.mask_type == "centerline"
        assert centerlinemask._mask.dtype == bool

    @pytest.mark.xfail(
        raises=NotImplementedError, strict=True, reason="Have not implemented pathway."
    )
    def test_default_vals_cubewithmeta(self):
        """Test that instantiation works for an array."""
        # define the mask
        centerlinemask = CenterlineMask(golfcube, t=-1)
        # make assertions
        assert centerlinemask._input_flag == "cube"
        assert centerlinemask.mask_type == "centerline"
        assert centerlinemask._mask.dtype == bool

    @pytest.mark.xfail(
        raises=NotImplementedError, strict=True, reason="Have not implemented pathway."
    )
    def test_default_vals_mask(self):
        """Test that instantiation works for an array."""
        # define the mask
        centerlinemask = CenterlineMask(self._ElevationMask)
        # make assertions
        assert centerlinemask._input_flag == "mask"
        assert centerlinemask.mask_type == "centerline"
        assert centerlinemask._mask.dtype == bool

    def test_angle_threshold(self):
        """
        Test that the angle threshold argument is passed along to the
        when instantiated.
        """
        # define the mask
        centerlinemask_default = CenterlineMask(
            rcm8cube["eta"][-1, :, :],
            rcm8cube["velocity"][-1, :, :],
            elevation_threshold=0,
            flow_threshold=0.5,
        )
        centerlinemask = CenterlineMask(
            rcm8cube["eta"][-1, :, :],
            rcm8cube["velocity"][-1, :, :],
            elevation_threshold=0,
            flow_threshold=0.5,
            contour_threshold=45,
        )
        # make assertions
        assert not np.all(centerlinemask_default == centerlinemask)
        # should be fewer pixels since channels are shorter
        assert np.sum(centerlinemask.integer_mask) < np.sum(
            centerlinemask_default.integer_mask
        )

    @pytest.mark.xfail(
        strict=True,
        reason=(
            "Breaking change to OAP leads to inlet not being classified as"
            " land. (v0.4.3)."
        ),
    )
    def test_submergedLand(self):
        """Check what happens when there is no land above water."""
        # define the mask
        centerlinemask = CenterlineMask(
            rcm8cube["eta"][0, :, :],
            rcm8cube["velocity"][-1, :, :],
            elevation_threshold=0,
            flow_threshold=0.5,
        )
        # assert - expect some values to be true and most false
        assert np.any(centerlinemask._mask == 1)
        assert np.any(centerlinemask._mask == 0)
        assert np.median(centerlinemask.integer_mask) == 0

    def test_static_from_OAP_not_implemented(self):
        with pytest.raises(
            NotImplementedError, match=r"`from_Planform` is not defined .*"
        ):
            _ = CenterlineMask.from_Planform(_OAP_0)

    def test_static_from_OAP_and_FlowMask(self):
        """
        Test combinations to ensure that arguments passed to array instant
        match the arguments passed to the independ FlowMask and OAP
        objects.
        """
        centerlinemask_03 = CenterlineMask(
            golfcube["eta"][-1, :, :],
            golfcube["velocity"][-1, :, :],
            elevation_threshold=0,
            flow_threshold=0.3,
        )
        flowmask_03 = FlowMask(golfcube["velocity"][-1, :, :], flow_threshold=0.3)
        mfOAP_03 = CenterlineMask.from_Planform_and_FlowMask(_OAP_0, flowmask_03)

        centerlinemask_06 = CenterlineMask(
            golfcube["eta"][-1, :, :],
            golfcube["velocity"][-1, :, :],
            elevation_threshold=0.5,
            flow_threshold=0.6,
        )
        flowmask_06 = FlowMask(golfcube["velocity"][-1, :, :], flow_threshold=0.6)
        mfOAP_06 = CenterlineMask.from_Planform_and_FlowMask(_OAP_05, flowmask_06)

        assert np.all(centerlinemask_03._mask == mfOAP_03._mask)
        assert np.all(centerlinemask_06._mask == mfOAP_06._mask)
        assert not np.all(centerlinemask_03._mask == mfOAP_06._mask)
        assert not np.all(centerlinemask_03._mask == centerlinemask_06._mask)
        assert np.sum(mfOAP_06.integer_mask) < np.sum(mfOAP_03.integer_mask)

    def test_static_from_mask_ChannelMask(self):
        centerlinemask_comp = CenterlineMask(
            golfcube["eta"][-1, :, :],
            golfcube["velocity"][-1, :, :],
            elevation_threshold=0,
            flow_threshold=0.3,
        )
        channelmask = ChannelMask(
            golfcube["eta"][-1, :, :],
            golfcube["velocity"][-1, :, :],
            elevation_threshold=0,
            flow_threshold=0.3,
        )
        mfem = CenterlineMask.from_mask(channelmask)

        assert np.all(centerlinemask_comp._mask == mfem._mask)

    def test_static_from_mask_ElevationMask_FlowMask(self):
        centerlinemask_comp = CenterlineMask(
            golfcube["eta"][-1, :, :],
            golfcube["velocity"][-1, :, :],
            elevation_threshold=0,
            flow_threshold=0.3,
        )
        flowmask = FlowMask(golfcube["velocity"][-1, :, :], flow_threshold=0.3)
        mfem = CenterlineMask.from_mask(self._ElevationMask, flowmask)
        mfem2 = CenterlineMask.from_mask(flowmask, self._ElevationMask)

        assert np.all(centerlinemask_comp._mask == mfem2._mask)
        assert np.all(mfem._mask == mfem2._mask)

    def test_static_from_mask_LandMask_FlowMask(self):
        centerlinemask_comp = CenterlineMask(
            golfcube["eta"][-1, :, :],
            golfcube["velocity"][-1, :, :],
            elevation_threshold=0,
            flow_threshold=0.3,
        )
        flowmask = FlowMask(golfcube["velocity"][-1, :, :], flow_threshold=0.3)
        landmask = LandMask.from_Planform(_OAP_0)

        mfem = CenterlineMask.from_mask(landmask, flowmask)
        mfem2 = CenterlineMask.from_mask(flowmask, landmask)

        assert np.all(centerlinemask_comp._mask == mfem2._mask)
        assert np.all(mfem._mask == mfem2._mask)

    def test_static_from_array(self):
        """Test that instantiation works for an array."""
        # define the mask
        _arr = np.ones((100, 200))
        _arr[50:55, :] = 0

        centerlinemask = CenterlineMask.from_array(_arr)
        # make assertions
        assert centerlinemask.mask_type == "centerline"
        assert centerlinemask._input_flag is None
        assert np.all(centerlinemask._mask == _arr)

        _arr2 = np.random.uniform(size=(100, 200))
        _arr2_bool = _arr2.astype(bool)

        assert _arr2.dtype == float

        centerlinemask2 = CenterlineMask.from_array(_arr2)
        # make assertions
        assert centerlinemask2.mask_type == "centerline"
        assert centerlinemask2._input_flag is None
        assert np.all(centerlinemask2._mask == _arr2_bool)

    @pytest.mark.xfail(raises=ImportError, reason="rivamap is not installed.")
    def test_rivamap_array(self):
        """Test rivamap extraction of centerlines."""
        # define the mask
        centerlinemask = CenterlineMask(
            golfcube["velocity"][-1, :, :],
            golfcube["eta"][-1, :, :],
            elevation_threshold=0,
            flow_threshold=0.3,
            method="rivamap",
        )

        # do assertion
        assert centerlinemask.minScale == 1.5
        assert centerlinemask.nrScales == 12
        assert centerlinemask.nms_threshold == 0.1
        assert hasattr(centerlinemask, "psi") is True
        assert hasattr(centerlinemask, "nms") is True
        assert hasattr(centerlinemask, "mask") is True

    @pytest.mark.xfail(raises=ImportError, reason="rivamap is not installed.")
    def test_rivamap_from_mask(self):
        """Test rivamap extraction of centerlines."""
        # define the mask
        channelmask = ChannelMask(
            golfcube["velocity"][-1, :, :],
            golfcube["eta"][-1, :, :],
            elevation_threshold=0,
            flow_threshold=0.3,
        )
        centerlinemask = CenterlineMask.from_mask(channelmask, method="rivamap")

        # do assertion
        assert centerlinemask.minScale == 1.5
        assert centerlinemask.nrScales == 12
        assert centerlinemask.nms_threshold == 0.1
        assert hasattr(centerlinemask, "psi") is True
        assert hasattr(centerlinemask, "nms") is True
        assert hasattr(centerlinemask, "mask") is True


class TestGeometricMask:
    """Tests associated with the GeometricMask class."""

    def test_initialize_gm(self):
        """Test initialization."""
        arr = np.random.uniform(size=(100, 200))
        gmsk = GeometricMask(arr)

        # assert the mask is empty
        assert gmsk.mask_type == "geometric"
        assert np.shape(gmsk._mask) == np.shape(arr)
        assert np.all(gmsk._mask == 1)
        assert gmsk._xc == 0
        assert gmsk._yc == 100
        assert gmsk.xc == gmsk._xc
        assert gmsk.yc == gmsk._yc

    def test_initialize_gm_tuple(self):
        """Test initialization."""
        gmsk = GeometricMask((100, 200))

        # assert the mask is empty
        assert gmsk.mask_type == "geometric"
        assert np.shape(gmsk._mask) == (100, 200)
        assert np.all(gmsk._mask == 1)
        assert gmsk._xc == 0
        assert gmsk._yc == 100
        assert gmsk.xc == gmsk._xc
        assert gmsk.yc == gmsk._yc

    def test_circular_default(self):
        """Test circular mask with defaults, small case."""
        arr = np.zeros((5, 5))
        gmsk = GeometricMask(arr)
        gmsk.circular(1)
        assert gmsk._mask[0, 2] == 0

        gmsk2 = GeometricMask(arr, circular={"rad1": 1})
        assert np.all(gmsk2.mask == gmsk.mask)

    def test_circular_2radii(self):
        """Test circular mask with 2 radii, small case."""
        arr = np.zeros((7, 7))
        gmsk = GeometricMask(arr)
        gmsk.circular(1, 2)
        assert gmsk._mask[0, 3] == 0
        assert np.all(gmsk._mask[:, -1] == 0)
        assert np.all(gmsk._mask[:, 0] == 0)
        assert np.all(gmsk._mask[-1, :] == 0)

        gmsk2 = GeometricMask(arr, circular={"rad1": 1, "rad2": 2})
        assert np.all(gmsk2.mask == gmsk.mask)

    def test_circular_custom_origin(self):
        """Test circular mask with defined origin."""
        arr = np.zeros((7, 7))
        gmsk = GeometricMask(arr)
        gmsk.circular(1, 2, origin=(3, 3))
        assert gmsk._mask[3, 3] == 0
        assert np.all(
            gmsk._mask.values
            == np.array(
                [
                    [
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0],
                        [0.0, 1.0, 1.0, 0.0, 1.0, 1.0, 0.0],
                        [0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    ]
                ]
            )
        )
        # check that the Mask origin is different
        #  from the one used in method (3, 3)
        assert gmsk.xc == 0
        assert gmsk.yc == 3

        gmsk2 = GeometricMask(arr, circular={"rad1": 1, "rad2": 2, "origin": (3, 3)})
        assert np.all(gmsk2.mask == gmsk.mask)

    def test_strike_one(self):
        """Test strike masking with one value."""
        arr = np.zeros((7, 7))
        gmsk = GeometricMask(arr)
        gmsk.strike(2)
        assert np.all(gmsk._mask[:2, :] == 0)
        assert np.all(gmsk._mask[2:, :] == 1)

        gmsk2 = GeometricMask(arr, strike={"ind1": 2})
        assert np.all(gmsk2.mask == gmsk.mask)

    def test_strike_two(self):
        """Test strike masking with two values."""
        arr = np.zeros((7, 7))
        gmsk = GeometricMask(arr)
        gmsk.strike(2, 4)
        assert np.all(gmsk._mask[:2, :] == 0)
        assert np.all(gmsk._mask[2:4, :] == 1)
        assert np.all(gmsk._mask[4:, :] == 0)

        gmsk2 = GeometricMask(arr, strike={"ind1": 2, "ind2": 4})
        assert np.all(gmsk2.mask == gmsk.mask)

    def test_dip_one(self):
        """Test dip masking with one value."""
        arr = np.zeros((7, 7))
        gmsk = GeometricMask(arr)
        gmsk.dip(5)
        assert np.all(gmsk._mask[:, 1:-1] == 1)
        assert np.all(gmsk._mask[:, 0] == 0)
        assert np.all(gmsk._mask[:, -1] == 0)

        gmsk2 = GeometricMask(arr, dip={"ind1": 5})
        assert np.all(gmsk2.mask == gmsk.mask)

    def test_dip_two(self):
        """Test dip masking with two values."""
        arr = np.zeros((7, 7))
        gmsk = GeometricMask(arr)
        gmsk.dip(2, 4)
        assert np.all(gmsk._mask[:, 0:2] == 0)
        assert np.all(gmsk._mask[:, 2:4] == 1)
        assert np.all(gmsk._mask[:, 4:] == 0)

        gmsk2 = GeometricMask(arr, dip={"ind1": 2, "ind2": 4})
        assert np.all(gmsk2.mask == gmsk.mask)

    def test_angular_half(self):
        """Test angular mask over half of domain"""
        arr = np.zeros((100, 200))
        gmsk = GeometricMask(arr)
        theta1 = 0
        theta2 = np.pi / 2
        gmsk.angular(theta1, theta2)
        # assert 1s half
        assert np.all(gmsk._mask[:, :101] == 1)
        assert np.all(gmsk._mask[:, 101:] == 0)

        gmsk2 = GeometricMask(arr, angular={"theta1": theta1, "theta2": theta2})
        assert np.all(gmsk2.mask == gmsk.mask)

    def test_angular_bad_dims(self):
        """raise error."""
        arr = np.zeros((5, 5))
        gmsk = GeometricMask(arr)
        with pytest.raises(ValueError):
            gmsk.angular(0, np.pi / 2)


class TestDepositMask:
    """Tests associated with the CenterlineMask class."""

    def test_default_tolerance_no_background(self):
        """Test that instantiation works for an array."""
        # define the mask
        depositmask = DepositMask(golfcube["eta"][-1, :, :])

        compval = 0 + depositmask._elevation_tolerance

        # make assertions
        assert depositmask._elevation_tolerance == 0.1  # check default
        assert (
            depositmask._mask.data.sum()
            == (golfcube["eta"][-1, :, :] > compval).data.sum()
        )

        assert depositmask._input_flag == "array"
        assert depositmask.mask_type == "deposit"
        assert depositmask._mask.dtype == bool

    def test_default_tolerance_background_array(self):
        """Test that instantiation works for an array."""
        # define the mask
        depositmask = DepositMask(
            golfcube["eta"][-1, :, :], background_value=golfcube["eta"][0, :, :]
        )

        with pytest.raises(TypeError):
            # fails without specifying key name
            _ = DepositMask(golfcube["eta"][-1, :, :], golfcube["eta"][0, :, :])

        # make assertions
        assert depositmask._elevation_tolerance == 0.1  # check default

        assert depositmask._input_flag == "array"
        assert depositmask.mask_type == "deposit"
        assert depositmask._mask.dtype == bool

    def test_default_tolerance_background_float(self):
        """Test that instantiation works for an array."""
        # define the mask
        depositmask = DepositMask(golfcube["eta"][-1, :, :], background_value=-1)

        with pytest.raises(TypeError):
            # fails without specifying key name
            _ = DepositMask(golfcube["eta"][-1, :, :], -1)

        compval = -1 + depositmask._elevation_tolerance

        assert (
            depositmask._mask.data.sum()
            == (golfcube["eta"][-1, :, :] > compval).data.sum()
        )
        assert depositmask._elevation_tolerance == 0.1  # check default

        assert depositmask._input_flag == "array"
        assert depositmask.mask_type == "deposit"
        assert depositmask._mask.dtype == bool

    def test_elevation_tolerance_background_array(self):
        defaultdepositmask = DepositMask(
            golfcube["eta"][-1, :, :], background_value=golfcube["eta"][0, :, :]
        )

        depositmask = DepositMask(
            golfcube["eta"][-1, :, :],
            background_value=golfcube["eta"][0, :, :],
            elevation_tolerance=1,
        )

        assert depositmask._input_flag == "array"
        assert depositmask.mask_type == "deposit"
        assert depositmask._mask.dtype == bool
        assert depositmask._elevation_tolerance == 1  # check NOT default
        assert defaultdepositmask._mask.sum() > depositmask._mask.sum()

    @pytest.mark.xfail(
        raises=NotImplementedError, strict=True, reason="Have not implemented pathway."
    )
    def test_default_vals_cube(self):
        """Test that instantiation works for an array."""
        # define the mask
        depositmask = DepositMask(rcm8cube, t=-1)
        # make assertions
        assert depositmask._input_flag == "cube"
        assert depositmask.mask_type == "deposit"
        assert depositmask._mask.dtype == bool

    @pytest.mark.xfail(
        raises=NotImplementedError, strict=True, reason="Have not implemented pathway."
    )
    def test_default_vals_cubewithmeta(self):
        """Test that instantiation works for an array."""
        # define the mask
        depositmask = DepositMask(golfcube, t=-1)
        # make assertions
        assert depositmask._input_flag == "cube"
        assert depositmask.mask_type == "deposit"
        assert depositmask._mask.dtype == bool
