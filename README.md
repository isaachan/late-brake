# Late Brake

> **晚刹车 —— 专业赛车圈速数据分析CLI工具**

Late Brake 是一个纯命令行（CLI）的赛车圈速数据分析工具，用于对比分析不同圈速数据文件中的单圈表现，帮助赛车手找出最佳走线和刹车时机，提升圈速成绩。

## 项目背景

作为一名业余赛车手，你每次下赛道都会记录GPS圈速数据。但现有的APP要么太贵，要么导出数据麻烦，对比分析不够灵活。

Late Brake 解决这些痛点：
- 🚀 **纯CLI工具**：轻量快速，适合脚本化和自动化处理
- 📊 **精准对比**：总圈时差 / 分段时差 / 弯道-by-弯道详细对比
- 🗺️ **支持多格式**：NMEA 0183 / VBO (RaceChrono) 开箱即用，后续可扩展更多格式
- 🎯 **专注核心**：只做圈速数据分析，不做轨迹可视化（留给你自己用Excel/Python处理）
- 🔓 **开源免费**：MIT许可证，可自由使用和修改

**项目命名由来**：赛车场上，圈速的提升往往来自于"晚一点刹车"——找到极限刹车点是突破圈速的关键。因此命名为 **Late Brake**。

## 目录结构说明

```
late-brake/
├── docs/               # 项目文档（需求、格式规范等）
├── late_brake/         # 主源码包（Python模块）
├── sample-data/        # 样例测试数据
├── tracks/             # 用户自定义赛道（git ignore）
├── README.md           # 本文档
├── pyproject.toml      # Python项目配置
└── LICENSE             # MIT许可证
```

- **docs/**：存放所有项目文档，包括需求、格式规范、接口定义等
- **late_brake/**：主源码目录，按功能分层
- **sample-data/**：公开的测试样例数据，用于开发和验证
- **tracks/**：用户自定义赛道存放位置，默认被git ignore

## 快速开始

### 安装

```bash
pip install -e .
```

安装完成后即可使用全局 `late-brake` 命令。

### 常用命令

```bash
# 列出所有已配置赛道
late-brake track list

# 查看赛道信息
late-brake track info tianma

# 加载数据文件，自动分割圈速并列出
late-brake load your-data.vbo

# 对比同一文件中第1圈和第2圈
late-brake compare data.vbo 1 data.vbo 2

# 对比结果输出JSON格式
late-brake compare data.vbo 1 data.vbo 2 --json

# 强制清除缓存重新加载
late-brake load --no-cache modified-data.vbo
```

## 产品文档

- [产品需求文档 (PRD)](docs/PRD.md) - 产品概述、目标用户和核心功能
- [内部数据格式规范](docs/data-format.md) - 统一数据结构定义
- [赛道数据格式规范](docs/track-format.md) - 自定义赛道JSON格式定义
- [对比功能数据依赖](docs/compare-data-requirements.md) - 对比功能数据依赖说明
- [compare JSON输出Schema](docs/compare-json-schema.md) - 完整JSON输出结构定义
- [VBO格式解析说明](docs/vbo-format.md) - RaceChrono VBO格式转换规则
- [用户故事看板（开发进度）](https://nio.feishu.cn/base/LjNWbfiAaa76mNsrdAqce05NnRf?table=tblSoyAKo8EInOAz&view=vewD5D6mGG)

## 测试数据

[Sample-data](sample-data) 目录下包含测试数据：
- `sample-data/running/tianma_1.vbo` / `tianma_2.vbo` - 天马赛车场VBO格式测试数据
- `sample-data/running/tianma_1.nmea` / `tianma_2.nmea` - 天马赛车场NMEA格式测试数据

## 许可证

MIT
