

import os
import sys
import logging

from . import config
from . import utils

logger = logging.getLogger(__name__)


WORK = os.getenv('WORK')
SCRATCH = os.getenv('SCRATCH')


def init_dir(user_config, root='.'):
    """initialize user work directory.
    """
    expid = user_config['expid']
    workDir = os.path.abspath(os.getcwd())
    logger.debug('current directory: ' + workDir)
    basedir = os.path.join(workDir, expid)
    os.makedirs(os.path.join(basedir, config.LOG_DIR))
    utils.write_yaml(user_config, os.path.join(basedir, 'config.yaml'))

def init_user_config(**kwargs):
    """initialize user config file.
    """
    user_config = config.user_config_default.copy()
    user_config.update(kwargs)
    return user_config

def init_workspace(expid, root):
    """initialize user workspace.
    """
    user_config = init_user_config(expid=expid)
    init_dir(user_config, root)
    logger.info('WORK: {}'.format(WORK))
    logger.info('SCRATCH: {}'.format(SCRATCH))
