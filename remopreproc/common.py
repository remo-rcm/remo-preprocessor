
import os
import logging
from configobj import ConfigObj
import shutil
import argparse
import datetime as dt

import yaml

import cftime

from constants import DATE_FMT as date_fmt

def print_datinfo(name, data):
    logging.debug('{:10} - min: {}, max: {}'.format(name, data.min(), data.max()))
    logging.debug('{:10} - shape: {}'.format(name, data.shape))
    logging.debug('{:10} - type: {}'.format(name, type(data)))


def parse_date(datetime):
    return dt.datetime.strptime(datetime, date_fmt)


class StoreDictKeyPair(argparse.Action):
    """Converts command line argument to dict.

    **Arguments:**

    Written byLars Buntemeyerr
    """
    def __call__(self, parser, namespace, values, option_string=None):
         my_dict = {}
         print(values)
         for kv in values:
             k,v = kv.split("=")
             my_dict[k] = v
         setattr(namespace, self.dest, my_dict)



def get_file_logger(logfile,level=logging.WARNING):
    logger = logging.getLogger('remo-cmor')
    hdlr = logging.FileHandler(logfile)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)
    return logger


def get_yaml(filename):
    logging.info('reading: {}'.format(filename))
    return yaml.load(open(filename), Loader=yaml.FullLoader)


def get_config(config_file, validator=None,stringify=False,silent=False,unrepr=False):
    if os.path.isfile(config_file):
      if not silent: logging.info('Reading: '+str(config_file))
      configObj = ConfigObj(config_file,configspec=validator,stringify=stringify,unrepr=unrepr)
    else:
      logging.error('File does not exist: '+str(config_file))
      raise Exception('Config File does not exists: '+str(config_file))
    return configObj

def create_dir(path,force=False):
    created = False
    if not (os.path.exists(path)):
      logging.info('Creating Directory: '+str(path))
      os.makedirs(path)
      created = True
    else:
      logging.warning('Directory already exists: '+str(path))
      created = False
      if(force):
       logging.warning('Removing: '+str(path))
       shutil.rmtree(path) 
       logging.info('Creating Directory: '+str(path))
       os.makedirs(path)
       created = True
    return created

def create_dirs(dirs,force=False):
    for path in dirs:
       create_dir(path,force)


def log_dict(dictionary, indent=None, n=None):
    if indent is None:
        indent = 2*'  '
    if n is None:
        n = 0
    for key, value in dictionary.items():
        if type(value) is dict or isinstance(value, ConfigObj):
            logging.info(n*indent+str(key))
            log_dict(value, indent=indent, n=n+1)
        else:
            logging.info(n*indent+str(key)+' : '+str(value))


def cfg_has(dictionary,sect,key):
    result = False
    if sect in dictionary.sections:
      if key in dictionary[sect].keys():
        result = True
    return result


def check_file(filename,fatal=False):
    found = False
    if os.path.isfile(filename): 
      found = True
      logging.debug('found file: '+filename)
    else:
      found = False
      logging.warning('could not find file: '+filename)
      if fatal:
        logging.error('file is required: '+filename)
        raise Exception('could not find file: '+filename)
    return found





def add_config_argument(parser):
    parser.add_argument(
        'user_config', help="user's configuration file")

def add_variable_argument(parser):
    parser.add_argument(
        '-v', '--variable', dest='variable', nargs='+', type=str, help='variable name')

def add_default_parser(parser, name, help):
    subparser = parser.add_parser(name, help=help)
    add_config_argument(subparser)
    add_variable_argument(subparser)
    return subparser




