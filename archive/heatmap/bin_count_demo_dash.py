import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import plotly.figure_factory as ff

import pandas as pd
import numpy as np

# import phik
# TODO: Replace hist2d_dummy (which is useeless) to calculate the
#       correlation bin heatmap using phik package (when it is released)

# df = pd.DataFrame(np.random.normal(size=(100000, 2)), columns=["x1", "x2"])
df = pd.read_csv("../data/diamonds.csv", index_col=0)
columns = df.columns

app = dash.Dash(__name__, assets_folder='../macros/assets', )


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


class GlobalState:
    """Container for global state variables"""

    X_BINS_ADD_CLICKS = 0
    Y_BINS_ADD_CLICKS = 0

    X_BINS_REMOVE_CLICKS = 0
    Y_BINS_REMOVE_CLICKS = 0


def min_max(arr):
    return np.min(arr), np.max(arr)


def hist2d_dummy(x, y, bins=None):
    """Not really a (categorical) 2d histogram"""

    x = list(x)
    y = list(y)

    if isinstance(bins, int) or bins is None:
        bins_tuple = (bins, bins)
    else:
        bins_tuple = tuple(bins)

    if isinstance(x[0], str) and isinstance(y[0], str):
        x_unique = np.unique(x)
        y_unique = np.unique(y)
        hist = np.random.randint(100, size=(len(x_unique), len(y_unique)))
        return hist, x_unique, y_unique

    elif isinstance(x[0], str):
        x_unique = np.unique(x)
        y_hist, y_edges = np.histogram(y, bins=bins_tuple[1])
        hist = np.ones(shape=(len(x_unique), len(y_edges) - 1)) * y_hist
        return hist, x_unique, y_edges

    elif isinstance(y[0], str):
        y_unique = np.unique(y)
        x_hist, x_edges = np.histogram(x, bins=bins_tuple[0])
        hist = x_hist.reshape(-1, 1) * np.ones(
            shape=(len(x_edges) - 1, len(y_unique))
        ).astype(int)
        return hist, x_edges, y_unique

    else:
        if bins is not None:
            return np.histogram2d(x, y, bins=bins)
        else:
            return np.histogram2d(x, y)


def heatmap_kwargs(z, x, y, **extra_kwargs):
    if len(x) == z.shape[0]:
        centers_x = x
    else:
        centers_x = x[:-1] + np.diff(x) / 2

    if len(y) == z.shape[1]:
        centers_y = y
    else:
        centers_y = y[:-1] + np.diff(y) / 2

    return dict(
        x=list(centers_x), y=list(centers_y), z=z.T.tolist(), **extra_kwargs
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

    figure.layout.title = "Bin it to me baby (aha aha)"
    figure.layout.font = {"color": "white"}

    return dict(
        data=[
            go.Heatmap(
                x=x,
                y=y,
                z=z,
                xgap=1,
                ygap=1,
                colorscale="Viridis",
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


first_heatmap, first_edges_x, first_edges_y = hist2d_dummy(
    columns[0], columns[1]
)
first_heatmap_kwargs = heatmap_kwargs(
    first_heatmap, first_edges_x, first_edges_y
)

app.layout = html.Div(
    children=[
        html.H1("Dynamic Binning Demo"),
        html.Div(children="Hit me with your best plot"),
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
    ]
)


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
    z, x, y = hist2d_dummy(df[x_col], df[y_col], bins=(edges_x, edges_y))
    return heatmap_figure(z, x, y)


@app.callback(
    Output(Ids.x_slider_container, "children"),
    inputs=[Input(Ids.x_col, "value")],
    state=[State(Ids.x_slider, "value")],
)
def update_x_col(x_col, current_edges):
    n_edges = len(current_edges)
    if isinstance(df[x_col].iloc[0], str):
        new_edges = np.unique(df[x_col])
    else:
        new_edges = np.linspace(df[x_col].min(), df[x_col].max(), n_edges)
    return [range_slider(id=Ids.x_slider, edges=new_edges.tolist())]


@app.callback(
    Output(Ids.y_slider_container, "children"),
    inputs=[Input(Ids.y_col, "value")],
    state=[State(Ids.y_slider, "value")],
)
def update_y_col(y_col, current_edges):
    n_edges = len(current_edges)
    if isinstance(df[y_col].iloc[0], str):
        new_edges = np.unique(df[y_col])
    else:
        new_edges = np.linspace(df[y_col].min(), df[y_col].max(), n_edges)
    return [
        range_slider(id=Ids.y_slider, edges=new_edges.tolist(), vertical=True)
    ]


@app.callback(
    Output(Ids.x_slider, "value"),
    inputs=[
        Input(Ids.x_bin_add_button, "n_clicks"),
        Input(Ids.x_bin_remove_button, "n_clicks"),
    ],
    state=[State(Ids.x_slider, "value")],
)
def update_x_bins(n_add, n_remove, edges_x_old):
    current_n_edges = len(edges_x_old)

    n_add = n_add or 0
    n_remove = n_remove or 0

    if n_add != GlobalState.X_BINS_ADD_CLICKS:
        new_n_edges = current_n_edges + 1
        GlobalState.X_BINS_ADD_CLICKS = n_add
    else:
        new_n_edges = current_n_edges - 1
        GlobalState.X_BINS_REMOVE_CLICKS = n_remove

    if new_n_edges <= 0:
        return edges_x_old

    x = np.linspace(*min_max(edges_x_old), new_n_edges)

    return x.tolist()


@app.callback(
    Output(Ids.y_slider, "value"),
    inputs=[
        Input(Ids.y_bin_add_button, "n_clicks"),
        Input(Ids.y_bin_remove_button, "n_clicks"),
    ],
    state=[State(Ids.y_slider, "value")],
)
def update_y_bins(n_add, n_remove, edges_y_old):
    current_n_edges = len(edges_y_old)

    n_add = n_add or 0
    n_remove = n_remove or 0

    if n_add != GlobalState.Y_BINS_ADD_CLICKS:
        new_n_edges = current_n_edges + 1
        GlobalState.Y_BINS_ADD_CLICKS = n_add
    else:
        new_n_edges = current_n_edges - 1
        GlobalState.Y_BINS_REMOVE_CLICKS = n_remove

    if new_n_edges <= 0:
        return edges_y_old

    y = np.linspace(*min_max(edges_y_old), new_n_edges)

    return y.tolist()


if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0')
