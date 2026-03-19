# -*- coding: utf-8 -*-
"""
Test automatic track matching
"""

from late_brake.models import DataPoint
from late_brake.core.matcher import calculate_centroid, match_track
from late_brake.io.track_store import get_track_by_id


import pytest

def test_calculate_centroid():
    """测试中心点计算"""
    points = [
        DataPoint(timestamp=0, latitude=31.0, longitude=121.0, speed=0, distance=0),
        DataPoint(timestamp=1, latitude=31.1, longitude=121.1, speed=0, distance=100),
    ]
    lat, lon = calculate_centroid(points)
    assert lat == pytest.approx(31.05)
    assert lon == pytest.approx(121.05)


def test_match_track_success():
    """测试成功匹配赛道"""
    # 用tianma样例数据测试
    from late_brake.io.parsers.nmea import parse_nmea_file
    points = parse_nmea_file("sample-data/tianma_1.nmea")
    assert points is not None
    track, msg = match_track(points)
    assert track is not None
    assert track.id == "tianma"
    assert "自动匹配成功" in msg


def test_match_track_no_candidates():
    """测试没有匹配赛道"""
    # 制造一个很远的点
    points = [
        DataPoint(timestamp=0, latitude=0.0, longitude=0.0, speed=0, distance=0),
    ]
    track, msg = match_track(points)
    assert track is None
    assert "没有找到匹配的赛道" in msg
