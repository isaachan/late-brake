---
name: late-brake
version: 1.0.0
description: 纯CLI赛车圈速数据分析工具，支持NMEA/VBO格式导入，自动分割圈速，对比两圈差异，输出专业对比数据供AI教练分析。Use when you need to analyze racing lap data files, compare two laps, and get structured comparison results.
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

# Late Brake - 赛车圈速数据分析skill

Late Brake 是一个纯命令行（CLI）的赛车圈速数据分析工具，可以：
- 导入NMEA 0183 / RaceChrono VBO格式圈速数据
- 自动根据赛道起终点线分割单圈
- 对比任意两个圈的圈速、分段、弯道差异
- 输出结构化JSON对比结果，可供AI教练进一步分析

## 依赖

- Python >= 3.10
- 依赖包：click, pydantic, numpy, geographiclib, jsonschema, wcwidth

依赖已声明在 SKILL.md 中，OpenClaw 安装时会自动处理。

## 入口命令

源码直接放在 `scripts/` 目录，可以直接调用：

```python
import sys
import os
SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(SKILL_DIR, "scripts"))
from late_brake.cli import main as late_brake_main
```

或作为命令行直接执行：

```bash
# 加载数据文件，列出所有圈
python -m late_brake.cli load <file> --json

# 对比两圈，输出JSON结果
python -m late_brake.cli compare <file1> <lap1> <file2> <lap2> --json
```

## 功能列表

| 功能 | 命令 | 说明 |
|------|------|------|
| 加载数据文件 | `late-brake load <file>` | 解析数据，自动分割圈，列出所有圈 |
| 对比两圈 | `late-brake compare <file1> <lap1> <file2> <lap2>` | 对比两圈差异，输出文本表格或JSON |
| 赛道管理 | `late-brake track list/info/add` | 管理内置/自定义赛道 |

## JSON输出格式

完整schema定义参见 [compare-json-schema.md](references/compare-json-schema.md)

## 适用场景

- 赛车手上传圈速数据文件，需要对比分析
- AI赛车教练需要结构化对比数据给出建议
- 批量处理多个圈速数据文件
