# -*- coding: utf-8 -*-
"""
Late Brake - Lap Comparator

对比两个圈速数据，计算时间差和速度差

US-007 / US-008 / US-009 / US-020 基础对比功能
"""

from typing import List, Tuple, Optional, Dict
import numpy as np

from late_brake.models import Track, Lap, DataPoint


def resample_lap(lap: Lap, step_m: float = 1.0) -> Tuple[np.ndarray, np.ndarray]:
    """
    按距离对圈速数据重采样
    返回 (distance数组, speed数组)
    distance: 0 ~ lap_distance，每 step_m 一个点
    """
    # 提取原始距离和速度
    distances = np.array([p.distance - lap.start_distance for p in lap.points])
    speeds = np.array([p.speed for p in lap.points])

    # 创建采样点
    total_dist = lap.lap_distance
    num_steps = int(np.floor(total_dist / step_m)) + 1
    sample_distances = np.linspace(0, total_dist, num_steps)

    # 线性插值
    sample_speeds = np.interp(sample_distances, distances, speeds)

    return sample_distances, sample_speeds


def compare_laps(
    lap1: Lap,
    lap2: Lap,
    track: Optional[Track] = None,
    step_m: float = 1.0
) -> Dict:
    """
    对比两个圈，返回对比结果
    包含：总时间差、分段时间差、速度差异
    """
    result = {
        "lap1": {
            "number": lap1.lap_number,
            "total_time": lap1.total_time,
            "distance": lap1.lap_distance,
        },
        "lap2": {
            "number": lap2.lap_number,
            "total_time": lap2.total_time,
            "distance": lap2.lap_distance,
        },
        "total_time_diff": lap2.total_time - lap1.total_time,
        "sector_diff": [],
    }

    # 重采样对齐
    dist1, speed1 = resample_lap(lap1, step_m)
    dist2, speed2 = resample_lap(lap2, step_m)

    # 计算速度差异统计
    min_len = min(len(dist1), len(dist2))
    speed_diff = speed2[:min_len] - speed1[:min_len]
    result["avg_speed_diff"] = float(np.mean(speed_diff))

    # 如果有赛道分段，计算分段时间差
    if track is not None and track.sectors is not None:
        for sector in track.sectors:
            # 在原始圈中计算分段时间
            t1 = sector_time(lap1, sector.start_distance_m, sector.end_distance_m)
            t2 = sector_time(lap2, sector.start_distance_m, sector.end_distance_m)
            result["sector_diff"].append({
                "sector_id": sector.id,
                "sector_name": sector.name,
                "start_distance": sector.start_distance_m,
                "end_distance": sector.end_distance_m,
                "time1": t1,
                "time2": t2,
                "time_diff": t2 - t1,
            })

    return result


def sector_time(lap: Lap, start_dist: float, end_dist: float) -> float:
    """
    计算圈在某分段（从start_dist到end_dist）所花时间
    """
    # 找到起点和终点
    start_point = None
    end_point = None

    for p in lap.points:
        dist_abs = p.distance - lap.start_distance
        if start_point is None and dist_abs >= start_dist:
            start_point = p
        if end_point is None and dist_abs >= end_dist:
            end_point = p
            break

    if start_point is None:
        return 0.0
    if end_point is None:
        if lap.points:
            end_point = lap.points[-1]
        else:
            return 0.0

    return end_point.timestamp - start_point.timestamp
