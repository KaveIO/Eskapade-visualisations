##############################
Making a dash app for eskapade
##############################

Eskapade_viz
------------

We've created two files for eskapade that can work in part as a template, and in part as an example on how
to build a dash app for your eskapade project:

 - dash_builder.py
 - dash_builder_macro.py

The ``eskapade_viz`` package can be installed to use the link and associated util functions. The macro is located on
the git repository.

Plotly vs Dash
--------------

Simply put, plotly is a plotting library (like matplotlib), which you can use to create interactive plots. You can make
interactive plots in a notebook as well. The plot will allow you to zoom in, select and de-select certain points and
attach a widget which can influence the plot output.
The 'things' which are the plots are called graph objects. The common way for plotly to import them in their examples as
``import plotly.graphs_obj as go`` so, you will often see the plot objects appear as, for example, ``go.Scatter()``.

Dash is a python framework which you can use to create complete interactive dashboards using just python. It uses
the graph objects from plotly, and wraps them in HTML functions to lay them in the page. In addition, dash allows you
to create callback functions that fire when you click a button or move a slider.

The macro
---------

The macro ``dash_builder_macro.py`` uses two links, the ``ReadToDf`` from the ``eskapade.analysis`` module, and the
``DashBuilder`` link from the ``eskapade_viz`` package.

The macro loads a pre-existing dataset called the diamonds dataset (Note: If you don't have this data, you can easily
find it online, or use the seaborn package to load it (``df = seaborn.load_data('diamonds')``).

If you change the dataset, you will have to enter the columns in the macro. These column names are transformed into
an options dictionary, which will later serve for the dropdown menus of our app.

The DashBuilder link
--------------------

The link is set up in a way so it's easy for you to make a simple report using dash, without to much manual work. The
basic setup creates 3 plots; 2 histograms and a scatter plot. They are filled in using dropdown menus, allowing you
to quickly look at your data by selecting different values.
In addition, there is a 'filter by' menu, which will allow you to color the plots based on a categorical variable.

Link DashBuilder arguments
^^^^^^^^^^^^^^^^^^^^^^^^^^

- **read_key**: strings name of the data stored in the datastore
- **store_key**: string name of the app to be stored in the datastore
- **figure_strings**: list of strings telling the link what kind of figures to make
    ex: ["Histogram", "Histogram", "Scatter", "Scatter"]
    TODO: Automatically fill graphs using this list. Currently only the length of the list is used to make the grid.
- **control_strings**: list of dictionaries containing the ``name`` and ``args`` passed on to the control widgets, where
    ``name`` is the name of a dash core component.

    ex: [dict(name='Dropdown', args={'options':['list', 'of', 'dropdown', 'options'], value='default_value', id='fig1')]
- **app_title**: string name of your app, will appear above the controls columns as the title
- **filter_controls**: controls to filter your graphs by.

Editing the link
^^^^^^^^^^^^^^^^

You can run the macro as is, on your dataset, and you will get 3 interactive plots which you can use to explore your data
(two histograms and a scatter plot).
However, if you want to edit the dashboard to your needs here are some things you need to consider:


#. Dash has ``dcc.Graph`` objects, which hold a ``go.WhateverPlot`` plotly object.

#. The page layout is generated automatically by stacking different ``dcc.Graph`` objects in a grid. The grid is created based on the length of the ``figure_strings`` list.

    #. The controls are currently placed all in one column to the left. If you add to many, you'll have to scroll down.

#. Adding new ``Graph`` can be done by simply adding more figure string names to the ``figure_strings`` input variable of the link. The link will create the space for it. It will **not** fill in the space with the correct plot automatically (yet).

#. Adding a new figure and filling it up will require you to create a callback function, which populates the graph with an actual ``graph_obj`` from plotly. The callback has to refer to a unique Graph id.
    #. Another option is to hardcode the figure input, but you will be left with a static figure that does not respond to dropdowns or sliders. It can however still zoom/scroll.

#. There are only two convenience functions available in the ``eskapade_viz`` package to do this simply, for histograms and for scatterplots. If you want to add a different plot, you'll need to create your own function.

#. Callbacks all work in the same way, they can take multiple things as input (the values of control widgets for example) but can only have 1 output. Usually this is the ``figure`` argument of the ``dcc.Graph`` object, which in turn has to have at least a 'data' argument and a 'layout' argument.

Callbacks
^^^^^^^^^

Callbacks in dash are functions that will fire based on an input. The input is some sort of change, most often triggered
by the changing of a widget like a dropdown menu, input field, slider etc.
A callback can listen to several inputs, but can return only one output. So, you need to have a separate callback function
for each figure you have in your dashboard.

An example of a callback:

.. code-block:: python

        @app.callback(Output('fig_0', 'figure'),
                      [Input('dropdown_0', 'value'),
                       Input('slider_0', 'value'),
                       Input('filter_dropdown', 'value')])
        def update_fig1(col, bins, filter):
            return du.make_histogram(ds[self.read_key], col, bins, filter, self.layout_kwargs)

In this example the callback takes input from three different widgets, with id's ``dropdown_0``, ``slider_0`` and ``filter_dropdown``. The dropdown menu's
control which variables is being displayed, and which categorical variable is used to color the output. The slider will
determine the number of bins. Note that the inputs appearing from top to bottom, correspond to the input arguments of the ``update_fig1``
function from left to right. So ``dropdown_0`` corresponds to ``col`` and ``slider_0`` corresponds to ``bins``.
The function calls a helper funtion called ``make_histogram`` which will return a dictonary containing a ``data`` and a ``layout`` key.
The corresponding value to ``data`` will be a list (one or multiple) go.Histogram objects, and the ``layout`` key will contain a
``go.Layout`` object.

For example:

.. code-block:: python

    {'data': [go.Histogram(x=df[col].values, nbinsx=bins)],
     'layout': go.Layout(title=f'{col.capitalize()}', **layout_kwargs)}

The output is returned to the ``dcc.Graph`` object with id ``fig_0`` and populate the ``figure`` argument. (aka, the plot)

FAQ
---

**Q: Can I change the colors of my app?**

A: Yes, you can edit the colors of the *plots* itself by changing the ``layout_kwargs`` in the initialize part of the ``dash_builder`` app.
To edit the colors of the app itself (background, font, etc) you will need to edit the css files found in the ``macros/assets`` folder.

**Q: Where is the data loaded?**

A: The link is setup so it uses a pandas DataFrame from the DataStore. You can thus either load it in using the ``ReadToDf`` link (as
shown in the ``dash_builder_macro`` or use any other analysis result saved as a DataFrame in the DataStore.

