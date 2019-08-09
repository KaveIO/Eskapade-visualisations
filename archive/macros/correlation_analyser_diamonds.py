"""Project: Eskapade - A _python-based package for data analysis.

Macro: correlation_analyser

Created: 2018/08/01

Description:
    This macro calculates correlations between categorical and/or continuous observables.

    This is done for a simulated training and test data for a motorcycle insurance portfolio,
    downloaded from freakonometrics.free.fr.

    Based on the hypothesis of no correlation expected frequencies of observations *
    are calculated. The measured frequencies are compared to expected frequencies. *
    From these the (significance of the) p-value of the hypothesis that the
    observables in the input dataset are not correlated is determined. The
    normalized residuals (pull values) for each bin in the dataset are also
    calculated. A detailed description of the method can be found in ABCDutils.h.
    A description of the method to calculate the expected frequencies can be found *
    in RooABCDHistPDF.cxx.

Authors:
    KPMG Advanced Analytics & Big Data team, Amstelveen, The Netherlands

Redistribution and use in source and binary forms, with or without
modification, are permitted according to the terms listed in the file
LICENSE.
"""

from eskapade import ConfigObject, Chain
from eskapade import core_ops, analysis, visualization, data_quality
from eskapade import process_manager
from eskapade.logger import Logger, LogLevel

import numpy as np
import ROOT

from esroofit.links import RooFitPercentileBinning, ConvertDataFrame2RooDataSet, UncorrelationHypothesisTester
# import dynamic_pricer.modelling as dpm
# from esroofit.links import RooFitPercentileBinning, ConvertDataFrame2RooDataSet, UncorrelationHypothesisTester

from eskapade_viz.links import CorrelationFrontend

logger = Logger()

logger.debug('Now parsing configuration file correlation_analyser.py')

#########################################################################################
# --- minimal analysis information

# 15-11-2018: running the correlation analyser for the example diamonds dataset

settings = process_manager.service(ConfigObject)

if settings['analysisName'] is None:
    settings['analysisName'] = 'correlation_analyser'
settings['version'] = settings.get('version', 0)

logger.log_level = settings.get('log_level', LogLevel.DEBUG)

log_level_hypotest = LogLevel.NOTSET

# --- settings for input and output
settings['main_path'] = settings.get('main_path', '../')


input_path = settings.get('input_path', settings['main_path'] + 'data/' +
                          'diamonds.csv')

# use this suffix to indicate any details of the dataset in the report-name (e.g. when filtering later in the macro)
# report_suffix = '_material'
report_suffix = ''

report_path = settings.get('report_path',
                           settings['main_path'] +
                           'results/reports/diamonds_data/report_correlations_diamonds{0:s}/'
                           .format(report_suffix))

results_path = settings.get('results_path',
                            settings['main_path'] + 'results/{0:s}/diamonds_data/matrices{1:s}/'
                            .format(settings['analysisName'], report_suffix))

# specify options for file-reader
reader_type = settings.get('reader_type', 'csv')
num_separator = settings.get('separator', ',')
num_decimal = settings.get('decimal', '.')

# specify options for output-report

# whether to include 1-D histograms of (normalised) residuals and p-values in final report or not
include_histograms = settings.get('include_histograms', True)


# --- settings for data filtering (if required)

# filter data
# specify columns that are used to filter dataset (these also need to be read)
filter_query = cols_filter = []

# --- settings for correlation analysis

# specify columns to evaluate
cols_str = ['cut', 'color', 'clarity']


cols_num = ['carat', 'depth', 'table', 'price',
            # 'x', 'y', 'z'
            ]

usecols = cols_str + cols_num
readcols = list(set(usecols + cols_filter))

# specify data types
# N.B. all elements in usecols need to be defined in cols_dtype
cols_dtype = {'carat': np.float64,
             'cut': str,
             'color': str,
             'clarity': str,
             'depth': np.float64,
             'table': np.float64,
             'price': np.int64,
             # 'x': np.float64,
             # 'y': np.float64,
             # 'z': np.float64
              }

# settings for hypothesis tester (number of bins, significance threshold, etc.)
DEFAULT_NUMBER_OF_BINS = settings.get('DEFAULT_NUMBER_OF_BINS', 4)
N_PERCENTILE_BINS = settings.get('N_PERCENTILE_BINS', 5)
FNAN = settings.get('FNAN', 99999999.)
Z_THRESHOLD = settings.get('Z_THRESHOLD', 3.0)

# var_number_of_bins = settings.get('var_number_of_bins', {'price': N_PERCENTILE_BINS,
#                                                          })

# specify what categories to ignore or to limit selection to
# N.B. this only determines for which categories correlations are calculated, the ignored categories
# will still be visible in the correlation-plots.
ignore_categories = settings.get('ignore_categories', ['None', 'not_a_str', 'not_a_bool', 'NaT'])
ignore_values = settings.get('ignore_values', [FNAN])  # nans


# one can also specify specific values to ignore per variable
# var_ignore_values = settings.get('var_ignore_values', {'REGION': [0, FNAN]})
# var_ignore_categories = settings.get('var_ignore_categories', {'VEHICLE_BRAND': ['opel', 'volkswagen', 'renault',
#                                                                                  'peugeot', 'ford', 'toyota'],
#                                                                'VEHICLE_TYPE': ['Van']})

# alternatively, limit values to accept if many categories exist, e.g. for vehicle brand
# var_accept_categories = settings.get('var_accept_categories', {'VEHICLE_BRAND': ['opel', 'volkswagen', 'renault',
#                                                                                  'peugeot', 'ford', 'toyota']})

# set default values to be empty
var_ignore_values = settings.get('var_ignore_values', {})
var_ignore_categories = settings.get('var_ignore_categories', {})
var_accept_categories = settings.get('var_accept_categories', {})


# furthermore, specific bin edges can be enforced.
# binregion = ROOT.RooBinning(4, 0.5, 4.5)
# binind = ROOT.RooBinning(2, -0.5, 1.5)
# binmls = ROOT.RooBinning(0, 1000000)
# binmls.addBoundary(5000)
# binmls.addBoundary(10000)
# binmls.addBoundary(15000)
# binmls.addBoundary(20000)
# binmls.addBoundary(24999)
# binmls.addBoundary(25001)
# binmls.addBoundary(40000)

# var_binning = {'INDICATOR_MATERIAL': binind,
#                'INDICATOR_INJURY': binind}
var_binning = {}

#########################################################################################
# --- now set up the chains and links based on configuration flags

ch = Chain('Data')

# --- read materials file
read_data = analysis.ReadToDf(name='reader',
                              path=input_path,
                              sep=num_separator,
                              decimal=num_decimal,
                              key='input_data',
                              usecols=readcols,
                              # parse_dates=['DATE_OF_BIRTH'],
                              reader=reader_type)

ch.add(read_data)

# --- filter data
link = analysis.ApplySelectionToDf(read_key=read_data.key,
                                   query_set=filter_query)
ch = Chain('Fix')

# --- percentile binning, done *before* nans get converted info floats below,
# such that these do not affect the percentile bins
# pb = RooFitPercentileBinning()
# pb.read_key = read_data.key
# pb.var_number_of_bins = var_number_of_bins
# pb.binning_name = 'percentile'
# ch.add(pb)

# --- fix nans if they exist in a row (set to same dtype with convert_inconsistent_nans)
fixer = data_quality.FixPandasDataFrame(name='fixer')
fixer.read_key = read_data.key
# fixer.read_key = transform.store_key
fixer.store_key = 'fix_nan'
fixer.logger.log_level = LogLevel.DEBUG
fixer.convert_inconsistent_nans = True
fixer.logger.log_level = LogLevel.DEBUG
fixer.copy_columns_from_df = False
fixer.original_columns = usecols
fixer.var_dtype = cols_dtype
fixer.nan_dtype_map[np.float64] = FNAN

# remove spaces from the cut-column (spaces not handled by correlation-analyser)
fixer.cleanup_string_columns = ['cut']
ch.add(fixer)

ch = Chain('Fact')

# --- 1. add the record factorizer to convert categorical observables into integers
#     By default, the mapping is stored in a dict under key: 'map_'+store_key+'_to_original'
fact = analysis.RecordFactorizer(name='category_factorizer')
fact.columns = cols_str
fact.read_key = fixer.store_key
fact.inplace = True
# factorizer stores a dict with the mappings that have been applied to all observables
fact.sk_map_to_original = 'to_original'
# factorizer also stores a dict with the mappings back to the original observables
fact.sk_map_to_factorized = 'to_factorized'
ch.add(fact)

# --- 2. turn the dataframe into a roofit dataset (= roodataset)
df2rds = ConvertDataFrame2RooDataSet()
df2rds.columns = usecols
df2rds.read_key = fixer.store_key
df2rds.store_key = 'rds_' + fixer.store_key
df2rds.store_key_vars = 'rds_varset'
# the observables in this map are treated as categorical observables by roofit (roocategories)
df2rds.map_to_factorized = 'to_factorized'
# booleans and all remaining numpy category observables are converted to roocategories as well
# the mapping to restore all roocategories is stored in the datastore under this key
df2rds.sk_map_to_original = 'rds_to_original'
# store results in roofitmanager workspace?
# df2rds.into_ws = True
ch.add(df2rds)

# --- here, if the original dataframe is large, delete it and only keep the roodataset
# link = core_ops.DsObjectDeleter()
# link.deletion_keys = [fixer.store_key]
# ch.add(link)

ch = Chain('Hypo')

# --- 3. run the hypothesis tester
# hypotest = dpm.UncorrelationHypothesisTester(results_path=report_path)
# use the standard Eskapade-ROOT 0.8 version
hypotest = UncorrelationHypothesisTester(results_path=report_path)
hypotest.map_to_original = df2rds.sk_map_to_original
hypotest.verbose_plots = True
hypotest.z_threshold = Z_THRESHOLD

# Choose one out of the three options a, b, c
# a. run test for all combinations of columns
hypotest.columns = df2rds.columns[:2]

# b. run test for pairs of observables from two lists
# Make one by one combinations between x and y columns if inproduct = True, otherwise
# make all possible combination.
# hypotest.y_columns = ['Obs_A*'] # ['Obs_A1','Obs_A2', .. ,'Obs_An']
# hypotest.x_columns = ['Obs_B*'] # ['Obs_B1','Obs_B2', .. ,'Obs_Bn']
# hypotest.inproduct = True
# c. Specify exactly for what combinations to run the test
# hypotest.combinations = [['Obs_A1','Obs_B1','Obs_A2'], ['Obs_A2','Obs_B2']]

# read and write keys datastore
hypotest.read_key = df2rds.store_key
hypotest.read_key_vars = df2rds.store_key_vars
hypotest.pages_key = 'report_pages'
hypotest.hist_dict_key = 'histograms'
# key to store the results of the significance test in the datastore
hypotest.sk_significance_map = 'significance'
# key to store the results of the residuals test in the datastore
hypotest.sk_residuals_map = 'residuals'
# key to store the results of the residuals test in the datastore, in format which
# is makes further processing more easy
hypotest.sk_residuals_overview = 'residuals_overview'

# Advanced settings
# Specify what categories to ignore or to limit selection to
# N.B. this only determines for which categories correlations are calculated, the ignored categories
# will still be visible in the correlation-plots.
hypotest.ignore_categories = ignore_categories
hypotest.ignore_values = ignore_values  # nans

# one can also specify specific values to ignore per variable
hypotest.var_ignore_values = var_ignore_values
hypotest.var_ignore_categories = var_ignore_categories

# alternatively, limit values to accept if many categories exist, e.g. for vehicle brand
hypotest.var_accept_categories = var_accept_categories

# Hypothesis tester is also applicable to continuous variables once they are categorised (i.e. divided in bins).
# The number of bins can be set using the following options
hypotest.default_number_of_bins = DEFAULT_NUMBER_OF_BINS
hypotest.var_binning = var_binning
# the following will append var_binning in hypotest with percentile bins evaluated earlier
# (before NaN to float-conversion, see above)
# hypotest.var_binning_key = pb.binning_nameame

hypotest.logger.log_level = log_level_hypotest

# comment these out if you don't want to store the matrices
hypotest.correlation_key = 'correlation_matrix'
hypotest.significance_key = 'significance_matrix'

ch.add(hypotest)

ch = Chain("dashboard")
link = CorrelationFrontend(
    read_key=read_data.key,
    hypotest_chain="Hypo",
    hypotest_link="UncorrelationHypothesisTester",
    residuals_key="residuals",
    columns=usecols,
)
ch.add(link)


# add 1-D histograms to existing report (as created by hypotest-link)
# ch = Chain('Overview')
# if include_histograms:
#     hist_summary = visualization.DfSummary(name='HistogramSummary',
#                                            read_key=hypotest.hist_dict_key,
#                                            pages_key=hypotest.pages_key,
#                                            results_path=report_path
#                                            )
#     ch.add(hist_summary)
#
# # store correlation matrix
# write_corr = analysis.WriteFromDf(name='write_corrmat',
#                                    key=hypotest.correlation_key,
#                                    path=report_path + 'correlation_matrix_motorcycles_train{0:s}.csv'
#                                         .format(report_suffix),
#                                    writer='csv',
#                                    index=True)
# ch.add(write_corr)
#
# # store correlation matrix
# write_sign = analysis.WriteFromDf(name='write_signmat',
#                                    key=hypotest.significance_key,
#                                    path=report_path + 'significance_matrix_motorcycles_train{0:s}.csv'
#                                         .format(report_suffix),
#                                    writer='csv',
#                                    index=True)
# ch.add(write_sign)

#########################################################################################

logger.debug('Done parsing configuration file correlation_analyser')
