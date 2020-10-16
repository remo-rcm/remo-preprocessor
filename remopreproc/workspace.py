

import os
import sys
import logging


logger = logging.getLogger(__name__)


WORK = os.getenv('WORK')
SCRATCH = os.getenv('SCRATCH')


def init_dir(expid, root='.'):
    runHomeDir = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
    workDir = os.path.abspath(os.getcwd())
    print(runHomeDir)
    print(workDir)

def init_workspace(expid, root):
    init_dir(expid, root)
    logger.info('WORK: {}'.format(WORK))
    logger.info('SCRATCH: {}'.format(SCRATCH))

