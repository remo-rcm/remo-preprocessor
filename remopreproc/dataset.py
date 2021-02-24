
import os

import datetime as dt
from cdo import Cdo
import logging
from netCDF4 import Dataset, MFDataset, date2index, num2date, date2num
import xarray as xr
import pandas as pd
from .cache_deco import cached, key_memoized
import numpy as np

from .exp import ExpVars

from . import filemanager as fm

cdo_logging = True

ak_valid = ['ap_bnds','a_bnds']
bk_valid = ['b_bnds']




class NC4Dataset():

    def __init__(self, file_list=None, ds=None, time_axis='time', **kwargs):
        self.time_axis = time_axis
        if file_list and not isinstance(file_list, list):
            file_list = [file_list]
        self.file_list = file_list
        if ds is None:
            if len(self.file_list) == 1:
                self.ds = Dataset(self.file_list[0], **kwargs)
            elif len(self.file_list) > 1:
                self.ds = MFDataset(self.file_list, **kwargs)
        else:
            self.ds = ds
        if file_list is None and ds is None:
            logging.warning('empty file list or dataset!')

    def __str__(self):
        return str(self.ds)

#    def __getattr__(self, item):
#        logging.debug('getting {} from dataset...'.format(item))
#        return getattr(self.ds, item)

#    @property
#    def file_list(self):
#        return list(self.df['path'])

    @property
    def calendar(self):
        return self.ds.variables[self.time_axis].calendar

    @property
    def units(self):
        return self.ds.variables[self.time_axis].units

    @property
    def variables(self):
        return self.ds.variables

    @property
    def positive_down(self):
        return self.ds.variables['lev'].positive == "down"

    def ncattrs(self):
        return self.ds.ncattrs()

    def global_coordinates(self, varname=None):
        return fm.get_lonlat_2d(self.ds)


    def get_vc(self):
        """Reads the vertical hybrid coordinate from a dataset.
        """
        ak_bnds = None
        bk_bnds = None
        for ak_name in ak_valid:
            if ak_name in self.ds.variables:
                ak_bnds = self.ds.variables[ak_name]
                logging.info('using {} for akgm'.format(ak_name))
        for bk_name in bk_valid:
            if bk_name in self.ds.variables:
                bk_bnds = self.ds.variables[bk_name]
                logging.info('using {} for bkgm'.format(bk_name))
        if not all([ak_bnds, bk_bnds]):
            logging.error('could not identify vertical coordinate, tried: {}, {}'.format(ak_valid, bk_valid))
            raise Exception('incomplete input dataset')
#        ak_bnds, bk_bnds  = (ak_bnds[:1], bk_bnds[:,1])
        nlev = ak_bnds.shape[0]
        ak = np.zeros([nlev+1], dtype=np.float64)
        bk = np.ones([nlev+1], dtype=np.float64)
        #ak[1:] = (ak_bnds[:])
        #bk[1:] = (bk_bnds[:])
        if self.positive_down:
            #ak[:-1] = np.flip(ak_bnds[:])
            #bk[:-1] = np.flip(bk_bnds[:])
            ak[:-1] = np.flip(ak_bnds[:,1])
            bk[:-1] = np.flip(bk_bnds[:,1])
        else:
            ak[1:] = np.flip(ak_bnds[:,1])
            bk[1:] = np.flip(bk_bnds[:,1])
        return ak, bk

    #def ncattrs_dict(self, varname=None):
    #    if varname:
    #        return {attr:self.ds.variables[varname].getncattr(attr)
    #                for attr in self.ds.variables[varname].ncattrs()}
    #    else:
    #        return {attr:self.ds.getncattr(attr)
    #                for attr in self.ds.ncattrs()}

    def ncattrs_dict(self, varname=None):
        if varname:
            return {attr:getattr(self.ds.variables[varname], attr)
                    for attr in self.ds.variables[varname].ncattrs()}
        else:
            return {attr:getattr(self.ds, attr)
                    for attr in self.ds.ncattrs()}

    def get_index_by_date(self, dates):
        logging.debug('dates: {}'.format(dates))
        return date2index(dates,
                self.ds.variables[self.time_axis], select='exact')

    def get_date_by_num(self, nums):
        return num2date(nums, self.units, calendar=self.calendar)

    def get_num_by_date(self, dates):
        return date2num(dates, self.units, calendar=self.calendar)

    def get_num_by_index(self, index):
        return self.variables[self.time_axis][index]

    def get_date_by_index(self, index):
        num = self.ds.variables[self.time_axis][index]
        return self.get_date_by_num(num)

    def get_timestep(self, date, varname):
        ix = self.get_index_by_date(date)
        return self.ds.variables[varname][ix]

    def get_variable(self, varname):
        return self.ds.variables[varname]

    def dynamic(self, varname):
        return self.ds.variables[varname].dimensions[0] == self.time_axis

    def data_by_date(self, variable, date):
        return self.timestep(variable, self.get_index_by_date(date))

    def static(self, varname):
        return not self.dynamic(varname)

    def timestep(self, varname, timestep=0):
        if self.dynamic(varname):
            return self.variables[varname][timestep]
        else:
            return self.variables[varname][:]

    def threeD(self, varname):
        return len(self.timestep(varname).shape) == 3

    def twoD(self, varname):
        return not self.threeD(varname)

    def nlev(self, varname=None):
        if self.threeD(varname):
            return self.ds.variables[varname].shape[1:-2][0]
        else:
            return 1

    def to_netcdf(self, varname=None, timestep=None, destination=None):
        ds = copy_dataset(self.ds, varname=varname, timestep=timestep, destination=destination)
        filepath = ds.filepath()
        ds.close()
        return filepath




#class NC4MFDataset(NC4Dataset):
#
#    def __init__(self, df, time_axis='time', **kwargs):
#        NC4Dataset.__init__(self, df, time_axis, **kwargs)
#
#    def ncattrs_dict(self, varname=None):
#        if varname:
#            return {attr:getattr(self.ds.variables[varname], attr)
#                    for attr in self.ds.variables[varname].ncattrs()}
#        else:
#            return {attr:getattr(self.ds, attr)
#                    for attr in self.ds.ncattrs()}
#
#    def getncattr(self, attr):
#        return getattr(self.ds, attr)
#


class XRDataset():

    def __init__(self, file_list, time_axis='time'):
        self.time_axis = time_axis
        self.ds = xr.open_dataset(file_list, decode_times=False, decode_cf=False,
                decode_coords=False, chunks={'time':1, 'lat':1000, 'lon':1000})


class XRMFDataset():

    def __init__(self, file_list, time_axis='time'):
        self.time_axis = time_axis
        self.ds = xr.open_mfdataset(file_list)



class ECMWF(NC4Dataset):

    date_fmt = "%Y-%m-%dT%H:%M:%S"
    codemap   = {130: 'ta', 134: 'ps', 131: 'ua', 132: 'va',
                 133: 'hus',  34 : 'tos',  31 :'sic',  129 : 'orog',
                 172: 'sftlf', 139: 'tsl1', 170: 'tsl2', 183: 'tsl3',
                 238: 'tsn', 236: 'tsl4', 246: 'clw', 141: 'snw', 198: 'src', 235: 'skt' ,
                 39: 'swvl1', 40: 'swvl2', 41: 'swvl2'}


    def __init__(self,df=None, time_axis='time'):
        self.cdo = Cdo(logging=True, tempdir=os.path.join(ExpVars.scratch,'python-cdo'))
        self.time_axis = time_axis
        self.df = df
        self.df['startdate'] = pd.to_datetime(self.df['startdate'])
        self.df['enddate'] = pd.to_datetime(self.df['enddate'])
        self.tmp_ds = {}

    @property
    def file_list(self):
        return self.df['path'].values

    def threeD(self, varname):
        """soil fields are handled as 2D although they have a depth dimension.
        """
        return len(self.timestep(varname).shape) == 3 and self.timestep(varname).shape[0] > 1

    @property
    def positive_down(self):
        """ERA5 data has the correct layer numbering for REMO.
        """
        return False

    @property
    def code(self):
        """returns code from dataframe, should be unique
        """
        code = self.df['code'].unique()
        if len(code) == 1:
            return code[0]
        else:
            raise Exception('code is not unique in file list')

    @property
    def ds(self):
        return Dataset(self._ref_file())

    def get_vc(self):
        """Reads the vertical hybrid coordinate from a dataset.
        """
        return self.variables['hyai'], self.variables['hybi']

    @cached
    def _tmp_file_by_date(self, datetime, nc):
        filename = self.get_file_by_date(datetime)
        date_str = datetime.strftime(self.date_fmt)
        logging.debug('selecting {} from {}'.format(date_str, filename))
        if nc:
            return self._nc_convert( self.cdo.seldate(date_str, input=filename ) )
        else:
            return self.cdo.seldate(date_str, input=filename )

    def _ref_file(self, filename=None, nc=True):
        """the reference dataset is used to access dataset attributes.

        This is required to give the preprocessor acces to, e.g., grid
        and calendar information.
        """
        if filename is None:
            filename = self.file_list[0]
        logging.info('getting reference dataset from {}'.format(filename))
        if nc:
            return self._nc_convert( self._reftimestep( filename ) )
        else:
            return self._reftimestep( filename )

        #logging.debug('reference dataset: {}'.format(self.ref_ds.filepath()))
    @cached
    def _reftimestep(self, filename):
        return self.cdo.seltimestep( 1, input=filename)

    @cached
    def _nc_convert(self, filename):
        regular = self._to_regular(filename)
        if self.code in self.codemap:
            return self.cdo.setname(self.codemap[self.code], input=regular)
        else:
            return regular

    def _gridtype(self, filename):
        griddes = self.cdo.griddes(input=filename)
        griddes = {entry.split('=')[0].strip():entry.split('=')[1].strip() for entry in griddes if '=' in entry}
        return griddes['gridtype']

    def _get_code(self, filename):
        showcode = self.cdo.showcode(input=filename)
        print(showcode)
        return showcode

    @cached
    def _to_regular(self, filename):
        """converts ecmwf spectral grib data to regular gaussian netcdf.

        cdo is used to convert ecmwf grid data to netcdf depending on the gridtype:
        For 'gaussian_reduced': cdo -R
            'spectral'        : cdo sp2gpl

        This follows the recommendation from the ECMWF Era5 Documentation.
        We also invert the latitudes to stick with cmor standard.

        """
        gridtype = self._gridtype(filename)
        if gridtype == 'gaussian_reduced':
            #return self.cdo.copy(options='-R -f nc', input=filename)
            gaussian = self.cdo.setgridtype('regular', options='-f nc', input=filename)
        elif gridtype == 'spectral':
            gaussian = self.cdo.sp2gpl(options='-f nc', input=filename)
        elif gridtype == 'gaussian':
            gaussian =  self.cdo.copy(options='-f nc', input=filename)
        else:
            raise Exception('unknown grid type for conversion to regular grid: {}'.format(gridtype))
        return self.cdo.invertlat(input=gaussian)

    def get_file_by_date(self, datetime):
        """search for a file in the dataframe that should contain the datetime.
        """
        df = self.df[ (datetime >= self.df['startdate']) & (datetime <= self.df['enddate']) ]
        if len(df['path'].values) == 0:
            raise Exception('no files found for {}'.format(datetime))
        elif len(df['path'].values) > 1:
            raise Exception('date selection must be unique')
        else:
            return df['path'].values[0]

    def data_by_date(self, variable, datetime, nc=True):
        return Dataset(self._tmp_file_by_date(datetime, nc)).variables[variable][0]



class Preprocessor():

    def __init__():
        pass



def copy_dataset(src, varname=None, timestep=None, destination=None):
    if varname is None:
        variables = src.variables
    else:
        variables = {varname:src.variables[varname]}
    if destination is None:
        destination = 'copy.nc'
    dst = Dataset(destination,'w')
    # copy attributes
    for name in src.ncattrs():
        dst.setncattr(name, getattr(src, name))
    # copy dimensions
    for name, dimension in src.dimensions.items():
        if timestep and name=='time':
            length = 1
        else:
            length = (len(dimension) if not dimension.isunlimited() else None)
        #dst.createDimension( name, (len(dimension) if not dimension.isunlimited() else None))
        dst.createDimension( name, length)
        # copy all file data except for the excluded
    for name, variable in variables.items():
        if hasattr(variable, '_FillValue'):
            fill_value = getattr(variable, '_FillValue')
        else:
            fill_value = None
        var = dst.createVariable(name, variable.dtype, variable.dimensions, fill_value=fill_value)
        for attr in variable.ncattrs():
            if attr != '_FillValue':
                dst.variables[name].setncattr(attr, getattr(variable, attr))
        if variable.shape:
            if timestep is None or 'time' not in variable.dimensions:
                dst.variables[name][:] = src.variables[name][:]
            else:
                dst.variables[name][0] = src.variables[name][timestep]
    return dst



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



def get_dataset(files, ds_type=None):
    if ds_type == 'NC4Dataset':
        return NC4Dataset(files)
    elif ds_type == 'ECMWF':
        return ECMWF(files)
