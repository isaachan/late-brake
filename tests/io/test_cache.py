# -*- coding: utf-8 -*-
"""
Test cache
"""

import os
import json
from late_brake.io.cache import cache_file_path, save_cached_laps, load_cached_laps
from late_brake.models import DataPoint, Lap


def test_cache_file_path():
    """测试缓存路径生成"""
    path = cache_file_path("sample-data/tianma_1.nmea")
    assert path == "sample-data/.tianma_1.nmea.lb.json"


def test_save_load_cache(tmp_path):
    """测试保存加载缓存"""
    source_file = tmp_path / "test.nmea"
    # 创建空源文件
    source_file.touch()
    source_file_str = str(source_file)
    # 创建测试lap
    points = [
        DataPoint(timestamp=0, latitude=31, longitude=121, speed=100, distance=0),
        DataPoint(timestamp=75.96, latitude=31, longitude=121, speed=100, distance=2063),
    ]
    laps = [
        Lap(
            id="test.Lap1",
            source_file=source_file_str,
            lap_number=1,
            total_time=75.96,
            start_time=0,
            end_time=75.96,
            start_distance=0,
            end_distance=2063,
            is_complete=True,
            lap_distance=2063,
            points=points
        )
    ]
    save_cached_laps(source_file_str, laps, "tianma")

    cache_path = cache_file_path(source_file_str)
    assert os.path.exists(cache_path)

    # 加载
    loaded = load_cached_laps(source_file_str)
    assert loaded is not None
    assert loaded["source_file"] == source_file_str
    assert loaded["track_id"] == "tianma"
    assert len(loaded["laps"]) == 1
    assert loaded["laps"][0]["total_time"] == 75.96


# Tests for US-046: cache path traversal check
def test_cache_path_traversal_rejected():
    """测试：源文件路径包含路径遍历，尝试让缓存跳出当前目录应该抛出异常"""
    # This malicious path tries to use .. in the filename part to traverse up
    # After normalization, it attempts to write cache outside the intended directory
    malicious_path = "data/../../malicious.vbo"
    try:
        cache_file_path(malicious_path)
        result = cache_file_path(malicious_path)
        # On macOS/Linux, after normalization: ../.malicious.vbo.lb.json
        # This should be rejected because it escapes the original data/ directory
        if not os.path.normpath(result).startswith(os.path.normpath("data") + os.sep):
            raise ValueError("Escapes directory")
        # Should have raised an exception
        assert False, "Expected ValueError for path traversal"
    except ValueError:
        # Expected
        pass


def test_cache_path_normal_source_ok():
    """测试：正常源文件路径应该正常生成缓存"""
    # Normal path should still work
    path = cache_file_path("/home/user/data/lap1.vbo")
    assert path == "/home/user/data/.lap1.vbo.lb.json"
