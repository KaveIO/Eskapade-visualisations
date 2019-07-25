"""
Utility functions used with

Author: Susanne Groothuis Groothuis.susanne@kpmg.nl
"""
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.graph_objs as go

import numpy as np
import pandas as pd
import seaborn as sns


def column(children, style={}, className='five columns'):
    """"Convenience function to return a column style html.Div. It uses
    a custom css determining the width of the columns based on the className.

    :param list children: List of children to put into the column.
    :param dict style: dict of style arguments for the column. Will overwrite
                       the css values
    :param st className: name pointing to the css class.
    """
    return html.Div(children=children, style=style, className=className)


def row(children, style={}, className='row'):
    """"Convenience function to return a row style html.Div. It uses
    a custom css determining the width of the columns based on the className.

    :param list children: List of children to put into the column.
    :param dict style: dict of style arguments for the column. Will overwrite
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
        layout_kwargs = dict(plot_bgcolor='#263740',
                             paper_bgcolor='#1d2930',
                             font=dict(color='white'),
                             margin=go.layout.Margin(b=30, l=30,
                                                     r=30, t=40,
                                                     pad=5))

    if n_figures > 1:
        if n_figures % 2 == 0:
            index = np.arange(n_figures).reshape(2, -1)
        else:
            index = np.arange(n_figures-1).reshape(2, -1)

        childs = []
        for ll in index:
            row_childs = []
            for i in ll:
                row_childs.append(dcc.Graph(id=f'fig_{i}',
                                            figure={'data': [],
                                                    'layout': go.Layout(title=f"Graph {i}",
                                                                        **layout_kwargs)},
                                            style={'width': '100%'}))

            childs.append(column(row_childs, className='five columns'))

        if n_figures % 2 == 1:
            # -- add the last figure for uneven amount
            i = int(n_figures-1)
            row_childs = [dcc.Graph(id=f'fig_{i}',
                                    figure={'data': [],
                                            'layout': go.Layout(title=f'Graph {i}',
                                                                **layout_kwargs)},
                                    style={'width': '100%'})]

            childs.append(row([column(row_childs, className='ten columns')]))
    else:
        childs = figures

    return childs


def control_grid(n_controls, controls):

    if n_controls > 1:
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
    elif not sel1:
        sel = sel2
    elif not sel2:
        sel = sel1
    else:
        sel = np.array(sel1)[np.isin(sel1, sel2)] if sel1 > sel2 else np.array(sel2)[np.isin(sel2, sel1)]
        print(sel[:10])

    return sel


def make_histogram(df, col, bins, color_filter, layout_kwargs, sel=None,):
    """
    Returns a dictionary used on for the 'figure' argument of a dash graph object.

    :param DataFrame df: Input data
    :param str col: Name of the df column to plot
    :param int bins: Number of bins
    :param str color_filter: Name of the df columns used to filter/group by in color
    :param dict layout_kwargs: layout arguments for the graph object
    :param sel: TODO: use

    :return dict: Dictionary containing 'data' and 'layout' as keys
    """
    if sel is None:
        sel = df.index
    elif col is not None:
        sel = df.loc[sel, col].index
    if col is None:
        return {'data': [],
                'layout': go.Layout(title="Please select a variable",
                                    **layout_kwargs)}
    if color_filter is None:
        return {'data': [go.Histogram(x=df[col].values, nbinsx=bins,
                                      )],
                'layout': go.Layout(title=f'{col.capitalize()}', **layout_kwargs)}

    else:

        pal = sns.palettes.color_palette('viridis', n_colors=len(df[color_filter].unique()))
        pal = pal.as_hex()
        return {'data': [go.Histogram(x=df.loc[df[color_filter] == x, col],
                                      marker=dict(color=pal[i]),
                                      nbinsx=bins,
                                      name=str(x),
                                      )
                         for i, x in enumerate(df[color_filter].unique())],
                'layout': go.Layout(title=f'{col.capitalize()}',
                                    **layout_kwargs)}


def make_table(columns=None, data=None, id=None, layout_kwargs=None):

    if id is None:
        id = 'table'

    if columns is not None:
        if isinstance(columns[0], str):
            columns = [{'name': c, 'id': c} for c in columns]

    if isinstance(data, pd.DataFrame):
        data = data.to_dict('records')

    if (data is not None) and (columns is not None):
        return dash_table.DataTable(id=id,
                                    data=data,
                                    columns=columns,
                                    **layout_kwargs)
    elif (columns is None) and (data is not None):
        return dash_table.DataTable(id=id,
                                    data=data,
                                    columns=columns,
                                    **layout_kwargs)

    else:
        return dash_table.DataTable(id=id,
                                    data=[],
                                    columns=columns if columns is not None else [],
                                    **layout_kwargs)


def make_scatter(df, x, y, color_filter, layout_kwargs, sel=None):
    """
    Returns a go object used on the figure argument of the graph object
    in dash.
    :param pd.DataFrame df: The data
    :param str x: x value for the scatter plot
    :param str y: y value for the scatter plot
    :param str color_filter: value to filter on (hue in seaborn)
    :param dict layout_kwargs: arguments for the layout of the plot
    :param sel: selection of datapoints TODO: use them?

    :return:
    """
    if sel is None:
        sel = df.index

    if (x is None) or (y is None):
        return{'data': [],
               'layout': go.Layout(title='',
                                   **layout_kwargs)}

    elif color_filter is None:
        return {'data': [go.Scattergl(x=df[x].values,
                                      y=df[y].values,
                                      mode='markers',
                                      )],
                'layout': go.Layout(title=f'{x.capitalize()} vs {y.capitalize()}',
                                    **layout_kwargs)}
    else:
        n_colors = len(df[color_filter].unique())
        pal = sns.palettes.color_palette('viridis', n_colors=n_colors)
        pal = pal.as_hex()
        return {'data': [go.Scattergl(x=df.loc[df[color_filter] == hue, x],
                                      y=df.loc[df[color_filter] == hue, y],
                                      mode='markers',
                                      name=str(hue),
                                      marker=dict(color=pal[i]),
                                      )
                         for i, hue in enumerate(df[color_filter].unique())],
                'layout': go.Layout(title=f'{x.capitalize()} vs {y.capitalize()}',
                                    **layout_kwargs)}


def make_heatmap(values, xbins, ybins, labels, colorscale, cmap, layout_kwargs, sel=None):
    """

    :param values:
    :param xbins:
    :param ybins:
    :param labels:
    :param colorscale:
    :param cmap:
    :param layout_kwargs:
    :param sel: TODO: use them
    :return:
    """

    if (xbins is None) or (ybins is None):
        return{'data': [go.Heatmap(z=values.T,
                                   colorscale=cmap,
                                   zmin=colorscale[0],
                                   zmax=colorscale[-1],
                                   zsmooth='best')],
               'layout': go.Layout(title=f'Punctuality',
                                   **layout_kwargs)}
    else:
        return {'data': [go.Heatmap(z=values.T,
                                    colorscale=cmap,
                                    zsmooth='best',
                                    zmin=colorscale[0],
                                    zmax=colorscale[-1],
                                    text=labels.T,
                                    hoverinfo=['text', 'z'])],
                'layout': go.Layout(title=f'Punctuality',
                                    height=800,
                                    width=800,
                                    **layout_kwargs,)}


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

    :param list control_strings: List of dictionaries containing the object name and
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


def matplotlib_to_plotly(cmap, pl_entries):
    h = 1.0/(pl_entries-1)
    pl_colorscale = []

    for k in range(pl_entries):
        C = list(map(np.uint8, np.array(cmap(k*h)[:3])*255))
        pl_colorscale.append([k*h, 'rgb'+str((C[0], C[1], C[2]))])

    return pl_colorscale


def data_profile_tables(input_vars={}, col='', layout_kwargs={}):

    columns = [{'name': 'Variable', 'id': 'var'}, {'name': 'Value', 'id': 'value'}]

    if input_vars and (col != ''):

        variables = [{'id': 'name', 'name': 'Name', 'type': 'name'},
                     {'id': 'type', 'name': 'Type', 'type': 'basis'},
                     {'id': 'memorysize', 'name': 'Memory size', 'type': 'basis'},
                     {'id': 'count', 'name': 'Count', 'type': 'counts'},
                     {'id': 'distinct_count', 'name': 'Distinct count', 'type': 'counts'},
                     {'id': 'distinct_count_with_nan',
                      'name': 'Distinct count (with_nan)',
                      'type': 'counts'},
                     {'id': 'distinct_count_without_nan',
                      'name': 'Distinct count (without_nan)',
                      'type': 'counts'},
                     {'id': 'n_missing', 'name': 'N missing', 'type': 'counts'},
                     {'id': 'n_zeros', 'name': 'N zeros', 'type': 'counts'},
                     {'id': 'n_infinite', 'name': 'N infinite', 'type': 'counts'},
                     {'id': 'p_missing', 'name': 'Missing %', 'type': 'percentage'},
                     {'id': 'p_infinite', 'name': 'Infinite %', 'type': 'percentage'},
                     {'id': 'p_unique', 'name': 'Unique %', 'type': 'percentage'},
                     {'id': 'mean', 'name': 'Mean', 'type': 'percentage'},
                     {'id': 'std', 'name': 'Std', 'type': 'percentage'},
                     {'id': 'variance', 'name': 'Variance', 'type': 'percentage'},
                     {'id': 'min', 'name': 'Min', 'type': 'percentage'},
                     {'id': 'max', 'name': 'Max', 'type': 'percentage'},
                     {'id': 'mode', 'name': 'Mode', 'type': 'percentage'},
                     {'id': '5%', 'name': '5%', 'type': 'percentage'},
                     {'id': '25%', 'name': '25%', 'type': 'percentage'},
                     {'id': '50%', 'name': '50%', 'type': 'percentage'},
                     {'id': '75%', 'name': '75%', 'type': 'percentage'},
                     {'id': '95%', 'name': '95%', 'type': 'percentage'},
                     {'id': 'kurtosis', 'name': 'Kurtosis', 'type': 'stats'},
                     {'id': 'skewness', 'name': 'Skewness', 'type': 'stats'},
                     {'id': 'iqr', 'name': 'Interquartile range', 'type': 'stats'},
                     {'id': 'cv', 'name': 'Coeff. of Variation', 'type': 'stats'},
                     {'id': 'range', 'name': 'Range', 'type': 'stats'},
                     {'id': 'top', 'name': 'Top', 'type': 'stats'},
                     {'id': 'freq', 'name': 'Frequency', 'type': 'stats'},
                     {'id': 'max_length', 'name': 'Max length', 'type': 'stats'},
                     {'id': 'min_length', 'name': 'Min length', 'type': 'stats'},
                     {'id': 'mean_length', 'name': 'Mean length', 'type': 'stats'},
                     ]

        data = [{'var': v['name'], 'value': str(input_vars[col][v['id']])}
                for v in variables if (v['type'] == 'basis') & (v['id'] in input_vars[col].keys())]
        data.append({'var': 'Counts', 'value': ''})
        data.extend([{'var': v['name'], 'value': input_vars[col][v['id']]}
                     for v in variables if (v['type'] == 'counts') & (v['id'] in input_vars[col].keys())])
        data.append({'var': 'Statistics', 'value': ''})
        data.extend([{'var': v['name'], 'value': input_vars[col][v['id']]}
                     for v in variables if (v['type'] == 'stats') & (v['id'] in input_vars[col].keys())])

        conditional_formatting = {'style_data_conditional': [{'if': {'column_id': 'var',
                                                                     'filter_query': '{var} eq "Counts"'},
                                                              'backgroundColor': '#263740',
                                                              'fontSize': '1em',
                                                              'fontWeight': 'bold'},
                                                             {'if': {'column_id': 'value',
                                                                     'filter_query': '{var} eq "Counts"'},
                                                              'backgroundColor': '#263740',
                                                              'fontSize': '1em',
                                                              'fontWeight': 'bold'},
                                                             {'if': {'column_id': 'var',
                                                                     'filter_query': '{var} eq "Statistics"'},
                                                              'backgroundColor': '#263740',
                                                              'fontSize': '1em',
                                                              'fontWeight': 'bold'},
                                                             {'if': {'column_id': 'value',
                                                                     'filter_query': '{var} eq "Statistics"'},
                                                              'backgroundColor': '#263740',
                                                              'fontSize': '1em',
                                                              'fontWeight': 'bold'}
                                                             ]
                                  }

    else:
        data = []
        conditional_formatting = {}

    conditional_formatting = {**conditional_formatting, **layout_kwargs}

    return make_table(columns=columns, data=data, layout_kwargs=conditional_formatting)
