import pandas as pd
import folium
from matplotlib import cm, colors

# 入力ファイルパス
input_file = "/Users/gokiyamamoto/Desktop/SUUMO_data/output/station_with_rent_coords.csv"

# データを読み込む
data = pd.read_csv(input_file)

# 緯度・経度がNaNでないデータをフィルタリング
data = data.dropna(subset=["lat", "lon", "家賃"])

# 家賃の「万円」を削除して数値化
data["家賃"] = data["家賃"].str.replace("万円", "").astype(float)

# 家賃の最小値・最大値を取得
min_rent = data["家賃"].min()
max_rent = data["家賃"].max()

# カラーマップの設定（青 -> 赤）
cmap = cm.get_cmap("coolwarm")
norm = colors.Normalize(vmin=min_rent, vmax=max_rent)

# 地図の初期設定（東京駅を中心に設定）
m = folium.Map(location=[35.681391, 139.766103], zoom_start=12, tiles="CartoDB Positron")

# 家賃ごとに色分けして円を描画
for _, row in data.iterrows():
    color = colors.rgb2hex(cmap(norm(row["家賃"])))
    
    # ポップアップの内容
    popup_text = f"<b>{row['駅']}</b><br>家賃相場: {row['家賃']}万円"
    
    # 円の描画
    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=8,  # 円の大きさ
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.6,
        popup=folium.Popup(popup_text, max_width=200)  # ポップアップ追加
    ).add_to(m)

# 地図を保存
output_file = "/Users/gokiyamamoto/Desktop/SUUMO_data/output/station_heatmap_with_popups.html"
m.save(output_file)
print(f"地図を保存しました: {output_file}")
