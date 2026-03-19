# -*- coding: utf-8 -*-
"""
Late Brake - Input Format Parsers

支持多种输入格式解析，统一输出 List[DataPoint]
"""

from typing import List, Optional
from late_brake.models import DataPoint

from .nmea import parse_nmea_file


def parse_file(file_path: str) -> Optional[List[DataPoint]]:
    """根据文件扩展名自动选择解析器"""
    ext = file_path.split('.')[-1].lower()
    if ext in ('nmea', 'log', 'txt'):
        # 尝试作为NMEA解析
        try:
            points = parse_nmea_file(file_path)
            if len(points) > 0:
                return points
            else:
                return None
        except Exception:
            return None
    # 其他格式后续添加
    return None
