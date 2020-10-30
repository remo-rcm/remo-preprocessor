"""Main module."""

from . import workspace
from . import input as inp
from . import process as prc

def init(expid=None, domain=None, root='.'):
    """initialize user workspace.
    """
    workspace.init_workspace(expid, domain, root)


def input(user_config):
    """searches for input files
    """
    inp.get_input(user_config)


def process(user_config):
    """process input files
    """
    prc.process(user_config)
