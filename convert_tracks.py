#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量转换现有赛道 JSON 到符合 track-format.md 规范的格式
"""

import json
import os

# 已知赛道信息
TRACK_INFO = {
    "saic": {
        "full_name": "上海国际赛车场",
        "location": "Shanghai, China",
        "length_m": 5451,
        "turn_count": 16,
    },
    "tianma": {
        "full_name": "上海天马赛车场",
        "location": "Shanghai, China",
        "length_m": 2063,
        "turn_count": 8,
    },
    "my_private_track_1": {
        "full_name": "私有赛道 1",
        "location": "Private",
        "length_m": None,  # 需要估算，从centerline计算
        "turn_count": None,  # 留空
    }
}


def calculate_length_from_centerline(centerline):
    """从中心线计算大致长度（用于未知长度的赛道）"""
    from geographiclib.geodesic import Geodesic
    geod = Geodesic.WGS84
    total = 0.0
    for i in range(len(centerline) - 1):
        lat1, lon1 = centerline[i]
        lat2, lon2 = centerline[i + 1]
        result = geod.Inverse(lat1, lon1, lat2, lon2)
        total += result["s12"]
    return total


def convert_track(input_path, output_path):
    """转换单个赛道文件"""
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    track_id = data["id"]
    info = TRACK_INFO.get(track_id, {})

    # 添加缺失字段
    if "full_name" not in data and "full_name" in info:
        data["full_name"] = info["full_name"]
    if "location" not in data and "location" in info:
        data["location"] = info["location"]
    if "length_m" not in data:
        if "length_m" in info and info["length_m"] is not None:
            data["length_m"] = info["length_m"]
        else:
            # 从中心线估算
            length = calculate_length_from_centerline(data["centerline"])
            data["length_m"] = round(length)
    if "turn_count" not in data:
        if "turn_count" in info and info["turn_count"] is not None:
            data["turn_count"] = info["turn_count"]
        else:
            data["turn_count"] = 0

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Converted: {track_id} -> {output_path} (length_m={data.get('length_m')}, turn_count={data.get('turn_count')})")
    return data


def main():
    tracks_dir = "/Users/kai.han/code/late-brake/src/late_brake/data/tracks"
    for filename in os.listdir(tracks_dir):
        if filename.endswith(".json"):
            input_path = os.path.join(tracks_dir, filename)
            output_path = input_path  # 覆盖
            convert_track(input_path, output_path)


if __name__ == "__main__":
    main()
