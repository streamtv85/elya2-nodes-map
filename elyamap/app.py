import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from elyamap import geoip

refresh_interval = 30  # in seconds
dfcountry = pd.read_csv('elyamap/countryMap.txt', sep='\t')

app = dash.Dash(__name__)

layout = dict(
    title='ElyaCoin Map of Network Nodes',
    height=600,
    hoverdistance=10,

    geo=dict(
        showframe=False,
        showcoastlines=True,
        coastlinecolor='rgb(92, 108, 108)',
        projection=dict(
            type='natural earth'
        )
    )
)


# returns top indicator div
def indicator(text, id_value):
    return html.Div(
        [
            html.P(
                text,
                className="twelve columns indicator_text"
            ),
            html.P(
                id=id_value,
                className="indicator_value"
            ),
        ],
        className="four columns indicator",
    )


def serve_layout():
    return html.Div(children=[

        html.Div(id='temp_value'
                 , style={'display': 'none'}
                 ),
        html.Div(
            dcc.Graph(
                className='twelve columns',
                id='elya_graph'
            ),
            className="row",
            style={"margin-bottom": "10px"}
        ),

        # indicators row
        html.Div(
            [
                indicator(
                    "Network Nodes",
                    "nodes_indicator",
                ),
                indicator(
                    "Block Height",
                    "block_indicator",
                ),
                indicator(
                    "Coins Supply (ELYA)",
                    "supply_indicator",
                ),
            ],
            className="row",
        ),

        dcc.Interval(
            id='timer',
            interval=refresh_interval * 1000,  # in milliseconds
            n_intervals=0
        )
    ],
        className='container')


# put layout to a separate function so that it is refreshed on page reload
app.layout = serve_layout
app.title = "Elya Coin World Map"


@app.callback(
    Output('elya_graph', 'figure'),
    [Input('timer', 'n_intervals')],
    [
        State("elya_graph", "figure"),
    ]
)
def update_world_map(n, current_figure):
    df = geoip.add_locations_to_df(geoip.get_peers())
    if len(df) == 0:
        return current_figure

    curr_layout = layout.copy()
    if current_figure:
        # print(current_figure['layout'])
        proj = current_figure['layout']['geo']['projection'].copy()
        if 'scale' in proj:
            curr_layout['geo']['projection']['scale'] = proj['scale']
        if 'rotation' in proj:
            curr_layout['geo']['projection']['rotation'] = proj['rotation']
        if 'center' in current_figure['layout']['geo']:
            curr_layout['geo']['center'] = current_figure['layout']['geo']['center']

    tpp = df['countryCode'].value_counts()
    df_temp = pd.DataFrame(data={'countryCode': tpp.index.tolist(), 'values': tpp.tolist()})

    ddd = df_temp.merge(dfcountry, how='inner', left_on=['countryCode'], right_on=['2let'])

    countries = dict(
        type='choropleth',
        locations=ddd['3let'],
        z=ddd['values'],
        text=ddd['Countrylet'],
        colorscale=[[0, "rgb(235, 250, 235)"], [1, "rgb(36, 143, 36)"]],
        autocolorscale=False,
        reversescale=False,
        marker=dict(
            line=dict(
                color='rgb(180,180,180)',
                width=0.5
            )),
    )
    scatter = dict(
        type='scattergeo',
        lon=df['longitude'],
        lat=df['latitude'],
        text=df['city'],
        mode='markers',
        marker=dict(
            size=6,
            opacity=0.8,
            reversescale=True,
            autocolorscale=False,
            symbol='circle',
            line=dict(
                width=1,
                color='rgba(102, 102, 102)'
            ),
            color="#ff471a"
        ))

    return dict(
        data=[countries, scatter],
        layout=curr_layout
    )


@app.callback(
    Output("nodes_indicator", "children"),
    [Input("timer", "n_intervals")],
)
def nodes_indicator_callback(n):
    return len(geoip.get_peers().index)


@app.callback(
    Output("supply_indicator", "children"),
    [Input("timer", "n_intervals")],
)
def supply_indicator_callback(n):
    return geoip.get_info()['supply']


@app.callback(
    Output("block_indicator", "children"),
    [Input("timer", "n_intervals")],
)
def block_indicator_callback(n):
    return geoip.get_info()['height']


if __name__ == '__main__':
    app.run_server(debug=True, port=8050, host='0.0.0.0')
