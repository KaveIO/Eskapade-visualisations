# KPMG Visualisations (dash_utils)

 - Version: 1.0.0
 - Released: Juli 2019
 - Web page: http://eskapade.kave.io
 - Repository: https://github.com/kaveio/Eskapade-visualisations


This specific module is to create a data exploration and demo app
using Dash (https://dash.plot.ly/). In addition, there is an interactive demo
for the phi_k correlation analyzer (https://github.com/KaveIO/PhiK), which will
calculate and display correlation matrices between two variables.

# Check it out

To install check out the github repository:

``` bash

    $ git clone https://github.com/KaveIO/Eskapade-visualisations
    $ pip install -e Eskapade-visualisations
```


## Dash Template

Please see `dash_tutorial.rst` for more details on the tutorial and template.

## Dash demo's

We created a couple of demos to showcase what you can do with dash and the dash_utils in the package.

**df summary**

Remix of the original df_summary link in Eskapade, now reworked to incorporate the pandas_profiling
calculations as well.
You can run the application by calling ``python [path/to/]df_summary.py`` which will then run on
`http://localhost:8050`. You can select any variable and it will be plotted in either a barchart
or a histogram, depending on the data type. In addition, the calculated values from
the pandas_profiling will be shown in the table next to it.

TODO: Add a data uploader

**template app**

A template example using the functions from dash_utils, such as the figure_grid and the
callback functions.
It shows a basic example with 3 graphs and a table, that will respond to your selections. The app
itself functions as an extension to the df_summary app. Where there you could only select a barchart,
here you can also add a scatterplot and compare multiple variables.

TODO: Add a data uploader

**The Phi_K demo**

Demonstrates the actual capabilities of the phi_k correlation analyzer package.
Consists of one file, `phik_frontend.py` which can be called from the `heatmap` folder
using `_python phik_frontend.py` to start the flask server.
**NB: as it currently stands, if the app is called from outside the heatmap folder the
.css files will not load correctly and the app will not be formatted correctly.**
As per default the app will server on `http://localhost:8050`. This version supports calculating
correlation matrices for ordinal, categorical and continuous variables. It also
allows for manual editing of the bin edges for continuous variables.
The demo uses the diamond dataset as input.

## Contact and support
Issues & Ideas: https://github.com/kaveio/Eskapade-visualisations/issues

Q&A Support: contact us at: kave [at] kpmg [dot] com

Please note that the KPMG Eskapade group provides support only on a best-effort basis.
