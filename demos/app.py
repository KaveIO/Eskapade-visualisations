import dash
import dash_html_components as html

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__)  # external_stylesheets=external_stylesheets)
server = app.server
app.config.suppress_callback_exceptions = True

data_container = html.Div([], id='data_container',  style={'display': 'none'})
var_container = html.Div([], id='var_container', style={'display': 'none'})