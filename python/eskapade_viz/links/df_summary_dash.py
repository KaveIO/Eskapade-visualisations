"""Project: Eskapade - A python-based package for data analysis.

Class: df_summary_dash

Created: 2018-11-08

Description:
    Algorithm to ...(fill in one-liner here)

Authors:
    KPMG Advanced Analytics & Big Data team, Amstelveen, The Netherlands

Redistribution and use in source and binary forms, with or without
modification, are permitted according to the terms listed in the file
LICENSE.
"""

from eskapade import process_manager, ConfigObject, DataStore, Link, StatusCode

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

from eskapade.analysis import statistics
import pandas as pd
import pickle
import os


class DfSummaryDash(Link):
    """Defines the content of link."""

    def __init__(self, **kwargs):
        """Initialize an instance.

        :param str name: name of link
        :param str read_key: key of input data to read from data store
        :param str store_key: key of output data to store in data store
        """
        # initialize Link, pass name from kwargs
        Link.__init__(self, kwargs.pop('name', 'df_summary_dash'))

        # Process and register keyword arguments. If the arguments are not given, all arguments are popped from
        # kwargs and added as attributes of the link. Otherwise, only the provided arguments are processed.
        self._process_kwargs(kwargs,
                             read_key=None,
                             app_store_key=None,
                             label_key=None,
                             col_key=None,
                             hue_key=None,
                             hue_cols=None,
                             stats_key=None,
                             assets_path=None,
                             plt_bgcolor='#263740',
                             plt_papercolor='#1d2930',
                             text_color='white',
                             ext_sheets=['https://codepen.io/crhiddyp/pen/bWLwgP.css'])

        # check residual kwargs; exit if any present
        self.check_extra_kwargs(kwargs)
        # Turn off the line above, and on the line below if you wish to keep these extra kwargs.
        # self._process_kwargs(kwargs)

    def _column(self, children, style={}, className='five columns'):

        return html.Div(children=children, style=style, className=className)

    def _row(self, children, style={}, className='row'):

        return html.Div(children=children, style=style, className=className)

    def initialize(self):
        """Initialize the link.

        :returns: status code of initialization
        :rtype: StatusCode
        """
        # -- load the datastore
        # ds = process_manager.service(DataStore)
        #
        # # -- get the stats

        return StatusCode.Success

    def execute(self):
        """Execute the link.

        :returns: status code of execution
        :rtype: StatusCode
        """
        settings = process_manager.service(ConfigObject)
        ds = process_manager.service(DataStore)

        ds[self.col_key] = ds[self.read_key].columns.values
        base_path = os.path.join(os.path.dirname(__file__), '../../../data/'+self.label_key)
        ds[self.label_key] = pickle.load(open(base_path, 'rb'))

        ds[self.hue_key] = self.hue_cols

        stats = statistics.ArrayStats(ds[self.read_key].iloc[:, 0].values,
                                      ds[self.read_key].columns[0],
                                      label=ds[self.label_key][ds[self.read_key].columns[0]])
        stats.create_stats()
        input_stats = pd.DataFrame.from_dict(stats.stat_vals, orient='columns').T.drop(1, 1)*0
        input_stats.reset_index(inplace=True)
        input_stats.columns = ['Variable', 'Value']
        self.initial_stats = input_stats

        # --- your algorithm code goes here
        self.logger.debug('Now executing link: {link}.', link=self.name)

        print('-'*20, '!!!')
        print(os.path.abspath(__file__))

        app = dash.Dash(__name__, assets_folder=os.path.join(os.path.dirname(__file__), '../../../macros/assets/'),)

        app.layout = html.Div([
            html.H1('DataFrames: a summary'),
            html.Div([  # -- the row
                html.Div([  # -- first column
                    html.H5("Variable"),
                    dcc.Dropdown(id='x_dropdown',
                                 options=[{'label': ds[self.label_key][x],
                                           'value': x} for x in ds[self.col_key]],
                                 value=0, placeholder='Select...',
                                 style={'width': '100%'}),
                    html.H5("Hue"),
                    dcc.Dropdown(id='hue_dropdown',
                                 options=[{'label': ds[self.label_key][x],
                                           'value': x} for x in ds[self.hue_key]],
                                 value=0, placeholder='Select...',
                                 style={'width': '100%'}), ], className='two columns'),
                html.Div([  # -- second column
                    html.Div([
                        dcc.Graph(id='histogram',
                                  figure={'layout': go.Layout(plot_bgcolor=self.plt_bgcolor,
                                                              paper_bgcolor=self.plt_papercolor,
                                                              font=dict(color=self.text_color),
                                                              title='Histogram'
                                                              )}),
                        dcc.Slider(id='bin_slider1',
                                   min=1,
                                   max=100,
                                   step=1,
                                   value=30,
                                   updatemode='drag',
                                   marks={x: {'label': str(x)} for x in range(0, 100, 10)}),
                    ])], className='six columns'),
                html.Div([  # --  third column
                    html.Div([
                        dash_table.DataTable(id='table',
                                             columns=[{"name": i, "id": i} for i in self.initial_stats],
                                             data=self.initial_stats.to_dict('rows'),
                                             style_as_list_view=True,
                                             style_header={
                                                 'backgroundColor': self.plt_papercolor,
                                                 'color': 'white', },
                                             style_cell={
                                                 'backgroundColor': self.plt_bgcolor,
                                                 'color': 'white'}, )

                    ],
                        className='offset-by-one columns', style={'width': '20%', })]
                ),
            ], className='row'),
        ])

        @app.callback(dash.dependencies.Output('histogram', 'figure'),
                      [dash.dependencies.Input('x_dropdown', 'value'),
                       dash.dependencies.Input('hue_dropdown', 'value'),
                       dash.dependencies.Input('bin_slider1', 'value')])
        def update_plot(value_x, hue, bins):
            import seaborn as sns
            if hue is None:
                hue = 0
            if value_x is None:
                value_x = 0

            df = ds[self.read_key]
            if value_x == 0:
                return {'data': [],
                        'layout':go.Layout(
                                xaxis={'title': 'Please select a variable'},
                                plot_bgcolor=self.plt_bgcolor,
                                paper_bgcolor=self.plt_papercolor,
                                font=dict(color=self.text_color),
                                title='Histogram')}
            elif hue != 0:
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
                        xaxis={'title': ds[self.label_key][value_x]},
                        plot_bgcolor=self.plt_bgcolor,
                        paper_bgcolor=self.plt_papercolor,
                        font=dict(color=self.text_color),
                        title='Histogram'),}
            else:
                return {'data': [go.Histogram(
                    x=df[value_x],
                    nbinsx=bins,
                    text=df[value_x])],
                    'layout': go.Layout(
                        xaxis={'title': ds[self.label_key][value_x]},
                        plot_bgcolor=self.plt_bgcolor,
                        paper_bgcolor=self.plt_papercolor,
                        font=dict(color=self.text_color),
                        title='Histogram'
                    )}

        @app.callback(dash.dependencies.Output('table', 'data'),
                      [dash.dependencies.Input('x_dropdown', 'value')])
        def update_table(value_x):
            if value_x is None:

                stats = statistics.ArrayStats(ds[self.read_key].iloc[:,0].values,
                                              value_x,
                                              label='fake')
                stats.create_stats()
                input_stats = pd.DataFrame.from_dict(stats.stat_vals, orient='columns').T.drop(1, 1)
                input_stats *= 0
                input_stats.reset_index(inplace=True)

                input_stats.columns = ['Variable', 'Value']
                return input_stats.to_dict('rows')
            elif value_x != 0:
                stats = statistics.ArrayStats(ds[self.read_key].loc[:, value_x].values,
                                              value_x,
                                              label=ds[self.label_key][value_x])
                stats.create_stats()
                input_stats = pd.DataFrame.from_dict(stats.stat_vals, orient='columns').T.drop(1, 1)
                input_stats.reset_index(inplace=True)
                input_stats.columns = ['Variable', 'Value']
                return input_stats.to_dict('rows')


                # return input_stats.describe().to_dict('rows')

        ds[self.app_store_key] = app
        return StatusCode.Success

    def finalize(self):
        """Finalize the link.

        :returns: status code of finalization
        :rtype: StatusCode
        """
        # --- any code to finalize the link follows here
        ds = process_manager.service(DataStore)
        ds['app'].run_server(debug=True)

        return StatusCode.Success
