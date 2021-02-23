"""Main module."""

from . import workspace
from . import input as inp
from . import process as prc
from . import constants as const


def init(expid=None, domain=None, root='.'):
    """initialize user workspace.
    """
    workspace.init_workspace(expid, domain, root)


def input(user_config):
    """searches for input files
    """
    inp.get_input(user_config)


def process(user_config, date, parallel):
    """process input files
    """
    #const.GVars.init('')
    workspace.Workspace.init(user_config)
    prc.process(user_config, date, parallel)
