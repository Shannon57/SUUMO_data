import pandas as pd
import folium
from streamlit_folium import st_folium
import streamlit as st
from matplotlib import cm, colors

# 入力CSVファイルのパス
data_path = "/Users/gokiyamamoto/Desktop/SUUMO_data/output/station_with_rent_coords.csv"

# データを読み込む
data = pd.read_csv(data_path)

# 家賃データをクリーンアップ
data["家賃"] = (
    data["家賃"]
    .str.replace("万円", "", regex=False)
    .str.strip()
    .replace("-", float("nan"))
)
data["家賃"] = pd.to_numeric(data["家賃"], errors="coerce")
data = data.dropna(subset=["家賃", "lat", "lon"])

# ユニークな物件タイプと部屋種別を取得
property_types = data["物件タイプ"].unique()
room_types = data["部屋種別"].unique()

# Streamlit設定
st.title("家賃ヒートマップ")
st.sidebar.header("フィルター")

# フィルターを作成
selected_property_type = st.sidebar.selectbox("物件タイプを選択:", property_types)
selected_room_type = st.sidebar.selectbox("部屋種別を選択:", room_types)

# 初期値（地図範囲）を設定
if "bounds" not in st.session_state:
    st.session_state["bounds"] = {
        "_southWest": {"lat": 35.6, "lng": 139.5},  # 仮の初期値（東京近辺）
        "_northEast": {"lat": 35.8, "lng": 139.9}
    }

# 現在の地図範囲
bounds = st.session_state["bounds"]
lat_min, lon_min = bounds["_southWest"]["lat"], bounds["_southWest"]["lng"]
lat_max, lon_max = bounds["_northEast"]["lat"], bounds["_northEast"]["lng"]

# 地図範囲内のデータをフィルタリング
filtered_data = data[
    (data["物件タイプ"] == selected_property_type) &
    (data["部屋種別"] == selected_room_type) &
    (data["lon"] >= lon_min) & (data["lon"] <= lon_max) &
    (data["lat"] >= lat_min) & (data["lat"] <= lat_max)
]

# フィルタリング後のデータがない場合の処理
if filtered_data.empty:
    st.warning("現在の地図範囲内にデータがありません。")
else:
    # 家賃の範囲を取得
    min_rent = filtered_data["家賃"].min()
    max_rent = filtered_data["家賃"].max()

    # カラーマップ設定
    cmap = cm.get_cmap("coolwarm")
    norm = colors.Normalize(vmin=min_rent, vmax=max_rent)

    # 地図作成
    m = folium.Map(location=[35.681391, 139.766103], zoom_start=12, tiles="CartoDB Positron")
    for _, row in filtered_data.iterrows():
        color = colors.rgb2hex(cmap(norm(row["家賃"])))
        popup_text = f"<b>{row['駅']}</b><br>家賃相場: {row['家賃']}万円"
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=8,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.6,
            popup=folium.Popup(popup_text, max_width=200),
        ).add_to(m)

    # 地図を表示
    st_folium(m, width=700, height=500)
