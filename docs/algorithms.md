# Late Brake — Core Algorithms

This document explains the mathematics behind Late Brake for developers: how raw GPS
samples become laps, how a session is matched to a track, and how two laps are compared.
The relevant code lives in:

| Topic | Module |
|---|---|
| Distance accumulation | `src/late_brake/io/parsers/nmea.py`, `vbo.py` |
| Track matching | `src/late_brake/core/matcher.py` |
| Lap splitting & timing | `src/late_brake/core/splitter.py` |
| Lap comparison | `src/late_brake/core/comparator.py` |

All geodesic computations use **geographiclib** on the **WGS84 ellipsoid**
(`Geodesic.WGS84`). The two primitives used everywhere are the *inverse geodesic
problem* — given two points `(lat1, lon1)` and `(lat2, lon2)`, return the geodesic
distance `s12` (meters) and the forward azimuth `azi1` (degrees, clockwise from north) —
accessed via `geod.Inverse(...)`.

---

## 1. The common coordinate: cumulative distance

Almost every downstream algorithm works in **distance space**, not time space. While
parsing, each sample gets a cumulative distance:

```
distance(p_0) = 0
distance(p_i) = distance(p_{i-1}) + s12(p_{i-1}, p_i)
```

where `s12` is the WGS84 geodesic distance between consecutive GPS fixes. This turns the
2-D trajectory into a 1-D arc-length parameterization. A `DataPoint` therefore carries
`(timestamp, latitude, longitude, speed, distance, ...)`.

Note that `distance` is relative to the **start of the recording file**, not the track's
start line. After lap splitting, the lap-local distance of a point is

```
d_local(p) = p.distance − lap.start_distance        # 0 at the start line
```

This conversion appears in every function in `comparator.py`. Track metadata
(`sectors`, `turns`) is also expressed in meters from the start line, so once a lap is
split, lap-local distance and track distance share the same origin and can be compared
directly.

**Why distance space?** Two laps of the same track cover (nearly) the same path, so the
same distance value corresponds to (nearly) the same physical location on track — even
though the times differ. This makes distance the natural alignment key for comparison,
sidestepping any need for spatial trajectory matching (e.g. map-matching or DTW).

---

## 2. Track matching (`matcher.py`)

**Problem:** given a session's GPS points, decide which configured track it was driven on.

The algorithm is deliberately coarse, because tracks are kilometers apart:

1. **Centroid** — arithmetic mean of latitudes and longitudes:

   ```
   c = ( mean(lat_i), mean(lon_i) )
   ```

   This is a planar approximation, not a true spherical mean. The error is at most a few
   hundred meters for a track-sized point cloud, which is negligible against anchor radii
   (typically > 1 km). (Caveat: a naive longitude mean breaks near the ±180° antimeridian;
   no configured track is near it.)

2. **Anchor test** — each track defines an anchor `(lat, lon, radius_m)`. A track is a
   candidate iff the geodesic distance from the centroid to its anchor is within the radius:

   ```
   s12(c, anchor) ≤ anchor.radius_m
   ```

3. **Decision** — exactly one candidate → match; zero or multiple candidates → fail with
   an explicit message asking the user to pass `--track <id>`.

This is effectively a 1-nearest-anchor classifier with a rejection region, trading
precision for robustness: it cannot confuse two distant tracks, and overlapping anchors
are surfaced to the user rather than guessed at.

---

## 3. Lap splitting (`splitter.py`)

**Problem:** detect every moment the car crosses the start/finish line and cut the point
stream into laps.

The start/finish line is defined in track metadata as a **gate**: a geodesic segment
between two GPS endpoints `G_start`, `G_end`.

### 3.1 Which side of the gate? (`side_of_line`)

Crossing detection is a **sign-change test**. For each point `P`, compute two azimuths
from the gate's start endpoint:

```
azi_gate  = azimuth(G_start → G_end)
azi_point = azimuth(G_start → P)
Δ = normalize(azi_point − azi_gate)   to (−180°, 180°]
side(P) = +1 if Δ > 0 else −1
```

Geometrically, `Δ` is the bearing of `P` relative to the gate direction as seen from
`G_start`; its sign tells you which half-plane (left/right of the infinite gate line) the
point lies in. This is the spherical analogue of the 2-D cross-product sign test.

### 3.2 Filtering false crossings (`point_to_line_distance`)

A sign change alone is not enough: the side test uses the *infinite* line through the
gate, so a car on the far side of the circuit can also flip sign. Each sign change is
therefore confirmed by requiring the point to be within **5 m** of the gate *segment*.

The point-to-segment distance combines a projection test with a spherical cross-track
formula. With `d1 = s12(G_start, P)`, `d2 = s12(G_end, P)`, `L = s12(G_start, G_end)`:

1. **Projection parameter** (law-of-cosines, treated planarly):

   ```
   x = (d1² + L² − d2²) / (2L)
   ```

   If `x < 0` the foot of the perpendicular falls before `G_start` → return `d1`.
   If `x > L` it falls past `G_end` → return `d2`.

2. **Cross-track distance** otherwise, using the spherical cross-track approximation
   with `α₁ = azi_gate − azimuth(G_start → P)`:

   ```
   h = d1 · | asin( sin(α₁) · cos(σ₁) ) |
   ```

   For gate-sized geometry (tens of meters) the small-angle behavior makes this accurate
   to well under the 5 m threshold, so the approximation is fine for its purpose as a
   yes/no gate-proximity filter.

### 3.3 Cutting laps from crossings

Walk the points in order; every confirmed sign-change at index `i` is recorded as a
crossing. Then:

- **Complete laps** — each pair of consecutive crossings `(i, j)` becomes a lap with
  `points[i:j]`, `total_time = t_j − t_i`, `lap_distance = distance_j − distance_i`,
  `is_complete = True`.
- **Debounce** — laps shorter than `min_lap_time_sec` (default **30 s**) are discarded.
  This suppresses double-triggers when GPS noise makes consecutive samples straddle the
  gate repeatedly.
- **Leading out-lap** — points before the first crossing (if ≥ 10 samples) become an
  `is_complete = False` lap.
- **Trailing in-lap** — points after the last crossing (if ≥ 10 samples) likewise.
- **Single-crossing special case** — if there is exactly one crossing and it sits within
  10 samples of the end of the file, the data is interpreted as one *standing-start
  flying lap*: the car started at the line and the recording ends right after it crossed.
  The whole file becomes one complete lap.

Finally laps are renumbered `1..n` in order.

**Known quantization:** the crossing timestamp is the timestamp of the **first sample on
the new side**, not the interpolated instant the line was crossed. Lap times are therefore
quantized to the GPS sample period (e.g. ±0.1 s at 10 Hz). The error largely cancels in
lap-to-lap *differences* when both laps were logged at the same rate, but it is the main
precision limit of the current timing.

### 3.4 Lap identity

A lap's identity is `"{source_file}.Lap{n}"` — i.e. (file, ordinal) after renumbering.
Two laps from different files are always distinct entities; comparison (next section)
aligns them by distance, never by identity.

---

## 4. Lap comparison (`comparator.py`)

**Problem:** given two laps (possibly from different sessions), quantify where time and
speed were gained or lost.

All comparison is done **in distance space** (see §1): position on track is the
independent variable, and speed/time are compared at equal distances.

### 4.1 Resampling onto a uniform distance grid (`resample_lap`)

Raw samples are uniform in *time*, hence non-uniform in *distance* (a sample every
~0.83 m at 30 km/h vs ~7 m at 250 km/h, at 10 Hz). To compare two laps pointwise, each
lap's speed trace is resampled onto a uniform distance grid:

```
grid    = linspace(0, lap_distance, ⌊lap_distance / step⌋ + 1)   # step = 1 m default
v(grid) = linear interpolation of (d_local(p_i), speed_i) at grid points
```

(`np.interp` — piecewise-linear, clamped at the ends.)

The mean speed delta is then computed over the common prefix of the two grids:

```
avg_speed_diff = mean( v2[0:m] − v1[0:m] ),   m = min(len(grid1), len(grid2))
```

Truncating to the shorter grid handles the fact that two laps of the same circuit never
measure *exactly* the same `lap_distance` (different lines through corners, GPS noise);
the residual misalignment grows toward the end of the lap but stays small because lap
distances agree to within a fraction of a percent.

### 4.2 Sector and turn times (`sector_time`)

Track metadata defines sectors and turns as distance intervals `[d_start, d_end]` from
the start line. The time a lap spent in an interval is:

```
t_in  = timestamp of the first point with d_local ≥ d_start
t_out = timestamp of the first point with d_local ≥ d_end   (or last point if none)
sector_time = t_out − t_in
```

Like lap timing, this snaps to sample boundaries rather than interpolating, so individual
sector times carry up to one sample period of noise — again mostly cancelling in the
`t2 − t1` differences that the report actually presents.

Sector **average speed** is derived from the *nominal* sector length rather than measured
distance, keeping the denominator identical for both laps:

```
avg_speed = (d_end − d_start) / sector_time × 3.6    # m/s → km/h
```

### 4.3 Point speeds at track landmarks (`get_speed_at_distance`)

For each turn, the report includes entry / apex / exit speeds, i.e. speed at a specific
track distance `d*`. This is a linear interpolation between the bracketing samples:

```
v(d*) = v_prev + (d* − d_prev) / (d_next − d_prev) · (v_next − v_prev)
```

with clamping to the first/last sample's speed when `d*` falls outside `[0, lap_distance]`.

### 4.4 Output

`compare_laps` assembles, for lap1 vs lap2:

- total time and `total_time_diff = t2 − t1` (positive ⇒ lap2 slower);
- overall `avg_speed_diff` from the resampled traces;
- per-sector `{time1, time2, time_diff, avg_speed1, avg_speed2, avg_speed_diff}`;
- per-turn the same, plus entry/apex/exit speed triples and their diffs.

Rounding follows the US-040 precision convention: times to 4 decimals, distances and
speeds to 2.

---

## 5. Summary of approximations and their justification

| Approximation | Where | Why it's acceptable |
|---|---|---|
| Planar mean for centroid | matcher | error ≪ anchor radius (>1 km) |
| Spherical cross-track formula for gate distance | splitter | only a 5 m yes/no filter |
| Crossing time snapped to sample, no interpolation | splitter | error ≤ 1 sample period; cancels in lap deltas |
| Sector boundaries snapped to first sample past threshold | comparator | same as above |
| Linear interpolation of speed in distance | comparator | speed is smooth at 1 m / 10 Hz resolution |
| Truncation to shorter grid for speed delta | comparator | lap distances agree to <1% |
| Nominal (not measured) sector length for avg speed | comparator | identical denominator for both laps ⇒ fair diff |

The design theme: **distance is the universal alignment key**, geodesic math is used
where absolute position matters (parsing, matching, gate detection), and simple linear
interpolation is used everywhere downstream because by then everything is 1-D.
