import unittest.mock as mock

import matplotlib.pyplot as plt
import numpy as np
import pytest
import xarray as xr

from sandplover.cube import DataCube
from sandplover.cube import StratigraphyCube
from sandplover.mask import ChannelMask
from sandplover.mask import ElevationMask
from sandplover.mask import LandMask
from sandplover.mask import ShorelineMask
from sandplover.plan import MorphologicalPlanform
from sandplover.plan import OpeningAnglePlanform
from sandplover.plan import Planform
from sandplover.plan import _get_channel_starts_and_ends
from sandplover.plan import compute_channel_depth
from sandplover.plan import compute_channel_width
from sandplover.plan import compute_land_area
from sandplover.plan import compute_shoreline_distance
from sandplover.plan import compute_shoreline_length
from sandplover.plan import compute_shoreline_roughness
from sandplover.plan import compute_surface_deposit_age
from sandplover.plan import compute_surface_deposit_time
from sandplover.plan import shaw_opening_angle_method
from sandplover.sample_data.sample_data import _get_golf_path
from sandplover.sample_data.sample_data import _get_rcm8_path
from sandplover.section import CircularSection

# a simple custom layout
simple_land = np.zeros((10, 10))
simple_shore = np.zeros((10, 10))
simple_land[:4, :] = 1
simple_land[4, 2:7] = 1
simple_shore_array = np.array(
    [[3, 3, 4, 4, 4, 4, 4, 3, 3, 3], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]]
).T
simple_shore[simple_shore_array[:, 0], simple_shore_array[:, 1]] = 1

# a perfect half-circle layout
hcirc = np.zeros((500, 1000), dtype=bool)
hcirc_dx = 10
x, y = np.meshgrid(
    np.linspace(0, hcirc_dx * hcirc.shape[1], num=hcirc.shape[1]),
    np.linspace(0, hcirc_dx * hcirc.shape[0], num=hcirc.shape[0]),
)
center = (0, 5000)

dists = np.sqrt((y - center[0]) ** 2 + (x - center[1]) ** 2)
dists_flat = dists.flatten()
in_idx = np.where(dists_flat <= 3000)[0]
hcirc.flat[in_idx] = True

# golf
golf_path = _get_golf_path()


class TestPlanform:
    def test_Planform_without_cube(self):
        plfrm = Planform(idx=-1)
        assert plfrm.name is None
        assert plfrm._input_z is None
        assert plfrm._input_t is None
        assert plfrm._input_idx is -1
        assert plfrm.shape is None
        assert plfrm.cube is None
        assert plfrm._dim0_idx is None
        assert plfrm.variables is None
        with pytest.raises(AttributeError, match=r"No cube connected.*."):
            plfrm["velocity"]

    def test_Planform_bad_cube(self):
        badcube = ["some", "list"]
        with pytest.raises(TypeError, match=r"Expected type is *."):
            _ = Planform(badcube, idx=12)

    def test_Planform_idx(self):
        golfcube = DataCube(golf_path)
        plnfrm = Planform(golfcube, idx=40)
        assert plnfrm.name == "data"
        assert plnfrm.idx == 40
        assert plnfrm.cube == golfcube
        assert len(plnfrm.variables) > 0

    def test_Planform_z_t_thesame(self):
        golfcube = DataCube(golf_path)
        plnfrm = Planform(golfcube, t=3e6)
        plnfrm2 = Planform(golfcube, z=3e6)
        assert plnfrm.name == "data"
        assert plnfrm.idx == 6
        assert plnfrm.idx == plnfrm2.idx
        assert plnfrm.cube == golfcube
        assert len(plnfrm.variables) > 0

    def test_Planform_idx_z_t_mutual_exclusive(self):
        golfcube = DataCube(golf_path)
        with pytest.raises(TypeError, match=r"Cannot .* `z` and `idx`."):
            _ = Planform(golfcube, z=5e6, idx=30)
        with pytest.raises(TypeError, match=r"Cannot .* `t` and `idx`."):
            _ = Planform(golfcube, t=3e6, idx=30)
        with pytest.raises(TypeError, match=r"Cannot .* `z` and `t`."):
            _ = Planform(golfcube, t=3e6, z=5e6)

    def test_Planform_slicing(self):
        # make the planforms
        golfcube = DataCube(golf_path)
        golfcubestrat = DataCube(golf_path)
        golfcubestrat.stratigraphy_from("eta", dz=0.1)
        golfstrat = StratigraphyCube.from_DataCube(golfcube, dz=0.1)
        plnfrm1 = Planform(golfcube, idx=-1)
        plnfrm2 = Planform(golfcubestrat, z=-2)
        plnfrm3 = Planform(golfstrat, z=-6)  # note should be deep enough for no nans
        assert np.all(plnfrm1["eta"] == golfcube["eta"][-1, :, :])
        assert np.all(plnfrm2["time"] == golfcubestrat["time"][plnfrm2.idx, :, :])
        assert np.all(plnfrm3["time"] == golfstrat["time"][plnfrm3.idx, :, :])

    def test_Planform_private_show(self):
        """Doesn't actually check the plots,
        just checks that the function runs.
        """
        # make the planforms
        golfcube = DataCube(golf_path)
        plnfrm = Planform(golfcube, idx=-1)
        _field = plnfrm["eta"]
        _varinfo = golfcube.varset["eta"]
        # with axis
        fig, ax = plt.subplots()
        plnfrm._show(_field, _varinfo, ax=ax)
        plt.close()
        # without axis
        fig, ax = plt.subplots()
        plnfrm._show(_field, _varinfo)
        plt.close()
        # with colorbar_label
        fig, ax = plt.subplots(1, 2)
        plnfrm._show(_field, _varinfo, ax=ax[0], colorbar_label="test")
        plnfrm._show(_field, _varinfo, ax=ax[1], colorbar_label=True)
        plt.close()
        # with ticks
        fig, ax = plt.subplots()
        plnfrm._show(_field, _varinfo, ax=ax, ticks=True)
        plt.close()
        # with title
        fig, ax = plt.subplots()
        plnfrm._show(_field, _varinfo, ax=ax, title="some title")
        plt.close()

    def test_Planform_public_show(self):
        golfcube = DataCube(golf_path)
        plnfrm = Planform(golfcube, idx=-1)
        plnfrm._show = mock.MagicMock()
        # test with ax
        fig, ax = plt.subplots()
        plnfrm.show("time", ax=ax)
        plt.close()
        assert plnfrm._show.call_count == 1
        # check that all bogus args are passed to _show
        plnfrm.show("time", ax=100, title=101, ticks=102, colorbar_label=103)
        assert plnfrm._show.call_count == 2
        # hacky method to pull out the keyword calls only
        kw_calls = plnfrm._show.mock_calls[1][2:][0]
        assert kw_calls["ax"] == 100
        assert kw_calls["title"] == 101
        assert kw_calls["ticks"] == 102
        assert kw_calls["colorbar_label"] == 103


class TestOpeningAnglePlanform:
    simple_ocean = 1 - simple_land

    golf_path = _get_golf_path()
    golfcube = DataCube(golf_path)

    def test_allblack(self):
        with pytest.raises(ValueError, match=r"No pixels identified in below_mask.*"):
            _ = shaw_opening_angle_method(np.zeros((10, 10), dtype=int))

    def test_defaults_array_int(self):
        oap = OpeningAnglePlanform(self.simple_ocean.astype(int))
        assert isinstance(oap.opening_angles, xr.core.dataarray.DataArray)
        assert oap.opening_angles.shape == self.simple_ocean.shape
        assert oap.below_mask.dtype == bool

    def test_defaults_array_bool(self):
        oap = OpeningAnglePlanform(self.simple_ocean.astype(bool))
        assert isinstance(oap.opening_angles, xr.core.dataarray.DataArray)
        assert oap.opening_angles.shape == self.simple_ocean.shape
        assert oap.below_mask.dtype == bool

    def test_defaults_array_float_error(self):
        with pytest.raises(TypeError):
            _ = OpeningAnglePlanform(self.simple_ocean.astype(float))

    @pytest.mark.xfail(
        raises=NotImplementedError, strict=True, reason="Have not implemented pathway."
    )
    def test_defaults_cube(self):
        _ = OpeningAnglePlanform(self.golfcube, t=-1)

    def test_defaults_static_from_elevation_data(self):
        oap = OpeningAnglePlanform.from_elevation_data(
            self.golfcube["eta"][-1, :, :], elevation_threshold=0
        )
        assert isinstance(oap.opening_angles, xr.core.dataarray.DataArray)
        assert oap.opening_angles.shape == self.golfcube.shape[1:]
        assert oap.below_mask.dtype == bool

    def test_defaults_static_from_elevation_data_needs_threshold(self):
        with pytest.raises(TypeError):
            _ = OpeningAnglePlanform.from_elevation_data(self.golfcube["eta"][-1, :, :])

    def test_defaults_static_from_ElevationMask(self):
        _em = ElevationMask(self.golfcube["eta"][-1, :, :], elevation_threshold=0)

        oap = OpeningAnglePlanform.from_ElevationMask(_em)

        assert isinstance(oap.opening_angles, xr.core.dataarray.DataArray)
        assert oap.opening_angles.shape == _em.shape
        assert oap.below_mask.dtype == bool

    def test_defaults_static_from_elevation_data_kwargs_passed(self):
        oap_default = OpeningAnglePlanform.from_elevation_data(
            self.golfcube["eta"][-1, :, :], elevation_threshold=0
        )

        oap_diff = OpeningAnglePlanform.from_elevation_data(
            self.golfcube["eta"][-1, :, :], elevation_threshold=0, numviews=10
        )

        assert np.all(oap_diff.composite_array >= oap_default.composite_array)

    def test_notcube_error(self):
        with pytest.raises(TypeError):
            OpeningAnglePlanform(self.golfcube["eta"][-1, :, :].data)

    def test_show_and_errors(self):
        oap = OpeningAnglePlanform.from_elevation_data(
            self.golfcube["eta"][-1, :, :], elevation_threshold=0
        )
        oap._show = mock.MagicMock()  # mock the private
        # test with defaults
        oap.show()
        assert oap._show.call_count == 1
        _field_called = oap._show.mock_calls[0][1][0]
        _varinfo_called = oap._show.mock_calls[0][1][1]
        assert _field_called is oap.opening_angles  # default
        assert _varinfo_called is oap._default_varinfo  # default
        # test that different field uses different varinfo
        oap.show("below_mask")
        assert oap._show.call_count == 2
        _field_called = oap._show.mock_calls[1][1][0]
        _varinfo_called = oap._show.mock_calls[1][1][1]
        assert _field_called is oap._below_mask
        assert _varinfo_called is oap._below_mask_varinfo
        # test that a nonexisting field throws error
        with pytest.raises(AttributeError, match=r".* no attribute 'nonexisting'"):
            oap.show("nonexisting")
        # test that a existing field, nonexisting varinfo uses default
        oap.existing = None  # just that it exists
        oap.show("existing")
        assert oap._show.call_count == 3
        _field_called = oap._show.mock_calls[2][1][0]
        _varinfo_called = oap._show.mock_calls[2][1][1]
        assert _field_called is oap.existing  # default
        assert _varinfo_called is oap._default_varinfo  # default
        # test that bad value raises error
        with pytest.raises(TypeError, match=r"Bad value .*"):
            oap.show(1000)


class TestMorphologicalPlanform:
    simple_land = simple_land
    golf_path = _get_golf_path()
    golfcube = DataCube(golf_path)

    def test_defaults_array_int(self):
        mpm = MorphologicalPlanform(self.simple_land.astype(int), 2)
        assert isinstance(mpm._mean_image, xr.core.dataarray.DataArray)
        assert isinstance(mpm._all_images, np.ndarray)
        assert mpm._mean_image.shape == self.simple_land.shape
        assert len(mpm._all_images.shape) == 3
        assert mpm._all_images.shape[0] == 3

    def test_defaults_array_bool(self):
        mpm = MorphologicalPlanform(self.simple_land.astype(bool), 2)
        assert isinstance(mpm._mean_image, xr.core.dataarray.DataArray)
        assert isinstance(mpm._all_images, np.ndarray)
        assert mpm._mean_image.shape == self.simple_land.shape
        assert len(mpm._all_images.shape) == 3
        assert mpm._all_images.shape[0] == 3

    def test_defaults_array_float(self):
        mpm = MorphologicalPlanform(self.simple_land.astype(float), 2.0)
        assert isinstance(mpm._mean_image, xr.core.dataarray.DataArray)
        assert isinstance(mpm._all_images, np.ndarray)
        assert mpm._mean_image.shape == self.simple_land.shape
        assert len(mpm._all_images.shape) == 3
        assert mpm._all_images.shape[0] == 3

    def test_invalid_disk_arg(self):
        with pytest.raises(TypeError):
            MorphologicalPlanform(self.simple_land.astype(int), "bad")

    def test_defaults_static_from_elevation_data(self):
        mpm = MorphologicalPlanform.from_elevation_data(
            self.golfcube["eta"][-1, :, :], elevation_threshold=0, max_disk=2
        )
        assert mpm.planform_type == "morphological method"
        assert mpm._mean_image.shape == (100, 200)
        assert mpm._all_images.shape == (3, 100, 200)
        assert isinstance(mpm._mean_image, xr.core.dataarray.DataArray)
        assert isinstance(mpm._all_images, np.ndarray)

    def test_static_from_mask(self):
        mpm = MorphologicalPlanform.from_mask(self.simple_land, 2)
        assert isinstance(mpm._mean_image, xr.core.dataarray.DataArray)
        assert isinstance(mpm._all_images, np.ndarray)
        assert mpm._mean_image.shape == self.simple_land.shape
        assert len(mpm._all_images.shape) == 3
        assert mpm._all_images.shape[0] == 3

    def test_static_from_mask_negative_disk(self):
        mpm = MorphologicalPlanform.from_mask(self.simple_land, -2)
        assert isinstance(mpm.mean_image, xr.core.dataarray.DataArray)
        assert isinstance(mpm.all_images, np.ndarray)
        assert mpm.mean_image.shape == self.simple_land.shape
        assert len(mpm.all_images.shape) == 3
        assert mpm.all_images.shape[0] == 2
        assert np.all(mpm.composite_array == mpm.mean_image)

    def test_empty_error(self):
        with pytest.raises(ValueError):
            MorphologicalPlanform()

    def test_bad_type(self):
        with pytest.raises(TypeError):
            MorphologicalPlanform("invalid string")


class TestShawOpeningAngleMethod:
    simple_ocean = 1 - simple_land  # ocean is at bottom of image

    def test_allblack(self):
        with pytest.raises(ValueError, match=r"No pixels identified in below_mask.*"):
            _ = shaw_opening_angle_method(np.zeros((10, 10), dtype=int))

    def test_simple_case_defaults(self):
        oam = shaw_opening_angle_method(self.simple_ocean)
        assert np.all(oam <= 180)
        assert np.all(oam >= 0)
        assert np.all(oam[-1, :] == 180)

    def test_simple_case_preprocess(self):
        # make a custom mask with a lake
        _custom_ocean = np.copy(self.simple_ocean)
        _custom_ocean[1:3, 1:3] = 1  # add a lake

        # the lake should be removed (default)
        oam1 = shaw_opening_angle_method(_custom_ocean, preprocess=True)
        assert np.all(oam1[1:3, 1:3] == 0)

        # the lake should persist
        oam2 = shaw_opening_angle_method(_custom_ocean, preprocess=False)
        assert np.all(oam2[1:3, 1:3] != 0)


class TestDeltaArea:
    golf_path = _get_golf_path()
    golfcube = DataCube(golf_path)

    lm = LandMask(
        golfcube["eta"][-1, :, :],
        elevation_threshold=golfcube.meta["H_SL"][-1],
        elevation_offset=-0.5,
    )
    lm.trim_mask(length=golfcube.meta["L0"].data + 1)

    def test_simple_case(self):
        land_area = compute_land_area(simple_land)
        assert land_area == 45

    def test_golf_case(self):
        land_area = compute_land_area(self.lm)
        assert land_area / 1e6 == pytest.approx(14.5, abs=1)

    def test_golf_array_case(self):
        # calculation without dx
        lm_array = np.copy(self.lm._mask.data)
        land_area = compute_land_area(lm_array)
        assert land_area == pytest.approx(14.5 * 1e6 / 50 / 50, abs=200)

    def test_half_circle(self):
        # circ radius is 3000
        land_area = compute_land_area(hcirc)  # does not have dimensions
        land_area = land_area * hcirc_dx * hcirc_dx / 1e6
        assert land_area == pytest.approx(0.5 * np.pi * (3000**2) / 1e6, abs=1)


class TestShorelineRoughness:
    rcm8_path = _get_rcm8_path()
    with pytest.warns(UserWarning):
        rcm8 = DataCube(rcm8_path)

    em = ElevationMask(rcm8["eta"][-1, :, :], elevation_threshold=0)
    em.trim_mask(value=1, length=1)
    OAP = OpeningAnglePlanform(~(em.mask))
    lm = LandMask.from_Planform(OAP)
    sm = ShorelineMask.from_Planform(OAP)
    em0 = ElevationMask(rcm8["eta"][-1, :, :], elevation_threshold=0)
    em0.trim_mask(value=1, length=1)
    OAP0 = OpeningAnglePlanform(~(em0.mask))
    lm0 = LandMask.from_Planform(OAP0)
    sm0 = ShorelineMask.from_Planform(OAP0)

    # lm = LandMask(rcm8["eta"][-1, :, :], elevation_threshold=0)
    # sm = ShorelineMask(rcm8["eta"][-1, :, :], elevation_threshold=0)
    # lm0 = LandMask(rcm8["eta"][0, :, :], elevation_threshold=0)
    # sm0 = ShorelineMask(rcm8["eta"][0, :, :], elevation_threshold=0)

    # _trim_length = 4
    # lm.trim_mask(length=_trim_length)
    # sm.trim_mask(length=_trim_length)
    # lm0.trim_mask(length=_trim_length)
    # sm0.trim_mask(length=_trim_length)

    rcm8_expected = 4.476379600936939

    def test_simple_case(self):
        simple_rgh = compute_shoreline_roughness(simple_shore, simple_land)
        exp_area = 45
        exp_len = (7 * 1) + (2 * 1.41421356)
        exp_rgh = exp_len / np.sqrt(exp_area)
        assert simple_rgh == pytest.approx(exp_rgh)

    def test_rcm8_defaults(self):
        # test it with default options
        rgh_0 = compute_shoreline_roughness(self.sm, self.lm)
        # assert rgh_0 == pytest.approx(self.rcm8_expected, abs=0.1)
        assert rgh_0 > 0

    def test_rcm8_ignore_return_line(self):
        # test that it ignores return_line arg
        rgh_1 = compute_shoreline_roughness(self.sm, self.lm, return_line=False)
        # assert rgh_1 == pytest.approx(self.rcm8_expected, abs=0.1)
        assert rgh_1 > 0

    def test_rcm8_defaults_opposite(self):
        # test that it is the same with opposite side origin
        rgh_2 = compute_shoreline_roughness(
            self.sm, self.lm, origin=[0, self.rcm8.shape[1]]
        )
        # assert rgh_2 == pytest.approx(self.rcm8_expected, abs=0.2)
        assert rgh_2 > 0

    def test_rcm8_fail_no_shoreline(self):
        # check raises error
        with pytest.raises(ValueError, match=r"No pixels in shoreline mask."):
            compute_shoreline_roughness(np.zeros((10, 10)), self.lm)

    def test_rcm8_fail_no_land(self):
        # check raises error
        with pytest.raises(ValueError, match=r"No pixels in land mask."):
            compute_shoreline_roughness(self.sm, np.zeros((10, 10)))

    def test_compute_shoreline_roughness_asarray(self):
        # test it with default options
        _smarr = np.copy(self.sm.mask)
        _lmarr = np.copy(self.lm.mask)
        assert isinstance(_smarr, np.ndarray)
        assert isinstance(_lmarr, np.ndarray)
        rgh_3 = compute_shoreline_roughness(_smarr, _lmarr)
        # assert rgh_3 == pytest.approx(self.rcm8_expected, abs=0.1)
        assert rgh_3 > 0


class TestShorelineLength:
    rcm8_path = _get_rcm8_path()
    with pytest.warns(UserWarning):
        rcm8 = DataCube(rcm8_path)

    sm = ShorelineMask(rcm8["eta"][-1, :, :], elevation_threshold=0)
    sm0 = ShorelineMask(rcm8["eta"][0, :, :], elevation_threshold=0)

    _trim_length = 4
    sm.trim_mask(length=_trim_length)
    sm0.trim_mask(length=_trim_length)

    def test_simple_case(self):
        simple_len = compute_shoreline_length(simple_shore)
        exp_len = (7 * 1) + (2 * 1.41421356)
        assert simple_len == pytest.approx(exp_len, abs=0.1)

    def test_simple_case_opposite(self):
        simple_len = compute_shoreline_length(simple_shore, origin=[10, 0])
        exp_len = (7 * 1) + (2 * 1.41421356)
        assert simple_len == pytest.approx(exp_len, abs=0.1)

    def test_simple_case_return_line(self):
        simple_len, simple_line = compute_shoreline_length(
            simple_shore, return_line=True
        )
        exp_len = (7 * 1) + (2 * 1.41421356)
        assert simple_len == pytest.approx(exp_len)
        assert np.all(simple_line == np.fliplr(simple_shore_array))

    def test_rcm8_defaults(self):
        # test that it is the same with opposite side origin
        len_0 = compute_shoreline_length(self.sm)
        assert len_0 > 0
        assert len_0 > self.rcm8.shape[1]

    def test_rcm8_defaults_opposite(self):
        # test that it is the same with opposite side origin
        len_0, line_0 = compute_shoreline_length(self.sm, return_line=True)
        _o = [self.rcm8.shape[2], 0]
        len_1, line_1 = compute_shoreline_length(self.sm, origin=_o, return_line=True)
        assert len_0 == pytest.approx(
            len_1, (len_1 * 0.5)
        )  # within 5%, not great, not terrible


class TestShorelineDistance:
    golf_path = _get_golf_path()
    golf = DataCube(golf_path)

    sm = ShorelineMask(
        golf["eta"][-1, :, :], elevation_threshold=0, elevation_offset=-0.5
    )

    def test_empty(self):
        _arr = np.zeros((10, 10))
        with pytest.raises(ValueError):
            _, _ = compute_shoreline_distance(_arr)

    def test_single_point(self):
        _arr = np.zeros((10, 10))
        _arr[7, 5] = 1
        mean00, stddev00 = compute_shoreline_distance(_arr)
        mean05, stddev05 = compute_shoreline_distance(_arr, origin=[5, 0])
        assert mean00 == np.sqrt(49 + 25)
        assert mean05 == 7
        assert stddev00 == 0
        assert stddev05 == 0

    def test_simple_case(self):
        mean, stddev = compute_shoreline_distance(
            self.sm, origin=[self.golf.meta["CTR"].data, self.golf.meta["L0"].data]
        )

        assert mean > stddev
        assert stddev > 0

    def test_simple_case_distances(self):
        m, s = compute_shoreline_distance(
            self.sm, origin=[self.golf.meta["CTR"].data, self.golf.meta["L0"].data]
        )
        m2, s2, dists = compute_shoreline_distance(
            self.sm,
            origin=[self.golf.meta["CTR"].data, self.golf.meta["L0"].data],
            return_distances=True,
        )

        assert len(dists) > 0
        assert np.mean(dists) == m
        assert m2 == m
        assert s2 == s


class TestComputeChannelWidth:
    simple_cm = np.array([[0, 1, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0]])
    trace = np.column_stack(
        (np.zeros(simple_cm.shape[1]), np.arange(simple_cm.shape[1]))
    ).astype(int)

    golf_path = _get_golf_path()
    golf = DataCube(golf_path)

    cm = ChannelMask(
        golf["eta"][-1, :, :],
        golf["velocity"][-1, :, :],
        elevation_threshold=0,
        flow_threshold=0.3,
    )
    sec = CircularSection(golf, radius_idx=40)

    def test_widths_simple(self):
        """Get mean and std from simple."""
        m, s = compute_channel_width(self.simple_cm, section=self.trace)
        assert m == (1 + 2 + 4 + 1) / 4
        assert s == pytest.approx(1.22474487)

    def test_widths_simple_list_equal(self):
        """Get mean, std, list from simple, check that same."""
        m1, s1 = compute_channel_width(self.simple_cm, section=self.trace)
        m2, s2, w = compute_channel_width(
            self.simple_cm, section=self.trace, return_widths=True
        )
        assert m1 == (1 + 2 + 4 + 1) / 4
        assert m1 == m2
        assert s1 == s2
        assert len(w) == 4

    def test_widths_example(self):
        """Get mean and std from example.

        This test does not actually test the computation, just that something
        valid is returned, i.e., the function takes the input.
        """
        m, s = compute_channel_width(self.cm, section=self.sec)
        # check valid values returned
        assert m > 0
        assert s > 0

    def test_bad_masktype(self):
        with pytest.raises(TypeError):
            m, s = compute_channel_width(33, section=self.sec)
        with pytest.raises(TypeError):
            m, s = compute_channel_width(True, section=self.sec)

    def test_no_section_make_default(self):
        with pytest.raises(NotImplementedError):
            m, s = compute_channel_width(self.cm)

    def test_get_channel_starts_and_ends(self):
        _cs, _ce = _get_channel_starts_and_ends(self.simple_cm, self.trace)
        assert _cs[0] == 1
        assert _ce[0] == 2

    def test_wraparound(self):
        alt_cm = np.array([[1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1]])
        _cs, _ce = _get_channel_starts_and_ends(alt_cm, self.trace)
        assert _cs[0] == 1
        assert _ce[0] == 2


class TestComputeChannelDepth:
    simple_cm = np.array([[0, 1, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0]])
    simple_depth = np.array(
        [[1.5, 0.5, 1.5, 0.2, 0.4, 1.5, 1.5, 1, 1, 1, 1, 1.5, 1.5, 9, 0]]
    )
    trace = np.column_stack(
        (np.zeros(simple_cm.shape[1]), np.arange(simple_cm.shape[1]))
    ).astype(int)

    golf_path = _get_golf_path()
    golf = DataCube(golf_path)

    cm = ChannelMask(
        golf["eta"][-1, :, :],
        golf["velocity"][-1, :, :],
        elevation_threshold=0,
        flow_threshold=0.3,
    )
    sec = CircularSection(golf, radius_idx=40)

    def test_depths_simple_thalweg(self):
        """Get mean and std from simple."""
        m, s = compute_channel_depth(
            self.simple_cm, self.simple_depth, section=self.trace
        )
        assert m == (0.5 + 0.4 + 1 + 9) / 4
        assert s == pytest.approx(3.6299965564)

    def test_depths_simple_mean(self):
        """Get mean and std from simple."""
        m, s = compute_channel_depth(
            self.simple_cm, self.simple_depth, section=self.trace, depth_type="mean"
        )
        assert m == (0.5 + 0.3 + 1 + 9) / 4
        assert s == pytest.approx(3.6462309307009066)

    def test_depths_simple_list_equal(self):
        """Get mean, std, list from simple, check that same."""
        m1, s1 = compute_channel_depth(
            self.simple_cm, self.simple_depth, section=self.trace
        )
        m2, s2, w = compute_channel_depth(
            self.simple_cm, self.simple_depth, section=self.trace, return_depths=True
        )
        assert m1 == (0.5 + 0.4 + 1 + 9) / 4
        assert m1 == m2
        assert s1 == s2
        assert len(w) == 4

    def test_depths_example_thalweg(self):
        """Get mean and std from example.

        This test does not actually test the computation, just that something
        valid is returned, i.e., the function takes the input.
        """

        m, s = compute_channel_depth(
            self.cm, self.golf["depth"][-1, :, :], section=self.sec
        )
        assert m > 0
        assert s > 0

    def test_bad_masktype(self):
        with pytest.raises(TypeError):
            m, s = compute_channel_depth(
                33, self.golf["depth"][-1, :, :], section=self.sec
            )
        with pytest.raises(TypeError):
            m, s = compute_channel_depth(
                True, self.golf["depth"][-1, :, :], section=self.sec
            )

    def test_bad_depth_type_arg(self):
        with pytest.raises(ValueError):
            m, s = compute_channel_depth(
                self.cm,
                self.golf["depth"][-1, :, :],
                depth_type="nonsense",
                section=self.sec,
            )

    def test_no_section_make_default(self):
        with pytest.raises(NotImplementedError):
            m, s = compute_channel_depth(self.cm, self.golf["depth"][-1, :, :])


class TestComputeSurfaceDepositTime:
    golfcube = DataCube(golf_path)

    def test_with_diff_indices(self):
        with pytest.raises(ValueError):
            # cannot be index 0
            _ = compute_surface_deposit_time(self.golfcube, surface_idx=0)
        sfc_date_1 = compute_surface_deposit_time(self.golfcube, surface_idx=1)
        assert np.all(sfc_date_1 == 0)
        sfc_date_m1 = compute_surface_deposit_time(self.golfcube, surface_idx=-1)
        assert np.any(sfc_date_m1 > 0)

        # test that cannot be above idx
        half_idx = self.golfcube.shape[0] // 2
        sfc_date_half = compute_surface_deposit_time(
            self.golfcube, surface_idx=half_idx
        )
        assert np.max(sfc_date_half) <= half_idx
        assert np.max(sfc_date_m1) <= self.golfcube.shape[0]

    def test_with_diff_stasis_tol(self):
        with pytest.raises(ValueError):
            # cannot be tol 0
            _ = compute_surface_deposit_time(
                self.golfcube, surface_idx=-1, stasis_tol=0
            )
        sfc_date_tol_000 = compute_surface_deposit_time(
            self.golfcube, surface_idx=-1, stasis_tol=1e-16
        )
        sfc_date_tol_001 = compute_surface_deposit_time(
            self.golfcube, surface_idx=-1, stasis_tol=0.01
        )
        sfc_date_tol_010 = compute_surface_deposit_time(
            self.golfcube, surface_idx=-1, stasis_tol=0.1
        )
        # time of deposition should always be older when threshold is greater
        assert np.all(sfc_date_tol_001 <= sfc_date_tol_000)
        assert np.all(sfc_date_tol_010 <= sfc_date_tol_001)


class TestComputeSurfaceDepositAge:
    golfcube = DataCube(golf_path)

    def test_idx_minus_date(self):
        with pytest.raises(ValueError):
            # cannot be index 0
            _ = compute_surface_deposit_time(self.golfcube, surface_idx=0)
        sfc_date_1 = compute_surface_deposit_age(self.golfcube, surface_idx=1)
        assert np.all(sfc_date_1 == 1)  # 1 - 0
        sfc_date_m1 = compute_surface_deposit_time(self.golfcube, surface_idx=-1)
        # check that the idx wrapping functionality works
        assert np.all(sfc_date_m1 >= 0)
