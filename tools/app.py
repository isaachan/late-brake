import streamlit as st
import folium
from streamlit_folium import st_folium
import io

st.set_page_config(page_title="GPS 坐标全量绘图仪", layout="wide")

st.title("📍 GPS 轨迹全量可视化")
st.write("已关闭采样优化，将渲染文件中的每一个坐标点。")

# 1. 文件上传
uploaded_file = st.file_uploader("上传坐标文本文件 (.txt, .log)", type=['txt', 'log'])

if uploaded_file:
    stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
    lines = stringio.readlines()

    locations = []
    
    # 2. 解析逻辑
    for line in lines:
        parts = line.strip().split()
        lat, lon = None, None
        
        if len(parts) == 2:
            lat = float(parts[0]) / 60.0
            lon = abs(float(parts[1]) / 60.0) 
        elif len(parts) >= 4:
            lat = float(parts[2]) / 60.0
            lon = abs(float(parts[3]) / 60.0) 

        if lat is not None and lon is not None:
            # 简单的去重逻辑：如果当前点与上一个点坐标完全相同，则跳过
            if not locations or [lat, lon] != locations[-1]:
                locations.append([lat, lon])

    if locations:
        st.info(f"正在渲染全部 {len(locations)} 个坐标点...")
        
        # 3. 创建地图
        m = folium.Map(location=locations[0], zoom_start=13, control_scale=True)

        # 4. 绘制轨迹线
        folium.PolyLine(
            locations=locations,
            color="#FF5733",
            weight=3,
            opacity=0.7
        ).add_to(m)

        # --- 全量添加悬停标记 ---
        for i, loc in enumerate(locations):
            folium.CircleMarker(
                location=loc,
                radius=2,                # 减小半径，避免点位过密重叠
                color="#1E90FF",         # 使用道奇蓝，区分轨迹线
                fill=True,
                fill_color="#1E90FF",
                fill_opacity=0.6,
                stroke=False,
                # 悬停显示经纬度及该点在序列中的索引
                tooltip=folium.Tooltip(f"序号: {i}<br>纬度: {loc[0]:.6f}<br>经度: {loc[1]:.6f}")
            ).add_to(m)
        # ----------------------

        # 标记起点和终点
        folium.Marker(locations[0], popup="Start", icon=folium.Icon(color='green', icon='play')).add_to(m)
        folium.Marker(locations[-1], popup="End", icon=folium.Icon(color='red', icon='stop')).add_to(m)

        # 5. 渲染到网页
        # 注意：全量渲染时，st_folium 的响应速度取决于浏览器处理 DOM 的能力
        st_folium(m, width=1200, height=700)
    else:
        st.error("无法解析有效坐标。")