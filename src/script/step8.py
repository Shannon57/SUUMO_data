import pandas as pd

# 入力ファイルパス
rent_data_path = "/Users/gokiyamamoto/Desktop/SUUMO_data/output/all_station_rent_with_progress.csv"
coords_data_path = "/Users/gokiyamamoto/Desktop/SUUMO_data/output/station_with_coords.csv"

# 出力ファイルパス
output_combined_path = "/Users/gokiyamamoto/Desktop/SUUMO_data/output/station_with_rent_coords.csv"

# 1. 家賃データと緯度・経度データを読み込む
print("ファイルを読み込み中...")
rent_data = pd.read_csv(rent_data_path)
coords_data = pd.read_csv(coords_data_path)

# 2. 不要な列（路線名）を削除し、重複を排除
print("路線名を削除し、重複を整理中...")
rent_data = rent_data.drop(columns=["路線名"])  # 路線名を削除
rent_data = rent_data.drop_duplicates(subset=["都道府県","物件タイプ", "部屋種別", "駅", "家賃"])  # 重複行を削除

# 3. 駅名を基に統合
print("データを結合中...")
combined_data = pd.merge(
    rent_data,
    coords_data,
    on=["都道府県", "駅"],
    how="left"
)

# 4. 結果を保存
combined_data.to_csv(output_combined_path, index=False, encoding="utf-8-sig")
print(f"家賃と緯度・経度を結合したデータを保存しました: {output_combined_path}")
