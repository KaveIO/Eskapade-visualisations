import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import plotly.figure_factory as ff

import pandas as pd
import numpy as np
import seaborn as sns

import phik, phik.binning
import logging


df = sns.load_dataset('diamonds')
columns = df.columns

mathjax = 'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML'

# in place so we can reuse this script in multipage app. If run stand-alone, new all is initialized
# if __name__ == 'phik_frontend':
#     from app import app
# else:
#     app = dash.Dash(__name__)



class Ids:
    """Container for ID strings"""

    heatmap = "heatmap"

    x_col = "x_col"
    x_slider = "x_slider"
    x_slider_container = "x_slider_container"
    x_bin_add_button = "x_bin_add_button"
    x_bin_remove_button = "x_bin_remove_button"

    y_col = "y_col"
    y_slider = "y_slider"
    y_slider_container = "y_slider_container"
    y_bin_add_button = "y_bin_add_button"
    y_bin_remove_button = "y_bin_remove_button"

    binning_radio = "binning_radio"

    phik_display = "phik_display"
    significance_display = "significance_display"


class GlobalState:
    """Container for global state variables"""

    X_BINS_ADD_CLICKS = 0
    Y_BINS_ADD_CLICKS = 0

    X_BINS_REMOVE_CLICKS = 0
    Y_BINS_REMOVE_CLICKS = 0


def min_max(arr):
    return np.min(arr), np.max(arr)


def get_edges(bin_list):
    # left bin edges + ast right edge
    return [t[0] for t in bin_list] + [bin_list[-1][-1]]


def make_matrix(x, y, bins=None, quantile=False):

    df_tmp = df[[x, y]]
    df_tmp.columns = ["x", "y"]

    if isinstance(bins, int):
        bins_arg = bins
    elif isinstance(bins, tuple) or isinstance(bins, list):
        bins_arg = {"x": bins[0], "y": bins[1]}
    else:
        bins_arg = 10

    corr_matrix, binning = phik.outlier_significance_matrix(
        df_tmp, retbins=True, bins=bins_arg, quantile=quantile
    )

    if "x" in binning:
        x_edges = get_edges(binning["x"])
    else:
        x_edges = corr_matrix.index.values

    if "y" in binning:
        y_edges = get_edges(binning["y"])
    else:
        y_edges = corr_matrix.columns.values

    return corr_matrix.values, x_edges, y_edges


def heatmap_kwargs(z, x, y, **extra_kwargs):
    if len(x) == z.shape[0]:
        centers_x = x
    else:
        centers_x = x[:-1] + np.diff(x) / 2

    if len(y) == z.shape[1]:
        centers_y = y
    else:
        centers_y = y[:-1] + np.diff(y) / 2

    text = np.empty_like(z)
    for i, row in enumerate(z):
        for j, val in enumerate(row):
            text[i, j] = f"{val:.3g}"

    colorscale = [
        [0, "rgb(163, 6, 42)"],
        [0.5, "rgb(252, 253, 190)"],
        [1, "rgb(11, 103, 57)"],
    ]

    return dict(
        x=list(centers_x),
        y=list(centers_y),
        z=z.T.tolist(),
        annotation_text=text.T.tolist(),
        colorscale=colorscale,
        **extra_kwargs,
    )


def heatmap_figure(z, x, y):
    kw = heatmap_kwargs(z, x, y)

    figure = ff.create_annotated_heatmap(**kw, showscale=True)

    figure.layout.xaxis.showgrid = False
    figure.layout.yaxis.showgrid = False

    figure.layout.xaxis.tickmode = "auto"
    figure.layout.yaxis.tickmode = "auto"

    figure.layout.xaxis.showline = False
    figure.layout.yaxis.showline = False

    figure.layout.xaxis.side = "bottom"

    figure.layout.paper_bgcolor = "#11191d"
    figure.layout.plot_bgcolor = "#11191d"
    figure.layout.title = f"Outlier Significance Heatmap"
    figure.layout.font = {"color": "white"}

    z_clipped = np.clip(z, -8, 8)

    return dict(
        data=[
            go.Heatmap(
                x=x,
                y=y,
                z=z_clipped,
                xgap=1,
                ygap=1,
                colorscale=kw.get("colorscale", "Viridis"),
                transpose=True,
            )
        ],
        layout=figure.layout,
    )


def range_slider(edges, **range_slider_kwargs):
    if isinstance(edges[0], str):
        if "disabled" in range_slider_kwargs:
            range_slider_kwargs.pop("disabled")

        return dcc.RangeSlider(
            min=0,
            max=len(edges) - 1,
            value=np.arange(len(edges)),
            disabled=True,
            **range_slider_kwargs,
        )

    step = (np.max(edges) - np.min(edges)) / 1000
    return dcc.RangeSlider(
        min=np.min(edges),
        max=np.max(edges),
        value=edges,
        step=step,
        pushable=step,
        **range_slider_kwargs,
    )


def column_dropdown(cols, first_value=None, **kwargs):
    val = first_value or cols[0]
    return dcc.Dropdown(
        options=[{"label": col, "value": col} for col in cols],
        value=val,
        clearable=False,
        **kwargs,
    )


first_heatmap, first_edges_x, first_edges_y = make_matrix(
    columns[0], columns[1]
)
first_heatmap_kwargs = heatmap_kwargs(
    first_heatmap, first_edges_x, first_edges_y
)

layout = html.Div(
    children=[
        html.H1(
            "\( \phi_k \) Demo",
            style={"marginLeft": "5%", "textAlign": "center"},
        ),
        html.Div(
            children=[
                html.P(
                    "correlation",
                    className="three offset-by-three columns",
                    style={
                        "color": "white",
                        "fontSize": "16pt",
                        "textAlign": "center",
                        "border": "2px solid #FFFFFF",
                    },
                    id=Ids.phik_display,
                ),
                html.P(
                    "significance",
                    className="three columns",
                    style={
                        "color": "white",
                        "fontSize": "16pt",
                        "textAlign": "center",
                        "border": "2px solid #FFFFFF",
                    },
                    id=Ids.significance_display,
                ),
            ],
            className="row",
            style={},
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        column_dropdown(columns, columns[0], id=Ids.y_col),
                        html.Button(
                            "+",
                            id=Ids.y_bin_add_button,
                            style={"marginBottom": "25px"},
                        ),
                        html.Div(
                            id=Ids.y_slider_container,
                            children=[
                                range_slider(
                                    id=Ids.y_slider,
                                    edges=first_edges_y,
                                    vertical=True,
                                )
                            ],
                            style={"height": "100%"},
                        ),
                        html.Button(
                            "-",
                            id=Ids.y_bin_remove_button,
                            style={"marginTop": "25px"},
                        ),
                    ],
                    className="one columns",
                    style={
                        "height": "350px",
                        "marginLeft": "2%",
                        "marginTop": "50px",
                    },
                ),
                dcc.Graph(
                    id=Ids.heatmap,
                    figure=heatmap_figure(
                        first_heatmap, first_edges_x, first_edges_y
                    ),
                    className="ten columns",
                    style={"minHeight": "500px"},
                ),
            ],
            className="row",
        ),
        html.Div(
            children=[
                html.Div("", className="one columns"),
                html.Button(
                    "-", id=Ids.x_bin_remove_button, className="one columns"
                ),
                html.Div(
                    id=Ids.x_slider_container,
                    children=[
                        range_slider(id=Ids.x_slider, edges=first_edges_x)
                    ],
                    className="eight columns",
                ),
                html.Button(
                    "+", id=Ids.x_bin_add_button, className="one columns"
                ),
                column_dropdown(
                    columns, columns[1], id=Ids.x_col, className="one columns"
                ),
            ],
            className="row",
            style={"marginLeft": "5%", "marginRight": "5%"},
        ),
        html.Div(
            children=[
                # "Binning Style:",
                dcc.RadioItems(
                    id=Ids.binning_radio,
                    options=[
                        dict(label="Equal Interval\t", value=False),
                        dict(label="Quantile", value=True),
                    ],
                    value=False,
                    labelStyle={
                        "display": "inline-block",
                        "marginLeft": "1em",
                        "marginRight": "1em",
                    },
                    className="four offset-by-four columns",
                )
            ],
            className="row",
            style={"paddingLeft": "5%", "color": "white"},
        ),
    ]
)

# --  app
# in place so we can reuse this script in multipage app. If run stand-alone, new all is initialized
if __name__ == "df_summary":
    from app import app
else:
    app = dash.Dash(__name__)
    app.layout = layout
    app.scripts.append_script({"external_url": mathjax})
    app.title = "Phi_K demo"
# -- update functions

# TODO: label raw bin values
# TODO: optional additional bin labels (for adding counts)


@app.callback(
    Output(Ids.x_slider, "marks"),
    inputs=[Input(Ids.x_slider, "value")],
    state=[State(Ids.x_col, "value")],
)
def x_slider_labels_callback(values, x_col):
    if isinstance(list(df[x_col])[0], str):
        return {i: f"{v}" for i, v in enumerate(np.unique(df[x_col]))}
    else:
        return {v: f"{v:.2f}" for v in values}


@app.callback(
    Output(Ids.y_slider, "marks"),
    inputs=[Input(Ids.y_slider, "value")],
    state=[State(Ids.y_col, "value")],
)
def y_slider_labels_callback(values, y_col):
    if isinstance(list(df[y_col])[0], str):
        return {i: f"{v}" for i, v in enumerate(np.unique(df[y_col]))}
    else:
        return {v: f"{v:.2f}" for v in values}


@app.callback(
    Output(Ids.heatmap, "figure"),
    inputs=[Input(Ids.x_slider, "value"), Input(Ids.y_slider, "value")],
    state=[State(Ids.x_col, "value"), State(Ids.y_col, "value")],
)
def heatmap_edges_callback(edges_x, edges_y, x_col, y_col):
    z, x, y = make_matrix(x_col, y_col, bins=(edges_x, edges_y))
    return heatmap_figure(z, x, y)


@app.callback(
    Output(Ids.x_slider_container, "children"),
    inputs=[Input(Ids.x_col, "value")],
    state=[State(Ids.x_slider, "value"), State(Ids.binning_radio, "value")],
)
def update_x_col(x_col, current_edges, quantile):
    n_edges = len(current_edges)
    if isinstance(df[x_col].iloc[0], str):
        new_edges = np.sort(np.unique(df[x_col]))
    else:
        new_edges = phik.binning.bin_edges(df[x_col], n_edges - 1, quantile)
    return [range_slider(id=Ids.x_slider, edges=new_edges.tolist())]


@app.callback(
    Output(Ids.y_slider_container, "children"),
    inputs=[Input(Ids.y_col, "value")],
    state=[State(Ids.y_slider, "value"), State(Ids.binning_radio, "value")],
)
def update_y_col(y_col, current_edges, quantile):
    n_edges = len(current_edges)
    if isinstance(df[y_col].iloc[0], str):
        new_edges = np.sort(np.unique(df[y_col]))
    else:
        new_edges = phik.binning.bin_edges(df[y_col], n_edges - 1, quantile)
    return [
        range_slider(id=Ids.y_slider, edges=new_edges.tolist(), vertical=True)
    ]


@app.callback(
    Output(Ids.x_slider, "value"),
    inputs=[
        Input(Ids.x_bin_add_button, "n_clicks"),
        Input(Ids.x_bin_remove_button, "n_clicks"),
        Input(Ids.binning_radio, "value"),
    ],
    state=[State(Ids.x_slider, "value"), State(Ids.x_col, "value")],
)
def update_x_bins(n_add, n_remove, quantile, edges_x_old, x_col):
    if isinstance(df[x_col].values[0], str):
        return edges_x_old

    current_n_edges = len(edges_x_old)

    n_add = n_add or 0
    n_remove = n_remove or 0

    if n_add != GlobalState.X_BINS_ADD_CLICKS:
        new_n_edges = current_n_edges + 1
        GlobalState.X_BINS_ADD_CLICKS = n_add
    elif n_remove != GlobalState.X_BINS_REMOVE_CLICKS:
        new_n_edges = current_n_edges - 1
        GlobalState.X_BINS_REMOVE_CLICKS = n_remove
    else:
        new_n_edges = current_n_edges

    if new_n_edges <= 0:
        return edges_x_old

    # x = np.linspace(*min_max(edges_x_old), new_n_edges)

    x = phik.binning.bin_edges(df[x_col], new_n_edges - 1, quantile)
    print(f'!!!! --- NEW X:{x}')
    return x.tolist()


@app.callback(
    Output(Ids.y_slider, "value"),
    inputs=[
        Input(Ids.y_bin_add_button, "n_clicks"),
        Input(Ids.y_bin_remove_button, "n_clicks"),
        Input(Ids.binning_radio, "value"),
    ],
    state=[State(Ids.y_slider, "value"), State(Ids.y_col, "value")],
)
def update_y_bins(n_add, n_remove, quantile, edges_y_old, y_col):
    if isinstance(df[y_col].values[0], str):
        return edges_y_old

    current_n_edges = len(edges_y_old)

    n_add = n_add or 0
    n_remove = n_remove or 0

    if n_add != GlobalState.Y_BINS_ADD_CLICKS:
        new_n_edges = current_n_edges + 1
        GlobalState.Y_BINS_ADD_CLICKS = n_add
    elif n_remove != GlobalState.Y_BINS_REMOVE_CLICKS:
        new_n_edges = current_n_edges - 1
        GlobalState.Y_BINS_REMOVE_CLICKS = n_remove
    else:
        new_n_edges = current_n_edges

    if new_n_edges <= 0:
        return edges_y_old

    # y = np.linspace(*min_max(edges_y_old), new_n_edges)

    y = phik.binning.bin_edges(df[y_col], new_n_edges - 1, quantile)

    return y.tolist()


@app.callback(
    Output(Ids.phik_display, "children"),
    inputs=[Input(Ids.x_slider, "value"), Input(Ids.y_slider, "value")],
    state=[State(Ids.x_col, "value"), State(Ids.y_col, "value")],
)
def update_phik_display(x_bins, y_bins, x_col, y_col):
    num_vars = []
    if not isinstance(df[x_col].iloc[0], str):
        num_vars.append("x")

    if not isinstance(df[y_col].iloc[0], str):
        num_vars.append("y")

    new_phik = phik.phik_from_array(
        df[x_col], df[y_col], num_vars, bins={"x": x_bins, "y": y_bins}
    )

    return f"correlation = {new_phik:.3g}"


@app.callback(
    Output(Ids.significance_display, "children"),
    inputs=[Input(Ids.x_slider, "value"), Input(Ids.y_slider, "value")],
    state=[State(Ids.x_col, "value"), State(Ids.y_col, "value")],
)
def update_significance_display(x_bins, y_bins, x_col, y_col):
    num_vars = []
    if not isinstance(df[x_col].iloc[0], str):
        num_vars.append("x")

    if not isinstance(df[y_col].iloc[0], str):
        num_vars.append("y")

    try:
        _, new_sig = phik.significance_from_array(
            df[x_col], df[y_col], num_vars, bins={"x": x_bins, "y": y_bins}
        )

        return f"significance = {new_sig:.3g}"

    except Exception as e:
        logging.exception("Error in significance calculation")
        return "significance <error>"


if __name__ == "__main__":
    app.run_server(debug=False, host="0.0.0.0", port=8050)
