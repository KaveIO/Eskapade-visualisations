"""Project: Eskapade - A python-based package for data analysis.

Macro: dash_builder_macro

Created: 2018-11-16

Description:
   This macro creates a dash app that can be used as a template for other
   data exploration apps. It build a basic setup of two columns, one containing
   controls (or widgets) and one containing a grid of plots.
   Check the dash_tutorial.rst for further details on how to customize.

Authors:
    KPMG Advanced Analytics & Big Data team, Amstelveen, The Netherlands

Redistribution and use in source and binary forms, with or without
modification, are permitted according to the terms listed in the file
LICENSE.
"""

from eskapade import process_manager, Chain, ConfigObject, DataStore
from eskapade.logger import Logger, LogLevel
from eskapade.analysis import ReadToDf

from eskapade_viz.links import DashBuilder
import os
import seaborn as sns

logger = Logger()

logger.debug('Now parsing configuration file dash_builder_macro.')

# --- minimal analysis information

settings = process_manager.service(ConfigObject)
settings['analysisName'] = 'dash_builder_macro'
settings['version'] = 0

settings['filepath'] = settings.get('filepath', '/Users/sgroothuis/Documents/Projecten/Clients/intern/VLA/VisualizationLibraryAnalysis/data/diamonds.csv')

settings['columns'] = ['carat', 'cut', 'color', 'clarity', 'depth', 'table', 'price', 'x', 'y', 'z']
# settings['columns'] = ['total_bill', 'tip', 'sex', 'smoker', 'day', 'time', 'size']
settings['options'] = [{"label":c.capitalize(), 'value':c} for c in settings['columns']]
settings['options_filter'] = [{"label":c.capitalize(), 'value':c} for c in settings['columns'][:3]]
# settings['options_filter'] = [{"label":c.capitalize(), 'value':c} for c in ['sex', 'smoker', 'day', 'time', 'size']]


# --- now set up the chains and links
print(settings['filepath'])
ch = Chain('load_data')
link = ReadToDf(path=settings['filepath'],
                key='df',
                reader='csv')

link.logger.log_level = LogLevel.DEBUG
ch.add(link)


ch = Chain('Start')
link = DashBuilder(read_key='df',
                   store_key='app',
                   figure_strings=['Histogram','Histogram','Scatter'],
                   control_strings = [dict(name='Dropdown', args={'options':settings['options'],'value':None, 'id':'dropdown_0'}),
                                      dict(name='Slider', args=dict(min=0, max=100, value=50, step=1, id="slider_0")),
                                      dict(name='Dropdown', args={'options':settings['options'],'value':None, 'id':'dropdown_1'}),
                                      dict(name='Slider', args=dict(min=0, max=100, value=50, step=1, id="slider_1")),
                                      dict(name='Dropdown', args={'options':settings['options'],'value':None, 'id':'dropdown_2'}),
                                      dict(name='Dropdown', args={'options':settings['options'],'value':None, 'id':'dropdown_3'})],
                   app_title='Dash Demo',
                   filter_controls=[dict(name='Dropdown', args={'options':settings['options_filter'],'value':None,
                                                                 'id':'filter_dropdown'})])
link.logger.log_level = LogLevel.DEBUG
ch.add(link)

logger.debug('Done parsing configuration file dash_builder_macro.')
