

from netCDF4 import Dataset
import numpy as np

import logging

from .variable import Variable, Set


ak_varname = 'ap_bnds'
bk_varname = 'b_bnds'

data_prec = 'f8'
dim_prec  = 'f8'


class FileReader(object):

    def __init__(self, filename):
        self.filename = filename


class FileWriter(object):
    """The :class:`FileWriter` manages forcing output files.

    It can create and write netcdf files using a :class:`Variable` object.

    **Arguments:**
        - **filename (str):**
            Filename of the output file.
        - **reffile  (str):**
            Filename of a reference file from which to copy
            netcdf attributes.

    Written by Lars Buntemeyer
    """
    def __init__(self, filename, ncattrs=None):
        self.filename = filename
        self.file     = Dataset(filename, mode='w')
        if ncattrs: self._def_ncattrs(ncattrs)

    def _def_ncattrs(self, ncattrs):
        """Defines nc attribtues by copying them from a reference file. This
        is used for keeping original input data netcdf attributes in the output 
        forcing file.

        **Arguments:**
            - **reffile  (str):**
                Filename of a reference file from which to copy
                netcdf attributes.
        """
        for key, value in ncattrs.items():
            self.file.setncattr(key, value)
            logging.debug('setting {:<30}:    {}'.format(key, value))

    def def_dims(self, grid):
        """Defines dimensions for a forcing file.

        **Arguments:**
            - **grid  (:class:`Grid`):**
                Grid object that holds dimensional information.

        """
        rlon_dim = self.file.createDimension('rlon', len(grid.rlon))
        rlat_dim = self.file.createDimension('rlat', len(grid.rlat))
        lev_dim  = self.file.createDimension('lev',  grid.nlev)
        rlon = self.file.createVariable('rlon', dim_prec, 'rlon')
        rlat = self.file.createVariable('rlat', dim_prec, 'rlat')
        lev  = self.file.createVariable('lev', dim_prec, 'lev')
        lon = self.file.createVariable('lon', dim_prec, ('rlat','rlon'))
        lat = self.file.createVariable('lat', dim_prec, ('rlat','rlon'))
        rlon[:] = grid.rlon
        rlat[:] = grid.rlat

    def def_ncvar(self, dst, src):
        """Defines a netcdf variable from a :class:`Variable` object.

        **Arguments:**
            - **var  (:class:`Variable`):**
                Variable object that holds meta information.

        """
        if src.threeD:
            ncvar = self.file.createVariable(dst.name, data_prec, ('lev','rlat','rlon'))
        else:
            ncvar = self.file.createVariable(dst.name, data_prec, ('rlat','rlon'))
        return ncvar

    def write_var(self, var, data):
        var.ncvar[:] = data


def create_file_writer(filename, grid, ncattrs=None):
    fw = FileWriter(filename, ncattrs)
    fw.def_dims(grid)
    return fw


def get_var_data(filename, varname, timestep=None):
    """Reads data from a netcdf file using a certain timestep if required.
    """
    logging.info('reading: {}'.format(filename))
    logging.debug('reading: {}'.format(varname))
    nc  = Dataset(filename, mode='r')
    var = nc.variables[varname]
    if timestep is not None:
        logging.info('returning timestep',timestep)
        return var[timestep]
    else:
        return var


def put_var_data(filename, varname, timestep=None):
    pass

def get_vc(filename):
    nc  = Dataset(filename)
    ak_bnds = nc.variables[ak_varname]
    bk_bnds = nc.variables[bk_varname]
    kegm = ak_bnds.shape[0]
    akgm = np.zeros([kegm+1], dtype=np.float64, order='F')
    bkgm = np.zeros([kegm+1], dtype=np.float64, order='F')
    akgm[1:] = ak_bnds[:,1]
    bkgm[1:] = bk_bnds[:,1]
    return (akgm, bkgm)



def read_era_interim(filename, varname):
    nc = Dataset(filename)
    var = nc.variables[varname]
    print(var)
    data = np.asfortranarray(var[0,:,:,:])
    return data

def read_grid(filename):
    nc = Dataset(filename)
    lat = nc.variables['lat']
    lon = nc.variables['lon']
    return lat, lon


def read_variables(filename, table):
    """Initializes the variable list
    """
    variables = {}
    for varname,info in table.items():
        logging.info('reading variable: {}'.format(varname))
        variable = Variable(varname)
        for attr in info:
            setattr(variable, attr, info[attr])
        variable.ncvar = get_var_data(filename, variable.src)
        variables[varname] = variable
    return variables


def write_variables(filename, table):
    pass


def copy_ncattrs(source, target):
    for name in source.ncattrs():
        target.setncattr(name, source.getncattr(name))

def copy_varattrs(target, variable):
    x = target.createVariable(name, variable.datatype, variable.dimensions)
    for attr in variable.ncattrs():
        target.variables[name].setncattr(attr, variable.getncattr(attr))


def copy_nc_file(source, destination='copy.nc'):
    dst = nc.Dataset(destination,'w')
    src = nc.Dataset(source)
    # copy attributes
    for name in src.ncattrs():
        dst.setncattr(name, src.getncattr(name))
    # copy dimensions
    for name, dimension in src.dimensions.items():
        print(name)
        print(len(dimension))
        print(dimension.isunlimited())
        dst.createDimension(
            name, (len(dimension) if not dimension.isunlimited() else None))
        # copy all file data except for the excluded
    for name, variable in src.variables.items():
        print(name)
        x = dst.createVariable(name, variable.datatype, variable.dimensions)
        for attr in variable.ncattrs():
            dst.variables[name].setncattr(attr, variable.getncattr(attr))
        if variable.shape:
            dst.variables[name][:] = src.variables[name][:]
    return dst
