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


def main():
    """CLI入口点，单次执行后退出（US-010）"""
    cli()


if __name__ == "__main__":
    main()
