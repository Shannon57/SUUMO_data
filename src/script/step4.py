import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# ChromeDriverのパス
driver_path = "/Users/gokiyamamoto/Desktop/SUUMO_data/src/data/chromedriver"

# テスト用リンク
test_url = "https://suumo.jp/jj/chintai/kensaku/FR301FB034/?ar=030&bs=040&ra=013&rn=0005&sort=1&ts=1&mdKbn=01&ts=1&mdKbn=1"  # 仮のリンク

# 出力CSVファイル
output_csv_path = "/Users/gokiyamamoto/Desktop/SUUMO_data/output/test_station_rent.csv"

# Serviceを利用してChromeDriverを起動
options = Options()
options.add_argument('--headless')  # ヘッドレスモードで実行
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=options)

# スクレイピング結果を格納するリスト
result_data = []

try:
    # 指定URLを開く
    driver.get(test_url)
    time.sleep(2)  # ページがロードされるのを待つ

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
            result_data.append({"駅": station, "家賃": rent})
        except Exception as e:
            print(f"データ取得エラー: {e}")
            continue

finally:
    # ブラウザを閉じる
    driver.quit()

# データフレームを作成
df = pd.DataFrame(result_data)

# CSVに保存
df.to_csv(output_csv_path, index=False, encoding="utf-8-sig")
print(f"テスト結果をCSVに保存しました: {output_csv_path}")
