

from datetime import datetime as dt

import os
import sys

from constants import GVars
from cdo import Cdo
import common as cm
import process as proc
import cal
import logging
import exp
from exp import ExpVars
import parallel as prl
import pandas as pd

import output as out
from logging.config import fileConfig

import grid

STEP = 'run'

DOCU = 'run the preprocessing\n'


def initialize_logger(output_dir):
    """initialize the logger configurations

    **Arguments:**
        *outpur_dir:*

    Written by Lars Buntemeyer
    """
    fileConfig(GVars.log_cfg)
    logger = logging.getLogger()


def check_cdo_version():
    cdo = Cdo(logging=True)
    cdo_version = cdo.version()
    logging.info("CDO Version: "+cdo_version)
    if cdo_version == "1.9.8":
        logging.critical("wrong cdo version, see https://code.mpimet.mpg.de/issues/9441")
        logging.critical("your cdo version has a bug concerning the dv2uv operator.")
        raise Exception("wrong cdo version")

def run(args):
    load_config(args.user_config)

def run_static(args):
    exp.load_config(args.user_config)
    if args.date:
        datetime = cm.parse_date(args.date)
    else:
        datetime = ExpVars.timerange[0]
    proc.run_static(datetime)


def run_initial(args):
    exp.load_config(args.user_config)
    if args.date:
        datetime = cm.parse_date(args.date)
    else:
        datetime = ExpVars.timerange[0]
    proc.run_initial(datetime)


def run_parallel(timerange, chunks='MS'):
    logging.info('preparing parallel mode')
    sub_ranges = prl.chunk_ranges(timerange, chunks)
    prl.create_jobscripts(sub_ranges)


def run_dynamic(args):
    check_cdo_version()
    exp.load_config(args.user_config)
    if args.date:
        datetime = cm.parse_date(args.date)
        timerange = (datetime, datetime)
    else:
        timerange = ExpVars.timerange
    if args.parallel:
        run_parallel(timerange, args.chunks)
    else:
        proc.run_dynamic(timerange)
    #datastore.load_datasets(ExpVars.gcm_var_attrs)
    #cal.init_calendar(datastore.ref_ds())
    #map_dynamic = proc.create_mapping()
    #tix = cal.calendar.index_by_datetime(dt(1975,1,1,3))
    #state = proc.remap_dynamic(map_dynamic, timestep=tix)


def init_constants(runHomeDir):
    # init constants and user specifics from environment
    GVars.init(runHomeDir)

    # create some directories
    if not os.path.exists(GVars.logDir):
      os.makedirs(GVars.logDir)
    if not os.path.exists(GVars.scpDir):
      os.makedirs(GVars.scpDir)

    # initialize logger
    logPath  = runHomeDir
    initialize_logger(logPath)
    GVars.log()

    # log python version
    logging.info('Using Python version ' + sys.version)




def run_parser(subparsers):
    """Define the subparser arguments and options"""
    parser_run = subparsers.add_parser(STEP, help=DOCU, epilog=DOCU)

    run_subparsers = parser_run.add_subparsers(dest=STEP, description='Available Sub-Commands')
    # run static processing
    parser_run_static = cm.add_default_parser(run_subparsers, 'static', 'preprocess static fields')
    parser_run_static.set_defaults(func=run_static)
    parser_run_static.add_argument('-d', '--date', dest='date',
            type=str, help='overwite date for initial conditions')

    # run initial conditions processing
    parser_run_initial = cm.add_default_parser(run_subparsers, 'initial', 'preprocess initial conditions')
    parser_run_initial.set_defaults(func=run_initial)
    parser_run_initial.add_argument('-d', '--date', dest='date',
            type=str, help='overwite date for initial conditions')

    # run dynamic processing
    parser_run_dynamic = cm.add_default_parser(run_subparsers, 'dynamic', 'preprocess dynamic fields')
    parser_run_dynamic.set_defaults(func=run_dynamic)
    parser_run_dynamic.add_argument('-d', '--date', dest='date',
            type=str, help='overwite date to preprocess')
    parser_run_dynamic.add_argument('-s', '--submit', dest='submit', action='store_true',
            help='submit to job queue')
    parser_run_dynamic.add_argument('-p', '--parallel', dest='parallel', action='store_true',
            help='submit to job queue')
    parser_run_dynamic.add_argument('-c', '--chunks', dest='chunks', type=str,
            help='chunking for parallel computation, default is MS', default='MS')
