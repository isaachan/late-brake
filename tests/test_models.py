"""
Tests for core data models.
"""

import pytest
from late_brake.models import DataPoint, Lap, LapCollection


def test_data_point_creation():
    """Test that a DataPoint can be created with required fields."""
    dp = DataPoint(
        timestamp=0.1,
        latitude=31.3401765,
        longitude=121.219292,
        speed=150.0,
        distance=100.0
    )
    assert dp.timestamp == 0.1
    assert dp.latitude == 31.3401765
    assert dp.longitude == 121.219292
    assert dp.speed == 150.0
    assert dp.distance == 100.0
    assert dp.altitude is None
    assert dp.g_force_x is None


def test_data_point_with_optional_fields():
    """Test that a DataPoint can be created with optional fields."""
    dp = DataPoint(
        timestamp=0.1,
        latitude=31.3401765,
        longitude=121.219292,
        speed=150.0,
        distance=100.0,
        g_force_x=0.8,
        g_force_y=-1.2,
        throttle_position=100.0,
        brake_pressure=0.0,
        rpm=6000,
        gear=3
    )
    assert dp.g_force_x == 0.8
    assert dp.g_force_y == -1.2
    assert dp.throttle_position == 100.0
    assert dp.brake_pressure == 0.0
    assert dp.rpm == 6000
    assert dp.gear == 3


def test_lap_creation():
    """Test that a Lap can be created."""
    dp1 = DataPoint(timestamp=0.0, latitude=0.0, longitude=0.0, speed=0.0, distance=0.0)
    dp2 = DataPoint(timestamp=1.0, latitude=0.001, longitude=0.001, speed=100.0, distance=50.0)
    
    lap = Lap(
        id="test.Lap1",
        source_file="test.nmea",
        lap_number=1,
        total_time=85.323,
        start_time=0.0,
        end_time=85.323,
        start_distance=0.0,
        end_distance=5451.0,
        is_complete=True,
        lap_distance=5451.0,
        points=[dp1, dp2]
    )
    
    assert lap.id == "test.Lap1"
    assert lap.source_file == "test.nmea"
    assert lap.lap_number == 1
    assert lap.total_time == 85.323
    assert lap.is_complete is True
    assert len(lap.points) == 2


def test_lap_collection_creation():
    """Test that a LapCollection can be created."""
    dp = DataPoint(timestamp=0.0, latitude=0.0, longitude=0.0, speed=0.0, distance=0.0)
    lap = Lap(
        id="test.Lap1",
        source_file="test.nmea",
        lap_number=1,
        total_time=85.323,
        start_time=0.0,
        end_time=85.323,
        start_distance=0.0,
        end_distance=5451.0,
        is_complete=True,
        lap_distance=5451.0,
        points=[dp]
    )
    
    collection = LapCollection(
        file_path="test.nmea",
        laps=[lap],
        track_id="saic"
    )
    
    assert collection.file_path == "test.nmea"
    assert len(collection.laps) == 1
    assert collection.track_id == "saic"
