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
    assert track.turn_count == 14


def test_get_track_by_id_not_exists():
    """测试获取不存在的赛道"""
    track = get_track_by_id("not_exists")
    assert track is None


# Tests for US-033 / US-034: track validation
import json
import tempfile
import os
from late_brake.io.track_store import validate_track_file, load_track_from_file


def test_validate_track_missing_required_fields():
    """测试校验：缺失必填字段"""
    incomplete_track = {
        "id": "test",
        "name": "Test Track"
        # missing: length_m, turn_count, anchor, gate, centerline
    }
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(incomplete_track, f)
        tmp_path = f.name

    try:
        valid, err, track = validate_track_file(tmp_path)
        assert not valid
        assert err is not None
        assert "格式验证失败" in err
        assert track is None
    finally:
        os.unlink(tmp_path)


def test_validate_track_gate_not_two_points():
    """测试校验：gate 不是两个点"""
    invalid_track = {
        "id": "test",
        "name": "Test Track",
        "length_m": 1000.0,
        "turn_count": 5,
        "anchor": {"lat": 31.0, "lon": 121.0, "radius_m": 1000.0},
        "gate": [[31.0, 121.0]],  # only one point
        "centerline": [[31.0, 121.0], [31.1, 121.1]]
    }
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(invalid_track, f)
        tmp_path = f.name

    try:
        valid, err, track = validate_track_file(tmp_path)
        assert not valid
        assert err is not None
        assert "格式验证失败" in err
        assert track is None
    finally:
        os.unlink(tmp_path)


def test_validate_track_empty_centerline():
    """测试校验：centerline 是空数组"""
    invalid_track = {
        "id": "test",
        "name": "Test Track",
        "length_m": 1000.0,
        "turn_count": 5,
        "anchor": {"lat": 31.0, "lon": 121.0, "radius_m": 1000.0},
        "gate": [[31.0, 121.0], [31.1, 121.1]],
        "centerline": []  # empty
    }
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(invalid_track, f)
        tmp_path = f.name

    try:
        valid, err, track = validate_track_file(tmp_path)
        assert not valid
        assert err is not None
        assert "格式验证失败" in err
        assert track is None
    finally:
        os.unlink(tmp_path)


def test_validate_valid_track():
    """测试校验：完整合法赛道"""
    valid_track = {
        "id": "test_valid",
        "name": "Test Valid",
        "length_m": 1000.0,
        "turn_count": 5,
        "anchor": {"lat": 31.0, "lon": 121.0, "radius_m": 1000.0},
        "gate": [[31.0, 121.0], [31.1, 121.1]],
        "centerline": [[31.0, 121.0], [31.1, 121.1], [31.2, 121.2]]
    }
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(valid_track, f)
        tmp_path = f.name

    try:
        valid, err, track = validate_track_file(tmp_path)
        assert valid
        assert err is None
        assert track is not None
        assert track.id == "test_valid"
        assert track.name == "Test Valid"
    finally:
        os.unlink(tmp_path)


def test_validate_turn_with_apex_coordinates():
    """测试校验：带弯道信息，包含新字段 apex_coordinates，没有 id/number"""
    valid_track = {
        "id": "test_turns",
        "name": "Test Track with Turns",
        "length_m": 1000.0,
        "turn_count": 1,
        "anchor": {"lat": 31.0, "lon": 121.0, "radius_m": 1000.0},
        "gate": [[31.0, 121.0], [31.1, 121.1]],
        "centerline": [[31.0, 121.0], [31.1, 121.1], [31.2, 121.2]],
        "turns": [
            {
                "name": "T1",
                "type": "left",
                "start_distance_m": 100.0,
                "apex_distance_m": 150.0,
                "apex_coordinates": [31.05, 121.05],
                "end_distance_m": 200.0
            }
        ]
    }
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(valid_track, f)
        tmp_path = f.name

    try:
        valid, err, track = validate_track_file(tmp_path)
        assert valid
        assert err is None
        assert track is not None
        assert track.turns is not None
        assert len(track.turns) == 1
        turn = track.turns[0]
        assert turn.name == "T1"
        assert turn.type == "left"
        assert turn.apex_coordinates == [31.05, 121.05]
        assert not hasattr(turn, 'id')
        assert not hasattr(turn, 'number')
    finally:
        os.unlink(tmp_path)


def test_validate_turn_missing_apex_coordinates():
    """测试校验：弯道缺少 apex_coordinates 应该失败"""
    invalid_track = {
        "id": "test_turns",
        "name": "Test Track with Turns",
        "length_m": 1000.0,
        "turn_count": 1,
        "anchor": {"lat": 31.0, "lon": 121.0, "radius_m": 1000.0},
        "gate": [[31.0, 121.0], [31.1, 121.1]],
        "centerline": [[31.0, 121.0], [31.1, 121.1], [31.2, 121.2]],
        "turns": [
            {
                "name": "T1",
                "type": "left",
                "start_distance_m": 100.0,
                "apex_distance_m": 150.0,
                "end_distance_m": 200.0
                # missing apex_coordinates
            }
        ]
    }
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(invalid_track, f)
        tmp_path = f.name

    try:
        valid, err, track = validate_track_file(tmp_path)
        assert not valid
        assert err is not None
        assert "apex_coordinates" in err
        assert track is None
    finally:
        os.unlink(tmp_path)


def test_validate_turn_apex_coordinates_wrong_length():
    """测试校验：apex_coordinates 不是两个数应该失败"""
    invalid_track = {
        "id": "test_turns",
        "name": "Test Track with Turns",
        "length_m": 1000.0,
        "turn_count": 1,
        "anchor": {"lat": 31.0, "lon": 121.0, "radius_m": 1000.0},
        "gate": [[31.0, 121.0], [31.1, 121.1]],
        "centerline": [[31.0, 121.0], [31.1, 121.1], [31.2, 121.2]],
        "turns": [
            {
                "name": "T1",
                "type": "left",
                "start_distance_m": 100.0,
                "apex_distance_m": 150.0,
                "apex_coordinates": [31.05],  # only one coordinate
                "end_distance_m": 200.0
            }
        ]
    }
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(invalid_track, f)
        tmp_path = f.name

    try:
        valid, err, track = validate_track_file(tmp_path)
        assert not valid
        assert err is not None
        assert "apex_coordinates" in err
        assert track is None
    finally:
        os.unlink(tmp_path)
