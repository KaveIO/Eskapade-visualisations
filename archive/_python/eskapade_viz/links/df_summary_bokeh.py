"""Project: Eskapade - A _python-based package for data analysis.

Class: df_summary_bokeh

Created: 2018-11-09

Description:
    Algorithm to ...(fill in one-liner here)

Authors:
    KPMG Advanced Analytics & Big Data team, Amstelveen, The Netherlands

Redistribution and use in source and binary forms, with or without
modification, are permitted according to the terms listed in the file
LICENSE.
"""

import pandas as pd
import numpy as np

from bokeh.layouts import column, row, widgetbox, layout
from bokeh.plotting import Figure, ColumnDataSource
from bokeh.models.widgets import Slider, Dropdown, DataTable, TableColumn
from bokeh.models.ranges import DataRange1d, FactorRange

from eskapade import process_manager, ConfigObject, DataStore, Link, StatusCode
from eskapade.analysis.statistics import ArrayStats


class DfSummaryBokeh(Link):

    """Defines the content of link."""

    def __init__(self, **kwargs):
        """Initialize an instance.

        :param str name: name of link
        :param str read_key: key of input data to read from data store
        """
        # initialize Link, pass name from kwargs
        Link.__init__(self, kwargs.pop("name", "df_summary_bokeh"))

        # Process and register keyword arguments. If the arguments are
        # not given, all arguments are popped from
        # kwargs and added as attributes of the link. Otherwise, only
        # the provided arguments are processed.
        self._process_kwargs(kwargs, read_key=None)

        # check residual kwargs; exit if any present
        self.check_extra_kwargs(kwargs)
        # Turn off the line above, and on the line below if you wish to
        # keep these extra kwargs.
        # self._process_kwargs(kwargs)

    def initialize(self):
        """Initialize the link.

        :returns: status code of initialization
        :rtype: StatusCode
        """
        return StatusCode.Success

    def execute(self):
        """Execute the link.

        :returns: status code of execution
        :rtype: StatusCode
        """
        settings = process_manager.service(ConfigObject)
        ds = process_manager.service(DataStore)

        # --- your algorithm code goes here
        self.logger.debug("Now executing link: {link}.", link=self.name)

        return StatusCode.Success

    @staticmethod
    def _col_stats(col, n_bins=None):
        clean_col = pd.Series(col).dropna()
        is_int = isinstance(clean_col.values[0], int)
        is_str = isinstance(clean_col.values[0], str)

        if is_str:
            counts = clean_col.value_counts().sort_index()
            hist = counts.values
            edges = np.array(counts.index)

        elif n_bins is None:

            if clean_col.nunique() <= 50:
                bins = np.arange(
                    np.min(clean_col) - 0.5, np.max(clean_col) + 1.5
                )
            else:
                # use numpy auto bin width estimation for continuous values
                bins = "auto"

            hist, edges = np.histogram(clean_col, bins=bins)

        else:
            hist, edges = np.histogram(clean_col, bins=n_bins)

        stats = ArrayStats(pd.DataFrame(col), col.name)

        return stats, hist, edges

    @staticmethod
    def _hist_source_dict(hist, edges):
        if isinstance(edges[0], str):
            return {"top": hist, "x": edges, "width": 0.8 * np.ones_like(edges)}

        else:
            w = np.diff(edges)
            x = np.array(edges[:-1]) + w / 2
            return {"top": hist, "x": x, "width": w}

    @staticmethod
    def _table_source_dict(stats: ArrayStats):
        if not stats.stat_vals:
            stats.create_stats()

        return {
            "quantity": list(stats.stat_vals.keys()),
            "value": [val for _, val in stats.stat_vals.values()],
        }

    def _update_histogram(self, figure, source, hist, edges, name=""):
        if isinstance(edges[0], str):
            figure.x_range = FactorRange(factors=edges)
        else:
            figure.x_range = DataRange1d()

        source.data = self._hist_source_dict(hist, edges)

        if name:
            figure.title.text = name

        figure.y_range.start = -0.1 * np.max(hist)
        figure.y_range.end = 1.1 * np.max(hist)

    def _update_table(self, table, source, stats):
        source.data = self._table_source_dict(stats)

    def _doc_factory(self, doc):
        settings = process_manager.service(ConfigObject)
        ds = process_manager.service(DataStore)

        df = ds[self.read_key]

        # calculate initial values to initialize displayed elements
        columns = df.columns
        first_col = columns[0]  # 'pl_letter' #columns[0]
        first_stats, first_hist, first_edges = self._col_stats(df[first_col])

        # set up data sources
        hist_source = ColumnDataSource(
            data=self._hist_source_dict(first_hist, first_edges)
        )
        table_source = ColumnDataSource(
            data=self._table_source_dict(first_stats)
        )

        # set up dashboard components
        plot = Figure(
            title=first_col,
            tools="xpan,xwheel_zoom,box_zoom,reset",
            active_drag="xpan",
            active_scroll="xwheel_zoom",
        )

        plot.vbar(top="top", x="x", width="width", bottom=0, source=hist_source)

        slider = Slider(
            start=1,
            end=5 * len(first_hist),
            value=len(first_hist),
            step=1,
            title="Bin Count",
        )
        slider.disabled = isinstance(first_edges[0], str)

        dropdown = Dropdown(
            label="Column",
            menu=[(col, col) for col in df.columns],
            value=df.columns[0],
        )

        table = DataTable(
            source=table_source,
            columns=[
                TableColumn(field="quantity", title="Quantity"),
                TableColumn(field="value", title="Value"),
            ],
        )

        # configure callbacks
        slider_interaction = True

        def dropdown_callback(attr, old, new):
            nonlocal df, plot, hist_source, dropdown
            nonlocal table, table_source
            nonlocal slider, slider_interaction
            stats, hist, edges = self._col_stats(df[new])
            self._update_histogram(plot, hist_source, hist, edges, new)
            self._update_table(table, table_source, stats)

            dropdown.label = new

            slider_interaction = False  # don't recalculate again
            slider.start = 1
            slider.value = len(hist)
            slider.end = 5 * len(hist)
            slider.disabled = isinstance(edges[0], str)
            slider_interaction = True  # re-enable slider

        dropdown.on_change("value", dropdown_callback)

        def slider_callback(attr, old, new):
            nonlocal df, plot, hist_source, dropdown
            nonlocal slider_interaction
            if slider_interaction:
                stats, hist, edges = self._col_stats(
                    df[dropdown.value], n_bins=new
                )
                self._update_histogram(plot, hist_source, hist, edges)

        slider.on_change("value", slider_callback)

        # Position elements in document
        root = layout(
            [[plot, widgetbox(dropdown, table)], [slider]]
        )


        doc.add_root(root)

    def finalize(self):
        """Finalize the link.

        :returns: status code of finalization
        :rtype: StatusCode
        """
        # --- any code to finalize the link follows here

        from bokeh.server.server import Server
        from bokeh.application import Application
        from bokeh.application.handlers.function import FunctionHandler

        apps = {"/": Application(FunctionHandler(self._doc_factory))}

        server = Server(applications=apps, port=5000)
        server.io_loop.add_callback(server.show, "/")

        try:
            server.io_loop.start()
        except KeyboardInterrupt:
            return StatusCode.Success
