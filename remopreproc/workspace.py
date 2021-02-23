

import os
import sys
import logging

from . import config
from . import utils

logger = logging.getLogger(__name__)


WORK = os.getenv('WORK')
SCRATCH = os.getenv('SCRATCH')


def init_dir(user_config, root='.'):
    """initialize user work directory and write config file
    """
    expid = user_config['expid']
    workDir = os.path.abspath(os.getcwd())
    logger.debug('current directory: ' + workDir)
    basedir = os.path.join(workDir, expid)
    os.makedirs(basedir)
    configfile = os.path.join(basedir, 'config.yaml')
    #os.makedirs(os.path.join(basedir, config.LOG_DIR))
    utils.write_yaml(user_config, configfile)
    Workspace.init(configfile)
    Workspace.makedirs()

def init_user_config(**kwargs):
    """initialize user config file.
    """
    user_config = config.user_config_default.copy()
    user_config.update(kwargs)
    return user_config

def init_workspace(expid, domain, root):
    """initialize user workspace.
    """
    user_config = init_user_config(expid=expid, domain=domain)
    init_dir(user_config, root)
    logger.info('WORK: {}'.format(WORK))
    logger.info('SCRATCH: {}'.format(SCRATCH))


class Workspace():

    work = os.getenv('WORK')
    scratch = os.getenv('SCRATCH')
    dflt_expid = '000000'

    dirs = []

    @staticmethod
    def staticmethod():
        pass

    @classmethod
    def init(cls, configfile):
        cls.user_config = configfile
        #self.configfile = os.path.join(GVars.runHomeDir,configfile)
        cls.configfile = configfile
        logging.info('configfile: {}'.format(configfile))
        cls.configdir  = os.path.dirname(cls.configfile)
        cls.config     = utils.get_yaml(cls.configfile)
        cls.logdir     = os.path.join(cls.configdir, 'log')
        cls.jobdir     = os.path.join(cls.configdir, 'job')
        cls.dirs.append(cls.logdir)
        cls.dirs.append(cls.jobdir)

    @classmethod
    def makedirs(cls):
        for dir in cls.dirs:
            os.makedirs(dir)
