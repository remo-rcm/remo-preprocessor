"""Main module."""

from . import workspace
from . import input as inp


def init(expid=None, domain=None, root='.'):
    """initialize user workspace.
    """
    workspace.init_workspace(expid, domain, root)


def input(user_config):
    """searches for input files
    """
    inp.get_input(user_config)
