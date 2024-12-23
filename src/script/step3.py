import pandas as pd
import re

# 入力CSVファイルのパス（リダイレクト後のURLが含まれる）
input_csv_path = "/Users/gokiyamamoto/Desktop/SUUMO_data/output/redirected_links.csv"

# 出力CSVファイルのパス（生成されたリンクを保存）
output_csv_path = "/Users/gokiyamamoto/Desktop/SUUMO_data/output/generated_links_with_types.csv"

# tsとmdKbnの全組み合わせ
ts_values = [1, 2, 3]  # 1: マンション, 2: アパート, 3: 一戸建て・その他
ts_labels = {1: "マンション", 2: "アパート", 3: "一戸建て・その他"}

mdKbn_values = ["01", "02", "03", "04", "05"]  # 間取りのカテゴリ
mdKbn_labels = {
    "01": "ワンルーム",
    "02": "1K/1DK",
    "03": "1LDK/2K/2DK",
    "04": "2LDK/3K/3DK",
    "05": "3LDK/4K以上"
}

# 入力CSVを読み込む
df = pd.read_csv(input_csv_path)

# 新しいリンクを保存するリスト
generated_links = []

# リンク生成
for index, row in df.iterrows():
    prefecture = row['都道府県']
    rosen_name = row['路線名']
    base_url = row['リダイレクト後URL']

    # tsとmdKbnの組み合わせでリンクを作成
    for ts in ts_values:
        for mdKbn in mdKbn_values:
            # tsとmdKbnを置き換える正規表現を作成
            updated_url = re.sub(r"ts=\d+&mdKbn=\d{2}", f"ts={ts}&mdKbn={mdKbn}", base_url)
            if "ts=" not in updated_url or "mdKbn=" not in updated_url:
                # もしも元URLにtsやmdKbnがない場合は新たに追加
                updated_url = f"{base_url}&ts={ts}&mdKbn={mdKbn}"
            generated_links.append({
                "都道府県": prefecture,
                "路線名": rosen_name,
                "物件タイプ": ts_labels[ts],  # tsの説明を追加
                "部屋種別": mdKbn_labels[mdKbn],  # mdKbnの説明を追加
                "生成されたURL": updated_url
            })

# 結果をデータフレームに変換
generated_df = pd.DataFrame(generated_links)

# CSVに保存
generated_df.to_csv(output_csv_path, index=False, encoding="utf-8-sig")
print(f"生成されたリンクをCSVに保存しました: {output_csv_path}")
