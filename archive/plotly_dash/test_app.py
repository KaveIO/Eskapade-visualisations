import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import seaborn as sns
import plotly.graph_objs as go

import pandas as pd

layout_kwargs = dict(
    autosize=True,
    plot_bgcolor="#191A1A",
    paper_bgcolor="#020202")

# df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')
df = sns.load_dataset('diamonds')
app = dash.Dash(__name__)

app.layout = html.Div([
            html.Div([ dcc.Graph(
                id = "histogram",
                      figure = dict(data = [go.Histogram(x=df['x'].values, nbinsx=30)],
                                    layout = go.Layout(title='My Histogram'), **layout_kwargs)),
                    dcc.Graph(id = 'scatterplot',
                      figure = dict(data = [go.Scatter(x=df['x'], y=df['y'], mode='markers')],
                                   layout = go.Layout(title='My Histogram'), **layout_kwargs))],
                style={'height':'100%', 'width':'50%'},
                className='one columns'),
            html.Div(children=[
                    dcc.Dropdown(id='Dropdown',
                                 options=[{"label":x, 'value':x} for x in ['List','Of','Options']],
                                 value='List'),
                    dcc.Slider(id='Slider', min=0, max=100, step=1, value=50)],
                 style={'marginLeft':'5%'})]
    )

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
