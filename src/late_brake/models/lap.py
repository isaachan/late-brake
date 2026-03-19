# -*- coding: utf-8 -*-
"""
Late Brake - Lap Model
统一内部数据格式 - 单圈定义

遵循 docs/data-format.md 规范
"""

from pydantic import BaseModel, Field
from typing import List

from .point import DataPoint


class Lap(BaseModel):
    """单个圈速数据，包含所有采样点和圈信息"""

    id: str = Field(
        ...,
        description="Lap ID (如 \"file1.Lap1\")"
    )
    source_file: str = Field(
        ...,
        description="源文件路径"
    )
    lap_number: int = Field(
        ...,
        description="圈号"
    )
    total_time: float = Field(
        ...,
        description="总圈时（秒）"
    )
    start_time: float = Field(
        ...,
        description="单圈起始时间（秒，相对于整个数据记录开始）"
    )
    end_time: float = Field(
        ...,
        description="单圈结束时间（秒，相对于整个数据记录开始）"
    )
    start_distance: float = Field(
        ...,
        description="起始点累计距离（米，相对于整个数据记录开始）"
    )
    end_distance: float = Field(
        ...,
        description="结束点累计距离（米，相对于整个数据记录开始）"
    )
    is_complete: bool = Field(
        ...,
        description="是否为完整圈。true = 通过起跑线完整绕一圈，false = 半路出发/半路结束，不完整"
    )
    lap_distance: float = Field(
        ...,
        description="单圈实际行驶距离（米）= end_distance - start_distance"
    )
    points: List[DataPoint] = Field(
        ...,
        description="数据点数组，包含圈中所有采样点"
    )

    model_config = {
        "extra": "forbid",
    }
