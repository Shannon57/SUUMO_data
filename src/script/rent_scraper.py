import os
import re
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# ChromeDriverの設定
service = Service("./src/data/chromedriver.exe")
options = Options()
# options.add_argument("--headless")  # ヘッドレスモード（表示なし）
options.add_argument("--disable-gpu")
driver = webdriver.Chrome(service=service, options=options)

# 地域ごとの設定（新しいURL）
#（1LDK、マンション、アパート、7分以内、10年以内、バス・トイレ別、2階以上、エアコン付き、オートロック）
regions = {
    "tokyo": {
        "url": "https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&pc=50&smk=&po1=25&po2=99&shkr1=03&shkr2=03&shkr3=03&shkr4=03&ekInput=84570&ta=13&kskbn=01&tj=60&nk=-1&cb=0.0&ct=9999999&md=04&ts=1&ts=2&et=7&mb=0&mt=9999999&cn=10&tc=0400301&tc=0400101&tc=0400601&tc=0400801&fw2=&page=",
    },
    "kanagawa": {
        "url": "https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&ta=14&bs=040&ekInput=84570&tj=60&nk=-1&ct=9999999&cb=0.0&md=04&ts=1&ts=2&et=7&mt=9999999&mb=0&cn=10&tc=0400101&tc=0400601&tc=0400301&tc=0400801&shkr1=03&shkr2=03&shkr3=03&shkr4=03&fw2=&pc=50&page=",
    },
    "chiba": {
        "url": "https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&ta=12&bs=040&ekInput=84570&tj=60&nk=-1&ct=9999999&cb=0.0&md=04&ts=1&ts=2&et=7&mt=9999999&mb=0&cn=10&tc=0400101&tc=0400601&tc=0400301&tc=0400801&shkr1=03&shkr2=03&shkr3=03&shkr4=03&fw2=&pc=50&page=",
    },
    "saitama": {
        "url": "https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&ta=11&bs=040&ekInput=84570&tj=60&nk=-1&ct=9999999&cb=0.0&md=04&ts=1&ts=2&et=7&mt=9999999&mb=0&cn=10&tc=0400101&tc=0400601&tc=0400301&tc=0400801&shkr1=03&shkr2=03&shkr3=03&shkr4=03&fw2=&pc=50&page=",
    },
}

# 最大ページ数を動的に取得
def get_max_pages():
    error_pop = driver.find_elements(By.CSS_SELECTOR, "#js-leftColumnForm > div.error_pop.error_pop--fr > div")
    return len(error_pop) == 0  # エラーがない場合、次のページが存在

# 出力フォルダ
output_dir = "./output"
os.makedirs(output_dir, exist_ok=True)

# データ取得関数
def scrape_region(region_name, region_info):
    region_dir = os.path.join(output_dir, region_name)
    os.makedirs(region_dir, exist_ok=True)
    all_data = []

    page = 1
    while True:
        url = f"{region_info['url']}{page}"
        driver.get(url)
        # time.sleep(1)  # 1秒間隔

        # 最大ページ判定
        if not get_max_pages():
            print(f"Reached last page for {region_name}. Total pages: {page-1}")
            break

        try:
            # 各物件情報を取得
            properties = driver.find_elements(By.CSS_SELECTOR, "#js-bukkenList > ul > li")
            for property in properties:
                # 建物種別
                building_type = property.find_element(By.CSS_SELECTOR, ".cassetteitem_content-label > span").text

                # 建物名
                building_name = property.find_element(By.CSS_SELECTOR, ".cassetteitem_content-title").text

                # 路線情報（元データ）
                line_info = property.find_element(By.CSS_SELECTOR, ".cassetteitem_detail-col2 > div:nth-child(1)").text

                # 駅名
                match = re.search(r"/(.+?)駅", line_info)
                station_name = match.group(1) if match else None

                # 賃料・管理費を取得し、月額を計算
                rows = property.find_elements(By.CSS_SELECTOR, ".cassetteitem-item > table > tbody > tr")
                for row in rows:
                    try:
                        rent_text = row.find_element(By.CSS_SELECTOR, "td:nth-child(4) > ul > li:nth-child(1) > span > span").text
                        management_fee_text = row.find_element(By.CSS_SELECTOR, "td:nth-child(4) > ul > li:nth-child(2) > span").text

                        # 賃料を「万円」単位に変換
                        rent = float(rent_text.replace("万円", "").strip())

                        # 管理費を「万円」単位に変換
                        if management_fee_text == "-":
                            management_fee = 0  # 管理費が`-`の場合は0
                        else:
                            management_fee = float(management_fee_text.replace("円", "").replace(",", "").strip()) / 10000  # 円を万円に変換

                        # 月額を計算
                        monthly_cost = rent + management_fee

                    except Exception as e:
                        print(f"Error processing rent or management fee: {e}")
                        rent, management_fee, monthly_cost = None, None, None

                    # データを格納
                    all_data.append({
                        "建物種別": building_type,
                        "建物名": building_name,
                        "路線情報": line_info,
                        "駅名": station_name,
                        "賃料": rent,
                        "管理費": management_fee,
                        "月額": monthly_cost,
                    })
        except Exception as e:
            print(f"Error on page {page} of {region_name}: {e}")

        page += 1

    # CSV保存
    df = pd.DataFrame(all_data)
    output_file = os.path.join(region_dir, "scraped_data.csv")
    df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"Saved {region_name} data to {output_file}")

# 全データをマージ
def merge_data():
    merged_data = []
    for region in regions.keys():
        file_path = os.path.join(output_dir, region, "scraped_data.csv")
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            merged_data.append(df)

    if merged_data:
        merged_df = pd.concat(merged_data, ignore_index=True)
        merged_df.to_csv(os.path.join(output_dir, "merged_data.csv"), index=False, encoding="utf-8-sig")
        print("Saved merged data to ./output/merged_data.csv")

# メイン関数
def main():
    # 地域ごとにスクレイピング
    for region, info in regions.items():
        scrape_region(region, info)

    # 全データをマージ
    merge_data()

    # ドライバーを終了
    driver.quit()

# エントリーポイント
if __name__ == "__main__":
    main()
