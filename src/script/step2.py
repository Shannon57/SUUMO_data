import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# ChromeDriverのパス
driver_path = "/Users/gokiyamamoto/Desktop/SUUMO_data/src/data/chromedriver"

# Serviceを利用してChromeDriverを起動
options = Options()
options.add_argument('--headless')  # ヘッドレスモードで実行
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=options)

# 入力CSVファイル
input_csv_path = "/Users/gokiyamamoto/Desktop/SUUMO_data/output/rosen_link.csv"

# 出力データを格納するリスト
result_data = []

# CSVを読み込む
df = pd.read_csv(input_csv_path)

try:
    for index, row in df.iterrows():
        prefecture = row['都道府県']
        rosen_name = row['路線名']
        start_url = row['URL']
        
        try:
            # URLを開く
            driver.get(start_url)
            time.sleep(1)  # ページがロードされるのを待つ

            # 指定のリンクをクリック
            clickable_element = driver.find_element(By.CSS_SELECTOR, "#js-graphpanel-form > div > div.ui-section-body > div > div.graphpanel-ctrl > a")
            clickable_element.click()
            time.sleep(1)  # リダイレクト完了を待つ

            # リダイレクト後のURLを取得
            redirected_url = driver.current_url

            # 結果を保存
            result_data.append({
                "都道府県": prefecture,
                "路線名": rosen_name,
                "元URL": start_url,
                "リダイレクト後URL": redirected_url
            })
            print(f"成功: {rosen_name} -> {redirected_url}")

        except Exception as e:
            # エラー発生時
            print(f"エラー: {rosen_name} ({start_url}) - {e}")
            result_data.append({
                "都道府県": prefecture,
                "路線名": rosen_name,
                "元URL": start_url,
                "リダイレクト後URL": "取得失敗"
            })

finally:
    # ブラウザを閉じる
    driver.quit()

# 結果をデータフレームに変換
result_df = pd.DataFrame(result_data)

# CSVに保存
output_csv_path = "/Users/gokiyamamoto/Desktop/SUUMO_data/output/redirected_links.csv"
result_df.to_csv(output_csv_path, index=False, encoding="utf-8-sig")
print(f"リダイレクト後のリンク情報をCSVに保存しました: {output_csv_path}")
