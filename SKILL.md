---
name: late-brake
version: 0.0.3
description: CLI racing lap analysis — NMEA/VBO import, auto lap splitting, lap comparison, JSON output for AI coaching.
metadata:
  openclaw:
    requires:
      python: ">=3.10"
      dependencies:
        - click>=8.0
        - pydantic>=2.0
        - numpy>=1.24
        - geographiclib>=2.0
        - jsonschema>=4.0
        - wcwidth>=0.2.0
---

# Late Brake

CLI for NMEA/VBO lap analysis and JSON coaching output.

## Import

```python
import os, sys
SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(SKILL_DIR, "scripts"))
from late_brake.cli import main as late_brake_main
```

## CLI

```bash
python -m late_brake.cli load <file> --json
python -m late_brake.cli compare <f1> <l1> <f2> <l2> --json
```

- `late-brake load <file>`: parse file, split laps, list laps
- `late-brake compare <f1> <l1> <f2> <l2>`: compare lap time and speed deltas
- `late-brake track list|info|add`: manage tracks

Schema: [compare-json-schema.md](references/compare-json-schema.md)
