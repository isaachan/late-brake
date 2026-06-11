# How to Add a New Input File Format

Late Brake ships with two input parsers: NMEA 0183 (`src/late_brake/io/parsers/nmea.py`)
and VBO / RaceChrono Pro (`src/late_brake/io/parsers/vbo.py`). This guide explains how to
add support for another format — GPX, CSV, FIT, or anything else that records a GPS lap
session.

The short version: **write one function that turns a file into `List[DataPoint]`, and
register its file extension in the dispatcher.** Everything downstream — track matching,
lap splitting, comparison, caching, the CLI — is format-agnostic and needs no changes.

---

## 1. Architecture overview

```
input file
   │
   ▼
parse_file()                    src/late_brake/io/parsers/__init__.py  ← add dispatch here
   │  (extension-based dispatch)
   ▼
parse_<format>_file()           src/late_brake/io/parsers/<format>.py  ← your new module
   │
   ▼
List[DataPoint]                 src/late_brake/models/point.py
   │
   ▼
matcher / splitter / comparator / cache / CLI   (format-agnostic)
```

The CLI calls the dispatcher in exactly two places (`load` and `compare` commands in
`src/late_brake/cli.py`), both through `parse_file(file_path)`. The cache layer
(`src/late_brake/io/cache.py`) stores already-split laps as `.{filename}.lb.json` next to
the source file, keyed by mtime — it never touches the raw format, so a new parser needs
zero cache changes.

## 2. The parser contract

Create `src/late_brake/io/parsers/<format>.py` exposing one function:

```python
def parse_<format>_file(file_path: str) -> Optional[List[DataPoint]]:
```

Behavioral rules (match the existing parsers exactly):

- **Return `None`** when the file does not exist (`except FileNotFoundError: return None`)
  or when zero valid points were parsed (`return points if points else None`).
- **Never raise on bad data.** Skip malformed lines/records and keep going — see the
  per-line `try/except (ValueError, KeyError): continue` pattern in `vbo.py` and the
  equivalent `(ValueError, IndexError)` handling in `nmea.py`. A single corrupt sample
  must not lose the session.
- Open text files defensively: `encoding=..., errors="replace"`.

### Required `DataPoint` fields and units

Every point must populate these five fields (see `src/late_brake/models/point.py` and
`docs/data-format.md`):

| Field | Unit / convention |
|---|---|
| `timestamp` | **relative seconds**, 0.0 at the first point of the file |
| `latitude` | WGS84 decimal degrees (south negative) |
| `longitude` | WGS84 decimal degrees (west negative) |
| `speed` | **km/h** (convert! NMEA gives knots × 1.852; GPX usually gives nothing — see §6) |
| `distance` | **cumulative meters** from the start of the file, 0.0 at the first point |

Optional fields (`altitude`, `g_force_x/y/z`, `steering_angle`, `throttle_position`,
`brake_pressure`, `rpm`, `gear`) should be filled when the source format has them —
formats like RaceChrono CSV or FIT carry far more channels than NMEA.

Do **not** round values in the parser. The US-040 precision convention (timestamps to 4
decimals, coordinates to 7, speed/distance to 2, etc.) is enforced by the
`field_serializer`s on `DataPoint` at serialization time; parsers store full precision.

## 3. Distance accumulation recipe

`distance` is the universal alignment key for everything downstream (see
[`algorithms.md`](algorithms.md) §1), so compute it the same way as the existing parsers:
accumulate WGS84 geodesic steps between consecutive fixes, even if the source format has
its own distance channel.

```python
from geographiclib.geodesic import Geodesic
geod = Geodesic.WGS84

# inside the point loop:
if last_lat is not None and last_lon is not None:
    total_distance += geod.Inverse(last_lat, last_lon, lat, lon)["s12"]
else:
    total_distance = 0.0
last_lat, last_lon = lat, lon
```

This is the reference implementation used in both `nmea.py` and `vbo.py`. Computing it
yourself (rather than trusting the source's odometer channel) keeps distance semantics
identical across formats, which is what makes the cross-format consistency tests in §5
possible.

## 4. Registration in the dispatcher

Add a branch to `parse_file()` in `src/late_brake/io/parsers/__init__.py`, mirroring the
existing ones:

```python
from .gpx import parse_gpx_file   # alongside the existing imports

# inside parse_file(), before the final `return None`:
if ext == 'gpx':
    try:
        points = parse_gpx_file(file_path)
        if points and len(points) > 0:
            return points
    except Exception:
        return None
```

Notes:

- The dispatcher matches on the **last extension segment, lowercased**
  (`file_path.split('.')[-1].lower()`).
- `.nmea`, `.log` and `.txt` are already claimed by the NMEA parser; pick an extension
  that doesn't collide, or extend the NMEA branch's fallback logic deliberately.
- `parse_file()` returning `None` is the single error signal the CLI understands — it
  prints the "unsupported/unparseable file" message. Keep that contract.

No other wiring is needed. The CLI, cache, splitter and comparator pick up the new format
automatically.

## 5. Testing checklist

Add `tests/io/test_<format>.py`, modeled on `tests/io/test_vbo.py`:

1. **Sample file** — commit a real (or trimmed) recording under `sample-data/`. Existing
   samples live in `sample-data/running/` (e.g. `tianma_0125_1.vbo`).
2. **Happy path** — parse the sample and assert:
   - a plausible point count;
   - `points[0].timestamp == 0` and timestamps are non-decreasing;
   - `points[0].distance == 0` and `points[-1].distance > 0`;
   - coordinates fall inside the expected bounding box;
   - speed values are in a sane km/h range (catches missed unit conversion).
3. **Missing file** — `parse_<format>_file("does/not/exist") is None`.
4. **Cross-format consistency** (strongly recommended when you can record the same
   session in two formats) — follow `test_vbo_nmea_consistency` in `test_vbo.py`: parse
   both files and assert total time within ~120 s, total distance within ~1000 m, and
   point counts within the expected sampling-rate ratio. This is the test that catches
   sign errors and unit mistakes that the happy path can't.

Run the suite with `python -m pytest`.

## 6. Worked skeleton: a hypothetical GPX parser

GPX is a good illustration because it lacks two of the required fields (speed, distance)
and both must be derived. Illustrative skeleton — not production code:

```python
# src/late_brake/io/parsers/gpx.py
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Optional
from geographiclib.geodesic import Geodesic

from late_brake.models import DataPoint

geod = Geodesic.WGS84
NS = {"gpx": "http://www.topografix.com/GPX/1/1"}


def parse_gpx_file(file_path: str) -> Optional[List[DataPoint]]:
    points: List[DataPoint] = []
    start_time = None
    last_lat = last_lon = last_t = None
    total_distance = 0.0

    try:
        root = ET.parse(file_path).getroot()
    except FileNotFoundError:
        return None
    except ET.ParseError:
        return None

    for trkpt in root.iterfind(".//gpx:trkpt", NS):
        try:
            lat = float(trkpt.get("lat"))
            lon = float(trkpt.get("lon"))
            t_abs = datetime.fromisoformat(
                trkpt.find("gpx:time", NS).text.replace("Z", "+00:00")
            ).timestamp()
        except (TypeError, ValueError, AttributeError):
            continue  # skip malformed trackpoints, never raise

        if start_time is None:
            start_time = t_abs
        timestamp = t_abs - start_time

        # GPX has no speed channel: derive km/h from the geodesic step.
        if last_lat is not None:
            step_m = geod.Inverse(last_lat, last_lon, lat, lon)["s12"]
            total_distance += step_m
            dt = t_abs - last_t
            speed = (step_m / dt) * 3.6 if dt > 0 else 0.0
        else:
            total_distance = 0.0
            speed = 0.0
        last_lat, last_lon, last_t = lat, lon, t_abs

        ele = trkpt.find("gpx:ele", NS)
        points.append(DataPoint(
            timestamp=timestamp,
            latitude=lat,
            longitude=lon,
            speed=speed,
            distance=total_distance,
            altitude=float(ele.text) if ele is not None else None,
        ))

    return points if points else None
```

Things this skeleton demonstrates: relative timestamps, geodesic distance accumulation,
unit derivation for a missing channel, optional-field population (`altitude`), per-record
error skipping, and the `None`-on-empty return.

## 7. Document the format

Finish by adding `docs/<format>-format.md` describing the source format's field encoding
and the mapping to `DataPoint` — `docs/vbo-format.md` is the template. Capture the
gotchas there (e.g. VBO's coordinates are in *minutes* requiring `/60`, with longitude
sign inverted in RaceChrono exports). Six months later, that file is the only record of
why the conversion code looks the way it does.

---

**Checklist recap**

- [ ] `src/late_brake/io/parsers/<format>.py` with `parse_<format>_file()` honoring §2
- [ ] Geodesic distance accumulation (§3)
- [ ] Dispatch branch + import in `parsers/__init__.py` (§4)
- [ ] Sample file in `sample-data/` + `tests/io/test_<format>.py` (§5)
- [ ] `docs/<format>-format.md` (§7)
- [ ] `python -m pytest` green
