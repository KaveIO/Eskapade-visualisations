# Eskapade Visualisations

 - Version: 0.1.0
 - Released: Januari 2019
 - Web page: http://eskapade.kave.io
 - Repository: https://github.com/kaveio/Eskapade-visualisations

Eskapade is a light-weight, python-based data analysis framework, meant
for developing and modularizing all sorts of data analysis problems into
reusable analysis components.

Eskapade uses a modular approach to analytics, meaning that you can use
pre-made operations (called 'links') to build an analysis. This is implemented in a chain-link framework, where you define a 'Chain', consisting of a number of Links. These links are the fundamental building block of your analysis. For example, a data loading link and a data transformation link will frequently be found together in a pre-processing Chain.

Each chain has a specific purpose, for example: data quality checks of
incoming data, pre-processing of data, booking and/or training of predictive
algorithms, validation of these algorithms, and their evaluation. By using
this work methodology, analysis links can be more easily reused in future
data analysis projects.

Eskapade is analysis-library agnostic. It is used to set up typical data
analysis problems from multiple packages, e.g.: scikit-learn, Spark MLlib,
and ROOT. Likewise, Eskapade can use a manner of different data structures
to handle data, such as: pandas DataFrames, numpy arrays, Spark DataFrames/RDDs,
and more.

For example, Eskapade has been used as a self-learning framework for typical
machine learning problems. Trained algorithms can predict real-time or batch data,
these models can be evaluated over time, and Eskapade can bookkeep and retrain
their algorithms.

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

## Dash Heatmaps

We created two versions of the correlation heatmap interface: the dummy version
and the link.

**The dummy version**

Demonstrates the capabilities of the interface without
actually calculating any correlations. It can handle both categorical and
continuous data, and allows the user to manually change the number and edges of
histogram bins. Since little calculation happens, this version is snappy and
easy to work out new ideas on. The code is a standalone python script located at
`heatmap/bin_count_demo_dash.py`.

**The link version**

Consists of the `CorrelationFrontend` link, the use of
which is demonstrated in `macros/correlation_analyser_diamonds.py`. The
interface is almost the same as the dummy version, but in the backend the actual
correlation heatmap is calculated. This version does not yet support editing
the bin edges, and further development is pending the release of the `PhiK`
package and corresponding correlation link to use as a back end.

**The Phi_K demo**

Demonstrates the actual capabilities of the phi_k correlation analyzer package.
Consists of one file, `phik_frontend.py` which can be called from the `heatmap` folder
using `python phik_frontend.py` to start the flask server.
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