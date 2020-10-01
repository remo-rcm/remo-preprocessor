

import logging

from cordex import ESGF
#from cordex.dataset import NC4Dataset, NC4MFDataset, XRDataset
from exp import ExpVars
from netCDF4 import Dataset, MFDataset, date2index, num2date, date2num
import xarray
import intake
from datetime import datetime
import pprint
import numpy as np

import common as cm

from cal import AbsoluteCalendar

from cdo import Cdo

#from PyRemo.OoPlot.DataFile import IegFile

ak_valid = ['ap_bnds','a_bnds', 'hyai']
bk_valid = ['b_bnds', 'hybi']

lon_valid = ['lon', 'longitude', 'nav_lat']
lat_valid = ['lat', 'latitude', 'nav_lon']

data_prec = 'f8'
dim_prec  = 'f8'



def get_bodlib(filename):
    logging.info('reading {}'.format(filename))
    cdo = Cdo()
    return cdo.copy(input=filename, returnCdf = True)


def get_lonlat_2d(dataset):
    """lon lat to radiants
    """
    lon, lat = get_lonlat(dataset)
    #lat = np.flip(lat)
    cm.print_datinfo('lon', lon)
    cm.print_datinfo('lat', lat)
    if len(lon.shape) == 2 and len(lat.shape == 2):
        logging.debug('found 2d coordinates')
        return lon.T * 1.0/57.296, lat.T * 1.0/57.296
    else:
        logging.debug('creating 2d coordinates')
        lon2d = np.stack([lon]*lat.size).T * 1.0/57.296
        lat2d = np.tile(lat, (lon.size,1)) * 1.0/57.296
        cm.print_datinfo('lon2d', lon2d)
        cm.print_datinfo('lat2d', lat2d)
        return lon2d, lat2d


def find_valid_variable(dataset, valid):
    found = None
    for ncvar in valid:
        if ncvar in dataset.variables:
            found = ncvar
            logging.debug('found: {}'.format(found))
    if found:
        return dataset.variables[found]
    else:
        raise Exception('could not find any of: {}'.format(valid))

def get_lonlat(dataset):
    lon = find_valid_variable(dataset, lon_valid)
    lat = find_valid_variable(dataset, lat_valid)
    return lon[:], lat[:]


def get_vc(dataset, flip=False):
    """Reads the vertical hybrid coordinate from a dataset.
    """
    ak_bnds = None
    bk_bnds = None
    for ak_name in ak_valid:
        if ak_name in dataset.variables:
            ak_bnds = dataset.variables[ak_name]
            logging.info('using {} for akgm'.format(ak_name))
    for bk_name in bk_valid:
        if bk_name in dataset.variables:
            bk_bnds = dataset.variables[bk_name]
            logging.info('using {} for bkgm'.format(bk_name))
    if not all([ak_bnds, bk_bnds]):
        logging.error('could not identify vertical coordinate, tried: {}, {}'.format(ak_valid, bk_valid))
        raise Exception('incomplete input dataset')
    nlev = ak_bnds.shape[0]
    ak = np.zeros([nlev+1], dtype=np.float64)
    bk = np.ones([nlev+1], dtype=np.float64)
    if flip:
        ak[:-1] = np.flip(ak_bnds[:,1])
        bk[:-1] = np.flip(bk_bnds[:,1])
    else:
        ak[1:] = np.flip(ak_bnds[:,1])
        bk[1:] = np.flip(bk_bnds[:,1])
    logging.debug('akgm: {}'.format(ak))
    logging.debug('bkgm: {}'.format(bk))
    return ak, bk


def get_dataset_dict(config, **kwargs):
    dataset_dict = {}
    for varname, attrs in config.items():
        dataset_dict[varname] = get_dataset_by_variable(attrs, varname, **kwargs)
    return dataset_dict


def get_files_by_variable(config, varname, dynamic=True):
    project_id = config['convention']['project_id']
    root       = config['convention']['root']
    attributes = config['attributes']
    logging.debug('project_id: {}'.format(project_id))
    logging.debug('root      : {}'.format(root))
    var_selections = {}
    filter = attributes.copy()
    filter.update({'variable':varname})
    fsel = ESGF.get_selection(project_id, root=root, filter=filter)
    if not fsel.unique:
        print(fsel)
        raise Exception('file selection of {} is ambiguous'.format(varname))
    if dynamic:
        fsel = fsel.to_datetime()
        fsel = fsel.select_timerange(ExpVars.timerange)
    print(fsel.df)
    return fsel.file_list


def get_index_by_date(dataset, dates):
    return date2index(dates, dataset.variables['time'], select='exact')

def get_date_by_num(dataset, nums):
    units = dataset.variables['time'].units
    cal   = dataset.variables['time'].calendar
    return num2date(nums, units, calendar=cal)


def get_dataset_by_variable(config, varname, dynamic=True):
    file_list = get_files_by_variable(config, varname, dynamic)
    #ds = XRDataset(file_list[0])
    if dynamic:
        return NC4MFDataset(file_list)
    else:
        return NC4Dataset(file_list[0])


def get_intake_catalog(url):
    logging.info('opening catalog: {}'.format(url))
    catalog = intake.open_esm_datastore(url)
    logging.info('found')
    return catalog


def get_collection_intake(config):
    url = "/work/ch0636/intake-esm/intake-esm-datastore/catalogs/mistral-cmip5.json"
    catalog = get_intake_catalog(url)
    print(catalog)
    print(catalog.df.columns)
    uni_dict = catalog.unique(['model', 'experiment', 'mip_table'])
    pprint.pprint(uni_dict, compact=True)

    project_id = config['convention']['project_id']
    root       = config['convention']['root']
    attributes = config['attributes']
    varnames = config['processing']['variables']
    print(varnames)
    variable_col = catalog.search(**attributes, variable = varnames)
    print(variable_col)



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
    def __init__(self, filename=None, ncattrs=None, ds=None, cal=None):
        if filename:
            self.filename = filename
        else:
            self.filename = ds.filepath()
        if ds is None:
            self.ds = Dataset(filename, mode='w')
        else:
            self.ds = ds
        if cal is None:
            self.cal = AbsoluteCalendar()
        else:
            self.cal = cal

        if self.cal: self.def_time(ncattrs=self.cal.ncattrs_dict())
        if ncattrs: self.def_ncattrs(ncattrs)

    def def_ncattrs(self, ncattrs):
        """Defines nc attribtues by copying them from a reference file. This
        is used for keeping original input data netcdf attributes in the output 
        forcing file.

        **Arguments:**
            - **reffile  (str):**
                Filename of a reference file from which to copy
                netcdf attributes.
        """
        for key, value in ncattrs.items():
            self.ds.setncattr(key, value)
            logging.debug('setting {:<30}:    {}'.format(key, value))

    def def_dims(self, rlon, rlat, nlev):
        """Defines dimensions for a forcing file.

        **Arguments:**
            - **grid  (:class:`Grid`):**
                Grid object that holds dimensional information.

        """
        rlon_dim = self.ds.createDimension('rlon', len(rlon))
        rlat_dim = self.ds.createDimension('rlat', len(rlat))
        lev_dim  = self.ds.createDimension('lev',  nlev)
        rlon = self.ds.createVariable('rlon', dim_prec, 'rlon')
        rlat = self.ds.createVariable('rlat', dim_prec, 'rlat')
        lev  = self.ds.createVariable('lev', dim_prec, 'lev')
        lon = self.ds.createVariable('lon', dim_prec, ('rlat','rlon'))
        lat = self.ds.createVariable('lat', dim_prec, ('rlat','rlon'))
        rlon[:] = rlon
        rlat[:] = rlat

    def def_vc(self, ak, bk):
        lev = self.ds.createDimension('lev', len(ak)-1)
        lev = self.ds.createDimension('nhyi', len(ak))
        ak_var = self.ds.createVariable('hyai', dim_prec, 'nhyi')
        bk_var = self.ds.createVariable('hybi', dim_prec, 'nhyi')
        ak_var[:] = ak
        bk_var[:] = bk
        return ak_var, bk_var

    def def_time(self, name='time', ncattrs=None):
        time = self.ds.createDimension(name)
        time_var = self.ds.createVariable(name, dim_prec, (name))
        if ncattrs: time_var.setncatts(ncattrs)
        return time_var

    def def_ncvar(self, name, dims, attrs=None, **kwargs):
        """Defines a netcdf variable from a :class:`Variable` object.

        **Arguments:**
            - **var  (:class:`Variable`):**
                Variable object that holds meta information.

        """
        var = self.ds.createVariable(name, data_prec, dims, **kwargs)
        if attrs:
            for key, value in attrs.items():
                if type(value) is int:
                    value = np.int32(value)
                var.setncattr(key, value)
        return var

    def write_timestep(self, varname, timestep, data):
        self.ds.variables[varname][timestep] = data

    def date_in_time(self, date):
        logging.debug('date: {}'.format(date))
        time = self.ds.variables['time']
        num = self.cal.date2num(date)
        return num in time[:]

    def add_date(self, date):
        time = self.ds.variables['time']
        num = self.cal.date2num(date)
        time[time.shape[0]] = num

    def write_date(self, varname, date, data):
        #timestep = date2index(date, self.ds.variables['time'])
        indx = self.ds.variables['time'].shape[0] - 1
        self.write_timestep(varname, indx, data)

    def close(self):
        self.ds.close()
