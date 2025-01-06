import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
import dash_bootstrap_components as dbc
from dotenv import load_dotenv
import os

# 環境変数からMapboxトークンを読み込み
load_dotenv()
mapbox_token = os.getenv("MAPBOX_ACCESS_TOKEN")
if not mapbox_token:
    raise ValueError("Mapbox APIキーが環境変数に設定されていません。")

MIN_MONTHLY_COST = 5
MAX_MONTHLY_COST = 30

px.set_mapbox_access_token(mapbox_token)

# データの読み込み
data = pd.read_csv("./output/joined_data.csv")
data["company"] = data["company"].replace("不明", "その他")

# カラーマッピング（デフォルト）
time_range_color_map = {
    "0-10分": "#d73027",
    "11-20分": "#fc8d59",
    "21-30分": "#fee08b",
    "31-40分": "#d9ef8b",
    "41-50分": "#91bfdb",
    "51-60分": "#4575b4"
}

# 月額のカラーパレット設計（パステルカラー）
def generate_monthly_cost_color_map():
    color_map = {}
    thresholds = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
    colors = px.colors.sequential.RdBu_r  # 赤から青のグラデーション
    for i, threshold in enumerate(thresholds):
        if i == 0:
            color_map[f"{threshold}以下"] = colors[0]
        elif i == len(thresholds) - 1:
            color_map[f"{threshold}以上"] = colors[-1]
        else:
            color_map[f"{threshold}超～{threshold + 1}以下"] = colors[i]
    return color_map

monthly_cost_color_map = generate_monthly_cost_color_map()

# Dashアプリの設定
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], suppress_callback_exceptions=True)


# 初期の地図範囲とズームレベルを設定
initial_view = {
    "center": {"lat": 35.635, "lon": 139.741},  # 高輪ゲートウェイ駅付近
    "zoom": 10
}

# フィルタカードの作成
def create_filter_card(title, children):
    return dbc.Card(
        dbc.CardBody(
            [
                html.H5(title, className="card-title text-light"),
                html.Div(children, className="mt-3")
            ]
        ),
        className="mb-4 bg-secondary shadow-sm"
    )

# 所要時間範囲の選択肢生成
def get_time_range_options():
    return [
        {"label": "10分まで", "value": "0-10分"},
        {"label": "20分まで", "value": "0-10分,11-20分"},
        {"label": "30分まで", "value": "0-10分,11-20分,21-30分"},
        {"label": "40分まで", "value": "0-10分,11-20分,21-30分,31-40分"},
        {"label": "50分まで", "value": "0-10分,11-20分,21-30分,31-40分,41-50分"},
        {"label": "60分まで", "value": "0-10分,11-20分,21-30分,31-40分,41-50分,51-60分"}
    ]

# 乗り換え回数の選択肢生成
def get_transfer_options():
    return [
        {"label": "乗り換え0回", "value": "乗換0回"},
        {"label": "乗り換え1回まで", "value": "乗換0回,乗換1回"},
        {"label": "乗り換え2回まで", "value": "乗換0回,乗換1回,乗換2回"},
        {"label": "乗り換え3回まで", "value": "乗換0回,乗換1回,乗換2回,乗換3回"}
    ]

def filter_data(selected_building_type, selected_time_ranges, selected_transfer_counts, monthly_cost_range):
    filtered_data = data

    # 建物種別フィルタを適用
    if selected_building_type != "所要時間マップ" and isinstance(selected_building_type, str):
        filtered_data = filtered_data[filtered_data["建物種別"] == selected_building_type]

    # 所要時間範囲と乗り換え回数でフィルタリング
    time_ranges = selected_time_ranges.split(",") if selected_time_ranges else data["所要時間範囲"].unique()
    transfer_counts = selected_transfer_counts.split(",") if selected_transfer_counts else data["乗り換え回数"].unique()
    filtered_data = filtered_data[
        (filtered_data["所要時間範囲"].isin(time_ranges)) &
        (filtered_data["乗り換え回数"].isin(transfer_counts))
    ]

    # 月額範囲でフィルタリング
    if monthly_cost_range and len(monthly_cost_range) == 2:
        min_mcr = monthly_cost_range[0]
        max_mcr = monthly_cost_range[1]
        if (min_mcr == MIN_MONTHLY_COST):
            min_mcr = 0
        if (max_mcr == MAX_MONTHLY_COST):
            max_mcr = 99999
        filtered_data = filtered_data[
            (filtered_data["月額"] >= monthly_cost_range[0]) &
            (filtered_data["月額"] <= monthly_cost_range[1])
        ]

    return filtered_data

# 色分け用のカラムを生成
def assign_color_category(row):
    if pd.isna(row["月額"]):
        return "不明"
    elif row["月額"] <= 8:
        return "8以下"
    elif row["月額"] > 18:
        return "18以上"
    else:
        return f"{int(row['月額'])}超～{int(row['月額']) + 1}以下"

data["月額カテゴリ"] = data.apply(assign_color_category, axis=1)

# 地図の生成
def create_map_figure(filtered_data, map_state, color_by):
    if color_by == "所要時間範囲":
        color_column = "所要時間範囲"
        color_map = time_range_color_map
    else:  # color_by == "月額"
        color_column = "月額カテゴリ"
        color_map = monthly_cost_color_map

    fig = px.scatter_mapbox(
        filtered_data,
        lat="lat",
        lon="lon",
        color=color_column,
        color_discrete_map=color_map,
        hover_name="駅名",
        hover_data={
            "所要時間": True,
            "乗り換え回数": True,
            "路線名": True,
            "company": True,
            "月額": True
        },
        mapbox_style="carto-darkmatter"
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="black",
        mapbox=dict(
            center=map_state["center"],
            zoom=map_state["zoom"]
        ),
        showlegend=False  # 凡例を非表示
    )
    fig.update_traces(marker=dict(size=12))
    return fig
# アプリのレイアウト
app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        create_filter_card(
                            "マップタイプ",
                            dcc.Dropdown(
                                id="building-type-filter",
                                options=[
                                    {"label": "所要時間マップ", "value": "所要時間マップ"},
                                    {"label": "賃貸アパートマップ", "value": "賃貸アパート"},
                                    {"label": "賃貸マンションマップ", "value": "賃貸マンション"}
                                ],
                                value="所要時間マップ",
                                className="text-dark"
                            )
                        ),
                        create_filter_card(
                            "所要時間範囲",
                            dcc.Dropdown(
                                id="time-range-filter",
                                options=get_time_range_options(),
                                value="0-10分",  # 初期値を設定
                                className="text-dark"
                            )
                        ),
                        create_filter_card(
                            "乗り換え回数",
                            dcc.Dropdown(
                                id="transfer-count-filter",
                                options=get_transfer_options(),
                                value="乗換0回",
                                className="text-dark"
                            )
                        ),
                        create_filter_card(
                            "家賃スライダー",
                            html.Div(
                                [
                                    dcc.RangeSlider(
                                        id="monthly-cost-slider",
                                        min=MIN_MONTHLY_COST,
                                        max=MAX_MONTHLY_COST,
                                        step=1,
                                        value=[MIN_MONTHLY_COST, MAX_MONTHLY_COST],  # 初期値を設定
                                        marks={i: f"{i}" for i in range(MIN_MONTHLY_COST, MAX_MONTHLY_COST+1, 5)},
                                        # tooltip={"always_visible": False, "placement": "bottom"},  # スライダーのツールチップを非表示
                                    ),
                                    html.Div(
                                        id="slider-output-container",
                                        className="text-light mt-2",
                                        style={"text-align": "center"}  # 中央揃え
                                    )
                                ]
                            )
                        ),
                        # 最安の駅カード
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H6("最安の駅", className="card-title text-light"),
                                    html.P(id="cheapest-station", className="card-text text-light"),
                                ]
                            ),
                            id="cheapest-station-card",  # カードのIDを追加
                            style={"display": "block"},  # デフォルトは表示
                            className="mb-4 bg-secondary shadow-sm"
                        ),
                        # 最も高い駅カード
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H6("最も高い駅", className="card-title text-light"),
                                    html.P(id="most-expensive-station", className="card-text text-light"),
                                ]
                            ),
                            id="most-expensive-station-card",  # カードのIDを追加
                            style={"display": "block"},  # デフォルトは表示
                            className="mb-4 bg-secondary shadow-sm"
                        ),
                        html.Div(id="route-table", className="mt-3"),  # フィルタ結果の表表示
                    ],
                    width=3,
                    className="bg-dark p-4"
                ),
                dbc.Col(
                    [
                        dcc.Graph(
                            id="map-graph",
                            style={"height": "90vh", "border": "2px solid white"},
                            config={"scrollZoom": True}
                        )
                    ],
                    width=9
                )
            ],
            className="g-0 bg-black"
        ),
        dcc.Store(id="map-state", data=initial_view)  # 地図状態を保持するためのストレージ
    ],
    fluid=True
)

@app.callback(
    Output("slider-output-container", "children"),
    Input("monthly-cost-slider", "value")
)
def update_slider_output(value):
    min_val = value[0]
    max_val = value[1]
    if (min_val == MIN_MONTHLY_COST):
        min_val = str(min_val) + '万円以下'
    else :
        min_val = str(min_val) + '万円'
    if (max_val == MAX_MONTHLY_COST):
        max_val = str(max_val) + '万円以上'
    else :
        max_val = str(max_val) + '万円'
    return f"選択範囲: {min_val} ～ {max_val}"


@app.callback(
    [
        Output("map-graph", "figure"),
        Output("map-state", "data"),
        Output("route-table", "children"),
        Output("cheapest-station", "children"),
        Output("most-expensive-station", "children"),
        Output("cheapest-station-card", "style"),
        Output("most-expensive-station-card", "style")
    ],
    [
        Input("building-type-filter", "value"),
        Input("time-range-filter", "value"),
        Input("transfer-count-filter", "value"),
        Input("monthly-cost-slider", "value")
    ],
    [
        State("map-state", "data")
    ]
)
def update_map(selected_building_type, selected_time_ranges, selected_transfer_counts, monthly_cost_range, map_state):
    # デフォルトの地図状態
    center = map_state.get("mapbox.center", initial_view["center"])
    zoom = map_state.get("mapbox.zoom", initial_view["zoom"])

    # データをフィルタリング
    filtered_data = filter_data(
        selected_building_type,
        selected_time_ranges,
        selected_transfer_counts,
        monthly_cost_range
    )

    # 条件に一致するデータがない場合の処理
    if filtered_data.empty:
        empty_figure = px.scatter_mapbox()
        empty_figure.update_layout(
            paper_bgcolor="black",
            mapbox=dict(
                center=center,
                zoom=zoom
            )
        )
        return (
            empty_figure,
            {"center": center, "zoom": zoom},
            html.Div("条件に一致するデータがありません。", className="text-light text-center mt-3"),
            "",
            "",
            {"display": "none"},
            {"display": "none"}
        )

    # 色分けを決定
    color_by = "所要時間範囲" if selected_building_type == "所要時間マップ" else "月額"

    # 最安・最も高い駅の計算
    try:
        cheapest = filtered_data.loc[filtered_data["月額"].idxmin()]
        cheapest_station = f"{cheapest['駅名']}（月額: {cheapest['月額']}万円）"
        most_expensive = filtered_data.loc[filtered_data["月額"].idxmax()]
        most_expensive_station = f"{most_expensive['駅名']}（月額: {most_expensive['月額']}万円）"
        cheapest_style = {"display": "block"}
        most_expensive_style = {"display": "block"}
    except ValueError:  # 万が一エラーが発生した場合
        cheapest_station = ""
        most_expensive_station = ""
        cheapest_style = {"display": "none"}
        most_expensive_style = {"display": "none"}

    # 地図の生成
    fig = create_map_figure(filtered_data, {"center": center, "zoom": zoom}, color_by)

    return (
        fig,
        {"center": center, "zoom": zoom},
        html.Div(),  # ダミー
        cheapest_station,
        most_expensive_station,
        cheapest_style,
        most_expensive_style
    )



# アプリケーション実行
if __name__ == "__main__":
    app.run_server(debug=True)