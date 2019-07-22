import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import seaborn as sns

import plotly.graph_objs as go

import pandas as pd

# -- data
df = pd.read_csv('../data/KV6_opendata_20140108.csv', sep=';', header=None)
df.columns = ['Timestamp1 UTC','Timestamp2 EUROPE/LONDEN','Timestamp3 EUROPE/LONDEN','EVENT','OperatingDay ','DataOwnerCode','LinePlanningNumber','JourneyNumber',
'ONBEKEND','UserStopCode','ONBEKEND','DistanceSinceLastUserStop','Punctuality','RD-X RDS','RD-Y RDS','BlockCode',
 'VehicleNumber','WheelChairAccesible','Source','ONBEKEND',]
#colnames = pd.read_csv('../data/planets.csv', sep=';', nrows=354, skiprows=2)
#colnames['dict'] = colnames['#'].apply(lambda x: x[8:])
#colnames['dict'] = colnames['dict'].apply(lambda x: {x.split(':')[0].strip(): x.split(':')[1].strip()}).values
colnames = [str(x) for x in df.columns]

plt_bgcolor = '#263740'
plt_papercolor = '#1d2930'
text_color = 'white'

pdict = {x: str(x) for x in colnames}
# pdict = {}
# for d in colnames['dict'].values:
#     pdict.update(d)

hue_cols = ['EVENT', 'VehicleNumber', 'WheelChairAccesible', 'Source', 'BlockCode']
hue_cols = colnames
data_cols = colnames

data_cols = ['Timestamp1 UTC', 'Timestamp2 EUROPE/LONDEN', 'Timestamp3 EUROPE/LONDEN', 'EVENT', 'LinePlanningNumber', 'JourneyNumber',
'UserStopCode', 'DistanceSinceLastUserStop', 'Punctuality', 'RD-X RDS', 'RD-Y RDS', 'BlockCode',
 'VehicleNumber', 'WheelChairAccesible', 'Source']

ext_sheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# --  app
app = dash.Dash(__name__, external_stylesheets=ext_sheets)
app.layout = html.Div( [
    html.H1('DataFrames: a summary'),
    html.Div([# -- first column
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
                         options=[{'label': pdict[x], 'value': x} for x in data_cols],
                         value=0, placeholder='Select...',
                         style={'width': '80%'}),
            html.H5("Hue"),
            dcc.Dropdown(id='hue_dropdown',
                         options=[{'label': pdict[x], 'value': x} for x in hue_cols],
                         value=0, placeholder='Select...',
                         style={'width': '80%'}),
            ]
            )], className='five columns'),
    html.Div([ # --  second column
        # dcc.Slider(id='bin_slider2',
        #            min=1,
        #            max=100,
        #            step=1,
        #            value=30),
        html.Div([
            dash_table.DataTable(id='table',
                                 data=df.describe().to_dict('rows'))
            # dcc.Graph(id='Table',
            #           figure={'layout': go.Layout(plot_bgcolor=plt_bgcolor,
            #                                       paper_bgcolor=plt_papercolor,
            #                                       font=dict(color=text_color))}),
            ],
             className='five columns')]
            )])
#         ),
#     html.Div([])# -- bottom row
#         # html.Div([
#         #         html.H5("Variable"),
#         #         dcc.Dropdown(id='x_dropdown',
#         #                      options=[{'label': pdict[x], 'value': x} for x in data_cols],
#         #                      value=0, placeholder='Select...',
#         #                      style={'width': '80%'})],
#         #          className='five columns'),
#         html.Div([
#                 html.H5("Hue"),
#                 dcc.Dropdown(id='hue_dropdown',
#                              options=[{'label': pdict[x], 'value': x} for x in hue_cols],
#                              value=0, placeholder='Select...',
#                              style={'width': '80%'})],
#                  className='five columns')]
#              )
# ]) #fin


# -- update functions

@app.callback(
    dash.dependencies.Output('Histogram', 'figure'),
    [dash.dependencies.Input('x_dropdown', 'value'),
     dash.dependencies.Input('hue_dropdown', 'value'),
     dash.dependencies.Input('bin_slider1', 'value')])
def update_plot(value_x, hue, bins):
    if hue != 0:
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
    else:
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


if __name__ == '__main__':
    app.run_server(debug=True)
