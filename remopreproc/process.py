
from configobj import ConfigObj
import logging



import tempfile

import numpy as np

#from pyintorg import grid as pygd
#from pyintorg import variable as var
#from pyintorg import file_io as fio, mapping as pyintmap
#from pyintorg import interface as intf
#from pyintorg import physics

from datetime import datetime as dt

#from state import atmo_state as atmo
from .state import State
from . import grid as gd
from . import variable as var
from . import filemanager as fm
from . import ocean as sst
from . import mapping
from . import static_data as sd
from . import output as out
from . import cal
from . import physics
#from datastore import datastore
from . import datastore as ds
import os
from . import input
from . import tables as tbl
from . import bodlib as bdl
from . import parallel as prl

import pandas as pd

from .catalog import Intake

from . import common as cm

from .exp import ExpVars
from . import exp
#from .constants import GVars

from cdo import Cdo

from netCDF4 import Dataset

#from scipy.interpolate import RegularGridInterpolator


STEP = 'process'

DOCU = 'process the global data\n'\


#def interpolate_ocean(ds):
#    interpolating_function = RegularGridInterpolator((x, y, z), data)

def check_cdo_version():
    cdo = Cdo(logging=True)
    cdo_version = cdo.version()
    logging.info("CDO Version: "+cdo_version)
    if cdo_version == "1.9.8":
        logging.critical("wrong cdo version, see https://code.mpimet.mpg.de/issues/9441")
        logging.critical("your cdo version has a bug concerning the dv2uv operator.")
        raise Exception("wrong cdo version")

def get_output_path():
    if 'path' in ExpVars.config['output']:
        return ExpVars.config['output']['path']
    else:
        return os.path.join(GVars.scratch,'intorg',ExpVars.config['experiment']['id'])


def do_timestep(map_dynamic, date, ocean_to_atmo, map_aux=None):
    #date  = cal.calendar.datetime_by_index(ti)
    #logging.info('timestep: {} - {}'.format(ti, date))
    logging.info('timestep: {}'.format(date))
    # remape primary dynamic variables
    aux = {}
    if map_aux:
        aux    = remap_aux(map_aux, timestep=date)
    atmos  = remap_atmos(map_dynamic, timestep=date)
    ocean  = remap_ocean(date, ExpVars.domain, ocean_to_atmo)

    state = {**aux, **atmos, **ocean}
    state = {**atmos, **ocean, **aux}

    logging.info('remapped data: {}'.format(state.keys()))

    state = add_physics(state)

    output = {varname: state[varname] for varname in ExpVars.config['output']['variables']}

    out.output.write_date(date, output)
    #out.output.write_date(date, sd.static_state)



def add_physics(state):
    """derive additional fields.
    """
    state = physics.ocean_physics(state)
    #state = physics.soil_layers(state)
    state = physics.water_content(state)
    return state


def run_static(datetime):
    bodlib_filename = ExpVars.config['input']['bodlib']
    static_vars = ExpVars.config['output']['static']
    bodlib = bdl.get_bodlib(bodlib_filename)
    static_vars = bdl.get_static_variables(bodlib, static_vars)
    print(static_vars)


def run_initial(datetime):
    bodlib_filename = ExpVars.config['input']['bodlib']
    bodlib = bdl.get_bodlib(bodlib_filename)
    logging.info('creating initial conditions for {}'.format(datetime))
    datastore = init_datastore()
    mapping = create_mapping_initial(datastore)
    remap_aux_fields(mapping, datetime)


def run_dynamic(timerange):
    check_cdo_version()
    ds.datastore = init_datastore()
    datastore = ds.datastore
    map_aux = create_aux_mapping(datastore)
    #print(map_aux)
    cal.init_calendar(datastore.ref_ds())
    init_static_data(datastore)
    init_output(timerange[0])
    map_dynamic = create_mapping(datastore)
    try:
        ocean_to_atmo = ExpVars.config_input_data['ocean']['to_atmo']
    except:
        ocean_to_atmo = True
    date_range = pd.date_range(timerange[0], timerange[1], freq='6h')
    old_date = date_range.min()
    for date in pd.date_range(timerange[0], timerange[1], freq='6h'):
        if date.month > old_date.month:
            out.output.archive(old_date)
        do_timestep(map_dynamic, date, ocean_to_atmo, map_aux)
        old_date = date

def init_static():
    init_static_data()

def init_datastore():
    ds_type = ExpVars.config_input_data['dataset']
    tables = input.read_input_tables(list(ExpVars.gcm_var_attrs.keys()))
    datastore = ds.create_datastore(tables, ds_type)
    ds.datastore = datastore
    logging.debug('datastore keys: {}'.format(datastore.dataset.keys()))
    return datastore

def init_output(startdate):
    #id = ExpVars.config['experiment']['id']
    id = ExpVars.config['expid']
    #startdate = cal.calendar.convert_to_cftime(startdate)
    out_path = get_output_path()
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    out.init_output(id, out_path, startdate, ExpVars.domain)

def init_static_data(datastore):
    """Load static data.

    Loads static data from the surface library and the global data
    set and interpolates it to the regional grid.

    """
    bodlib = ExpVars.config['input']['bodlib']
    domain = ExpVars.domain
    sd.bodlib.load_bodlib(bodlib)
    sd.bodlib.load_static(datastore)
    sd.bodlib = sd.interpolate_static(sd.bodlib, domain)
    # save static data for output
    sd.static_state['FIB'] = sd.bodlib.fibem * 0.10197
    sd.static_state['BLA'] = sd.bodlib.blaem
    #sd.static_state['FIBGE'] = sd.static_data.fibge
    #sd.static_state['BLAGE'] = sd.static_data.blage

    #for field, attrs in GVars.stcvars.items():
    # add all other fields from the bodlib
    for field, attrs in tbl.bodlib.items():
        print('adding: {}'.format(field))
        ncvar = sd.bodlib.field_by_code(attrs['attributes']['code'])
        if ncvar:
            sd.bodlib[field] = ncvar[:].T
        else:
            raise Exception('could not find {} ({}) in bodlib'.format(field, attrs['attributes']['code']))


def create_mapping(datastore):
    #mapping_file  = ExpVars.config['mapping']['map']
    #table = ConfigObj(mapping_file)
    table = tbl.mapping #ConfigObj(mapping_file)
    dataset_dict = datastore
    domain = ExpVars.domain
    mapping_table = mapping.mapping_table_dynamic(dataset_dict, table, domain)

    return mapping_table


def create_aux_mapping(datastore):
    #mapping_file  = tables.mapping #ExpVars.config['mapping']['map']
    #print(mapping_file)
    table = tbl.mapping #ConfigObj(mapping_file)
    print(table)
    domain = ExpVars.domain
    if ExpVars.aux_vars:
        return mapping.mapping_table_aux(datastore, ExpVars.aux_vars, table, domain)
    else:
        return None

def create_mapping_initial(datastore):
    mapping_file  = ExpVars.config['mapping']['map']
    table = ConfigObj(mapping_file)
    domain = ExpVars.domain
    initial_vars = ExpVars.config['output']['initial']
    init_mapping = mapping.create_mapping_table(datastore, initial_vars, table, domain)
    return init_mapping

def remap_atmos(mapping_table, timestep):
    return mapping.remap_dynamic(mapping_table, timestep)

def remap_aux(mapping_table, timestep):
    return mapping.remap_aux_fields(mapping_table, timestep)

def remap_ocean(date, domain, to_atmo=True):
    return mapping.remap_ocean(date, domain, to_atmo)

#def process(args):
#    ExpVars.init(args.user_config)
#    ExpVars.log()
#    run(0)

def process(user_config, date=None, parallel=False):
    exp.load_config(user_config)
    if date:
        date = cm.parse_date(date)
        timerange = (date, date)
    else:
        timerange = ExpVars.timerange
    if parallel:
        run_parallel(timerange)
    else:
        run_dynamic(timerange)


def run_parallel(timerange, chunks='MS'):
    logging.info('preparing parallel mode')
    sub_ranges = prl.chunk_ranges(timerange, chunks)
    scheduler = prl.create_jobscripts(sub_ranges)
    scheduler.submit()



def process_parser(subparsers):
    """Define the subparser arguments and options"""
    parser_process = subparsers.add_parser(STEP, help=DOCU, epilog=DOCU)
    parser_process.add_argument("user_config", help="user's configuration file")
    parser_process.add_argument('-v', '--variable', dest='variable', nargs='+', 
            type=str, help='overwite variable list from config file')
    parser_process.set_defaults(func=process)
