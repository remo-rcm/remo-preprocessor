"""Main module."""

from . import workspace


def init(expid='000000', root='.'):
    workspace.init_workspace(expid, root)



