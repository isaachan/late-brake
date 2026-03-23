# Late Brake - 赛道数据格式定义

## 概述

赛道分析严重依赖赛道元数据。Late Brake 采用独立的JSON文件存储赛道信息，支持内置赛道和用户自定义赛道。

## 赛道文件存放位置规范

- **内置赛道**：存放在安装目录 `data/tracks/` 下
- **用户自定义赛道**：默认存放在 `~/.late-brake/tracks/` 目录
- **每个赛道对应一个独立的JSON文件**，文件名格式：`{track-id}.json`

## 赛道文件JSON结构定义

```json
{
  "id": "saic",
  "name": "Shanghai International Circuit",
  "full_name": "上海国际赛车场",
  "location": "Shanghai, China",
  "length_m": 5451,
  "turn_count": 16,

  "anchor": {
    "lat": 31.3401765,
    "lon": 121.219292,
    "radius_m": 1062
  },

  "gate": [
    [31.3375154, 121.2223689],
    [31.3378142, 121.2222865]
  ],

  "geofence": [
    [lat, lon],
    ...
  ],

  "centerline": [
    [lat, lon],
    ...
  ],

  "sectors": [
    {
      "id": 1,
      "name": "Sector 1",
      "start_distance_m": 0,
      "end_distance_m": 2020,
      "turns": [1, 2, 3, 4, 5, 6]
    },
    {
      "id": 2,
      "name": "Sector 2",
      "start_distance_m": 2020,
      "end_distance_m": 3740,
      "turns": [7, 8, 9, 10]
    },
    {
      "id": 3,
      "name": "Sector 3",
      "start_distance_m": 3740,
      "end_distance_m": 5451,
      "turns": [11, 12, 13, 14, 15, 16]
    }
  ],

  "turns": [
    {
      "name": "T1",
      "type": "left-right",
      "start_distance_m": 120,
      "apex_distance_m": 280,
      "apex_coordinates": [31.3389, 121.2218],
      "end_distance_m": 350,
      "radius_m": 85,
      "peak_speed_kph_expected": 165
    },
    {
      "name": "T2",
      "type": "right",
      "start_distance_m": 350,
      "apex_distance_m": 410,
      "apex_coordinates": [31.3395, 121.2205],
      "end_distance_m": 460,
      "radius_m": 35,
      "peak_speed_kph_expected": 110
    }
  ]
}
```

## 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 赛道唯一标识 |
| `name` | string | 是 | 赛道英文名称 |
| `full_name` | string | 否 | 赛道完整名称（含中文） |
| `location` | string | 否 | 赛道地理位置 |
| `length_m` | number | 是 | 赛道总长度（米） |
| `turn_count` | number | 是 | 弯道总数 |
| `anchor` | object | 是 | 赛道锚点，用于GPS数据匹配 |
| `anchor.lat` | number | 是 | 锚点纬度 |
| `anchor.lon` | number | 是 | 锚点经度 |
| `anchor.radius_m` | number | 是 | 赛道范围半径 |
| `gate` | array | 是 | 起终点线两个GPS坐标，定义一条线 |
| `geofence` | array | 否 | 赛道边界GPS坐标点数组 |
| `centerline` | array | 是 | 赛道中心线GPS坐标点数组（按行驶顺序） |
| `sectors` | array | 否 | 赛道分段信息 |
| `turns` | array | 否 | 每个弯道的详细信息 |

## 新增字段说明

### 赛道分段（sectors）
- `id`: 分段ID
- `name`: 分段名称
- `start_distance_m`: 分段起点距离赛道起点的距离（米）
- `end_distance_m`: 分段终点距离赛道起点的距离（米）
- `turns`: 该分段包含的弯道编号列表

### 弯道信息（turns）
- `name`: 弯道名称（通常为 T{编号}）
- `type`: 弯道类型：`left`/`right`/`left-right`/`right-left` 等
- `start_distance_m`: 弯道起点距离（从赛道起点开始计算，米）
- `apex_distance_m`: 弯心距离（从赛道起点到弯心的距离，米）
- `apex_coordinates`: 弯心顶点GPS坐标，`[纬度, 经度]`
- `end_distance_m`: 弯道终点距离
- `radius_m`: 弯道半径（米），复合弯道可留空
- `peak_speed_kph_expected`: 该弯道理论最佳车速（公里/小时）
