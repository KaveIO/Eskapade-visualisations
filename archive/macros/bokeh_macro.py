"""Project: Eskapade - A _python-based package for data analysis.

Macro: bokeh_macro.py

Created: 2018-11-09

Description:
    This macro will make a small demonostration of a df-summary app
    using bokeh

Authors:
    KPMG Advanced Analytics & Big Data team, Amstelveen, The Netherlands

Redistribution and use in source and binary forms, with or without
modification, are permitted according to the terms listed in the file
LICENSE.
"""

from eskapade import process_manager, Chain, ConfigObject
from eskapade.logger import Logger, LogLevel
from eskapade.analysis.links import ReadToDf

from eskapade_viz.links import DfSummaryBokeh

logger = Logger()

logger.debug('Now parsing configuration file bokeh_macro.')

# --- minimal analysis information

settings = process_manager.service(ConfigObject)
settings['analysisName'] = 'bokeh_macro'
settings['version'] = 0

# --- now set up the chains and links

ch = Chain('load_data')
link = ReadToDf(path='../data/planets.csv', skiprows=79, key='data')
ch.add(link)

ch = Chain('viz')
link = DfSummaryBokeh(read_key='data')
ch.add(link)

logger.debug('Done parsing configuration file bokeh_macro.py.')
