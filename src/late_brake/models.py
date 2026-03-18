"""
Core data models for Late Brake lap analysis tool.
Based on the internal data format specification.
"""

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class DataPoint(BaseModel):
    """
    A single data point in the lap data.
    Represents one sampling moment on the track.
    """
    timestamp: float  # Relative time in seconds from start of recording
    latitude: float   # WGS84 latitude
    longitude: float  # WGS84 longitude
    speed: float      # Instantaneous speed in km/h
    distance: float   # Cumulative distance in meters from start
    
    # Optional fields based on data source
    altitude: Optional[float] = None        # Altitude in meters
    g_force_x: Optional[float] = None       # Lateral G-Force (left positive, right negative)
    g_force_y: Optional[float] = None       # Longitudinal G-Force (positive acceleration, negative braking)
    g_force_z: Optional[float] = None       # Vertical G-Force
    steering_angle: Optional[float] = None  # Steering angle in degrees, left negative, right positive
    throttle_position: Optional[float] = None  # Throttle position (0-100%)
    brake_pressure: Optional[float] = None  # Brake pressure (0-100%)
    rpm: Optional[int] = None               # Engine RPM
    gear: Optional[int] = None              # Current gear (0 = neutral)


class Lap(BaseModel):
    """
    Represents a single lap in the data.
    """
    id: str                      # Lap ID (e.g., "file1.Lap1")
    source_file: str             # Source file path
    lap_number: int              # Lap number (1-based)
    total_time: float            # Total lap time in seconds
    start_time: float            # Start time in seconds (relative to entire recording)
    end_time: float              # End time in seconds (relative to entire recording)
    start_distance: float        # Start cumulative distance in meters
    end_distance: float          # End cumulative distance in meters
    is_complete: bool            # Whether this is a complete lap (crossed start/finish line)
    lap_distance: float          # Actual lap distance in meters
    points: List[DataPoint]      # Array of data points in this lap

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "sample.Lap1",
                "source_file": "sample.nmea",
                "lap_number": 1,
                "total_time": 85.323,
                "start_time": 0.0,
                "end_time": 85.323,
                "start_distance": 0.0,
                "end_distance": 5451.0,
                "is_complete": True,
                "lap_distance": 5451.0,
                "points": []
            }
        }
    }


class LapCollection(BaseModel):
    """
    Collection of laps from a single input file.
    """
    file_path: str
    laps: List[Lap]
    track_id: Optional[str] = None  # Associated track ID if matched
