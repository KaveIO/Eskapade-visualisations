"""
Utility functions used with

Author: Susanne Groothuis Groothuis.susanne@kpmg.nl
"""
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

import numpy as np
import pandas as pd
import seaborn as sns


def column(children, style={}, className='five columns'):
    """"Convenience function to return a column style html.Div. It uses
    a custom css determining the width of the columns based on the className.

    :param list children: List of children to put into the column.
    :param style dict: dict of style arguments for the column. Will overwrite
                       the css values
    :param st className: name pointing to the css class.
    """
    return html.Div(children=children, style=style, className=className)


def row(children, style={}, className='row'):
    """"Convenience function to return a row style html.Div. It uses
    a custom css determining the width of the columns based on the className.

    :param list children: List of children to put into the column.
    :param style dict: dict of style arguments for the column. Will overwrite
                       the css values
    :param st className: name pointing to the css class.
    """
    return html.Div(children=children, style=style, className=className)

def figure_grid(n_figures, figures=None, fig_names=None,
                layout_kwargs=None):
    """Convenience function to return a grid of Graph objects. The grid is created
    based on the amount of figures passed.

    :param int n_figures: Number of figures to make a grid for. Max allowed = 6
    :param list figures: list of plotly.graph_objs
    :param list fig_names: Optional list of figure names.
    :param layout_kwargs: Optional layout arguments passed on to the go.Layout object.
    """

    if fig_names is None:
        fig_names = [f"Graph {i}" for i in range(n_figures)]
    if layout_kwargs is None:
        layout_kwargs = dict(plot_bgcolor = '#263740',
                             paper_bgcolor = '#1d2930',
                             font=dict(color = 'white'),
                             margin=go.layout.Margin(b=30, l=30,
                                                     r=30, t=40,
                                                     pad=5))

    if (n_figures > 1):
        if n_figures % 2 == 0:
            index = np.arange(n_figures).reshape(2, -1)
        else:
            index = np.arange(n_figures-1).reshape(2, -1)

        childs = []
        for ll in index:
            row_childs = []
            for i in ll:
                row_childs.append(dcc.Graph(id=f'fig_{i}',
                                            figure={'data':[],
                                                    'layout': go.Layout(title=f"Graph {i}",
                                                                          **layout_kwargs)},
                                            style={'width': '100%'}))

            childs.append(column(row_childs, className='five columns'))

        if n_figures % 2 == 1:
            # -- add the last figure for uneven amount
            i = int(n_figures-1)
            row_childs = [dcc.Graph(id=f'fig_{i}',
                                    figure={'data':[],
                                            'layout': go.Layout(title=f'Graph {i}',
                                                                  **layout_kwargs)},
                                    style={'width':'100%'})]

            childs.append(row([column(row_childs, className='ten columns')]))
    else:
        childs = figures

    return childs

def control_grid(n_controls, controls):
    if (n_controls > 1):
        if n_controls % 2 == 0:
            index = np.arange(n_controls).reshape(2, -1)
        else:
            index = np.arange(n_controls-1).reshape(2, -1)

        childs = []
        for ll in index:
            row_childs = []
            for item in ll:
                row_childs.append(controls[item])
            childs.append(row(row_childs))

        if n_controls % 2 == 1:
            childs.append([controls[-1]])
    else:
        childs = controls

    return childs


def return_selection(points1, points2, df):

    if points1 is not None:
        try:
            sel1 = [x['pointNumbers'] for x in points1['points']]
            sel1 = [k for elem in sel1 for k in elem]

        except KeyError:
            sel1 = None
    else:
        sel1 = []

    if points2 is not None:
        print(points2['points'][0].keys())

        try:
            sel2 = [x['pointNumber'] for x in points2['points']]
        except KeyError:
            sel2 = None
    else:
        sel2 = []

    if (sel1 == []) & (sel2 == []):
        sel = df.index.values
    elif (sel1 == []):
        sel = sel2
    elif sel2 == []:
        sel = sel1
    else:
        sel = np.array(sel1)[np.isin(sel1, sel2)] if sel1 > sel2 else np.array(sel2)[np.isin(sel2, sel1)]
        print(sel[:10])

    return sel


def make_histogram(df, col, bins, filter, layout_kwargs, sel=None,):
    """
    Returns a dictionary used on for the 'figure' argument of a dash graph object.

    :param str col: Name of the df column to plot
    :param int bins: Number of bins
    :param str filter: Name of the df columns used to filter/group by in color

    :return dict: Dictionary containing 'data' and 'layout' as keys
    """
    if sel is None:
        sel = df.index
    elif col is not None:
        sel = df.loc[sel, col].index
    if col is None:
        return {'data':[],
                'layout': go.Layout(title="Please select a variable",
                                    **layout_kwargs)}
    if filter is None:
        return {'data': [go.Histogram(x=df[col].values, nbinsx=bins,
                                      )],
                'layout': go.Layout(title=f'{col.capitalize()}', **layout_kwargs)}

    else:

        pal = sns.palettes.color_palette('viridis', n_colors=len(df[filter].unique()))
        pal = pal.as_hex()
        return {'data': [go.Histogram(x=df.loc[df[filter] == x, col],
                                      marker=dict(color=pal[i]),
                                      nbinsx=bins,
                                      name=str(x),
                                      )
                         for i, x in enumerate(df[filter].unique())],
                'layout': go.Layout(title=f'{col.capitalize()}',
                                    **layout_kwargs)}


def make_scatter(df, x, y, filter, layout_kwargs, sel=None):
    """
    Returns a go object used on the figure argument of the graph object
    in dash.
    :param pd.DataFrame df: The data
    :param str x: x value for the scatter plot
    :param str y: y value for the scatter plot
    :param str filter: value to filter on
    :param dict layout_kwargs: arguments for the layout of the plot
    :return:
    """
    if sel is None:
        sel = df.index

    if (x is None) or (y is None):
        return{'data':[],
               'layout':go.Layout(title='',
                                  **layout_kwargs)}

    elif filter is None:
        return {'data':[go.Scattergl(x=df[x].values,
                                     y=df[y].values,
                                     mode='markers',
                                     )],
                'layout': go.Layout(title=f'{x.capitalize()} vs {y.capitalize()}',
                                    **layout_kwargs)}
    else:
        n_colors = len(df[filter].unique())
        pal = sns.palettes.color_palette('viridis', n_colors=n_colors)
        pal = pal.as_hex()
        return {'data': [go.Scattergl(x=df.loc[df[filter]==hue, x],
                                    y=df.loc[df[filter]==hue, y],
                                    mode='markers',
                                    name=str(hue),
                                    marker=dict(color=pal[i]),
                                    )
                         for i, hue in enumerate(df[filter].unique())],
                'layout': go.Layout(title=f'{x.capitalize()} vs {y.capitalize()}',
                                    **layout_kwargs)}


def make_go_list(go_strings):
    """
    Returns a list of plotly.graph_objs
    :param list go_strings:
        - Histogram
        - Scatter
        - Layout
         etc
    :return:
    """
    figure_list = []
    for f in go_strings:
        figure_list.append(getattr(go, f))
    return figure_list

def make_control_list(control_strings):
    """

    :param list control_lost: List of dictionaries containing the object name and
    the arguments as a dict
    :return:

    Example input:
        [{"Name": "Histogram", "args": {"Options":[1,2,3],"value":None}]
    """
    control_list = []
    for c in control_strings:
        control = getattr(dcc, c['name'].capitalize())
        control_list.append(control(**c['args']))
    return control_list