"""Project: Eskapade - A _python-based package for data analysis.

Class: dash_builder

Created: 2018-11-16

Description:
    Algorithm to make a interactive dashboard using plotly dash.

Authors:
    KPMG Advanced Analytics & Big Data team, Amstelveen, The Netherlands


Redistribution and use in source and binary forms, with or without
modification, are permitted according to the terms listed in the file
LICENSE.
"""

from eskapade import process_manager, ConfigObject, DataStore, Link, StatusCode
import eskapade_viz.dash_utils as du

import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Output, Input
import plotly.graph_objs as go

import os


class DashBuilder(Link):

    """Defines the content of link."""

    def __init__(self, **kwargs):
        """Initialize an instance.

        :param str name: name of link
        :param str read_key: key of input data to read from data store
        :param str store_key: key of output data to store in data store
        """
        # initialize Link, pass name from kwargs
        Link.__init__(self, kwargs.pop('name', 'dash_builder'))

        # Process and register keyword arguments. If the arguments are not given, all arguments are popped from
        # kwargs and added as attributes of the link. Otherwise, only the provided arguments are processed.
        self._process_kwargs(kwargs,
                             read_key=None,
                             store_key=None,
                             layout_kwargs=None,
                             figure_strings=[],
                             control_strings=[],
                             figure_titles=[],
                             filter_controls=[],
                             assets_folder=None,
                             app_title='Dash template')

        # check residual kwargs; exit if any present
        self.check_extra_kwargs(kwargs)
        # Turn off the line above, and on the line below if you wish to keep these extra kwargs.
        # self._process_kwargs(kwargs)

    def initialize(self):
        """Initialize the link.

        :returns: status code of initialization
        :rtype: StatusCode
        """
        if self.assets_folder is None:
            self.assets_folder = os.path.join(os.path.dirname(du.__file__), '../../macros/assets/')

        self.figures = du.make_go_list(self.figure_strings)
        self.controls = du.make_control_list(self.control_strings)
        self.filter_controls = du.make_control_list(self.filter_controls)

        if self.layout_kwargs is None:
            self.layout_kwargs = dict(plot_bgcolor = '#263740',
                                      paper_bgcolor = '#1d2930',
                                      font=dict(color = 'white'),
                                      margin=go.layout.Margin(b=30, l=30,
                                                              r=30, t=40,
                                                              pad=5))
        return StatusCode.Success

    def execute(self):
        """Execute the link.

        :returns: status code of execution
        :rtype: StatusCode
        """
        settings = process_manager.service(ConfigObject)
        ds = process_manager.service(DataStore)

        # --- your algorithm code goes here
        self.logger.debug('Now executing link: {link}.', link=self.name)


        app = dash.Dash(__name__, assets_folder=self.assets_folder,)


        figure_childs = du.figure_grid(len(self.figures), self.figures,
                                       layout_kwargs=self.layout_kwargs)


        app.layout = html.Div([
            html.Div([
                du.row([
                    du.column([html.H1(self.app_title), *self.controls,
                               html.H2('Filter by:'), *self.filter_controls], className="two columns"),
                    du.column(figure_childs, className='ten columns'),
                ])
            ])
        ])

        # Make the callbacks --  This needs to be done manually for each control!

        # FIGURE 1
        @app.callback(Output('fig_0', 'figure'),
                      [Input('dropdown_0', 'value'),
                       Input('slider_0', 'value'),
                       Input('filter_dropdown', 'value')])
        def update_fig1(col, bins, filter):
            return du.make_histogram(ds[self.read_key], col, bins, filter, self.layout_kwargs)

        # FIGURE 2
        @app.callback(Output('fig_1', 'figure'),
                      [Input('dropdown_1', 'value'),
                       Input('slider_1', 'value'),
                       Input('filter_dropdown', 'value')])
        def update_fig2(col, bins, filter):
            return du.make_histogram(ds[self.read_key], col, bins, filter, self.layout_kwargs)

        # FIGURE 3
        @app.callback(Output('fig_2', 'figure'),
                      [Input('dropdown_2', 'value'),
                       Input('dropdown_3', 'value'),
                       Input('filter_dropdown', 'value')])
        def update_fig3(x, y, filter):
            return du.make_scatter(ds[self.read_key], x, y, filter, self.layout_kwargs)


        # save app in datastore
        ds[self.store_key] = app

        return StatusCode.Success

    def finalize(self):
        """Finalize the link.

        :returns: status code of finalization
        :rtype: StatusCode
        """
        # --- any code to finalize the link follows here
        ds = process_manager.service(DataStore)
        ds[self.store_key].run_server(debug=True, port=8050)

        return StatusCode.Success
