# Late Brake

Late Brake 是一个纯命令行（CLI）的赛车圈速数据分析工具，用于对比分析不同圈速数据文件中的单圈表现，帮助赛车手找出最佳走线和刹车时机。

## 产品文档

- [产品需求文档 (PRD)](docs/PRD-v1.md) - 产品概述、目标用户和核心功能
- [内部数据格式规范](docs/data-format.md) - 统一数据结构定义
- [赛道数据格式规范](docs/track-format.md) - 自定义赛道 JSON 格式定义
- [用户故事待办列表](https://nio.feishu.cn/base/LjNWbfiAaa76mNsrdAqce05NnRf?table=tblSoyAKo8EInOAz&view=vewD5D6mGG)
- [User Story 依赖关系](docs/user-story-deps.png) - 开发顺序依赖图（实线=强依赖，虚线=弱依赖）

## 赛道数据
[赛道数据](tracks)包含了三个赛道的数据，分别是“上海国际赛车场”、“上海天马赛车场”和一个我自己定义的“私有赛车场”。这些赛道的数据来自其他项目，不一定满足late brake项目的需要，请**谨慎使用**。

## 测试数据
[Sample-data](sample-data) 目录下包含了四个用于测试的赛道数据，其中[private_1.nmea](sample-data/private_1.nmea),[private_2.nmea](sample-data/private_2.nmea)对应赛道“my_private_track_1”。[tianma_1.nmea](sample-data/tianma_1.nmea),[tianma_2.nmea](sample-data/tianma_2.nmea)对应赛道“tianma”。

## 许可证

MIT
