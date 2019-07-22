"""Project: Eskapade - A _python-based package for data analysis.

Macro: df_summary_macro

Created: 2018-11-08

Description:
    This Macro recreates the df_summary has an interactive
    dash app. It uses the DfSummaryDash link which will display a set of
    plots (2 histograms and a scatter plot) to be used to explore the
    data.

Authors:
    KPMG Advanced Analytics & Big Data team, Amstelveen, The Netherlands

Redistribution and use in source and binary forms, with or without
modification, are permitted according to the terms listed in the file
LICENSE.
"""

import os
from eskapade import process_manager, Chain, ConfigObject
from eskapade.logger import Logger, LogLevel
from eskapade.analysis.links import ReadToDf
from eskapade_viz import links

logger = Logger()

logger.debug('Now parsing configuration file df_summary_macro.')

# --- minimal analysis information


settings = process_manager.service(ConfigObject)
settings['analysisName'] = 'df_summary_macro'
settings['version'] = 0

settings['base_path'] = settings.get('base_path', os.path.dirname(links.__file__))
settings['filepath'] = settings.get('filepath', os.path.join(settings['base_path'], '../../../data/planets_clean.csv'))


# --- now set up the chains and links
ch = Chain('load_data')

print()

link = ReadToDf(path=settings['filepath'],
                key='data',
                reader='csv')

link.logger.log_level = LogLevel.DEBUG
ch.add(link)


ch = Chain("make_dash")
link = links.DfSummaryDash(read_key='data',
                           app_store_key='app',
                           label_key='pdict',
                           col_key='columns',
                           hue_key='hue',
                           stats_key='stats',
                           assets_path=os.path.join(settings['base_path'], '../../../macros/assets/'),
                           hue_cols=['pl_hostname', 'pl_letter', 'pl_discmethod', 'pl_pnum', 'st_sp', 'pl_disc_reflink',
                                     'pl_locale', 'pl_facility', 'pl_telescope', 'pl_instrument', 'pl_mnum']
                           )
link.logger.log_level = LogLevel.DEBUG
ch.add(link)

logger.debug('Done parsing configuration file df_summary_macro.')
