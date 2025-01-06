import pandas as pd
import re

# ファイルパスの設定
reachable_stations_file = "./output/reachable_stations.csv"  # スクレイピング結果のCSV
station_data_file = "./src/data/station20240426free.csv"    # 元データのCSV
output_file = "./output/cleaned_station_data.csv"           # クリーンデータの出力先
final_output_file = "./output/final_reachable_stations.csv" # 突合結果の出力先

# ファイルの読み込み
reachable_stations = pd.read_csv(reachable_stations_file)  # スクレイピング結果
station_data = pd.read_csv(
    station_data_file,
    usecols=["station_name", "address", "lon", "lat"]
)  # 必要な列のみ読み込み

# 位置フィルタリング（指定された範囲内のデータのみ）
station_data = station_data[(
    (station_data["lon"] >= 139.357090) &
    (station_data["lon"] <= 140.972770) &
    (station_data["lat"] >= 35.270070) &
    (station_data["lat"] <= 36.322553)
)]

# reachable_stationsの駅名から括弧とそれ以降を除去
reachable_stations["駅名_cleaned"] = reachable_stations["駅名"].apply(
    lambda x: re.sub(r"\s*\(.*\)|\s*（.*）|\s*\[.*\]|\s*〔.*〕", "", x) if isinstance(x, str) else x
)

# 駅名でフィルタリング
filtered_stations = station_data[station_data["station_name"].isin(reachable_stations["駅名_cleaned"])]

# 重複データを削除（最初のレコードだけを残す）
filtered_stations = filtered_stations.drop_duplicates(subset=["station_name"], keep="first")

# 突合結果をreachable_stationsに結合
merged_stations = pd.merge(
    reachable_stations,
    filtered_stations,
    left_on="駅名_cleaned",
    right_on="station_name",
    how="left"
)

# latとlonが存在しない場合、行を削除
merged_stations = merged_stations.dropna(subset=["lat", "lon"])

# 路線データ
lines = [
    "ＪＲ山手線", "ＪＲ京浜東北線", "都営浅草線", "京急本線", "東急大井町線", "東京メトロ銀座線", "都営三田線",
    "東急池上線", "東京メトロ日比谷線", "東急目黒線", "都営大江戸線（環状部）", "東京メトロ南北線", "りんかい線",
    "ゆりかもめ", "東京モノレール", "東京メトロ有楽町線", "ＪＲ中央本線（東京-塩尻）", "ＪＲ横須賀線",
    "ＪＲ総武線各停（御茶ノ水-錦糸町）", "東京メトロ丸ノ内線", "東京メトロ東西線", "ＪＲ総武本線（東京-銚子）",
    "東急多摩川線", "東急田園都市線", "京王井の頭線", "東京メトロ千代田線", "ＪＲ南武線（川崎-立川）",
    "東京メトロ半蔵門線", "京急空港線", "都営新宿線", "京急大師線", "東急東横線", "京成本線",
    "ＪＲ宇都宮線〔東北本線〕・ＪＲ上野東京ライン", "ＪＲ京葉線", "ＪＲ鶴見線（鶴見-扇町）", "東京メトロ副都心線",
    "ＪＲ常磐線", "小田急小田原線", "都電荒川線", "京成押上線", "ＪＲ根岸線", "つくばエクスプレス",
    "西武新宿線", "京王新線", "都営大江戸線（放射部）", "都営日暮里・舎人ライナー", "東武伊勢崎線〔スカイツリーライン〕",
    "京王線", "東急世田谷線", "東武亀戸線", "東武東上線", "ＪＲ横浜線", "ＪＲ埼京線",
    "東武伊勢崎線〔スカイツリーライン〕（押上-曳舟）", "東急新横浜線", "横浜市営ブルーライン",
    "ＪＲ東海道本線（東京-熱海）", "西武池袋線", "相鉄本線", "横浜高速鉄道みなとみらい線",
    "東京メトロ丸ノ内線（中野坂上-方南町）", "ＪＲ南武線（尻手-浜川崎）", "埼玉高速鉄道線",
    "東京メトロ千代田線（綾瀬-北綾瀬）", "京成成田空港線・北総鉄道線", "横浜市営グリーンライン",
    "西武有楽町線", "ＪＲ鶴見線（浅野-海芝浦）", "ＪＲ相鉄直通線", "ＪＲ鶴見線（安善-大川）",
    "東武大師線", "東葉高速線", "ＪＲ高崎線", "西武豊島線", "金沢シーサイドライン",
    "東武野田線〔アーバンパークライン〕", "京成金町線", "新京成電鉄", "ＪＲ武蔵野線（府中本町-南船橋）",
    "湘南モノレール", "西武多摩川線"
]

# 路線と会社名を分割
line_data = []
for line in lines:
    if line.startswith("ＪＲ"):
        company = "ＪＲ"
        line_name = line.replace("ＪＲ", "", 1).strip()
    elif line.startswith("東京メトロ"):
        company = "東京メトロ"
        line_name = line.replace("東京メトロ", "", 1).strip()
    elif line.startswith("都営"):
        company = "都営"
        line_name = line.replace("都営", "", 1).strip()
    elif line.startswith("京急"):
        company = "京急"
        line_name = line.replace("京急", "", 1).strip()
    elif line.startswith("西武"):
        company = "西武"
        line_name = line.replace("西武", "", 1).strip()
    elif line.startswith("東武"):
        company = "東武"
        line_name = line.replace("東武", "", 1).strip()
    elif line.startswith("京成"):
        company = "京成"
        line_name = line.replace("京成", "", 1).strip()
    elif line.startswith("東急"):
        company = "東急"
        line_name = line.replace("東急", "", 1).strip()
    elif line.startswith("京王"):
        company = "京王"
        line_name = line.replace("京王", "", 1).strip()
    elif line.startswith("相鉄"):
        company = "相鉄"
        line_name = line.replace("相鉄", "", 1).strip()
    elif line.startswith("横浜市営"):
        company = "横浜市営"
        line_name = line.replace("横浜市営", "", 1).strip()
    elif line.startswith("湘南モノレール"):
        company = "湘南モノレール"
        line_name = line.replace("湘南モノレール", "", 1).strip()
    elif line.startswith("埼玉高速鉄道"):
        company = "埼玉高速鉄道"
        line_name = line.replace("埼玉高速鉄道", "", 1).strip()
    elif line.startswith("つくばエクスプレス"):
        company = "つくばエクスプレス"
        line_name = line.replace("つくばエクスプレス", "", 1).strip()
    elif line.startswith("金沢シーサイドライン"):
        company = "金沢シーサイドライン"
        line_name = line.replace("金沢シーサイドライン", "", 1).strip()
    else:
        company = "不明"
        line_name = line

    line_data.append({"company": company, "line": line, "line_name": line_name})

# データフレーム化
line_df = pd.DataFrame(line_data)

# 路線名で結合
merged_stations = pd.merge(
    merged_stations,
    line_df,
    left_on="路線名",
    right_on="line",
    how="left"
)

# 不要な列を削除
merged_stations = merged_stations.drop(columns=["line"])

# CSV出力
merged_stations.to_csv(final_output_file, index=False, encoding="utf-8-sig")

# ログ出力
print(f"路線データが作成されました")
print(f"突合結果が作成されました: {final_output_file}")
