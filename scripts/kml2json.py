#!/usr/bin/env python3
"""
KML to Track JSON converter for late-brake
Converts a KML file with track waypoints to the late-brake track JSON format.
"""

import xml.etree.ElementTree as ET
import json
import math
from typing import List, Dict, Tuple, Optional

# KML namespace
NS = {'kml': 'http://www.opengis.net/kml/2.2'}

Point = Tuple[float, float]  # (lat, lon)

def parse_coordinates(coords_str: str) -> List[Point]:
    """Parse KML coordinates string into list of (lat, lon) points."""
    points = []
    for line in coords_str.strip().split():
        if not line:
            continue
        lon, lat, _ = line.split(',')
        points.append((float(lat), float(lon)))
    return points

def distance_between(p1: Point, p2: Point) -> float:
    """Calculate approximate distance between two lat/lon points in meters."""
    # Haversine formula
    lat1, lon1 = p1
    lat2, lon2 = p2
    R = 6371000  # Earth radius in meters
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi / 2)**2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def cumulative_distances(points: List[Point]) -> List[float]:
    """Calculate cumulative distance along a path from the start point."""
    distances = [0.0]
    current = 0.0
    for i in range(1, len(points)):
        current += distance_between(points[i-1], points[i])
        distances.append(current)
    return distances

def find_closest_point_distance(target: Point, centerline: List[Point], cum_dist: List[float]) -> float:
    """Find the closest point on centerline to target and return its distance from start."""
    min_dist = float('inf')
    closest_dist = 0.0
    for point, dist in zip(centerline, cum_dist):
        d = distance_between(target, point)
        if d < min_dist:
            min_dist = d
            closest_dist = dist
    return closest_dist

def midpoint(p1: Point, p2: Point) -> Point:
    """Calculate midpoint between two points."""
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)

def parse_kml(kml_path: str) -> Dict:
    """Parse KML file and extract all track data."""
    tree = ET.parse(kml_path)
    root = tree.getroot()
    doc = root.find('kml:Document', NS)
    
    # Extract folders
    folders = {}
    for folder in doc.findall('kml:Folder', NS):
        name = folder.find('kml:name', NS).text
        folders[name] = folder
    
    result = {}
    
    # 1. Extract geofence
    geofence_folder = folders.get('geofence')
    if geofence_folder:
        placemark = geofence_folder.find('kml:Placemark', NS)
        linestring = placemark.find('kml:LineString', NS)
        coords_str = linestring.find('kml:coordinates', NS).text
        result['geofence'] = parse_coordinates(coords_str)
    
    # 2. Extract centerline
    centerline_folder = folders.get('centerline')
    centerline_points = []
    if centerline_folder:
        placemark = centerline_folder.find('kml:Placemark', NS)
        linestring = placemark.find('kml:LineString', NS)
        coords_str = linestring.find('kml:coordinates', NS).text
        centerline_points = parse_coordinates(coords_str)
        result['centerline'] = centerline_points
    
    # Calculate cumulative distances along centerline
    cum_dist = cumulative_distances(centerline_points)
    total_length = cum_dist[-1] if cum_dist else 0.0
    
    # 3. Extract anchor
    anchor = None
    if 'anchor' in folders:
        anchor_folder = folders['anchor']
        placemark = anchor_folder.find('kml:Placemark', NS)
        point_elem = placemark.find('kml:Point', NS)
        coords_str = point_elem.find('kml:coordinates', NS).text
        lon, lat, _ = coords_str.strip().split(',')
        radius_m = 300.0
        # Try to get radius from ExtendedData
        extended_data = placemark.find('kml:ExtendedData', NS)
        if extended_data:
            for data in extended_data.findall('kml:Data', NS):
                if data.get('name') == 'radius_m':
                    value = data.find('kml:value', NS).text
                    radius_m = float(value)
                    break
        anchor = {
            'lat': float(lat),
            'lon': float(lon),
            'radius_m': radius_m
        }
        result['anchor'] = anchor
    
    # 4. Extract gate (two points)
    gate = []
    if 'gate' in folders:
        gate_folder = folders['gate']
        for placemark in gate_folder.findall('kml:Placemark', NS):
            point_elem = placemark.find('kml:Point', NS)
            coords_str = point_elem.find('kml:coordinates', NS).text
            lon, lat, _ = coords_str.strip().split(',')
            gate.append([float(lat), float(lon)])
        # Sort gate points by distance from start of centerline to get [start, end]
        if len(gate) == 2:
            d1 = find_closest_point_distance((gate[0][0], gate[0][1]), centerline_points, cum_dist)
            d2 = find_closest_point_distance((gate[1][0], gate[1][1]), centerline_points, cum_dist)
            if d1 > d2:
                gate.reverse()
        result['gate'] = gate
    
    # 5. Extract turns and their entry/apex/exit points
    turns_data = {}
    if 'turns' in folders:
        turns_folder = folders['turns']
        for placemark in turns_folder.findall('kml:Placemark', NS):
            name = placemark.find('kml:name', NS).text
            point_elem = placemark.find('kml:Point', NS)
            coords_str = point_elem.find('kml:coordinates', NS).text
            lon, lat, _ = coords_str.strip().split(',')
            apex_point = (float(lat), float(lon))
            
            # Extract extended data
            turn_info = {
                'name': name,
                'apex_point': apex_point
            }
            
            extended_data = placemark.find('kml:ExtendedData', NS)
            if extended_data:
                for data in extended_data.findall('kml:Data', NS):
                    data_name = data.get('name')
                    value = data.find('kml:value', NS).text
                    if data_name in ['type', 'radius_m', 'min_speed_target', 'sector']:
                        if data_name in ['radius_m', 'min_speed_target', 'sector']:
                            turn_info[data_name] = float(value)
                        else:
                            turn_info[data_name] = value
            
            turns_data[name] = turn_info
    
    # 6. Extract entry/p/exit points from turns-distances
    if 'turns-distances' in folders:
        td_folder = folders['turns-distances']
        for placemark in td_folder.findall('kml:Placemark', NS):
            full_name = placemark.find('kml:name', NS).text
            point_elem = placemark.find('kml:Point', NS)
            coords_str = point_elem.find('kml:coordinates', NS).text
            lon, lat, _ = coords_str.strip().split(',')
            point = (float(lat), float(lon))
            
            # Parse name: T1-Entry, T1-P, T1-Exit
            if '-' in full_name:
                turn_name, point_type = full_name.split('-', 1)
                if turn_name in turns_data:
                    if point_type == 'Entry':
                        turns_data[turn_name]['entry_point'] = point
                    elif point_type == 'P':
                        turns_data[turn_name]['p_point'] = point
                    elif point_type == 'Exit':
                        turns_data[turn_name]['exit_point'] = point
    
    # Convert to turns array with distances - sort by turn number
    def turn_sort_key(name):
        # T1 -> 1, T10 -> 10
        num_part = name[1:]
        try:
            return int(num_part)
        except ValueError:
            return name
    turns = []
    for turn_name in sorted(turns_data.keys(), key=turn_sort_key):
        td = turns_data[turn_name]
        entry_point = td.get('entry_point')
        exit_point = td.get('exit_point') or td.get('p_point')
        apex_point = td.get('apex_point') or td.get('p_point')
        
        turn = {
            'name': turn_name,
            'type': td.get('type'),
            'apex_coordinates': [apex_point[0], apex_point[1]],
            'radius_m': int(td.get('radius_m', 0)) if td.get('radius_m', 0).is_integer() else td.get('radius_m'),
            'min_speed_target': int(td.get('min_speed_target', 0)) if td.get('min_speed_target', 0).is_integer() else td.get('min_speed_target'),
        }
        
        # Calculate distances from start along centerline
        if entry_point:
            turn['start_distance_m'] = round(find_closest_point_distance(entry_point, centerline_points, cum_dist))
        if apex_point:
            turn['apex_distance_m'] = round(find_closest_point_distance(apex_point, centerline_points, cum_dist))
        if exit_point:
            turn['end_distance_m'] = round(find_closest_point_distance(exit_point, centerline_points, cum_dist))
        
        turns.append(turn)
    
    result['turns'] = turns
    
    # 7. Build sectors based on turn sector information
    sectors = []
    if turns:
        # Group turns by sector
        sector_groups: Dict[int, List[Dict]] = {}
        for turn in turns:
            sector_id = int(turns_data[turn['name']]['sector'])
            if sector_id not in sector_groups:
                sector_groups[sector_id] = []
            sector_groups[sector_id].append(turn)
        
        # Get sorted sector ids
        sorted_sector_ids = sorted(sector_groups.keys())
        
        for i, sector_id in enumerate(sorted_sector_ids):
            sector_turns = sector_groups[sector_id]
            first_turn = sector_turns[0]
            last_turn = sector_turns[-1]
            
            # Get start distance
            if i == 0:
                # First sector starts at 0
                start_dist = 0.0
            else:
                # Midpoint between previous sector last turn exit and this sector first turn entry
                prev_sector = sectors[i-1]
                prev_last_turn = sector_groups[sorted_sector_ids[i-1]][-1]
                if 'entry_point' in turns_data[first_turn['name']] and 'exit_point' in turns_data[prev_last_turn['name']]:
                    prev_exit = turns_data[prev_last_turn['name']]['exit_point']
                    curr_entry = turns_data[first_turn['name']]['entry_point']
                    mid = midpoint(prev_exit, curr_entry)
                    start_dist = find_closest_point_distance(mid, centerline_points, cum_dist)
                else:
                    # Fallback: previous sector end is start of this sector
                    start_dist = prev_sector['end_distance_m']
            
            # Get end distance
            if i == len(sorted_sector_ids) - 1:
                # Last sector ends at total length
                end_dist = total_length
            else:
                # Midpoint between this sector last turn exit and next sector first turn entry
                next_sector_id = sorted_sector_ids[i+1]
                next_first_turn = sector_groups[next_sector_id][0]
                if 'exit_point' in turns_data[last_turn['name']] and 'entry_point' in turns_data[next_first_turn['name']]:
                    curr_exit = turns_data[last_turn['name']]['exit_point']
                    next_entry = turns_data[next_first_turn['name']]['entry_point']
                    mid = midpoint(curr_exit, next_entry)
                    end_dist = find_closest_point_distance(mid, centerline_points, cum_dist)
                else:
                    # Fallback: use last turn end distance
                    end_dist = last_turn['end_distance_m']
            
            sectors.append({
                'id': sector_id,
                'name': f'Sector {sector_id}',
                'start_distance_m': round(start_dist),
                'end_distance_m': round(end_dist),
                'turns': [int(t['name'].replace('T', '')) for t in sector_turns]
            })
        
        result['sectors'] = sectors
    
    result['length_m'] = round(total_length)
    result['turn_count'] = len(turns)
    
    return result

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Convert KML to track JSON for late-brake')
    parser.add_argument('input', help='Input KML file path')
    parser.add_argument('output', help='Output JSON file path')
    parser.add_argument('--id', required=True, help='Track ID (e.g. tianma)')
    parser.add_argument('--name', required=True, help='Track name (e.g. Shanghai Tianma Circuit)')
    parser.add_argument('--full-name', help='Full name (e.g. 上海天马赛车场)')
    parser.add_argument('--location', help='Location (e.g. Shanghai, China)')
    args = parser.parse_args()
    
    # Parse KML
    data = parse_kml(args.input)
    
    # Add metadata
    data['id'] = args.id
    data['name'] = args.name
    if args.full_name:
        data['full_name'] = args.full_name
    if args.location:
        data['location'] = args.location
    
    # Write with nice formatting
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully converted to {args.output}")
    print(f"Track: {args.name}")
    print(f"Total length: {data['length_m']} m")
    print(f"Number of turns: {data['turn_count']}")
    if 'sectors' in data:
        print(f"Number of sectors: {len(data['sectors'])}")

if __name__ == '__main__':
    main()
