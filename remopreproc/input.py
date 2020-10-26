"""input module deals with finding files and managing tables.
"""
from . import common as cm
import logging
from . import exp
import os
from .exp import ExpVars
from .constants import GVars

from . import constants as const

from . import datastore as ds
from .catalog import Intake

import pandas as pd

STEP = 'input'
DOCU = 'collect input tables'

file_format = '{}.csv'


def find_input_files(catalog, var_attrs):
    """search a catalog for variable attributes.
    """
    dataframes = {}
    for key, attrs in var_attrs.items():
        logging.info('search catalog for: {}'.format(attrs))
        df = catalog.df(**attrs)
        print(df)
        if df.empty:
            logging.warning('!!! -> input search returned no results, check your attributes!!!')
        dataframes[key] = df
    return dataframes


def write_input_tables(dataframes):
    """writes csv input tables from a catalog search
    """
    for varname, df in dataframes.items():
        filename = os.path.join(ExpVars.configdir, file_format.format(varname))
        logging.info('writing table for {} to {}'.format(varname, filename))
        if df.empty:
            logging.warning('table for {} is empty!'.format(varname))
        df.to_csv(filename, index=False)


def read_input_tables(varnames):
    """reads csv input tables from a former catalog search
    """
    dataframes = {}
    for varname in varnames:
        filename = os.path.join(ExpVars.configdir, file_format.format(varname))
        logging.info('reading table for {} from {}'.format(varname, filename))
        df = pd.read_csv(filename)
        dataframes[varname] = df
    return dataframes


def create_input_tables():
    """creates input tables from a catalog search.
    """
    url = ExpVars.config_input_data['catalog']['url']
    sort_by = ExpVars.config_input_data['catalog'].get('sort_by', None)

    catalog = Intake(url, sort_col=sort_by)
    input_files = find_input_files(catalog, ExpVars.gcm_var_attrs)
    write_input_tables(input_files)


def collect_input(user_config):
    """main driver for finding input files
    """
    exp.load_config(user_config)
    create_input_tables()

def get_input(user_config):
    config_file = cm.get_abs_path(user_config)
    logging.info('user_config: {}'.format(config_file))
    logging.debug('current directory: {}'.format(const.CUR_DIR))
    exp.load_config(user_config)
    create_input_tables()

def input_parser(subparsers):
    """Define the subparser arguments and options"""
    parser_input = cm.add_default_parser(subparsers, STEP, help=DOCU)
    parser_input.set_defaults(func=collect_input)
