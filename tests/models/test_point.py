# -*- coding: utf-8 -*-
"""
Test DataPoint model
"""

import pytest
from late_brake.models import DataPoint


def test_data_point_minimal():
    """测试创建最小必填字段的DataPoint"""
    p = DataPoint(
        timestamp=0.0,
        latitude=31.0,
        longitude=121.0,
        speed=100.0,
        distance=0.0
    )
    assert p.timestamp == 0.0
    assert p.latitude == 31.0
    assert p.longitude == 121.0
    assert p.speed == 100.0
    assert p.distance == 0.0
    assert p.altitude is None
    assert p.g_force_x is None


def test_data_point_with_optional():
    """测试带可选字段的DataPoint"""
    p = DataPoint(
        timestamp=1.0,
        latitude=31.0,
        longitude=121.0,
        speed=100.0,
        distance=10.0,
        g_force_x=0.5,
        g_force_y=-1.0,
        throttle_position=80.0,
        brake_pressure=0.0,
    )
    assert p.g_force_x == 0.5
    assert p.g_force_y == -1.0
    assert p.throttle_position == 80.0
    assert p.brake_pressure == 0.0


def test_data_point_missing_required():
    """测试缺少必填字段应该报错"""
    with pytest.raises(Exception):
        DataPoint(
            timestamp=0.0,
            latitude=31.0,
            # missing longitude
            speed=100.0,
            distance=0.0
        )
