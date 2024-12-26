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
options.add_argument('--headless')
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=options)

# 都道府県ごとのURLリスト
urls = {
    "tokyo": "https://suumo.jp/chintai/soba/tokyo/ensen/",
    "kanagawa": "https://suumo.jp/chintai/soba/kanagawa/ensen/",
    "saitama": "https://suumo.jp/chintai/soba/saitama/ensen/",
    "chiba": "https://suumo.jp/chintai/soba/chiba/ensen/",
}

# リンクデータを格納するリスト
link_data = []

try:
    for prefecture, url in urls.items():
        # 指定URLを開く
        driver.get(url)
        time.sleep(2)  # ページがロードされるのを待つ

        # テーブル要素を取得
        table = driver.find_element(By.CSS_SELECTOR, "body > div.wrapper > div > div.ui-section-body > div > div > div > div.ui-section-body.ui-section-body--mt20 > table > tbody")

        rows = table.find_elements(By.TAG_NAME, "tr")  # 各行を取得

        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")  # 各セルを取得
            for col in cols:
                # 各セル内のリンク要素をすべて取得
                links = col.find_elements(By.TAG_NAME, "a")  # <a>タグを全て探す
                for link in links:
                    try:
                        link_name = link.text  # リンクの表示名を取得
                        link_url = link.get_attribute("href")  # リンクURLを取得
                        link_data.append({
                            "都道府県": prefecture,
                            "路線名": link_name,
                            "URL": link_url
                        })
                    except Exception as e:
                        print(f"リンク取得中にエラー: {e}")  # エラーログを出力（デバッグ用）

    # データフレームを作成
    df = pd.DataFrame(link_data)

    # CSVに保存
    output_csv_path = "/Users/gokiyamamoto/Desktop/SUUMO_data/output/rosen_link.csv"
    df.to_csv(output_csv_path, index=False, encoding="utf-8-sig")
    print(f"リンク情報をCSVに保存しました: {output_csv_path}")

finally:
    # ブラウザを閉じる
    driver.quit()
