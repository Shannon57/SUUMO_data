import pandas as pd

# 入力ファイルパス
unique_stations_path = "/Users/gokiyamamoto/Desktop/SUUMO_data/output/unique_stations.csv"
station_data_path = "/Users/gokiyamamoto/Desktop/SUUMO_data/src/data/station20240426free.csv"

# 出力ファイルパス
output_coords_path = "/Users/gokiyamamoto/Desktop/SUUMO_data/output/station_with_coords.csv"

# 1. 必須ファイルを読み込む
print("ファイルを読み込み中...")
unique_stations = pd.read_csv(unique_stations_path)
station_data = pd.read_csv(station_data_path)

# 2. 座標範囲の設定（首都圏）
lon_min = 138.95  # 一番西
lon_max = 140.8   # 一番東
lat_min = 34.8    # 一番南
lat_max = 36.28   # 一番北

# 3. フィルタリング（首都圏範囲外を除外）
station_data = station_data[
    (station_data["lon"] >= lon_min) & (station_data["lon"] <= lon_max) &
    (station_data["lat"] >= lat_min) & (station_data["lat"] <= lat_max)
]

# 4. unique_stationsの「駅」列から「駅」を削除
unique_stations["駅（正規化）"] = unique_stations["駅"].str.replace("駅", "", regex=False)

# 5. 必要な列を選択し、キーを揃える
station_data_filtered = station_data[["station_name", "lon", "lat"]]

# 6. レフトジョインで緯度・経度を取得
print("緯度・経度を結合中...")
merged_data = pd.merge(
    unique_stations,
    station_data_filtered,
    left_on="駅（正規化）",
    right_on="station_name",
    how="left"
)

# 7. 必要な列を整理
merged_data = merged_data.drop(columns=["station_name", "駅（正規化）"])

# 8. 駅ごとに緯度・経度の平均を計算
print("駅ごとに緯度・経度の平均を計算中...")
merged_data = merged_data.groupby(["都道府県", "駅"], as_index=False).agg({
    "lon": "mean",
    "lat": "mean"
})

# 9. データを保存
merged_data.to_csv(output_coords_path, index=False, encoding="utf-8-sig")
print(f"緯度・経度を結合し、平均値を保存しました: {output_coords_path}")
