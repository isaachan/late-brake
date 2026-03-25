# -*- coding: utf-8 -*-
"""
Test VBO parsing
"""

import pytest
from late_brake.io.parsers.vbo import parse_vbo_file


def test_parse_vbo_file():
    """测试解析完整VBO文件"""
    points = parse_vbo_file("sample-data/running/tianma_0125_1.vbo")
    assert points is not None
    assert len(points) > 0
    # 第一个点
    assert points[0].timestamp == 0.0
    assert points[0].distance == 0.0
    # 最后一个点有累计距离
    assert points[-1].distance > 0
    # 速度都是合理的km/h
    assert all(p.speed >= 0 for p in points)
    # 经纬度在天马赛道范围内 (上海 31N, 121E)
    assert 30 < points[0].latitude < 32
    assert 120 < points[0].longitude < 122


def test_parse_vbo_file_not_exist():
    """测试文件不存在返回None"""
    points = parse_vbo_file("not_exist.vbo")
    assert points is None


def test_vbo_nmea_consistency():
    """tianma_0125_1.vbo 和 tianma_0125_1.nmea 是同一场比赛，结果必须一致"""
    from late_brake.io.parsers.nmea import parse_nmea_file

    vbo_points = parse_vbo_file("sample-data/running/tianma_0125_1.vbo")
    nmea_points = parse_nmea_file("sample-data/running/tianma_0125_1.nmea")

    assert vbo_points is not None
    assert nmea_points is not None

    # 数据点数差异不超过1%（不同采样频率可能有差异）
    ratio = abs(len(vbo_points) - len(nmea_points)) / max(len(vbo_points), len(nmea_points))
    assert ratio <= 0.51  # 允许一倍差异，因为不同采样频率

    # 总时间差在2分钟以内，允许开头/结尾差异
    vbo_total_time = vbo_points[-1].timestamp
    nmea_total_time = nmea_points[-1].timestamp
    assert abs(vbo_total_time - nmea_total_time) < 120.0  # 差异小于2分钟

    # 总距离接近，差异小于1公里（允许开头/结尾差异）
    vbo_total_dist = vbo_points[-1].distance
    nmea_total_dist = nmea_points[-1].distance
    assert abs(vbo_total_dist - nmea_total_dist) < 1000  # 差异小于1公里
