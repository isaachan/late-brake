"""
Late Brake CLI entry point.
"""

import click
import json
import sys
from typing import Optional

from late_brake.track import Track
from late_brake.track_manager import TrackManager


def format_time(seconds: float) -> str:
    """Format time in seconds to MM:SS.sss format."""
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes}:{secs:06.3f}"


@click.group()
@click.version_option()
@click.option('--json', 'output_json', is_flag=True, default=False, help='Output JSON instead of human-readable text')
@click.pass_context
def main(ctx, output_json):
    """Late Brake - CLI tool for lap time analysis and comparison in motorsport."""
    ctx.ensure_object(dict)
    ctx.obj['output_json'] = output_json


@main.group(name='track')
def track_group():
    """Track management commands."""
    pass


@track_group.command(name='list')
@click.pass_context
def track_list(ctx):
    """List all configured tracks."""
    tm = TrackManager()
    tracks = tm.list_tracks()
    
    if ctx.obj['output_json']:
        result = {
            "count": len(tracks),
            "tracks": [
                {
                    "id": t.id,
                    "name": t.name,
                    "full_name": t.full_name,
                    "length_m": t.length_m,
                    "turn_count": t.turn_count
                }
                for t in tracks
            ]
        }
        click.echo(json.dumps(result, indent=2))
        return
    
    click.echo(f"\n已配置赛道 ({len(tracks)}):\n")
    for track in tracks:
        name_display = track.full_name if track.full_name else track.name
        length_str = f"{track.length_m}m" if track.length_m is not None else "未知长度"
        turn_str = f"{track.turn_count} 弯道" if track.turn_count is not None else "未知弯道数"
        click.echo(f"  {track.id:<18} - {name_display} - {length_str}, {turn_str}")
    click.echo()


@track_group.command(name='info')
@click.argument('track_id')
@click.pass_context
def track_info(ctx, track_id):
    """Show detailed information about a specific track."""
    tm = TrackManager()
    track = tm.get_track(track_id)
    
    if track is None:
        click.echo(f"Error: Track '{track_id}' not found", err=True)
        sys.exit(1)
    
    if ctx.obj['output_json']:
        click.echo(json.dumps(track.model_dump(), indent=2))
        return
    
    click.echo(f"\nID:          {track.id}")
    click.echo(f"名称:        {track.name}")
    if track.full_name:
        click.echo(f"中文名:      {track.full_name}")
    if track.location:
        click.echo(f"位置:        {track.location}")
    length_str = str(track.length_m) if track.length_m is not None else "未知"
    click.echo(f"长度:        {length_str} 米")
    turn_str = str(track.turn_count) if track.turn_count is not None else "未知"
    click.echo(f"弯道数:      {turn_str}")
    
    if track.sectors:
        click.echo(f"分段:        {len(track.sectors)} 个分段")
        for sector in track.sectors:
            turns_str = ', '.join(str(t) for t in sector.turns) if sector.turns else '无'
            click.echo(f"  - {sector.name}: {sector.start_distance_m}m - {sector.end_distance_m}m ({len(sector.turns)} 弯道: {turns_str})")
    
    if track.turns:
        click.echo(f"\n弯道列表:")
        for turn in track.turns:
            click.echo(f"  {turn.name}: {turn.type}, {turn.start_distance_m}m - {turn.end_distance_m}m")
    
    click.echo()


@track_group.command(name='add')
@click.argument('json_file', type=click.Path(exists=True))
def track_add(json_file):
    """Add or update a track from a JSON file."""
    tm = TrackManager()
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        track = Track.model_validate(data)
        tm.add_track(track)
        click.echo(f"Successfully added track '{track.id}'")
    except Exception as e:
        click.echo(f"Error adding track: {str(e)}", err=True)
        sys.exit(1)


@main.command(name='load')
@click.argument('files', nargs=-1, required=True, type=click.Path(exists=True))
@click.option('--track', 'track_id', help='Manually specify track ID')
@click.pass_context
def load_files(ctx, files, track_id):
    """Load lap data from one or more files and list detected laps."""
    # TODO: Implementation in subsequent user story
    if ctx.obj['output_json']:
        result = {"files": []}
        for f in files:
            result["files"].append({
                "path": f,
                "lapCount": 0,
                "laps": []
            })
        click.echo(json.dumps(result, indent=2))
        return
    
    click.echo("\nLoad functionality not implemented yet.\n")


@main.command(name='compare')
@click.argument('file1')
@click.argument('lap1', type=int)
@click.argument('file2')
@click.argument('lap2', type=int)
@click.option('--track', 'track_id', help='Manually specify track ID')
@click.pass_context
def compare_laps(ctx, file1, lap1, file2, lap2, track_id):
    """Compare two specified laps from two files."""
    # TODO: Implementation in subsequent user story
    click.echo("\nCompare functionality not implemented yet.\n")
