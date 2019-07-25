import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input

import plotly.graph_objs as go

import viz_k.dash.dash_utils as du
from viz_k.dash.dash_utils import row, column
import pandas as pd
from pandas_profiling.model.describe import describe as describe_df

import seaborn as sns
import os

# Stand alone dash app template, is reused as a link and utils functions in the dash_builder link, dash_builder_macro and
# dash_utils in the eskapade_viz package.

# -- DATA
df = sns.load_dataset('diamonds')
# TODO: Add a data uploader

desc = describe_df(df)
variables = desc['variables']
variables = {k: v for k, v in variables.items() if str(v['type'] != 'Variabe.TYPE_UNSUPPORTED')}
cats = {col: {'CAT': variables[col]['type'],
              'n_unique': variables[col]['distinct_count'] if
              str(variables[col]['type']) == "Variable.TYPE_CAT" else 0}
        for col in variables.keys()}

# get columns
selected_options = [k for k, v in cats.items() if
            (str(v['CAT']) == 'Variable.TYPE_CAT') and (int(v['n_unique']) < 10)]
options = [k for k, v in cats.items()]
# colnames = data_cols


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
options = [{'label': x, 'value': x} for x in df.columns.values]
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

# -- APP
app = dash.Dash(__name__,
                assets_folder=os.path.join(os.path.dirname(__file__)), )
app_title = 'Dash template'

# -- LAYOUT
app.layout = html.Div([
    html.Div([
        row([
            column([html.H1(app_title), *controls,
                    html.H2("Filter by:"), *filter_controls,
                    du.data_profile_tables(variables, layout_kwargs=table_layout_kwargs)], className='two columns'),
            column(figure_childs, className='ten columns'), ])
    ]),
])


# -- CALLBACKS

@app.callback(Output('fig_0', 'figure'),
              [Input('dropdown_0', 'value'),
               Input('slider_0', 'value'),
               Input('filter_dropdown', 'value')
               ])
def make_histogram1(col, bins, color_filter,):
    return du.make_histogram(df, col, bins, color_filter, layout_kwargs)


@app.callback(Output('fig_1', 'figure'),
              [Input('dropdown_1', 'value'),
               Input('slider_1', 'value'),
               Input('filter_dropdown', 'value')
               ]
              )
def make_histogram2(col, bins, color_filter,):
    return du.make_histogram(df, col, bins, color_filter, layout_kwargs)


@app.callback(Output('fig_2', 'figure'),
              [Input('dropdown_2', 'value'),
               Input('dropdown_3', 'value'),
               Input('filter_dropdown', 'value')
               ])
def make_scatter1(x, y, color_filter,):
    return du.make_scatter(df, x, y, color_filter, layout_kwargs)


@app.callback(Output('table', 'data'),
              [Input('dropdown_0', 'value')])
def update_describe(col):

    if (col != 0) and (col is not None):
        return du.data_profile_tables(variables, col).data
    else:
        return []


@app.callback(Output('table', 'style_data_conditional'),
              [Input('dropdown_0', 'value')])
def update_describe_cols(col):
    if (col != 0) and (col is not None):
        return du.data_profile_tables(variables, col).style_data_conditional
    else:
        return []


if __name__ == '__main__':
    app.run_server(debug=False, port=8089)
