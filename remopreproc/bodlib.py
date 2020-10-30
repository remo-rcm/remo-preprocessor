


from .dataset import NC4Dataset
from . import filemanager as fm
import logging

from .constants import GVars



def get_bodlib(bodlib):
    logging.info('loading bodlib: {}'.format(bodlib))
    return fm.get_bodlib(bodlib)


def field_by_code(dataset, code):
    for varname, ncvar in dataset.variables.items():
        if 'code' in ncvar.ncattrs():
            return ncvar
        elif str(code).zfill(3) in varname:
            return ncvar
    logging.warning('could not find code {} in bodlib {}!'.format(code, dataset.filepath()))
    return None


def get_static_variables(bodlib, varnames):
    static_vars = {}
    var_attrs = GVars.var_attrs
    for varname in varnames:
        if varname in bodlib.variables:
            static_vars[varname] = bodlib.variables[varname]
        else:
            static_vars[varname] = field_by_code(bodlib, var_attrs[varname]['attributes']['code'])
    return static_vars

