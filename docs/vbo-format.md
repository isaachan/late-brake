# VBO 格式说明

本文档定义 RaceChrono Pro 导出的 VBO (VBox) 格式说明，以及到 Late Brake 内部数据格式的映射关系。

## 1. 文件结构

VBO 文件是 RaceChrono Pro 导出的文本格式日志，结构如下：

1. **文件头**：多行文本描述，包含生成时间、软件版本等信息
2. **字段定义段**：`[column names]` 之后列出所有数据列名称
3. **数据段**：`[data]` 之后每行一个数据采样点，空格分割字段

解析时需要跳过文件头，找到 `[data]` 段之后开始解析实际数据行。

## 2. 关键字段说明

VBO 使用 `DDMM.NNNNN` 格式存储经纬度，时间使用 `HHMMSS.ss` 格式：

| 列名          | 类型   | 说明                                     |
|---------------|--------|------------------------------------------|
| `time`        | string | 时间，格式 `HHMMSS.ss`                   |
| `lat`         | float  | 纬度，格式 `DDMM.NNNNN`，符号表示南北   |
| `long`        | float  | 经度，格式 `DDMM.NNNNN`，符号表示东西   |
| `velocity`    | float  | 速度，单位 km/h                          |

**其他字段**：VBO 支持很多可选字段（加速度、陀螺仪、OBD 数据等），v1 版本暂不解析，后续迭代可扩展支持。

## 3. 转换规则

### 3.1 坐标转换

原始格式 `DDMM.NNNN`，转换：lat_dec = abs(lat) / 60，保留原始符号
原始格式 `DDDMM.NNNN`，转换：lon_dec = abs(lon) / 60，保留原始符号

也就是说，直接除以60，且统一成正数。

### 3.2 时间转换

原始时间 `HHMMSS.ss` 转换为相对时间（相对于第一个数据点）：

```python
# 输入示例：053855.06 → 05时 38分 55.06秒
hours = int(time_str / 10000)
minutes = int((time_str - hours * 10000) / 100)
seconds = time_str - hours * 10000 - minutes * 100
total_seconds = hours * 3600 + minutes * 60 + seconds
timestamp = total_seconds - start_total_seconds
```

### 3.3 距离计算

累计距离使用 GeographicLib 对相邻两点使用测地线公式计算距离并累加，与 NMEA 解析保持一致。

## 4. 内部格式映射

| VBO 字段    | 内部字段    | 转换说明                      |
|-------------|-------------|-------------------------------|
| time        | timestamp   | 转换为相对时间（秒）          |
| lat         | latitude    | DDMM.NNNNN → 十进制度         |
| long        | longitude   | DDMM.NNNNN → 十进制度         |
| velocity    | speed       | 已经是 km/h，直接使用         |
| (计算得到)  | distance    | 相邻坐标距离累加，单位米      |

## 5. 错误处理

- 跳过 `[data]` 之前的所有行
- 字段数量不足的行跳过
- 解析错误（数值转换失败）的行跳过
- 不崩溃，只跳过坏行

