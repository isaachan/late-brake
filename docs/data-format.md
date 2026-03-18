# 内部数据格式定义

本文档定义 Late Brake 内部统一的JSON数据结构规范。

## 1. 数据点结构

每个数据点包含赛道上某个采样时刻的所有信息：

```json
{
  "timestamp": float,    // 相对时间（秒），从记录开始计算
  "latitude": float,     // 纬度 (WGS84)
  "longitude": float,    // 经度 (WGS84)
  "altitude": float,     // 海拔高度 (米)，可选字段
  "speed": float,        // 瞬时速度 (km/h)
  "distance": float,     // 累计距离（米），从数据记录开始计算
  "g_force_x": float,    // 横向G值 (左右方向，左正右负)，可选字段
  "g_force_y": float,    // 纵向G值 (前后方向，正为加速，负为刹车)，可选字段
  "g_force_z": float,    // 垂直G值，可选字段
  "steering_angle": float, // 方向盘角度 (度)，可选字段，左负右正
  "throttle_position": float, // 油门开合度 (0-100%)，可选字段
  "brake_pressure": float,    // 刹车压力 (0-100%)，可选字段
  "rpm": int,                 // 发动机转速 (RPM)，可选字段
  "gear": int,                // 当前档位，0=N，1-...=档位，可选字段
}
```

**说明**：
- 必填字段：`timestamp`, `latitude`, `longitude`, `speed`, `distance`
- 可选字段：根据数据源提供的信息而定，如果数据源没有则留空或不包含该字段
- G值说明：参考行业标准，横向G值反映离心力，纵向G值反映加速/刹车力度
- 单位统一：所有单位采用公制，速度统一为km/h，角度为度，百分比0-100%

## 2. 单圈（Lap）数据结构

```json
{
  "id": string,              // Lap ID (如 "file1.Lap1")
  "source_file": string,     // 源文件路径
  "lap_number": int,         // 圈号
  "total_time": float,       // 总圈时（秒）
  "start_time": float,       // 单圈起始时间（秒，相对于整个数据记录开始）
  "end_time": float,         // 单圈结束时间（秒，相对于整个数据记录开始）
  "start_distance": float,   // 起始点累计距离（米，相对于整个数据记录开始）
  "end_distance": float,     // 结束点累计距离（米，相对于整个数据记录开始）
  "is_complete": bool,       // 是否为完整圈。true = 通过起跑线完整绕一圈，false = 半路出发/半路结束，不完整
  "lap_distance": float,     // 单圈实际行驶距离（米）= end_distance - start_distance
  "points": array,           // 数据点数组，包含圈中所有采样点
}
```

**字段说明**：

- `start_time` / `end_time`：记录单圈在整个数据记录中的绝对时间位置，便于后续处理和分段分析
- `is_complete`：标记该圈是否完整。数据文件开始前已经在赛道上行驶，或者数据文件结束时还没完成一圈，这两种情况都是不完整圈
- `start_distance` / `end_distance`：**保留该字段**，用途如下：
  1. 计算单圈实际距离 `lap_distance = end_distance - start_distance`，验证赛道长度
  2. 在整条数据记录中定位该圈的位置，便于切割提取
  3. 处理多圈连续记录时，可以通过距离快速找到圈的起止点
  4. 不同单圈之间的距离对比，帮助发现走线长度差异
- `lap_distance`：新增计算字段，直接给出单圈行驶距离，方便使用


