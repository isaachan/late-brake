# -*- coding: utf-8 -*-
"""
Test automatic lap splitting
"""

import pytest
from late_brake.core.splitter import point_to_line_distance, side_of_line, split_laps
from late_brake.io.parsers.nmea import parse_nmea_file
from late_brake.io.track_store import get_track_by_id


def test_point_to_line_distance():
    """测试点到线距离计算"""
    # 简单直角测试
    # gate from (0,0) to (0, 1) on sphere (small scale approx)
    dist = point_to_line_distance(
        0.00001, 0.0,  # point
        0.0, 0.0,  # gate start
        0.0, 0.00001  # gate end
    )
    # 大约 1.11 meters (1 degree lat ≈ 111 km)
    assert dist > 0.5
    assert dist < 2.0


def test_side_of_line():
    """测试侧判断"""
    side = side_of_line(
        31.1, 121.1,
        31.0, 121.0,
        31.0, 121.2
    )
    assert side in (1, -1)


def test_split_laps_tianma():
    """测试实际文件分割"""
    points = parse_nmea_file("sample-data/tianma_1.nmea")
    assert points is not None
    track = get_track_by_id("tianma")
    assert track is not None
    laps = split_laps(points, track, "tianma_1.nmea")
    assert len(laps) == 6
    # 第二个圈是完整的
    assert laps[1].is_complete is True
    assert laps[1].total_time == pytest.approx(75.96)
    assert laps[1].lap_distance == pytest.approx(2016.5, rel=0.01)
    # 开头不完整，结尾不完整
    assert laps[0].is_complete is False
    assert laps[-1].is_complete is False


def test_split_laps_no_crossings():
    """测试没有穿越点应该返回空"""
    from late_brake.models import DataPoint
    points = [
        DataPoint(timestamp=0, latitude=0, longitude=0, speed=0, distance=0)
    ]
    track = get_track_by_id("tianma")
    laps = split_laps(points, track, "test")
    assert len(laps) == 0
