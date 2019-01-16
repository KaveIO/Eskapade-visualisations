import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input

import plotly.graph_objs as go

import eskapade_viz.dash_utils as du
from eskapade_viz.dash_utils import row, column

import seaborn as sns
import os

# Stand alone dash app template, is reused as a link and utils functions in the dash_builder link, dash_builder_macro and
# dash_utils in the eskapade_viz package.

# -- DATA
# df = sns.load_dataset('diamonds')
# selected_options = ['cut', 'color', 'clarity', 'carat']
# ['anscombe', 'attention', 'brain_networks', 'car_crashes', 'diamonds', 'dots', 'exercise', 'flights', 'fmri', 'gammas', 'iris', 'mpg', 'planets', 'tips', 'titanic']
ds_name = 'diamonds'
df = sns.load_dataset(ds_name)
selected_options = df.loc[:, df.nunique() < 10].columns


# -- SETTINGS
layout_kwargs = dict(plot_bgcolor='#263740',
                     paper_bgcolor='#1d2930',
                     font=dict(color='white'),
                     margin=go.layout.Margin(b=30, l=30,
                                             r=30, t=40,
                                             pad=5))



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
                assets_folder=os.path.join(os.path.dirname(__file__), '../macros/assets/'), )
app_title = 'Dash template'

# -- LAYOUT
app.layout = html.Div([
    html.Div([
        row([
            column([html.H1(app_title), *controls,
                    html.H2("Filter by:"), *filter_controls], className='two columns'),
            column(figure_childs, className='ten columns'), ])
    ]),
])


# -- CALLBACKS

@app.callback(Output('fig_0', 'figure'),
              [Input('dropdown_0', 'value'),
               Input('slider_0', 'value'),
               Input('filter_dropdown', 'value')
               ])
def make_histogram1(col, bins, filter,):
    return du.make_histogram(df, col, bins, filter, layout_kwargs)


@app.callback(Output('fig_1', 'figure'),
              [Input('dropdown_1', 'value'),
               Input('slider_1', 'value'),
               Input('filter_dropdown', 'value')
               ]
              )
def make_histogram2(col, bins, filter,):
    return du.make_histogram(df, col, bins, filter, layout_kwargs)


@app.callback(Output('fig_2', 'figure'),
              [Input('dropdown_2', 'value'),
               Input('dropdown_3', 'value'),
               Input('filter_dropdown', 'value')
               ])
def make_scatter1(x, y, filter,):
    return du.make_scatter(df, x, y, filter, layout_kwargs)


if __name__ == '__main__':
    app.run_server(debug=True, port=8089)
