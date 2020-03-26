import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def define_layout(app):
    cities = pd.read_csv('vTweet/locations.csv')

    fig = go.Figure(go.Scattermapbox(
        lat=cities.lat,
        lon=cities.lon,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=15
        ),
        text=cities.City,
    ))

    fig.update_layout(
        hovermode='closest',
        mapbox=dict(
            accesstoken="pk.eyJ1IjoicHJheWFncyIsImEiOiJjazg0a2s2cW0wMjZ4M2ZxaWVwN2RjaWNyIn0.KyGDUQeBGGFCjD2UWjFixg",
            center=dict(lat=22, lon=72),
            zoom=6
        ),
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        height=500
    )

    app.layout = html.Div(children=[
        html.H3(children='Hello GG'),

        dcc.Graph(
            id='example-map',
            figure=fig
        )
    ])
