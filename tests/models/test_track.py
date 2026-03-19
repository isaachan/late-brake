# -*- coding: utf-8 -*-
"""
Test Track model
"""

import pytest
from late_brake.models import Track, TrackAnchor, TrackSector, TrackTurn


def test_track_minimal():
    """测试最小必填字段Track"""
    track = Track(
        id="tianma",
        name="Shanghai Tianma Circuit",
        length_m=2063.0,
        turn_count=8,
        anchor=TrackAnchor(lat=31.079, lon=121.114, radius_m=300),
        gate=[[31.078, 121.114], [31.079, 121.115]],
        centerline=[[31.078, 121.114], [31.079, 121.115]]
    )
    assert track.id == "tianma"
    assert track.name == "Shanghai Tianma Circuit"
    assert track.length_m == 2063.0
    assert track.turn_count == 8
    assert track.anchor.radius_m == 300
    assert len(track.gate) == 2
    assert len(track.centerline) == 2
    assert track.sectors is None
    assert track.turns is None


def test_track_with_sectors():
    """测试带分段的Track"""
    track = Track(
        id="saic",
        name="Shanghai International Circuit",
        full_name="上海国际赛车场",
        location="Shanghai, China",
        length_m=5451.0,
        turn_count=16,
        anchor=TrackAnchor(lat=31.340, lon=121.219, radius_m=1062),
        gate=[[31.337, 121.222], [31.337, 121.222]],
        centerline=[[31.337, 121.222]],
        sectors=[
            TrackSector(
                id=1,
                name="Sector 1",
                start_distance_m=0,
                end_distance_m=2020,
                turns=[1, 2, 3, 4, 5, 6]
            )
        ]
    )
    assert track.full_name == "上海国际赛车场"
    assert len(track.sectors) == 1
    assert track.sectors[0].turns == [1, 2, 3, 4, 5, 6]


def test_track_missing_required():
    """测试缺少必填字段应该报错"""
    with pytest.raises(Exception):
        Track(
            id="tianma",
            # missing name
            length_m=2063.0,
            turn_count=8,
            anchor=TrackAnchor(lat=31.079, lon=121.114, radius_m=300),
            gate=[[31.078, 121.114], [31.079, 121.115]],
            centerline=[[31.078, 121.114], [31.079, 121.115]]
        )
