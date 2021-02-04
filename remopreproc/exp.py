

import os
import socket
import logging
from configobj import ConfigObj
import datetime as dt

from . import grid as gd
from . import tables

import yaml

import pandas as pd

from .constants import GVars
from . import common as cm
from .constants import DATE_FMT as date_fmt

from pyremo2 import vc

def parse_timerange(range):
    split = range.split('/to/')
    return (cm.parse_date(split[0]), cm.parse_date(split[1]))

def load_config(user_config):
    ExpVars.init(user_config)
    ExpVars.log()

class ExpClass:
    """Stores Experiment config variables (visible to most of the code).

    There should only be one global instance of this class holding information
    about the input data and preprocessing configuration.
    """
    def init(self, configfile):
        # we should always use absolute pathes, it's safer
        # constant directory names
        # read in and store the main configuration
        self.user_config = configfile
        #self.configfile = os.path.join(GVars.runHomeDir,configfile)
        self.configfile = configfile 
        self.configdir  = os.path.dirname(self.configfile)
        self.config     = cm.get_yaml(self.configfile)

        self.userid  = os.getenv('USER')
        self.scratch = os.getenv('SCRATCH')
        self.work    = os.getenv('WORK')
        self.home    = os.getenv('HOME')
        self.host    = socket.gethostname()
        # this should be obsolete soon.
        #self.config['namelist']['file'] = os.path.join(GVars.usrDir, self.config['namelist']['file'] )
        #self.config['mapping']['map'] = os.path.join(GVars.mapDir, self.config['mapping']['map'] )
        # this stores the input yaml chosen by the user in a dictionary
        self.init_input_config()
        # parse the timerange chosen by the user into datetime objects.
        self.timerange = parse_timerange(str(self.config['processing']['timerange']))
        # read in the vertical coordinate table chosen by the user
        #self.vc_table  = pd.read_csv(os.path.join(GVars.vctDir, self.config['grid']['vc_table']))
        self.vc_table  = vc.table(self.config['grid']['vc_table']) 
        # load remo domain from pyremo
        self.domain     = gd.load_domain(self.config['grid']['domain'])
        # create a dictionary from the input dynamic variables chosen by the user
        self.gcm_var_attrs = self.init_var_attrs(self.config_input_data['processing']['variables'])
        # create a dictionary from the input static variables chosen by the user
        self.gcm_static_attrs = self.init_var_attrs(self.config_input_data['processing']['static'])
        # create a dictionary from the input static variables chosen by the user
        self.aux_vars = self.config_input_data['processing'].get('aux', [])
        if self.aux_vars:
            self.gcm_aux_var_attrs = self.init_var_attrs(self.aux_vars)


    def init_input_config(self):
        # store input yaml chosen by the user
        self.config_input_filename = os.path.join(tables.input_gcm_path, self.config['input']['dataset'])
        # derive input project from basename of the directory
        self.config_input_project = os.path.basename(os.path.dirname(self.config_input_filename))
        self.config_input_project_filename = os.path.join(os.path.dirname(self.config_input_filename), self.config_input_project+'.yaml')
        self.config_input_project_data = cm.get_yaml(self.config_input_project_filename)
        # combine defaults from project data and input dataset
        self.config_input_data = { **self.config_input_project_data, **cm.get_yaml(os.path.join(tables.input_gcm_path, self.config['input']['dataset']))}
        print(type(self.config_input_data))


    def init_var_attrs(self, varnames):
        """creates a dictionary of variable attributes.

        The variable attributes are a combination of default attributes that are valid
        for all variables (e.g. of an input gcm) and variable specific attributes from
        the input yaml file in the `input` directory.
        """
        input_var_attrs = {}
        default = self.config_input_data['attributes']
        return {var : {**default, **attrs} for var, attrs in self.config_input_data['variables'].items()}

    def log(self):
        logging.info("USERID  :   {}".format(self.userid))
        logging.info("SCRATCH :   {}".format(self.scratch))
        logging.info("WORK    :   {}".format(self.work))
        logging.info("---------- user's config -----------")
        cm.log_dict(dict(self.config))
        logging.info("---------- config of input data ----")
        cm.log_dict(self.config_input_data)
        logging.info("---------- variable attributes ----")
        cm.log_dict(self.gcm_var_attrs)


ExpVars = ExpClass()
