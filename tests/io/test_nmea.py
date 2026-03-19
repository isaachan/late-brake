# -*- coding: utf-8 -*-
"""
Test NMEA parsing
"""

import pytest
from late_brake.io.parsers.nmea import parse_nmea_coord, parse_nmea_file


def test_parse_nmea_coord():
    """测试坐标解析"""
    # 纬度 3116.62407,N -> 31 + 16.62407/60 ≈ 31.2770678
    lat = parse_nmea_coord("3116.62407", "N")
    assert lat == pytest.approx(31.2770678, rel=1e-5)

    # 经度 12111.62621,E -> 121 + 11.62621/60 ≈ 121.193770
    lon = parse_nmea_coord("12111.62621", "E")
    assert lon == pytest.approx(121.193770, rel=1e-5)

    # 南纬
    lat_s = parse_nmea_coord("3116.62407", "S")
    assert lat_s == pytest.approx(-31.2770678, rel=1e-5)


def test_parse_nmea_file():
    """测试解析完整文件"""
    points = parse_nmea_file("sample-data/private_1.nmea")
    assert points is not None
    assert len(points) > 6000
    # 第一个点
    assert points[0].distance == 0.0
    # 最后一个点有累计距离
    assert points[-1].distance > 0
    # 速度单位转换正确：0.1517 knots -> 0.2809 km/h
    assert points[0].speed == pytest.approx(0.2809, rel=1e-3)


def test_parse_nmea_file_not_exist():
    """测试文件不存在返回None"""
    # 应该捕获异常返回 None
    points = parse_nmea_file("not_exist.nmea")
    assert points is None
