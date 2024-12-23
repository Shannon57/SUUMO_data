import pandas as pd

# 入力データファイル（スクレイピング済みデータ）
input_csv_path = "/Users/gokiyamamoto/Desktop/SUUMO_data/output/all_station_rent_with_progress.csv"


# 出力ファイル（ユニークな駅情報）
output_csv_path = "/Users/gokiyamamoto/Desktop/SUUMO_data/output/unique_stations.csv"

# CSVを読み込む
df = pd.read_csv(input_csv_path)

# 路線名を削除し、駅名と都道府県でユニークなデータを作成
unique_stations = df[['都道府県', '駅']].drop_duplicates()

# ユニークな駅情報を保存
unique_stations.to_csv(output_csv_path, index=False, encoding="utf-8-sig")
print(f"ユニークな駅データをCSVに保存しました: {output_csv_path}")
