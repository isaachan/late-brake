"""
Tests for track models.
"""

import pytest
from late_brake.track import Anchor, Turn, Sector, Track


def test_anchor_creation():
    """Test that an Anchor can be created."""
    anchor = Anchor(lat=31.3401765, lon=121.219292, radius_m=1062)
    assert anchor.lat == 31.3401765
    assert anchor.lon == 121.219292
    assert anchor.radius_m == 1062


def test_turn_creation():
    """Test that a Turn can be created."""
    turn = Turn(
        id="t1",
        number=1,
        name="T1",
        type="right",
        start_distance_m=120,
        apex_distance_m=280,
        end_distance_m=350,
        radius_m=85,
        peak_speed_kph_expected=165
    )
    assert turn.number == 1
    assert turn.type == "right"
    assert turn.peak_speed_kph_expected == 165


def test_sector_creation():
    """Test that a Sector can be created."""
    sector = Sector(
        id="s1",
        name="Sector 1",
        start_distance_m=0,
        end_distance_m=2020,
        turns=[1, 2, 3, 4, 5, 6]
    )
    assert sector.name == "Sector 1"
    assert len(sector.turns) == 6
    assert 1 in sector.turns


def test_track_creation():
    """Test that a complete Track can be created."""
    anchor = Anchor(lat=31.3401765, lon=121.219292, radius_m=1062)
    gate = [[31.3375154, 121.2223689], [31.3378142, 121.2222865]]
    centerline = [[31.3401765, 121.219292]]
    
    track = Track(
        id="saic",
        name="Shanghai International Circuit",
        full_name="上海国际赛车场",
        location="Shanghai, China",
        length_m=5451,
        turn_count=16,
        anchor=anchor,
        gate=gate,
        centerline=centerline
    )
    
    assert track.id == "saic"
    assert track.name == "Shanghai International Circuit"
    assert track.full_name == "上海国际赛车场"
    assert track.length_m == 5451
    assert len(track.gate) == 2
    assert len(track.centerline) == 1


def test_get_sector_for_distance():
    """Test getting sector by distance."""
    anchor = Anchor(lat=0, lon=0, radius_m=1000)
    sector1 = Sector(id="s1", name="S1", start_distance_m=0, end_distance_m=2020, turns=[1, 2, 3])
    sector2 = Sector(id="s2", name="S2", start_distance_m=2020, end_distance_m=3740, turns=[4, 5])
    sector3 = Sector(id="s3", name="S3", start_distance_m=3740, end_distance_m=5451, turns=[6, 7, 8])
    
    track = Track(
        id="test",
        name="Test Track",
        length_m=5451,
        turn_count=8,
        anchor=anchor,
        gate=[[0, 0], [0, 0]],
        centerline=[],
        sectors=[sector1, sector2, sector3]
    )
    
    assert track.get_sector_for_distance(0) == sector1
    assert track.get_sector_for_distance(1000) == sector1
    assert track.get_sector_for_distance(2019) == sector1
    assert track.get_sector_for_distance(2020) == sector2
    assert track.get_sector_for_distance(3000) == sector2
    assert track.get_sector_for_distance(3739) == sector2
    assert track.get_sector_for_distance(3740) == sector3
    assert track.get_sector_for_distance(5450) == sector3
    assert track.get_sector_for_distance(6000) is None


def test_get_turn_for_distance():
    """Test getting turn by distance."""
    anchor = Anchor(lat=0, lon=0, radius_m=1000)
    turn1 = Turn(id="t1", number=1, name="T1", type="right", start_distance_m=120, apex_distance_m=280, end_distance_m=350)
    turn2 = Turn(id="t2", number=2, name="T2", type="left", start_distance_m=350, apex_distance_m=410, end_distance_m=460)
    
    track = Track(
        id="test",
        name="Test Track",
        length_m=1000,
        turn_count=2,
        anchor=anchor,
        gate=[[0, 0], [0, 0]],
        centerline=[],
        turns=[turn1, turn2]
    )
    
    assert track.get_turn_for_distance(0) is None
    assert track.get_turn_for_distance(119) is None
    assert track.get_turn_for_distance(120) == turn1
    assert track.get_turn_for_distance(280) == turn1
    assert track.get_turn_for_distance(350) == turn1
    assert track.get_turn_for_distance(351) == turn2
    assert track.get_turn_for_distance(460) == turn2
    assert track.get_turn_for_distance(461) is None
