import glob
import os
import pathlib
import time

import numpy as np
import pytest

from sandplover.mobility import calculate_channel_abandonment
from sandplover.sample_data.sample_data import _get_golf_path
from sandplover.utils import NoStratigraphyError
from sandplover.utils import curve_fit
from sandplover.utils import format_number
from sandplover.utils import format_table
from sandplover.utils import line_to_cells
from sandplover.utils import runtime_from_log


class TestNoStratigraphyError:

    def test_needs_obj_argument(self):
        with pytest.raises(TypeError):
            raise NoStratigraphyError()

    def test_only_obj_argument(self):
        _mtch = "'str' object has no*."
        with pytest.raises(NoStratigraphyError, match=_mtch):
            raise NoStratigraphyError("someobj")

    def test_obj_and_var(self):
        _mtch = "'str' object has no attribute 'somevar'."
        with pytest.raises(NoStratigraphyError, match=_mtch):
            raise NoStratigraphyError("someobj", "somevar")


class TestLineToCells:

    def test_flat_inputs(self):
        x0, y0, x1, y1 = 10, 40, 50, 40
        ret1 = line_to_cells(np.array([[x0, y0], [x1, y1]]))
        ret2 = line_to_cells((x0, y0), (x1, y1))
        ret3 = line_to_cells(x0, y0, x1, y1)
        ret1, ret2, ret3 = np.vstack(ret1), np.vstack(ret2), np.vstack(ret3)
        assert np.all(ret1 == ret2) and np.all(ret1 == ret3)
        assert ret1.shape[1] == 41

    def test_vert_inputs(self):
        x0, y0, x1, y1 = 40, 10, 40, 70
        ret1 = line_to_cells(np.array([[x0, y0], [x1, y1]]))
        ret2 = line_to_cells((x0, y0), (x1, y1))
        ret3 = line_to_cells(x0, y0, x1, y1)
        ret1, ret2, ret3 = np.vstack(ret1), np.vstack(ret2), np.vstack(ret3)
        assert np.all(ret1 == ret2) and np.all(ret1 == ret3)
        assert ret1.shape[1] == 61

    def test_quadrantI_angle_inputs(self):
        x0, y0, x1, y1 = 10, 10, 60, 92
        ret1 = line_to_cells(np.array([[x0, y0], [x1, y1]]))
        ret2 = line_to_cells((x0, y0), (x1, y1))
        ret3 = line_to_cells(x0, y0, x1, y1)
        ret1, ret2, ret3 = np.vstack(ret1), np.vstack(ret2), np.vstack(ret3)
        assert np.all(ret1 == ret2) and np.all(ret1 == ret3)
        assert ret1.shape[1] == 83
        # check line is sorted correctly: p0 --> p1
        assert np.all(ret1[:, 0] == np.array([x0, y0]))
        assert np.all(ret1[:, -1] == np.array([x1, y1]))

    def test_quadrantII_angle_inputs(self):
        x0, y0, x1, y1 = 80, 20, 40, 50
        ret1 = line_to_cells(np.array([[x0, y0], [x1, y1]]))
        ret2 = line_to_cells((x0, y0), (x1, y1))
        ret3 = line_to_cells(x0, y0, x1, y1)
        ret1, ret2, ret3 = np.vstack(ret1), np.vstack(ret2), np.vstack(ret3)
        assert np.all(ret1 == ret2) and np.all(ret1 == ret3)
        assert ret1.shape[1] == 41
        # check line is sorted correctly: p0 --> p1
        assert np.all(ret1[:, 0] == np.array([x0, y0]))
        assert np.all(ret1[:, -1] == np.array([x1, y1]))

    def test_quadrantIII_angle_inputs(self):
        x0, y0, x1, y1 = 80, 70, 40, 40
        ret1 = line_to_cells(np.array([[x0, y0], [x1, y1]]))
        ret2 = line_to_cells((x0, y0), (x1, y1))
        ret3 = line_to_cells(x0, y0, x1, y1)
        ret1, ret2, ret3 = np.vstack(ret1), np.vstack(ret2), np.vstack(ret3)
        assert np.all(ret1 == ret2) and np.all(ret1 == ret3)
        assert ret1.shape[1] == 41
        # check line is sorted correctly: p0 --> p1
        assert np.all(ret1[:, 0] == np.array([x0, y0]))
        assert np.all(ret1[:, -1] == np.array([x1, y1]))

    def test_quadrantIV_angle_inputs(self):
        x0, y0, x1, y1 = 10, 80, 60, 30
        ret1 = line_to_cells(np.array([[x0, y0], [x1, y1]]))
        ret2 = line_to_cells((x0, y0), (x1, y1))
        ret3 = line_to_cells(x0, y0, x1, y1)
        ret1, ret2, ret3 = np.vstack(ret1), np.vstack(ret2), np.vstack(ret3)
        assert np.all(ret1 == ret2) and np.all(ret1 == ret3)
        assert ret1.shape[1] == 51
        assert np.all(ret1[:, 0] == np.array([x0, y0]))
        assert np.all(ret1[:, -1] == np.array([x1, y1]))

    def test_bad_inputs(self):
        x0, y0, x1, y1 = 10, 10, 60, 92
        with pytest.raises(TypeError, match=r"Length of input .*"):
            _ = line_to_cells(x0, y0, x1, y1, x0, y1)
        with pytest.raises(ValueError):
            _ = line_to_cells(np.array([[x0, y0], [x1, y1], [x0, y1]]))


chmap = np.zeros((5, 4, 4))
# define time = 0
chmap[0, :, 1] = 1
# every time step one cell of the channel will migrate one pixel to the right
for i in range(1, 5):
    chmap[i, :, :] = chmap[i - 1, :, :].copy()
    chmap[i, -1 * i, 1] = 0
    chmap[i, -1 * i, 2] = 1
# define the fluvial surface - entire 4x4 area
fsurf = np.ones((4, 4))
# define the index corresponding to the basemap at time 0
basevalue = [0]
# define the size of the time window to use
time_window = 5


def test_linear_fit():
    """Test linear curve fitting."""
    ch_abandon = calculate_channel_abandonment(
        chmap, basevalues_idx=basevalue, window_idx=time_window
    )
    yfit, popts, cov, err = curve_fit(ch_abandon, fit="linear")
    assert yfit == pytest.approx([0.0, 0.25, 0.5, 0.75, 1.0])
    assert popts == pytest.approx([0.25, 0.0])
    assert cov.shape == (2, 2) and cov == pytest.approx(0.0)
    assert err == pytest.approx([0.0, 0.0])


def test_harmonic_fit():
    """Test harmonic curve fitting."""
    ch_abandon = calculate_channel_abandonment(
        chmap, basevalues_idx=basevalue, window_idx=time_window
    )
    yfit, popts, cov, err = curve_fit(ch_abandon, fit="harmonic")
    assert pytest.approx(yfit) == np.array(
        [-0.25986438, 0.41294455, 0.11505591, 0.06683947, 0.04710091]
    )
    assert pytest.approx(popts) == np.array([-0.25986438, -1.62929608])
    assert pytest.approx(cov) == np.array(
        [[0.50676407, 1.26155952], [1.26155952, 4.3523343]]
    )
    assert pytest.approx(err) == np.array([0.71187364, 2.08622489])


def test_invalid_fit():
    """Test invalid fit parameter."""
    ch_abandon = calculate_channel_abandonment(
        chmap, basevalues_idx=basevalue, window_idx=time_window
    )
    with pytest.raises(ValueError):
        curve_fit(ch_abandon, fit="invalid")


def test_exponential_fit():
    """Test exponential fitting."""
    ydata = np.array([10, 5, 2, 1])
    yfit, popts, cov, err = curve_fit(ydata, fit="exponential")
    assert pytest.approx(yfit) == np.array(
        [10.02900253, 4.85696353, 2.22612537, 0.88790858]
    )
    assert pytest.approx(popts) == np.array([10.02900253, -0.49751195, 0.67596451])
    assert pytest.approx(cov) == np.array(
        [
            [0.0841566, 0.04554967, 0.01139969],
            [0.04554967, 0.59895713, 0.08422946],
            [0.01139969, 0.08422946, 0.01327807],
        ]
    )
    assert pytest.approx(err) == np.array([0.29009757, 0.77392321, 0.11523053])


def test_format_number_float():
    _val = float(5.2)
    _fnum = format_number(_val)
    assert _fnum == "10"

    _val = float(50.2)
    _fnum = format_number(_val)
    assert _fnum == "50"

    _val = float(15.0)
    _fnum = format_number(_val)
    assert _fnum == "20"


def test_format_number_int():
    _val = int(5)
    _fnum = format_number(_val)
    assert _fnum == "0"

    _val = int(6)
    _fnum = format_number(_val)
    assert _fnum == "10"

    _val = int(52)
    _fnum = format_number(_val)
    assert _fnum == "50"

    _val = int(15)
    _fnum = format_number(_val)
    assert _fnum == "20"


def test_format_table_float():
    _val = float(5.2)
    _fnum = format_table(_val)
    assert _fnum == "5.2"

    _val = float(50.2)
    _fnum = format_table(_val)
    assert _fnum == "50.2"

    _val = float(15.0)
    _fnum = format_table(_val)
    assert _fnum == "15.0"

    _val = float(15.03689)
    _fnum = format_table(_val)
    assert _fnum == "15.0"

    _val = float(15.0689)
    _fnum = format_table(_val)
    assert _fnum == "15.1"


def test_format_table_int():
    _val = int(5)
    _fnum = format_table(_val)
    assert _fnum == "5"

    _val = int(5.8)
    _fnum = format_table(_val)
    assert _fnum == "5"

    _val = int(5.2)
    _fnum = format_table(_val)
    assert _fnum == "5"


@pytest.mark.xfail(raises=ImportError, reason="pyDeltaRCM is not a required dependency")
def test_time_from_log_new(tmp_path):
    """Generate run+logfile and then read runtime from it."""
    from pyDeltaRCM.model import DeltaModel

    delta = DeltaModel(out_dir=str(tmp_path))  # init delta to make log file
    time.sleep(1)
    delta.finalize()  # finalize and end log file
    log_path = os.path.join(tmp_path, os.listdir(tmp_path)[0])  # path to log
    elapsed_time = runtime_from_log(log_path)
    # elapsed time should exceed 0, but exact time will vary
    assert isinstance(elapsed_time, float)
    assert elapsed_time > 0


def test_time_from_log_sampledataset(tmp_path):
    golfpath = pathlib.PurePath(_get_golf_path())
    # find the log file there
    found = glob.glob(os.path.join(golfpath.parent, "*.log"))
    assert len(found) == 1
    elapsed_time = runtime_from_log(found[0])
    # elapsed time should exceed 0, but exact time will vary
    assert isinstance(elapsed_time, float)
    assert elapsed_time > 0
