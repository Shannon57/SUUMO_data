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

px.set_mapbox_access_token(mapbox_token)

# データの読み込み
data = pd.read_csv("./output/final_reachable_stations.csv")
data["company"] = data["company"].replace("不明", "その他")

# カラーマッピング
color_map = {
    "0-10分": "#d73027",
    "11-20分": "#fc8d59",
    "21-30分": "#fee08b",
    "31-40分": "#d9ef8b",
    "41-50分": "#91bfdb",
    "51-60分": "#4575b4"
}

# Dashアプリの設定
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# 初期の地図範囲とズームレベルを設定
initial_view = {
    "center": {"lat": 35.68, "lon": 139.76},  # 東京駅付近
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

# データのフィルタリング
def filter_data(selected_time_ranges, selected_transfer_counts):
    # 所要時間範囲と乗り換え回数でフィルタリング
    time_ranges = selected_time_ranges.split(",") if selected_time_ranges else data["所要時間範囲"].unique()
    transfer_counts = selected_transfer_counts.split(",") if selected_transfer_counts else data["乗り換え回数"].unique()
    return data[
        (data["所要時間範囲"].isin(time_ranges)) &
        (data["乗り換え回数"].isin(transfer_counts))
    ]

# 地図の生成
def create_map_figure(filtered_data, map_state):
    fig = px.scatter_mapbox(
        filtered_data,
        lat="lat",
        lon="lon",
        color="所要時間範囲",
        color_discrete_map=color_map,
        hover_name="駅名",
        hover_data={
            "所要時間": True,
            "乗り換え回数": True,
            "路線名": True,
            "company": True
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


# 路線名リストをスクロール可能な領域に表示するスタイルを追加
@app.callback(
    [
        Output("map-graph", "figure"),
        Output("map-state", "data"),
        Output("route-table", "children")
    ],
    [
        Input("time-range-filter", "value"),
        Input("transfer-count-filter", "value"),
        Input("map-graph", "relayoutData")
    ],
    State("map-state", "data")
)
def update_map(selected_time_ranges, selected_transfer_counts, relayout_data, map_state):
    # 地図状態を更新
    if relayout_data:
        if "mapbox.center" in relayout_data:
            map_state["center"] = relayout_data["mapbox.center"]
        if "mapbox.zoom" in relayout_data:
            map_state["zoom"] = relayout_data["mapbox.zoom"]

    # データをフィルタリング
    filtered_data = filter_data(selected_time_ranges, selected_transfer_counts)

    # ユニークな路線名を取得して表形式で表示
    unique_routes = filtered_data["路線名"].unique()
    table_children = html.Div(
        [
            html.Table(
                [
                    html.Thead(html.Tr([html.Th("路線名")])),
                    html.Tbody([html.Tr([html.Td(route)]) for route in unique_routes])
                ],
                className="table table-dark table-striped"
            )
        ],
        style={"maxHeight": "300px", "overflowY": "scroll", "border": "1px solid #ccc"}
    )

    # 地図の生成
    if not filtered_data.empty:
        fig = create_map_figure(filtered_data, map_state)
    else:
        fig = px.scatter_mapbox()
        fig.update_layout(
            paper_bgcolor="black",
            mapbox=dict(
                center=map_state["center"],
                zoom=map_state["zoom"]
            )
        )
    return fig, map_state, table_children


# アプリケーション実行
if __name__ == "__main__":
    app.run_server(debug=True)
    
    
