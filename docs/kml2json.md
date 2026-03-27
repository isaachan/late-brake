# KML to Track JSON Conversion

## Overview

`scripts/kml2json.py` converts a KML file containing race track waypoints to the JSON format used by `late-brake` for track data.

## KML Structure Requirements

The KML file must follow this folder structure:

```
Document/
├── geofence/               # Track boundary
│   └── Placemark (LineString)
│       └── coordinates     # Boundary points
├── centerline/             # Track center line
│   └── Placemark (LineString)
│       └── coordinates     # Center line points
├── turns/                  # Turn apex information
│   ├── T1 (Placemark)
│   │   ├── Point/coordinates
│   │   └── ExtendedData
│   │       ├── Data name="type"         # left/right
│   │       ├── Data name="radius_m"     # turn radius
│   │       ├── Data name="min_speed_target"  # minimum speed target
│   │       └── Data name="sector"       # sector number
│   ├── T2...
│   └── ...
├── turns-distances/        # Turn entry/apex/exit markers
│   ├── T1-Entry (Placemark Point)   # Turn entry point
│   ├── T1-P (Placemark Point)       # Apex (apex point)
│   ├── T1-Exit (Placemark Point)    # Turn exit point
│   ├── T2-Entry...
│   └── ...
├── gate/                   # Start/Finish line (two points)
│   ├── gate-1 (Placemark Point)
│   └── gate-2 (Placemark Point)
└── anchor/                 # Track center anchor
    └── Placemark Point
    └── ExtendedData
        └── Data name="radius_m"    # Anchor search radius
```

## Conversion Logic

### 1. Coordinate Extraction
- `geofence`: Extract all coordinates from the LineString → `geofence[]` (array of `[lat, lon]`)
- `centerline`: Extract all coordinates from the LineString → `centerline[]` (array of `[lat, lon]`)

### 2. Distance Calculation
- Use **Haversine formula** to calculate cumulative distance along the centerline from the start point
- Total track length = last cumulative distance value

### 3. Anchor
- Extract center point and radius from `anchor` folder → `anchor { lat, lon, radius_m }`

### 4. Start/Finish Gate
- Extract two points from `gate` folder
- Sort by distance from start → `gate[first, second]`
- Result: `gate[]` (array of two `[lat, lon]`)

### 5. Turns
1. From `turns` folder:
   - Get turn name, apex coordinates, extended data (`type`, `radius_m`, `min_speed_target`, `sector`)
   
2. From `turns-distances` folder:
   - Match `T<N>-Entry`, `T<N>-P`, `T<N>-Exit` points
   
3. Calculate distances:
   - `start_distance_m`: distance of Entry point from start along centerline
   - `apex_distance_m`: distance of apex point from start along centerline
   - `end_distance_m`: distance of Exit point from start along centerline

### 6. Sectors
Sectors are automatically generated following these rules:

1. **Grouping**: Group turns by the `sector` value from ExtendedData
2. **Sorting**: Sort sectors by sector ID
3. **Start distance**:
   - First sector: `start_distance_m = 0` (starts at start/finish line)
   - Other sectors: midpoint between **previous sector last turn exit** and **current sector first turn entry**, get distance of this midpoint
4. **End distance**:
   - Last sector: `end_distance_m = total_length` (ends at start/finish line)
   - Other sectors: midpoint between **current sector last turn exit** and **next sector first turn entry**, get distance of this midpoint

## Usage

```bash
python3 scripts/kml2json.py \
  <input-kml> \
  <output-json> \
  --id <track-id> \
  --name "Track Name" \
  --full-name "Track Full Name" \
  --location "City, Country"
```

### Example

```bash
python3 scripts/kml2json.py \
  sample-data/tracks/Shanghai-Tianma.kml \
  sample-data/tracks/tianma.json \
  --id tianma \
  --name "Shanghai Tianma Circuit" \
  --full-name "上海天马赛车场" \
  --location "Shanghai, China"
```

## Output JSON Schema

```javascript
{
  "id": "tianma",                    // Track ID (short, lowercase)
  "name": "Shanghai Tianma Circuit", // Track name
  "full_name": "上海天马赛车场",      // Full name (optional)
  "location": "Shanghai, China",      // Location (optional)
  "length_m": 2044,                  // Total track length in meters
  "turn_count": 14,                  // Number of turns
  "anchor": {                        // Center anchor for map display
    "lat": 31.07938,
    "lon": 121.11454,
    "radius_m": 300
  },
  "gate": [             // Start/finish line (two points)
    [lat1, lon1],
    [lat2, lon2]
  ],
  "geofence": [         // Track boundary polygon
    [lat, lon],
    ...
  ],
  "centerline": [       // Track center line points
    [lat, lon],
    ...
  ],
  "turns": [            // Turn information
    {
      "name": "T1",
      "type": "left",               // left/right
      "apex_coordinates": [lat, lon],
      "start_distance_m": 107,      // Distance from start to turn entry
      "apex_distance_m": 171,       // Distance from start to apex
      "end_distance_m": 179,        // Distance from start to turn exit
      "radius_m": 20,               // Turn radius in meters
      "min_speed_target": 165,      // Minimum speed target (km/h)
      "sector": 1                   // Sector number
    },
    ...
  ],
  "sectors": [          // Sector information
    {
      "id": 1,
      "name": "Sector 1",
      "start_distance_m": 0,
      "end_distance_m": 485,
      "turns": ["1", "2", "3"]      // Turn numbers in this sector
    },
    ...
  ]
}
```

## Notes

- Coordinate order: `[lat, lon]` (latitude first, longitude second)
- All distances are in **meters**
- Speed targets are in **km/h**
- Distance calculation uses Haversine formula for approximate geodesic distance on Earth
- Entry/apex/exit distances are calculated by finding the closest point on the centerline
