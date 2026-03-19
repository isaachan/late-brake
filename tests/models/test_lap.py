# -*- coding: utf-8 -*-
"""
Test Lap model
"""

import pytest
from late_brake.models import DataPoint, Lap


def test_lap_complete():
    """测试完整Lap"""
    points = [
        DataPoint(timestamp=0.0, latitude=0, longitude=0, speed=0, distance=0),
        DataPoint(timestamp=1.0, latitude=0, longitude=0, speed=0, distance=10),
        DataPoint(timestamp=75.96, latitude=0, longitude=0, speed=0, distance=2063),
    ]
    lap = Lap(
        id="test.Lap1",
        source_file="test.nmea",
        lap_number=1,
        total_time=75.96,
        start_time=0.0,
        end_time=75.96,
        start_distance=0.0,
        end_distance=2063.0,
        is_complete=True,
        lap_distance=2063.0,
        points=points
    )
    assert lap.id == "test.Lap1"
    assert lap.lap_number == 1
    assert lap.total_time == 75.96
    assert lap.is_complete is True
    assert lap.lap_distance == 2063.0
    assert len(lap.points) == 3


def test_lap_incomplete():
    """测试不完整Lap"""
    points = [
        DataPoint(timestamp=0.0, latitude=0, longitude=0, speed=0, distance=0),
        DataPoint(timestamp=34.0, latitude=0, longitude=0, speed=0, distance=783),
    ]
    lap = Lap(
        id="test.Lap1",
        source_file="test.nmea",
        lap_number=1,
        total_time=34.0,
        start_time=0.0,
        end_time=34.0,
        start_distance=0.0,
        end_distance=783.0,
        is_complete=False,
        lap_distance=783.0,
        points=points
    )
    assert lap.is_complete is False
