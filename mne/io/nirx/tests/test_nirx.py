# -*- coding: utf-8 -*-
# Authors: Robert Luke  <mail@robertluke.net>
#          Eric Larson <larson.eric.d@gmail.com>
#          simplified BSD-3 license

import os.path as op

import pytest
from numpy.testing import assert_allclose, assert_array_equal

from mne.datasets.testing import data_path, requires_testing_data
from mne.io import read_raw_nirx
from mne.io.tests.test_raw import _test_raw_reader
from mne.transforms import apply_trans, _get_trans
from mne.utils import run_tests_if_main
from mne.preprocessing._beer_lambert_law import _probe_distances,\
    _short_channels

fname_nirx_15_0 = op.join(data_path(download=False),
                          'NIRx', 'nirx_15_0_recording')
fname_nirx_15_2 = op.join(data_path(download=False),
                          'NIRx', 'nirx_15_2_recording')
fname_nirx_15_2_short = op.join(data_path(download=False),
                                'NIRx', 'nirx_15_2_recording_w_short')


@requires_testing_data
def test_nirx_15_2_short():
    """Test reading NIRX files."""
    raw = read_raw_nirx(fname_nirx_15_2_short, preload=True)

    # Test data import
    assert raw._data.shape == (26, 145)
    assert raw.info['sfreq'] == 12.5

    # Test channel naming
    assert raw.info['ch_names'][:4] == ["S1-D1 760", "S1-D1 850",
                                        "S1-D9 760", "S1-D9 850"]
    assert raw.info['ch_names'][24:26] == ["S5-D13 760", "S5-D13 850"]

    # Test info import
    assert raw.info['subject_info'] == dict(sex=1, first_name="MNE",
                                            middle_name="Test",
                                            last_name="Recording")

    # Test distance between optodes matches values from
    # nirsite https://github.com/mne-tools/mne-testing-data/pull/51
    # step 4 figure 2
    allowed_distance_error = 0.0002
    distances = _probe_distances(raw)
    assert_allclose(distances[::2], [
        0.0304, 0.0078, 0.0310, 0.0086, 0.0416,
        0.0072, 0.0389, 0.0075, 0.0558, 0.0562,
        0.0561, 0.0565, 0.0077], atol=allowed_distance_error)

    # Test which channels are short
    # These are the ones marked as red at
    # https://github.com/mne-tools/mne-testing-data/pull/51 step 4 figure 2
    short_channels = _short_channels(raw)
    assert_array_equal(short_channels[:9:2], [False, True, False, True, False])
    short_channels = _short_channels(raw, threshold=0.003)
    assert_array_equal(short_channels[:3:2], [False, False])
    short_channels = _short_channels(raw, threshold=50)
    assert_array_equal(short_channels[:3:2], [True, True])

    # Test trigger events
    assert_array_equal(raw.annotations.description, ['3.0', '2.0', '1.0'])

    # Test location of detectors
    # The locations of detectors can be seen in the first
    # figure on this page...
    # https://github.com/mne-tools/mne-testing-data/pull/51
    # And have been manually copied below
    # These values were reported in mm, but according to this page...
    # https://mne.tools/stable/auto_tutorials/intro/plot_40_sensor_locations.html
    # 3d locations should be specified in meters, so that's what's tested below
    # Detector locations are stored in the third three loc values
    allowed_dist_error = 0.0002
    locs = [ch['loc'][6:9] for ch in raw.info['chs']]
    head_mri_t, _ = _get_trans('fsaverage', 'head', 'mri')
    mni_locs = apply_trans(head_mri_t, locs)

    assert raw.info['ch_names'][0][3:5] == 'D1'
    assert_allclose(
        mni_locs[0], [-0.0841, -0.0464, -0.0129], atol=allowed_dist_error)

    assert raw.info['ch_names'][4][3:5] == 'D3'
    assert_allclose(
        mni_locs[4], [0.0846, -0.0142, -0.0156], atol=allowed_dist_error)

    assert raw.info['ch_names'][8][3:5] == 'D2'
    assert_allclose(
        mni_locs[8], [0.0207, -0.1062, 0.0484], atol=allowed_dist_error)

    assert raw.info['ch_names'][12][3:5] == 'D4'
    assert_allclose(
        mni_locs[12], [-0.0196, 0.0821, 0.0275], atol=allowed_dist_error)

    assert raw.info['ch_names'][16][3:5] == 'D5'
    assert_allclose(
        mni_locs[16], [-0.0360, 0.0276, 0.0778], atol=allowed_dist_error)

    assert raw.info['ch_names'][19][3:5] == 'D6'
    assert_allclose(
        mni_locs[19], [0.0352, 0.0283, 0.0780], atol=allowed_dist_error)

    assert raw.info['ch_names'][21][3:5] == 'D7'
    assert_allclose(
        mni_locs[21], [0.0388, -0.0477, 0.0932], atol=allowed_dist_error)


@requires_testing_data
def test_nirx_15_2():
    """Test reading NIRX files."""
    raw = read_raw_nirx(fname_nirx_15_2, preload=True)

    # Test data import
    assert raw._data.shape == (64, 67)
    assert raw.info['sfreq'] == 3.90625

    # Test channel naming
    assert raw.info['ch_names'][:4] == ["S1-D1 760", "S1-D1 850",
                                        "S1-D10 760", "S1-D10 850"]

    # Test info import
    assert raw.info['subject_info'] == dict(sex=1, first_name="TestRecording")

    # Test trigger events
    assert_array_equal(raw.annotations.description, ['4.0', '6.0', '2.0'])

    # Test location of detectors
    allowed_dist_error = 0.0002
    locs = [ch['loc'][6:9] for ch in raw.info['chs']]
    head_mri_t, _ = _get_trans('fsaverage', 'head', 'mri')
    mni_locs = apply_trans(head_mri_t, locs)

    assert raw.info['ch_names'][0][3:5] == 'D1'
    assert_allclose(
        mni_locs[0], [-0.0292, 0.0852, -0.0142], atol=allowed_dist_error)

    assert raw.info['ch_names'][15][3:5] == 'D4'
    assert_allclose(
        mni_locs[15], [-0.0739, -0.0756, -0.0075], atol=allowed_dist_error)


@requires_testing_data
def test_nirx_15_0():
    """Test reading NIRX files."""
    raw = read_raw_nirx(fname_nirx_15_0, preload=True)

    # Test data import
    assert raw._data.shape == (20, 92)
    assert raw.info['sfreq'] == 6.25

    # Test channel naming
    assert raw.info['ch_names'][:12] == ["S1-D1 760", "S1-D1 850",
                                         "S2-D2 760", "S2-D2 850",
                                         "S3-D3 760", "S3-D3 850",
                                         "S4-D4 760", "S4-D4 850",
                                         "S5-D5 760", "S5-D5 850",
                                         "S6-D6 760", "S6-D6 850"]

    # Test info import
    assert raw.info['subject_info'] == {'first_name': 'NIRX',
                                        'last_name': 'Test', 'sex': '0'}

    # Test trigger events
    assert_array_equal(raw.annotations.description, ['1.0', '2.0', '2.0'])

    # Test location of detectors
    allowed_dist_error = 0.0002
    locs = [ch['loc'][6:9] for ch in raw.info['chs']]
    head_mri_t, _ = _get_trans('fsaverage', 'head', 'mri')
    mni_locs = apply_trans(head_mri_t, locs)

    assert raw.info['ch_names'][0][3:5] == 'D1'
    assert_allclose(
        mni_locs[0], [0.0287, -0.1143, -0.0332], atol=allowed_dist_error)

    assert raw.info['ch_names'][15][3:5] == 'D8'
    assert_allclose(
        mni_locs[15], [-0.0693, -0.0480, 0.0657], atol=allowed_dist_error)

    # Test distance between optodes matches values from
    allowed_distance_error = 0.0002
    distances = _probe_distances(raw)
    assert_allclose(distances[::2], [
        0.0301, 0.0315, 0.0343, 0.0368, 0.0408,
        0.0399, 0.0393, 0.0367, 0.0336, 0.0447], atol=allowed_distance_error)


@requires_testing_data
@pytest.mark.parametrize('fname, boundary_decimal', (
    [fname_nirx_15_2_short, 1],
    [fname_nirx_15_2, 0],
    [fname_nirx_15_0, 0]
))
def test_nirx_standard(fname, boundary_decimal):
    """Test standard operations."""
    _test_raw_reader(read_raw_nirx, fname=fname,
                     boundary_decimal=boundary_decimal)  # low fs


run_tests_if_main()