from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time

# ChromeDriverの設定
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# URLとパラメータの設定
base_url = "https://realestate.navitime.co.jp/chintai/reachable"
node = "00009773"
transit_limit = 3

time_ranges = [
    (0, 10),
    (11, 20),
    (21, 30),
    (31, 40),
    (41, 50),
    (51, 60),
]

data = []

# WebDriverの起動
service = Service("./src/data/chromedriver.exe")  # ChromeDriverの相対パス
with webdriver.Chrome(service=service, options=options) as driver:
    for lower_term, higher_term in time_ranges:
        url = f"{base_url}?node={node}&lower_term={lower_term}&higher_term={higher_term}&transit_limit={transit_limit}"
        print(f"アクセス中: {url}")  # URLログ出力
        driver.get(url)
        time.sleep(3)  # ページの読み込みを待つ

        # li要素を取得
        list_items = driver.find_elements(By.CSS_SELECTOR, "#text-area > ul > li")
        print(f"時間範囲 {lower_term}-{higher_term}分: {len(list_items)}件のリストを取得")

        for item in list_items:
            # 路線名の取得
            try:
                route_name = item.find_element(By.CSS_SELECTOR, "h2").text
                print(f"路線名: {route_name}")
            except Exception as e:
                route_name = ""
                print(f"路線名取得エラー: {e}")

            # 駅情報を取得
            station_items = item.find_elements(By.CSS_SELECTOR, "ul > li > div.station-info-area")
            print(f"駅情報: {len(station_items)}件取得")
            for station in station_items:
                try:
                    station_name = station.find_element(By.CSS_SELECTOR, "div.station-name").text
                except Exception as e:
                    station_name = ""
                    print(f"駅名取得エラー: {e}")

                try:
                    transit_time = station.find_element(By.CSS_SELECTOR, "div.station-note > span.time").text
                except Exception as e:
                    transit_time = ""
                    print(f"所要時間取得エラー: {e}")

                try:
                    transfer_count = station.find_element(By.CSS_SELECTOR, "div.station-note > span.transit-count").text
                except Exception as e:
                    transfer_count = ""
                    print(f"乗り換え回数取得エラー: {e}")

                print(f"データ: 駅名={station_name}, 所要時間={transit_time}, 乗り換え回数={transfer_count}, 路線名={route_name}")
                data.append([
                    station_name,
                    f"{lower_term}-{higher_term}分",
                    transit_time,
                    transfer_count,
                    route_name,
                ])

# DataFrameに変換
columns = ["駅名", "所要時間範囲", "所要時間", "乗り換え回数", "路線名"]
df = pd.DataFrame(data, columns=columns)

# CSV出力
output_path = "./output/reachable_stations.csv"
df.to_csv(output_path, index=False, encoding="utf-8-sig")
print(f"データのスクレイピングと保存が完了しました: {output_path}")
