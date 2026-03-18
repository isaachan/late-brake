"""
Track data models for Late Brake.
Based on the track data format specification.
"""

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class Anchor(BaseModel):
    """Track anchor for GPS matching."""
    lat: float        # Anchor latitude
    lon: float        # Anchor longitude
    radius_m: float   # Track radius in meters


class Turn(BaseModel):
    """Information about a single turn/corner."""
    id: str
    number: int
    name: str
    type: str  # left/right/left-right/right-left
    start_distance_m: float
    apex_distance_m: float
    end_distance_m: float
    radius_m: Optional[float] = None
    peak_speed_kph_expected: Optional[float] = None


class Sector(BaseModel):
    """Track sector information."""
    id: str
    name: str
    start_distance_m: float
    end_distance_m: float
    turns: List[int] = Field(default_factory=list)


class Track(BaseModel):
    """
    Complete track definition.
    """
    id: str
    name: str
    full_name: Optional[str] = None
    location: Optional[str] = None
    length_m: Optional[float] = None
    turn_count: Optional[int] = None
    anchor: Anchor
    gate: List[List[float]]  # Start/finish line coordinates [ [lat1, lon1], [lat2, lon2] ]
    centerline: List[List[float]]  # Centerline GPS points [[lat, lon], ...]
    geofence: Optional[List[List[float]]] = None
    sectors: Optional[List[Sector]] = None
    turns: Optional[List[Turn]] = None

    def get_sector_for_distance(self, distance_m: float) -> Optional[Sector]:
        """Get the sector that contains the given distance."""
        if not self.sectors:
            return None
        for sector in self.sectors:
            if sector.start_distance_m <= distance_m < sector.end_distance_m:
                return sector
        return None

    def get_turn_for_distance(self, distance_m: float) -> Optional[Turn]:
        """Get the turn that contains the given distance."""
        if not self.turns:
            return None
        for turn in self.turns:
            if turn.start_distance_m <= distance_m <= turn.end_distance_m:
                return turn
        return None
