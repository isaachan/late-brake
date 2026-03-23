import streamlit as st
import folium
from streamlit_folium import st_folium
import io

st.set_page_config(page_title="GPS 坐标转换绘图仪", layout="wide")

st.title("📍 特殊格式 GPS 轨迹绘制")
st.write("上传原始文本文件（格式如：`+1864.59 -7266.88`），程序将自动除以 60 并绘制轨迹。")

# 1. 文件上传
uploaded_file = st.file_uploader("上传坐标文本文件 (.txt, .log)", type=['txt', 'log'])

if uploaded_file:
    # 读取原始文本内容
    stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
    lines = stringio.readlines()

    locations = []
    
    # 2. 解析逻辑
    for line in lines:
        parts = line.strip().split()
        if len(parts) >= 2:
            try:
                # 转换逻辑：原始值 / 60
                # 根据你的示例：-7266.88 转换后为正数 121.11，所以这里取了绝对值
                # 如果你的数据中负号代表西经且地图需要保留，请去掉 abs()
                lat = float(parts[0]) / 60.0
                lon = abs(float(parts[1]) / 60.0) 
                
                locations.append([lat, lon])
            except ValueError:
                continue # 跳过无法解析的行

    if locations:
        st.info(f"成功解析 {len(locations)} 个坐标点")
        
        # 显示转换后的数据预览
        with st.expander("查看转换后的坐标数据"):
            st.write(locations[:10], "... (仅显示前10条)")

        # 3. 创建地图
        # 以第一个点为中心
        m = folium.Map(location=locations[0], zoom_start=13, control_scale=True)

        # 4. 绘制线段 (PolyLine)
        folium.PolyLine(
            locations=locations,
            color="#FF5733", # 使用醒目的橙红色
            weight=4,
            opacity=0.8
        ).add_to(m)

        # 标记起点和终点
        folium.Marker(locations[0], popup="Start", icon=folium.Icon(color='green', icon='play')).add_to(m)
        folium.Marker(locations[-1], popup="End", icon=folium.Icon(color='red', icon='stop')).add_to(m)

        # 5. 渲染到网页
        st_folium(m, width=1000, height=600)
    else:
        st.error("无法从文件中解析出有效的坐标，请检查文件格式。")