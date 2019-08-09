import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State

import plotly.graph_objs as go

import dash_utils as du
from dash_utils import row, column
import pandas as pd
from pandas_profiling.model.describe import describe as describe_df

import seaborn as sns
import os
import json

# Stand alone dash app template, is reused as a link and utils functions in the dash_builder link, dash_builder_macro and


def update_data(var_kids, data_kids):
    variables_ = var_kids[0]
    variables_ = {k: v for k, v in variables_.items() if str(v['type'] != 'Variable.TYPE_UNSUPPORTED')}

    cats = {col: {'CAT': variables_[col]['type'],
                  'n_unique': variables_[col]['distinct_count'] if
                  str(variables_[col]['type']) == "Variable.TYPE_CAT" else 0}
            for col in variables_.keys()}
    # get columns
    selected_options_ = [k for k, v in cats.items() if
                         (str(v['CAT']) == 'Variable.TYPE_CAT') and (int(v['n_unique']) < 10)]
    options_ = [k for k, v in cats.items()]

    return variables_, options_, selected_options_


def get_from_json(var_kids=None):
    if var_kids != []:
        out = json.loads(var_kids)
        vari = dict(out['variables'])
        opt = list(out['options'])
        selopt = list(out['selected_options'])
    else:
        return {}, [], []

    return vari, opt, selopt


if __name__ == '__main__':
    print("New containers")
    df = sns.load_dataset('diamonds')
    desc = describe_df(df)

    data_container = html.Div([df.to_json(orient='split')], id='data_container', style={'display': 'none'})
    var_container = html.Div([desc['variables']], id='var_container', style={'display': 'none'})

    variables, options, selected_options = update_data(var_container.children, data_container.children)
else:

    # variables, options, selected_options = get_from_json(var_container.children)
    options = []
    selected_options = []
    variables = {}
# -- SETTINGS
layout_kwargs = dict(plot_bgcolor='#263740',
                     paper_bgcolor='#1d2930',
                     font=dict(color='white'),
                     margin=go.layout.Margin(b=30, l=30,
                                             r=30, t=40,
                                             pad=5))

table_layout_kwargs = dict(style_header={'backgroundColor': layout_kwargs['plot_bgcolor'],
                                         'fontWeight': 'bold',
                                         'fontSize': '2em'},
                           style_cell={'backgroundColor': layout_kwargs['paper_bgcolor'],
                                       'color': layout_kwargs['font']['color'],
                                       'fontSize': '.7em',
                                       'height': '5px'},
                           style_cell_conditional=[{'if': {'column_id': 'var'},
                                                   'textAlign': 'left'}])


# -- FIGURES AND CONTROLS
# options = [{'label': x, 'value': x} for x in df.columns.values]
controls = du.make_control_list([dict(name='Dropdown', args={'options': options, 'value': None, 'id': 'dropdown_0'}),
                                 dict(name='Slider', args=dict(min=0, max=100, value=50, step=1, id="slider_0")),
                                 dict(name='Dropdown', args={'options': options, 'value': None, 'id': 'dropdown_1'}),
                                 dict(name='Slider', args=dict(min=0, max=100, value=50, step=1, id="slider_1")),
                                 dict(name='Dropdown', args={'options': options, 'value': None, 'id': 'dropdown_2'}),
                                 dict(name='Dropdown', args={'options': options, 'value': None, 'id': 'dropdown_3'})])

# -- make grids
figure_childs = du.figure_grid(3, layout_kwargs=layout_kwargs)
filter_controls = [dcc.Dropdown(options=[{'label': x, 'value': x} for x in selected_options],
                                id='filter_dropdown',
                                value=None)]


# -- LAYOUT
layout = html.Div([
    html.Div([
        row([
            column([html.H1('Dash Template', id='title'), *controls,
                    html.H2("Filter by:"), *filter_controls,
                    du.data_profile_tables(variables, layout_kwargs=table_layout_kwargs, id='ta_table')], className='two columns'),
            column(figure_childs, className='ten columns'), ])
    ])
])

# -- APP
# in place so we can reuse this script in multipage app. If run stand-alone, new all is initialized
if __name__ == 'template_app':
    from app import app
else:
    app = dash.Dash(__name__,
                    assets_folder=os.path.join(os.path.dirname(__file__)))
    app.layout = layout
    app.title = 'Dash template'

# -- CALLBACKS


@app.callback(Output('fig_0', 'figure'),
              [Input('dropdown_0', 'value'),
               Input('slider_0', 'value'),
               Input('filter_dropdown', 'value')],
              [State('data_container', 'children')])
def make_histogram1(col, bins, color_filter, raw_data):
    print(raw_data)
    if raw_data:
        dff = pd.read_json(raw_data, orient='split')
        return du.make_histogram(dff, col, bins, color_filter, layout_kwargs)


@app.callback(Output('fig_1', 'figure'),
              [Input('dropdown_1', 'value'),
               Input('slider_1', 'value'),
               Input('filter_dropdown', 'value')],
              [State('data_container', 'children')]
              )
def make_histogram2(col, bins, color_filter, raw_data):
    if raw_data:
        dff = pd.read_json(raw_data[0], orient='split')
        return du.make_histogram(dff, col, bins, color_filter, layout_kwargs)


@app.callback(Output('fig_2', 'figure'),
              [Input('dropdown_2', 'value'),
               Input('dropdown_3', 'value'),
               Input('filter_dropdown', 'value')],
              [State('data_container', 'children')]
              )
def make_scatter1(x, y, color_filter, raw_data):
    if raw_data:
        dff = pd.read_json(raw_data[0], orient='split')
        return du.make_scatter(dff, x, y, color_filter, layout_kwargs)


@app.callback(Output('ta_table', 'data'),
              [Input('dropdown_0', 'value')],
              [State('var_container', 'children')]
              )
def update_describe(col, var_string):

    if (col != 0) and (col is not None):
        return du.data_profile_tables(var_string, col).data
    else:
        return []

# this worked before??
# @app.callback(Output('ta_table', 'style_data_conditional'),
#               [Input('dropdown_0', 'value')],
#               [State('var_container', 'children')])
# def update_describe_cols(col, var_string):
#     if (col != 0) and (col is not None):
#         return du.data_profile_tables(var_string, col).style_data_conditional
#     else:
#         return []


if __name__ == '__main__':
    app.run_server(debug=False, port=8089)
