import os
import pandas as pd
import folium
from matplotlib import cm, colors

# 入力ファイルパス
input_file = "/Users/gokiyamamoto/Desktop/SUUMO_data/output/station_with_rent_coords.csv"
output_dir = "/Users/gokiyamamoto/Desktop/SUUMO_data/output/"

# データを読み込む
data = pd.read_csv(input_file)

# 家賃のデータをクリーンアップして数値に変換
data["家賃"] = (
    data["家賃"]
    .str.replace("万円", "", regex=False)  # 「万円」を削除
    .str.strip()  # 空白を削除
    .replace("-", float("nan"))  # 「-」をNaNに置換
)
data["家賃"] = pd.to_numeric(data["家賃"], errors="coerce")  # 数値に変換できない値をNaNに設定

# NaNを含むデータを除外
data = data.dropna(subset=["家賃", "lat", "lon"])

# ユニークな物件タイプと部屋種別を取得
property_types = data["物件タイプ"].unique()
room_types = data["部屋種別"].unique()

# カラーマップの設定（青 -> 赤）
cmap = cm.get_cmap("coolwarm")

# 出力ディレクトリが存在しない場合は作成
os.makedirs(output_dir, exist_ok=True)

# 物件タイプ × 部屋種別でヒートマップを生成
for property_type in property_types:
    for room_type in room_types:
        # フィルタリング
        filtered_data = data[
            (data["物件タイプ"] == property_type) & 
            (data["部屋種別"] == room_type)
        ]

        # データがない場合はスキップ
        if filtered_data.empty:
            continue

        # 家賃の最小値と最大値
        min_rent = filtered_data["家賃"].min()
        max_rent = filtered_data["家賃"].max()

        # 正規化の設定
        norm = colors.Normalize(vmin=min_rent, vmax=max_rent)

        # 地図の初期設定（東京駅を中心に設定）
        m = folium.Map(location=[35.681391, 139.766103], zoom_start=12, tiles="CartoDB Positron")

        # 家賃ごとに色分けして円を描画
        for _, row in filtered_data.iterrows():
            color = colors.rgb2hex(cmap(norm(row["家賃"])))
            popup_text = f"<b>{row['駅']}</b><br>家賃相場: {row['家賃']}万円"
            folium.CircleMarker(
                location=[row["lat"], row["lon"]],
                radius=8,  # 円の大きさ
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.6,
                popup=folium.Popup(popup_text, max_width=200)  # ポップアップ追加
            ).add_to(m)

        # ファイル名を生成
        file_name = f"{property_type}_{room_type}.html".replace("/", "_")  # ファイル名にスラッシュが含まれる場合は置換
        output_file_path = os.path.join(output_dir, file_name)

        # 地図を保存
        m.save(output_file_path)
        print(f"地図を保存しました: {output_file_path}")
