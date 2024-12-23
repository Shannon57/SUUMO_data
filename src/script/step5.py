import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm  # 進捗バー表示用

# ChromeDriverのパス
driver_path = "/Users/gokiyamamoto/Desktop/SUUMO_data/src/data/chromedriver"

# 入力CSVファイル（生成されたリンクが含まれているファイル）
input_csv_path = "/Users/gokiyamamoto/Desktop/SUUMO_data/output/generated_links_with_types.csv"

# 出力CSVファイル（全リンクの結果を統合）
output_csv_path = "/Users/gokiyamamoto/Desktop/SUUMO_data/output/all_station_rent_with_progress.csv"

# Serviceを利用してChromeDriverを起動
options = Options()
options.add_argument('--headless')  # ヘッドレスモードで実行
options.add_argument('--disable-logging')  # ログ出力を抑制
options.add_argument('--log-level=3')  # エラーレベルのみ表示
service = Service(driver_path, log_output=None)  # ChromeDriverのログを非表示
driver = webdriver.Chrome(service=service, options=options)

# 入力データを読み込む
links_df = pd.read_csv(input_csv_path)

# 結果を格納するリスト
all_result_data = []

try:
    # tqdmで進捗バーを表示
    for index, row in tqdm(links_df.iterrows(), total=links_df.shape[0], desc="リンク処理中"):
        prefecture = row['都道府県']
        rosen_name = row['路線名']
        property_type = row['物件タイプ']
        room_type = row['部屋種別']
        target_url = row['生成されたURL']

        try:
            # 指定URLを開く
            driver.get(target_url)
            time.sleep(0.5)  # ページがロードされるのを待つ

            # テーブル要素を取得
            table = driver.find_element(By.CSS_SELECTOR, "#js-graphpanel-campus > table > tbody")

            # テーブル内の行を取得
            rows = table.find_elements(By.TAG_NAME, "tr")
            for row in rows:
                try:
                    # 駅名
                    station = row.find_element(By.CSS_SELECTOR, "td:nth-child(1)").text

                    # 相場（値段）
                    rent = row.find_element(By.CSS_SELECTOR, "td.graphpanel_matrix-td_graphinfo").text

                    # 結果を保存
                    all_result_data.append({
                        "都道府県": prefecture,
                        "路線名": rosen_name,
                        "物件タイプ": property_type,
                        "部屋種別": room_type,
                        "駅": station,
                        "家賃": rent
                    })
                except Exception as e:
                    # 駅や相場の取得に失敗した場合
                    print(f"データ取得エラー: {e}")
                    continue

        except Exception as e:
            # 各URLの処理でエラーが発生した場合
            print(f"URL処理エラー: {e} (URL: {target_url})")
            continue

finally:
    # ブラウザを閉じる
    driver.quit()

# データフレームを作成
all_results_df = pd.DataFrame(all_result_data)

# CSVに保存
all_results_df.to_csv(output_csv_path, index=False, encoding="utf-8-sig")
print(f"全てのリンクの結果をCSVに保存しました: {output_csv_path}")
