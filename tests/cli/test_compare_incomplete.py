# -*- coding: utf-8 -*-
"""
Test US-032: Prevent comparing incomplete laps
"""
import json
import tempfile
import os
from click.testing import CliRunner
from late_brake.cli import cli


def create_test_lap_cache(file_path: str, is_complete1: bool, is_complete2: bool):
    """创建一个测试用的缓存文件，包含两个圈"""
    from late_brake.models import Lap, DataPoint

    # 创建两个空数据点
    points1 = [
        DataPoint(timestamp=0, latitude=31.0, longitude=121.0, speed=100.0, distance=0.0),
        DataPoint(timestamp=1, latitude=31.1, longitude=121.1, speed=100.0, distance=100.0),
    ]
    points2 = [
        DataPoint(timestamp=2, latitude=31.2, longitude=121.2, speed=100.0, distance=200.0),
        DataPoint(timestamp=3, latitude=31.3, longitude=121.3, speed=100.0, distance=300.0),
    ]

    lap1 = Lap(
        id="test1",
        source_file=file_path,
        lap_number=1,
        total_time=60.0,
        start_time=0,
        end_time=60.0,
        start_distance=0,
        end_distance=2063.0,
        is_complete=is_complete1,
        lap_distance=2063.0,
        points=points1
    )
    lap2 = Lap(
        id="test2",
        source_file=file_path,
        lap_number=2,
        total_time=61.0,
        start_time=60.0,
        end_time=121.0,
        start_distance=2063.0,
        end_distance=4126.0,
        is_complete=is_complete2,
        lap_distance=2063.0,
        points=points2
    )

    cache_data = {
        "track_id": "tianma",
        "laps": [lap1.model_dump(), lap2.model_dump()]
    }

    file_dir = os.path.dirname(file_path)
    base_name = os.path.basename(file_path)
    cache_path = os.path.join(file_dir, f".{base_name}.lb.json")
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache_data, f)

    return cache_path


def test_compare_one_incomplete_lap():
    """测试对比一个完整圈和一个不完整圈，应该拒绝"""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建测试文件（空文件就行，缓存会被命中）
        test_file = os.path.join(tmpdir, "test.nmea")
        with open(test_file, "w") as f:
            f.write("")

        cache_path = create_test_lap_cache(test_file, True, False)

        try:
            # 对比 lap 1 (完整) vs lap 2 (不完整)
            result = runner.invoke(cli, [
                "compare", test_file, "1", test_file, "2", "--track", "tianma"
            ])

            assert result.exit_code != 0
            assert "错误" in result.output
            assert "无法对比不完整圈" in result.output
            assert "圈 2" in result.output
        finally:
            if os.path.exists(cache_path):
                os.unlink(cache_path)


def test_compare_both_incomplete_laps():
    """测试对比两个不完整圈，应该拒绝"""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.nmea")
        with open(test_file, "w") as f:
            f.write("")

        cache_path = create_test_lap_cache(test_file, False, False)

        try:
            result = runner.invoke(cli, [
                "compare", test_file, "1", test_file, "2", "--track", "tianma"
            ])

            assert result.exit_code != 0
            assert "错误" in result.output
            assert "无法对比不完整圈" in result.output
            assert "圈 1" in result.output
            assert "圈 2" in result.output
        finally:
            if os.path.exists(cache_path):
                os.unlink(cache_path)


def test_compare_both_complete_laps():
    """测试对比两个完整圈，应该正常执行"""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.nmea")
        with open(test_file, "w") as f:
            f.write("")

        cache_path = create_test_lap_cache(test_file, True, True)

        try:
            result = runner.invoke(cli, [
                "compare", test_file, "1", test_file, "2", "--track", "tianma"
            ])

            # 能正常执行到对比完成（虽然两个圈数据太少，但不会在检查步骤就拒绝）
            assert result.exit_code == 0
            assert "对比" in result.output
        finally:
            if os.path.exists(cache_path):
                os.unlink(cache_path)


def test_compare_incomplete_json_output():
    """测试 --json 输出时，错误也输出 JSON"""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.nmea")
        with open(test_file, "w") as f:
            f.write("")

        cache_path = create_test_lap_cache(test_file, True, False)

        try:
            result = runner.invoke(cli, [
                "compare", test_file, "1", test_file, "2", "--track", "tianma", "--json"
            ])

            assert result.exit_code != 0
            # 输出是 JSON
            output_json = json.loads(result.output)
            assert "error" in output_json
            assert "无法对比不完整圈" in output_json["error"]
        finally:
            if os.path.exists(cache_path):
                os.unlink(cache_path)
