import os
import pandas as pd

# 出力ディレクトリ
output_dir = "./output"

# 平均月額計算関数
def calculate_average_monthly_cost():
    # マージ済みデータのファイルパス
    merged_file_path = os.path.join(output_dir, "merged_data.csv")
    
    # ファイルが存在するかチェック
    if not os.path.exists(merged_file_path):
        print("Merged data file not found!")
        return

    # マージ済みデータを読み込む
    df = pd.read_csv(merged_file_path)

    # 月額の平均値を計算 (建物種別と駅名でグループ化)
    grouped = df.groupby(["建物種別", "駅名"], as_index=False)["月額"].mean()

    # 四捨五入して少数第2位まで
    grouped["月額"] = grouped["月額"].round(2)

    # 平均月額データを保存する
    output_file = os.path.join(output_dir, "average_monthly_cost_by_building_and_station.csv")
    grouped.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"Saved average monthly cost data to {output_file}")

# 平均月額計算関数を実行
if __name__ == "__main__":
    calculate_average_monthly_cost()
