import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash_utils import row

#
from data_loader import *
from df_summary_multi import *
# from template_app import *
# from phik_frontend import *

from data_loader import layout as dt_layout
from df_summary_multi import layout as df_layout
# from template_app import layout as tmp_layout
# from phik_frontend import layout as ph_layout


# from data_loader import data_container, var_container

from app import app

footer = row([
    html.A(html.Button('Home'), href='http://localhost:8050'),
    html.A(html.Button('DF Summary'), href='http://localhost:8050/apps/app1'),
    # html.A(html.Button('Template app'), href='http://localhost:8050/apps/app2'),
    # html.A(html.Button('Phi K'), href='http://localhost:8050/apps/app3'),
])

page_content = html.Div(id='page-content')

app.layout = html.Div([
    html.Div([], id='bla', style={'display': 'none'}),
    dcc.Location(id='url', refresh=False),
    row([page_content]),
    row([data_container, var_container]),
    row([footer], style={'position': 'fixed',
                         'left': 0,
                         'bottom': 0,
                         'width': '100%',
                         'text-align': 'center'})
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/app1':
        return df_layout
    # elif pathname == '/apps/app2':
    #     return tmp_layout
    # elif pathname == '/apps/app3':
    #     return ph_layout
    elif pathname == '/':
        return dt_layout
    else:
        return '404'


@app.callback(Output('bla', 'children'),
              [Input('page-content', 'children'),
               Input('var_container', 'children')],
              [State('url', 'pathname')]
)
def trigger_data_refresh(page_content, var_children, pathname):
    print(pathname)
    if pathname == '/apps/app1':
        # update_describe_cols(var_children)
        update_options_xdropdown(var_children)
        update_options_huedropdown(var_children)
        # update_describe_cols(var_children)
        # update_describe(var_children)
#
# @app.callback(Output('bla', 'children'),
#               [Input('var_container', 'children')])
# def test_output(var_kids):
#
#     if (var_kids is not None) & (var_kids != []):
#         print("Variables updates")
#         out = json.loads(var_kids)
#         options = list(out['options'])
#         for contr in controls:
#             if hasattr(contr, 'options'):
#                 contr.options = [{'label': x, 'value': x} for x in options]
#
#
# @app.callback(Output('bla', 'id'),
#               [Input('data_container', 'children')])
# def test_output(data_kids):
#     if (data_kids is not None) & (data_kids != []):
#         print("Data update")
#         print(data_kids)
#         # print(dict(json.loads(var_kids)).keys())
#

# @app.callback(Output('bla', 'children'),
#               [Input('url', 'pathname')],
#               [State('var_container', 'children'),
#                State('data_container', 'children')])
# def update_data_output(pathname, var_kids, data_kids):
#     print("Loading new data from data loader")
#     if (pathname == '/apps/app2') & (var_kids != []):
#         print(var_kids)
#         print(pathname)
#         global variables, options, selected_options
#         variables, options, selected_options = update_data(var_kids, data_kids)


if __name__ == '__main__':
    app.run_server(debug=True)