import pandas as pd
import folium
from streamlit_folium import st_folium
import streamlit as st
from matplotlib import cm, colors

# 入力CSVファイルのパス
data_path = "station_with_rent_coords.csv"

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

# 家賃の範囲を取得
min_rent_actual = data["家賃"].min()
max_rent_actual = data["家賃"].max()
min_rent_slider = 3.0  # スライダーの下限は3万円以下
max_rent_slider = 25.0  # スライダーの上限は25万円以上

# Streamlit設定
st.set_page_config(layout="wide")
st.title("家賃ヒートマップ")
st.sidebar.header("フィルター")

# Session state 初期化
def initialize_session_state():
    if "selected_property_type" not in st.session_state:
        st.session_state["selected_property_type"] = property_types[0]
    if "selected_room_type" not in st.session_state:
        st.session_state["selected_room_type"] = room_types[0]
    if "bounds" not in st.session_state:
        st.session_state["bounds"] = {
            "_southWest": {"lat": 35.6, "lng": 139.5},  # 仮の初期値（東京近辺）
            "_northEast": {"lat": 35.8, "lng": 139.9},
        }
    if "center" not in st.session_state:
        st.session_state["center"] = {"lat": 35.7, "lng": 139.7}  # 仮の初期値（東京駅近辺）
    if "zoom" not in st.session_state:
        st.session_state["zoom"] = 12  # 初期ズームレベル
    if "search_triggered" not in st.session_state:
        st.session_state["search_triggered"] = False
    if "rent_range" not in st.session_state:
        st.session_state["rent_range"] = [float(min_rent_actual), float(max_rent_actual)]
    if "rent_range_temp" not in st.session_state:
        st.session_state["rent_range_temp"] = [float(min_rent_actual), float(max_rent_actual)]

initialize_session_state()

# フィルターを作成
selected_property_type = st.sidebar.selectbox(
    "物件タイプを選択:", property_types, key="selected_property_type"
)
selected_room_type = st.sidebar.selectbox(
    "部屋種別を選択:", room_types, key="selected_room_type"
)

# 家賃範囲のスライダー
new_rent_range_temp = st.sidebar.slider(
    "家賃範囲 (万円):",
    float(min_rent_slider),
    float(max_rent_slider),
    value=[
        max(float(min_rent_slider), float(st.session_state["rent_range_temp"][0])),
        min(float(max_rent_slider), float(st.session_state["rent_range_temp"][1])),
    ],
    step=0.1
)

# 一時的なスライダー値を更新
if new_rent_range_temp != st.session_state["rent_range_temp"]:
    st.session_state["rent_range_temp"] = new_rent_range_temp

# 検索ボタン
def trigger_search():
    st.session_state["rent_range"] = st.session_state["rent_range_temp"]
    st.session_state["search_triggered"] = True

search_button = st.sidebar.button("検索", on_click=trigger_search)

# 地図作成（常に1つだけ作成）
m = folium.Map(
    location=[
        st.session_state["center"]["lat"],
        st.session_state["center"]["lng"],
    ],
    zoom_start=st.session_state["zoom"],
    tiles="CartoDB Positron",
)

if st.session_state["search_triggered"]:
    # 地図範囲の取得
    bounds = st.session_state["bounds"]
    lat_min, lon_min = bounds["_southWest"]["lat"], bounds["_southWest"]["lng"]
    lat_max, lon_max = bounds["_northEast"]["lat"], bounds["_northEast"]["lng"]

    # 地図範囲内のデータをフィルタリング
    filtered_data = data[
        (data["物件タイプ"] == st.session_state["selected_property_type"]) &
        (data["部屋種別"] == st.session_state["selected_room_type"]) &
        (data["家賃"] >= max(float(min_rent_slider), float(st.session_state["rent_range"][0]))) &
        (data["家賃"] <= min(float(max_rent_slider), float(st.session_state["rent_range"][1]))) &
        (data["lon"] >= lon_min) & (data["lon"] <= lon_max) &
        (data["lat"] >= lat_min) & (data["lat"] <= lat_max)
    ]

    if not filtered_data.empty:
        # 家賃の範囲を取得
        min_rent = filtered_data["家賃"].min()
        max_rent = filtered_data["家賃"].max()

        # カラーマップ設定
        cmap = cm.get_cmap("coolwarm")
        norm = colors.Normalize(vmin=min_rent, vmax=max_rent)

        # フィルタリング後のデータを地図に追加
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

        # 地図と表の表示
        col1, col2 = st.columns([3, 1])

        with col1:
            st_data = st_folium(m, width=700, height=500)

        with col2:
            st.subheader("駅名と家賃一覧")
            sort_order = st.radio("ソート順", ("昇順", "降順"), index=0)
            sorted_data = filtered_data.sort_values("家賃", ascending=(sort_order == "昇順"))
            st.dataframe(sorted_data[["駅", "家賃"]].reset_index(drop=True))

        # 地図の表示範囲と中心位置を更新（検索ボタンが押されている場合のみ）
        if st_data and search_button:
            if "bounds" in st_data:
                st.session_state["bounds"] = st_data["bounds"]
            if "center" in st_data:
                st.session_state["center"] = st_data["center"]
            if "zoom" in st_data:
                st.session_state["zoom"] = st_data["zoom"]
    else:
        st.warning("現在の地図範囲内にデータがありません。")

# 検索がトリガーされていない場合は初期状態の地図を表示
else:
    col1, col2 = st.columns([3, 1])

    with col1:
        st_folium(m, width=700, height=500)

    with col2:
        st.subheader("駅名と家賃一覧")
        st.text("条件を指定して検索してください。")