import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_utils as du

import seaborn as sns
import json
import plotly.graph_objs as go

from app import app

import pandas as pd

# base_path = os.path.abspath(os.path.dirname(__file__))

# -- data
# df = pd.read_csv('./data/diamonds.csv', sep=',', index_col=0)
# df = sns.load_dataset('diamonds')
# # using pandas profiling to create the description
# desc = describe_df(df)
# variables = desc['variables']
# variables = {k: v for k, v in variables.items() if str(v['type'] != 'Variabe.TYPE_UNSUPPORTED')}
# cats = {col: {'CAT': variables[col]['type'],
#               'n_unique': variables[col]['distinct_count'] if
#               str(variables[col]['type']) == "Variable.TYPE_CAT" else 0}
#         for col in variables.keys()}
#
# # get columns
# hue_cols = [k for k, v in cats.items() if
#             (str(v['CAT']) == 'Variable.TYPE_CAT') and (int(v['n_unique']) < 10)]
# data_cols = [k for k, v in cats.items()]
# colnames = data_cols
#
# if __name__ == 'df_summary':
#     from data_loader import data_container
#     df = pd.read_json(data_container.children)
#
plt_bgcolor = '#263740'
plt_papercolor = '#1d2930'
text_color = 'white'
#
# pdict = {x: str(x) for x in colnames}

layout = html.Div([
    html.H1('DataFrames: A summary'),
    html.Div([
        html.Div([
            dcc.Graph(id='Histogram',
                      figure={'layout': go.Layout(plot_bgcolor=plt_bgcolor,
                                                  paper_bgcolor=plt_papercolor,
                                                  font=dict(color=text_color))}),
            dcc.Slider(id='bin_slider1',
                       min=1,
                       max=100,
                       step=1,
                       value=30,
                       updatemode='drag'),
            html.H5("Variable"),
            dcc.Dropdown(id='x_dropdown',
                         # options=[{'label': pdict[x], 'value': x} for x in data_cols],
                         options=[],
                         value=0, placeholder='Select...',
                         style={'width': '80%'}),
            html.H5("Hue"),
            dcc.Dropdown(id='hue_dropdown',
                         # options=[{'label': pdict[x], 'value': x} for x in hue_cols],
                         options=[],
                         value=0, placeholder='Select...',
                         style={'width': '80%'}),
            ]
            )], className='five columns'),
    html.Div([
        html.Div([], className='two columns'),
        html.Div([
            dash_table.DataTable(id='table',
                                 data=[],
                                 columns=[{'name': 'Description', 'id': 'description'},
                                          {'name': 'Value', 'id': 'value'}],
                                 style_header={'backgroundColor': plt_bgcolor,
                                               'fontWeight': 'bold',
                                               'fontSize': '2em'},
                                 style_cell={'backgroundColor': plt_papercolor,
                                             'color': text_color,
                                             'fontSize': '.7em',
                                             'height': '5px'},
                                 style_cell_conditional=[{'if': {'column_id': 'var'},
                                                         'textAlign': 'left'}]
                                 )
            ],
             className='four columns')]
            )])

# --  app
# in place so we can reuse this script in multipage app. If run stand-alone, new all is initialized
# if __name__ == "df_summary":

# else:
#     app = dash.Dash(__name__)
#     app.layout = layout
# # -- update functions


@app.callback(
    Output('Histogram', 'figure'),
    [Input('x_dropdown', 'value'),
     Input('hue_dropdown', 'value'),
     Input('bin_slider1', 'value')],
     [State('data_container', 'children')])
def update_plot(value_x, hue, bins, raw_data):
    if raw_data:
        df = pd.read_json(raw_data, orient='split')
        colnames = df.columns
        pdict = {x: str(x) for x in colnames}
    else:
        df = pd.DataFrame()
        pdict = {}
    if (hue != 0) & (value_x != 0):
        pal = sns.palettes.color_palette('YlGnBu', n_colors=len(df[hue].unique()))
        pal = pal.as_hex()
        return {'data': [go.Histogram(
                     x=df.loc[df[hue] == col, value_x],
                     nbinsx=bins,
                     name=str(col),
                     marker=dict(color=pal[i]),
                     text=df[value_x])
                   for i, col in enumerate(df[hue].unique())],
                'layout': go.Layout(
                          xaxis={'title': pdict[value_x]},
                          plot_bgcolor=plt_bgcolor,
                          paper_bgcolor=plt_papercolor,
                          font=dict(color=text_color))}
    elif value_x != 0:
        return {'data': [go.Histogram(
                     x=df[value_x],
                     nbinsx=bins,
                     text=df[value_x])],
                'layout': go.Layout(
                          xaxis={'title': pdict[value_x]},
                          plot_bgcolor=plt_bgcolor,
                          paper_bgcolor=plt_papercolor,
                          font=dict(color=text_color),
                            )}
    else:
        return {'data': [],
                'layout': go.Layout(
                          xaxis={'title': ''},
                          plot_bgcolor=plt_bgcolor,
                          paper_bgcolor=plt_papercolor,
                          font=dict(color=text_color),
                            )}


@app.callback(Output('table', 'data'),
              [Input('x_dropdown', 'value')],
              [State('var_container', 'children')])
def update_describe(col, var_kids):
    variables = json.loads(var_kids)['variables'] if var_kids else {}
    if (col != 0) and (col is not None):
        return du.data_profile_tables(variables, col).data
    else:
        return []


@app.callback(Output('table', 'columns'),
              [Input('x_dropdown', 'value')],
              [State('var_container', 'children')])
def update_describe_cols(col, var_kids):
    variables = json.loads(var_kids)['variables'] if var_kids else {}
    if (col != 0) and (col is not None):
        return du.data_profile_tables(variables, col).columns
    else:
        return []


@app.callback(Output('table', 'style_data_conditional'),
              [Input('x_dropdown', 'value')],
              [State('var_container', 'children')])
def update_describe_cols(col, var_kids):
    variables = json.loads(var_kids)['variables'] if var_kids else {}
    if (col != 0) and (col is not None):
        return du.data_profile_tables(variables, col).style_data_conditional
    else:
        return []


@app.callback(Output('x_dropdown', 'options'),
              [Input('var_container', 'children')])
def update_options_xdropdown(var_kids):
    variables = json.loads(var_kids)['variables'] if var_kids else {}
    # vari = [v for v in variables.keys() if variables[v]['type'] == 'TYPE_CAT']
    return [{'label': x, 'value': x} for x in variables]


@app.callback(Output('hue_dropdown', 'options'),
              [Input('var_container', 'children')])
def update_options_huedropdown(var_kids):
    variables = json.loads(var_kids)['variables'] if var_kids else {}
    vari = [v for v in variables.keys() if variables[v]['type'] == 'TYPE_CAT']
    return [{'label': x, 'value': x} for x in vari]

# if __name__ == '__main__':
#     app.run_server(debug=False)
