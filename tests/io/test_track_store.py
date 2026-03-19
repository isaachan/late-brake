# -*- coding: utf-8 -*-
"""
Test track store
"""

from late_brake.io.track_store import list_all_tracks, get_track_by_id


def test_list_all_tracks():
    """测试列出所有赛道"""
    tracks = list_all_tracks()
    assert len(tracks) == 3
    ids = [t.id for t in tracks]
    assert "saic" in ids
    assert "tianma" in ids
    assert "my_private_track_1" in ids


def test_get_track_by_id_exists():
    """测试获取存在的赛道"""
    track = get_track_by_id("tianma")
    assert track is not None
    assert track.id == "tianma"
    assert track.full_name == "上海天马赛车场"
    assert track.length_m == 2063.0
    assert track.turn_count == 8


def test_get_track_by_id_not_exists():
    """测试获取不存在的赛道"""
    track = get_track_by_id("not_exists")
    assert track is None
