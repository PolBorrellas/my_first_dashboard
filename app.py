###################################################
# SETUP
###################################################

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import json

# We start up the server. This first line is the key!
app = dash.Dash(__name__)
server = app.server

# The rest of the code is to design the webpage.
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})


# Load dataset and some required transformations
df = pd.read_csv('nama_10_gdp_1_Data.csv')

df.replace(':', np.nan, inplace=True)

df["Value"] = df["Value"].str.replace('.', '')
df["Value"] = df["Value"].str.replace(',', '.')
df["Value"] = pd.to_numeric(df["Value"])

available_indicators = df['NA_ITEM'].unique()

available_measures = df['UNIT'].unique()

available_countries = df['GEO'].unique()


###################################################
# LAYOUT
###################################################

app.layout = html.Div(children=[  # DIV = Container for content.

    html.Div([
        html.H1('Analyzing the EUROSTAT', style={'color': 'white'}),  # H1 = Main header.

        html.H2('Analyze macroeconomic indicators by year and country', style={'color': 'white'}),

        html.Div('Please, select the unit of measure, the indicator for the X axis and the indicator ' +
                 'for the Y one that you prefer.',
                 style={'color': 'white'}),
        html.Br(),

        html.Div('NOTE: If you click on a country or change the X axis indicator,' +
                 'the second graph is going to be initialized and updated.',
                 style={'color': 'white'}),

    ], style={'backgroundColor': 'black', 'padding': '15px', 'font-family': 'sans-serif'}),


    html.Div([
        html.Br(),
        html.Br(),
    ]),

    html.Div([

        html.Div([
            html.Label('Unit of measure'),
            dcc.Dropdown(
                id='unit',
                options=[{'label': i, 'value': i} for i in available_measures],
                value=available_measures[0]  # Default value
            )],
            style={'width': '48%', 'display': 'inline-block', 'font-family': 'sans-serif'}),
        html.Br(),
        html.Br(),
        html.Br(),
    ]),


    html.Div([

        html.Div([
            html.Label('Indicator for X axis'),
            dcc.Dropdown(
                id='xaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value=available_indicators[0]
            )],
            style={'width': '48%', 'display': 'inline-block', 'font-family': 'sans-serif'}),

        html.Div([
            html.Label('Indicator for Y axis'),
            dcc.Dropdown(
                id='yaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value=available_indicators[1]
            )],
            style={'width': '48%', 'float': 'right', 'display': 'inline-block', 'font-family': 'sans-serif'})
    ]),


    html.Div([

        html.Div([
            dcc.Graph(id='indicator-graphic')
        ])
    ]),


    html.Div([
        html.Div([
            dcc.Slider(
                id='year-slider',
                min=df['TIME'].min(),
                max=df['TIME'].max(),
                value=df['TIME'].max(),
                step=None,
                marks={str(year): str(year) for year in df['TIME'].unique()}
            )],
            style={'width': '90%', 'padding-left': '5%', 'padding-right': '5%', 'font-family': 'sans-serif'}),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
    ]),


    html.Div([

        html.Div([
            html.Label('Country'),
            dcc.Dropdown(
                id='country_hue',
                options=[{'label': i, 'value': i} for i in available_countries],
                value=available_countries[0]
            )],
            style={'width': '48%', 'display': 'inline-block', 'font-family': 'sans-serif'}),


        html.Div([
            html.Label('Indicator'),
            dcc.Dropdown(
                id='indicator-second-graph',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value=available_indicators[0]
            )],
            style={'width': '48%', 'float': 'right', 'display': 'inline-block', 'font-family': 'sans-serif'}),
        html.Br(),
        html.Br(),
    ]),


    html.Div([

        html.Div(id='display', style={'font-family': 'sans-serif'}),

        html.Div([
            dcc.Graph(id='country-graphic', style={'font-family': 'sans-serif'})
        ])
    ]),

])


###################################################
# INTERACTIVITY
###################################################

# FIRST: Text explaining what is plotted in second graph is updated when Country or Indicator change.
@app.callback(
    dash.dependencies.Output('display', 'children'),
    [dash.dependencies.Input('country_hue', 'value'),
     dash.dependencies.Input('indicator-second-graph', 'value')])
def set_display_children(selected_country, selected_indicator):
    return u'"{}" is being displayed for the following country: {}.'.format(
        selected_indicator, selected_country)


# SECOND: Indicator of second graph is updated if X axis indicator changes.
@app.callback(
    dash.dependencies.Output('indicator-second-graph', 'value'),
    [dash.dependencies.Input('xaxis-column', 'value')])
def indicador_update(x_indicator):
    return x_indicator


# THIRD: If the user clicks in a country, the country dropdown menu is updated.
# NOTE: I tried for 3 hours to solve this... :(
@app.callback(
    dash.dependencies.Output('country_hue', 'value'),
    [dash.dependencies.Input('indicator-graphic', 'clickData')])
def display_click_data(clickData):
    if clickData == "":
        return available_countries[0]
    else:
        data = dict(clickData)
        clickData = str(data['points'][0]['text'])
        return clickData


# FOURTH: First graph is updated if the user changes the units, the X axis, the Y axis or the year.
@app.callback(
    dash.dependencies.Output('indicator-graphic', 'figure'),
    [dash.dependencies.Input('unit', 'value'),
     dash.dependencies.Input('xaxis-column', 'value'),
     dash.dependencies.Input('yaxis-column', 'value'),
     dash.dependencies.Input('year-slider', 'value')])
def update_graph(unit_measure, xaxis_column_name,
                 yaxis_column_name, year_value):

    dff = df[(df['TIME'] == year_value) & (df['UNIT'] == unit_measure)]

    return {
        'data': [go.Scatter(
            x=dff[dff['NA_ITEM'] == xaxis_column_name]['Value'],
            y=dff[dff['NA_ITEM'] == yaxis_column_name]['Value'],
            text=dff[dff['NA_ITEM'] == yaxis_column_name]['GEO'],
            mode='markers',
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            }
        )],

        'layout': go.Layout(
            xaxis={
                'title': xaxis_column_name,
                'type': 'linear'
            },
            yaxis={
                'title': yaxis_column_name,
                'type': 'linear'
            },
            margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest'
        )
    }


# FIFTH: Second graph is updated if the user changes the units, the indicator or the country.
@app.callback(
    dash.dependencies.Output('country-graphic', 'figure'),
    [dash.dependencies.Input('unit', 'value'),
     dash.dependencies.Input('indicator-second-graph', 'value'),
     dash.dependencies.Input('country_hue', 'value')])
def update_graph(unit_measure, indicator, country):

    dff2 = df[(df['GEO'] == country) & (df['UNIT'] == unit_measure)]

    return {
        'data': [go.Scatter(
            x=dff2[dff2['NA_ITEM'] == indicator]['TIME'],
            y=dff2[dff2['NA_ITEM'] == indicator]['Value'],
            text=dff2[dff2['NA_ITEM'] == indicator]['Value'],
            mode='lines+markers',
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            }
        )],

        'layout': go.Layout(
            xaxis={
                'title': 'Time',
                'type': 'linear'
            },
            yaxis={
                'title': country,
                'type': 'linear'
            },
            margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest'
        )
    }


if __name__ == '__main__':  # Code to execute the Python script.
    app.run_server(debug=False)
