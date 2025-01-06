import os
import pandas as pd

# 出力ディレクトリ
output_dir = "./output"

# ファイル名
average_file = os.path.join(output_dir, "average_monthly_cost_by_building_and_station.csv")
final_reachable_file = os.path.join(output_dir, "final_reachable_stations.csv")  # ファイル名をご確認ください
output_file = os.path.join(output_dir, "joined_data.csv")

# レフトジョイン処理
def left_join_data():
    # ファイルの存在確認
    if not os.path.exists(average_file):
        print(f"Average monthly cost file not found: {average_file}")
        return
    if not os.path.exists(final_reachable_file):
        print(f"Final reachable stations file not found: {final_reachable_file}")
        return

    # ファイル読み込み
    average_df = pd.read_csv(average_file)
    final_reachable_df = pd.read_csv(final_reachable_file)

    # レフトジョインを実行（建物種別を除外し、駅名のみをキーにする）
    joined_df = pd.merge(
        final_reachable_df,
        average_df.rename(columns={"駅名": "駅名_cleaned"}),  # 駅名を駅名_cleaned にリネームしてキーを一致
        on="駅名_cleaned",
        how="left"
    )

    # 出力
    joined_df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"Joined data saved to {output_file}")

# 実行
if __name__ == "__main__":
    left_join_data()
