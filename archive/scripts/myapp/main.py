import pandas as pd
import numpy as np

from bokeh.models.widgets import Dropdown, Slider, DataTable, TableColumn, markups
from bokeh.plotting import curdoc, figure, ColumnDataSource
from bokeh.layouts import widgetbox, row, column
from bokeh.models import LabelSet

from eskapade.analysis.statistics import ArrayStats

# def my_func(doc):
    # load the data

# doc.theme = Theme(filename='../bokeh/kpmg_style.yaml')
# doc.template = open('templates/index.html', 'r').read()

SKIP_ROWS = 358
DATA_PATH = "../data/planets.csv"

df = pd.read_csv("../data/planets.csv", skiprows=SKIP_ROWS)

NUMERIC_KINDS = set("buifc")

NUMERIC_COLS = [
    col for col in df.columns if df[col].dtype.kind in NUMERIC_KINDS
]

ALLOWED_COLS = NUMERIC_COLS  # df.columns

first_col = NUMERIC_COLS[0]
first_stats = ArrayStats(df, first_col)
first_stats.create_stats()

first_table = first_stats.create_stats()

first_hist, first_edges = np.histogram(df[first_col], bins="auto")

def source_dict_from_hist(hist, edges):
    return {
        "top": hist,
        "left": edges[:-1],
        "right": edges[1:],
        "name": len(hist) * [""],
    }

def source_dict_from_col_counts(col_name):
    value_counts = df[col_name].value_counts().sort_index()

    top = value_counts.values
    left = np.arange(len(top))
    right = left + 0.9

    ticks = {(i + 0.45): name for i, name in enumerate(value_counts.index)}

    return {
        "top": top,
        "left": left,
        "right": right,
        "name": value_counts.index.tolist(),
    }

def table_source_dict_from_col_name(col_name):
    stats = ArrayStats(df[[col_name]], col_name)
    stats.create_stats()

    stat_vals = stats.stat_vals

    return {
        "quantity": list(stat_vals.keys()),
        "value": [val for _, val in stat_vals.values()],
    }

HIST_SOURCE = ColumnDataSource(
    source_dict_from_hist(first_hist, first_edges)
)
TABLE_SOURCE = ColumnDataSource(table_source_dict_from_col_name(first_col))

HISTOGRAM = figure(
    title=first_col,
    tools="xpan,xwheel_zoom,reset",
    active_drag="xpan",
    active_scroll="xwheel_zoom",
)

HISTOGRAM.quad(
    top="top", left="left", right="right", bottom=0, source=HIST_SOURCE
)
HISTOGRAM.add_layout(
    LabelSet(
        x="left",
        y=0,
        text="name",
        level="glyph",
        source=HIST_SOURCE,
        x_offset=0.45,
        y_offset=-1,
    )
)

DROPDOWN = Dropdown(
    label="Column",
    menu=[(col, col) for col in ALLOWED_COLS],
    value=first_col,
)

SLIDER = Slider(
    start=1, end=5 * len(first_hist), value=len(first_hist), step=1
)

TABLE = DataTable(
    source=TABLE_SOURCE,
    columns=[
        TableColumn(field="quantity", title="Quantity"),
        TableColumn(field="value", title="Value"),
    ],
)

def update_state(col=None, nbins=None):
    current_col = col or DROPDOWN.value

    if current_col in NUMERIC_COLS:
        hist, edges = np.histogram(
            df[current_col].dropna(), nbins or "auto"
        )

        HIST_SOURCE.data = source_dict_from_hist(hist, edges)
        HISTOGRAM.y_range.start = -0.1 * np.max(hist)
        HISTOGRAM.y_range.end = 1.1 * np.max(hist)

        SLIDER.disabled = False

        if nbins is None:
            SLIDER.end = 5 * len(hist)
            SLIDER.value = len(hist)

    elif col is not None:
        HIST_SOURCE.data = source_dict_from_col_counts(current_col)
        SLIDER.disabled = True

    HISTOGRAM.title.text = current_col

    if col is not None:
        TABLE_SOURCE.data = table_source_dict_from_col_name(current_col)

def slider_callback(attr, old, new):
    update_state(nbins=new)

def dropdown_callback(attr, old, new):
    update_state(col=new)

SLIDER.on_change("value", slider_callback)
DROPDOWN.on_change("value", dropdown_callback)

header = markups.Div(text="<link rel='stylesheet' type='text/css' href='myapp/static/kpmg.css'>")
ROOT = column(header, row(
    column(HISTOGRAM, widgetbox(SLIDER)),
    column(widgetbox(DROPDOWN), TABLE, sizing_mode="scale_width"),
))

# ROOT.__css__ = 'templates/kpmg.css'

# doc.add_root(ROOT)


DOC = curdoc()
# DOC.theme= 'caliber'
DOC.add_root(ROOT)

# if __name__ == "__main__":
#     from bokeh.server.server import Server
#     from bokeh.application import Application
#     from bokeh.application.handlers.function import FunctionHandler
#     from bokeh.plotting import figure, ColumnDataSource

#     apps = {"/": Application(FunctionHandler(my_func))}

#     server = Server(applications=apps, port=5000)
#     server.io_loop.add_callback(server.show, "/")
#     server.io_loop.start()
