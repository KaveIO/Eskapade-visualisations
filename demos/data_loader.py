import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash_utils import row
import dash
import base64
import io
import tqdm
import json

import pandas as pd
import numpy as np
from pandas_profiling.model.describe import multiprocess_1d
from app import data_container, var_container


upload_button = dcc.Upload(html.A("Upload File"), id='upload_button', multiple=False)

# data_container = html.Div([], id='data_container',  style={'display': 'none'})
# var_container = html.Div([], id='var_container', style={'display': 'none'})

loading_container = html.Div([], id='loading_message', style={'color': 'white'})

layout = html.Div([
    row([upload_button, data_container,
         var_container, loading_container])
])

if __name__ == 'data_loader':
    from app import app
else:
    app = dash.Dash(__name__)
    app.layout = layout
    app.title = 'Upload file'


@app.callback(Output('data_container', 'children'),
              [Input('upload_button', 'contents')],
              [State('data_container', 'children')])
def save_data(list_of_contents, data_kids):

    # dont overwrite
    if (list_of_contents is not None) and (data_kids == []):
        decoded = base64.b64decode(list_of_contents.split(',')[1])
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

        data = df.to_json(orient='split')
        # return f'''{data}'''
        return data


@app.callback(Output('loading_message', 'children'),
              [Input('data_container', 'children'),
               Input('var_container', 'children')])
def get_load_message(data, variables):

    if data and not variables:
        return '''Calculating!'''
    if data and variables:
        return '''Done!'''


@app.callback(Output('var_container', 'children'),
              [Input('data_container', 'children')])
def load_variables(children):

    if children:

        df = pd.read_json(children, orient='split')
        variables = {}
        for col, series in tqdm.tqdm(df.iteritems(), total=len(df.columns)):
            result = multiprocess_1d(col, series)
            variables[result[0]] = result[1]

        variables = {k: v for k, v in variables.items() if str(v['type'] != 'Variable.TYPE_UNSUPPORTED')}
        variables = {K: {k: v for k, v in V.items() if not isinstance(v, pd.Series)} for K, V in variables.items()}
        variables = {K: {k: (int(v) if isinstance(v, np.int64) else v) for k, v in V.items()} for K, V in variables.items()}
        variables = {K: {k: (str(v).replace("Variable.", "") if k == 'type' else v) for k, v in V.items()}
                     for K, V in variables.items()}

        cats = {col: {'CAT': variables[col]['type'],
                      'n_unique': variables[col]['distinct_count'] if
                      str(variables[col]['type']) == "Variable.TYPE_CAT" else 0}
                for col in variables.keys()}
        selected_options = [k for k, v in cats.items() if
                            (str(v['CAT']) == 'Variable.TYPE_CAT') and (int(v['n_unique']) < 10)]
        options = [k for k, v in cats.items()]
        output = {"variables": {k: pd.DataFrame.from_dict(v, orient='index').to_json(orient='split') for k, v in variables.items()},
                  "options": options, "selected_options": selected_options}
        # print(output)
        # return f"{output}"
        return json.dumps(output)

if __name__ == '__main__':
    app.run_server(debug=True)
