# -*- coding: utf-8 -*-
"""
Test lap comparison
"""

import pytest
import numpy as np
from late_brake.core.comparator import resample_lap, compare_laps
from late_brake.io.parsers.nmea import parse_nmea_file
from late_brake.io.track_store import get_track_by_id
from late_brake.core.splitter import split_laps


def test_resample_lap():
    """测试重采样"""
    from late_brake.models import DataPoint, Lap
    points = [
        DataPoint(timestamp=0, latitude=0, longitude=0, speed=100, distance=0),
        DataPoint(timestamp=10, latitude=0, longitude=0, speed=100, distance=10),
    ]
    lap = Lap(
        id="test.Lap1",
        source_file="test",
        lap_number=1,
        total_time=10,
        start_time=0,
        end_time=10,
        start_distance=0,
        end_distance=10,
        is_complete=True,
        lap_distance=10,
        points=points
    )
    dist, speed = resample_lap(lap, step_m=1.0)
    assert len(dist) == 11
    assert len(speed) == 11
    assert dist[0] == 0
    assert dist[-1] == 10
    assert speed[0] == 100
    assert speed[-1] == 100


def test_compare_laps():
    """测试对比两个圈"""
    points1 = parse_nmea_file("sample-data/tianma_1.nmea")
    points2 = parse_nmea_file("sample-data/tianma_2.nmea")
    track = get_track_by_id("tianma")
    assert points1 is not None
    assert points2 is not None
    assert track is not None
    laps1 = split_laps(points1, track, "tianma_1.nmea")
    laps2 = split_laps(points2, track, "tianma_2.nmea")
    result = compare_laps(laps1[1], laps2[3], track)
    assert result["total_time_diff"] == pytest.approx(13.24)
    assert result["avg_speed_diff"] < 0
