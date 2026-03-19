# -*- coding: utf-8 -*-
"""
Late Brake - CLI Entry Point

US-013: 赛道管理CLI框架 (track list/info/add)
US-010: 单次执行退出模式
US-011: 默认文本输出
US-012: JSON输出支持
"""

import json
import click
from typing import List, Optional

from late_brake.io.track_store import (
    list_all_tracks,
    get_track_by_id,
    add_track_from_file,
)
from late_brake.models import Track


def print_track_list_text(tracks: List[Track]) -> None:
    """默认文本格式输出赛道列表"""
    if not tracks:
        click.echo("没有已配置的赛道")
        return

    click.echo(f"\n已配置赛道 ({len(tracks)}):\n")
    for track in tracks:
        full_name = track.full_name if track.full_name else track.name
        if full_name != track.name:
            click.echo(f"  {track.id:6} - {full_name} ({track.name}) - {track.length_m}m, {track.turn_count} 弯道")
        else:
            click.echo(f"  {track.id:6} - {track.name} - {track.length_m}m, {track.turn_count} 弯道")
    click.echo()


def print_track_list_json(tracks: List[Track]) -> None:
    """JSON格式输出赛道列表"""
    data = [track.model_dump() for track in tracks]
    click.echo(json.dumps(data, indent=2, ensure_ascii=False))


def print_track_info_text(track: Track) -> None:
    """默认文本格式输出赛道详情"""
    click.echo()
    click.echo(f"ID:          {track.id}")
    click.echo(f"名称:        {track.name}")
    if track.full_name:
        click.echo(f"中文名:      {track.full_name}")
    if track.location:
        click.echo(f"位置:        {track.location}")
    click.echo(f"长度:        {track.length_m} 米")
    click.echo(f"弯道数:      {track.turn_count}")

    if track.sectors:
        click.echo(f"分段:        {len(track.sectors)} 个分段")
        for sector in track.sectors:
            turns = f"({len(sector.turns)} 弯道)" if sector.turns else ""
            click.echo(f"  - {sector.name}: {sector.start_distance_m}m - {sector.end_distance_m}m {turns}")

    if track.turns:
        click.echo(f"弯道:        {len(track.turns)} 个弯道")
        for turn in track.turns[:5]:
            click.echo(f"  - {turn.name}: {turn.type}, {turn.start_distance_m}m-{turn.end_distance_m}m")
        if len(track.turns) > 5:
            click.echo(f"  ... 还有 {len(track.turns) - 5} 个弯道")

    click.echo()


def print_track_info_json(track: Track) -> None:
    """JSON格式输出赛道详情"""
    click.echo(json.dumps(track.model_dump(), indent=2, ensure_ascii=False))


@click.group(invoke_without_command=False)
@click.version_option()
def cli():
    """Late Brake - 赛车圈速数据分析命令行工具

    用于对比分析不同圈速数据，帮助找出最佳走线和刹车时机。
    """
    pass


@click.group(name="track")
def track_group():
    """赛道管理命令

    管理内置和自定义赛道数据。
    """
    pass


@track_group.command(name="list")
@click.option("--json", "output_json", is_flag=True, default=False, help="输出JSON格式")
def track_list(output_json: bool):
    """列出所有已配置赛道"""
    tracks = list_all_tracks()
    if output_json:
        print_track_list_json(tracks)
    else:
        print_track_list_text(tracks)


@track_group.command(name="info")
@click.argument("track_id")
@click.option("--json", "output_json", is_flag=True, default=False, help="输出JSON格式")
def track_info(track_id: str, output_json: bool):
    """显示指定赛道详细信息"""
    track = get_track_by_id(track_id)
    if track is None:
        click.echo(f"错误: 赛道ID '{track_id}' 不存在")
        raise SystemExit(1)

    if output_json:
        print_track_info_json(track)
    else:
        print_track_info_text(track)


@track_group.command(name="add")
@click.argument("track_json_file")
def track_add(track_json_file: str):
    """从JSON文件添加或更新赛道"""
    success, msg, track = add_track_from_file(track_json_file)
    if not success:
        click.echo(f"错误: {msg}")
        raise SystemExit(1)

    click.echo()
    click.echo(f"✓ {msg}")
    click.echo()


# 注册子命令
cli.add_command(track_group)


@click.command(name="load")
@click.argument("data_files", nargs=-1, required=True)
@click.option("--track", "track_id", default=None, help="手动指定赛道ID")
@click.option("--json", "output_json", is_flag=True, default=False, help="输出JSON格式")
def load_command(data_files, track_id, output_json):
    """加载数据文件，自动匹配赛道并分割圈速，输出圈速列表"""
    from late_brake.io.parsers import parse_file
    from late_brake.core.matcher import match_track
    from late_brake.io.track_store import get_track_by_id
    from late_brake.core.splitter import split_laps

    results = []
    any_failed = False

    for file_path in data_files:
        result = {
            "path": file_path,
            "success": False,
            "lap_count": 0,
            "laps": [],
            "error": None,
        }

        # 解析文件
        points = parse_file(file_path)
        if points is None or len(points) == 0:
            result["error"] = "无法解析文件或没有有效数据点"
            results.append(result)
            any_failed = True
            continue

        # 获取赛道
        if track_id is not None:
            track = get_track_by_id(track_id)
            if track is None:
                result["error"] = f"指定的赛道ID '{track_id}' 不存在"
                results.append(result)
                any_failed = True
                continue
            match_msg = f"手动指定赛道: {track.id}"
        else:
            # 自动匹配
            track, match_msg = match_track(points)
            if track is None:
                result["error"] = match_msg
                results.append(result)
                any_failed = True
                continue

        # 分割圈速
        laps = split_laps(points, track, file_path)
        if not laps:
            result["error"] = "未能检测到任何圈速，请检查赛道是否正确"
            results.append(result)
            any_failed = True
            continue

        result["success"] = True
        result["lap_count"] = len(laps)
        result["laps"] = [
            {
                "number": lap.lap_number,
                "time": lap.total_time,
                "is_complete": lap.is_complete,
            }
            for lap in laps
        ]
        result["track_id"] = track.id
        result["track_name"] = track.name
        results.append(result)

    # 输出
    if output_json:
        click.echo(json.dumps({
            "files": results
        }, indent=2, ensure_ascii=False))
    else:
        click.echo()
        for res in results:
            click.echo(f"文件: {res['path']}")
            if not res["success"]:
                click.echo(f"  错误: {res['error']}")
            else:
                click.echo(f"  赛道: {res['track_id']} - {res['track_name']}")
                click.echo(f"  共 {res['lap_count']} 圈")
                for lap in res["laps"]:
                    mark = "" if lap["is_complete"] else " (不完整)"
                    minutes = int(lap["time"] // 60)
                    seconds = lap["time"] % 60
                    if minutes > 0:
                        time_str = f"{minutes}:{seconds:06.3f}"
                    else:
                        time_str = f"{seconds:.3f}"
                    click.echo(f"  Lap {lap['number']}: {time_str}{mark}")
            click.echo()

    if any_failed:
        raise SystemExit(1)


# 注册子命令
cli.add_command(load_command)


def main():
    """CLI入口点，单次执行后退出（US-010）"""
    cli()


if __name__ == "__main__":
    main()
