

from netCDF4 import Dataset
from cdo import Cdo
import xarray as xr
import datetime as dt
import tempfile
import logging
import numpy as np
#from scipy.interpolate import interp1d
from . import datastore as ds
from . import static_data
from . import filemanager as fm
from .import cal
from .dataset import NC4Dataset


SST_VARNAME = 'tos'

# cdo operator for remapping the ocen sst t
# the atmospheric grid
REMAP_OP = 'remapdis'


def get_ds_timestep(ds, timestep=None):
    """Creates a temporary netcdf file of the ocean dataset.

    Creates a temporary netcdf file for a certain timestep of the
    ocean dataset.
    """
    return ds.to_netcdf(timestep=timestep, destination=tempfile.mkstemp()[1])


def sst_to_regular(ds, timestep=None, output=None):
    """Remap sst to regular grid using cdo.

    Creates a temporary file with the sst remapped to a regular grid
    using a cdo operator.
    """
    ocean_tmp = get_ds_timestep(ds, timestep)
    tmp_ds = Dataset(ocean_tmp)
    shape   = tmp_ds.variables[SST_VARNAME].shape
    nx = shape[-1]
    ny = shape[-2]
    return Cdo(logging=True).remapbil('r{}x{}'.format(nx,ny), input=ocean_tmp, output=output)

def sst_to_atm_grid(ds, ds_atmo, timestep=None, output=None):
    """Remap sst to regular grid using cdo.

    Creates a temporary file with the sst remapped to a regular grid
    using a cdo operator. The target grid is definen by the grid of atmo_ds.
    """
    ocean_tmp = get_ds_timestep(ds, timestep)
    atmo_tmp = get_ds_timestep(ds_atmo, 0)
    return getattr(Cdo(logging=True, logFile='cdo.log'), REMAP_OP)(atmo_tmp, input=ocean_tmp, output=output)
    #return cdo.Cdo(logFile='cdo.log').remapbil('r{}x{}'.format(nx,ny), input=ocean_tmp, output=output)

#def prepare_sst_variable(timestep):
#    mapping_file  = ExpVars.config['mapping']['map']
#    table = ConfigObj(mapping_file)
#    ocean_config = ExpVars.gcm_var_attrs['tos']
#    ds = fm.get_dataset_by_variable(ocean_config, 'tos')
#    ds_tmp = sst.sst_to_regular(ds, timestep=0, output='sst.nc')
#    return fm.NC4Dataset(ds_tmp)


def prepare_sst(datetime):
    """main interface routine for the preprocessor.

    This function manages grid and temporal interpolation of the sst
    to the atmospheric grid and frequency.
    """
#    tos_ds  = DataStore.dataset['tos']
    tos_ds  = ds.datastore['tos']
    # use orog dataset as grid reference
    #grid_ds = static_data['orog']
    grid_ds = ds.datastore['orog']
    logging.info('ocean sst will be interpolated in time to the atmosphere frequency.')
    sst_at_date    = interpolate_to_datetime(tos_ds, datetime)
    ds_timestep    = get_ds_timestep(tos_ds, 0)
    print(ds_timestep)
    sst_ds_at_date = NC4Dataset(ds_timestep, mode='r+')
    print('sst_at_date', sst_at_date.min(), sst_at_date.max())
    sst_ds_at_date.variables['tos'][0] = sst_at_date
    #sst_ds_at_date.variables['time'][0] = sst_ds_at_date.get_num_by_date(dt.datetime(datetime.year, datetime.month, datetime.day, 12,0,0))
    sst_ds_at_date.variables['time'][0] = sst_ds_at_date.get_num_by_date(datetime)
    grid_tmp_nc    = get_ds_timestep(grid_ds)
    return sst_to_atm_grid(sst_ds_at_date, grid_ds)
    #return Cdo(logging=True).remapdis(grid_tmp_nc, input=sst_ds_at_date, output='ocean_tmp.nc')



def interpolate_to_datetime(sst_ds, datetime):
    """interpolates the sst dataset in time.

    The subroutines interpolates the sst between two adjacent timesteps of
    daily sst means. The adjacent timesteps are assumed to be at 12:00:00 hours.
    """
    date = dt.datetime(datetime.year, datetime.month, datetime.day, 12,0,0)
    # noon time
    noon = dt.time(12,0,0)
    # time of the target datetime
    time = dt.time(datetime.hour, datetime.minute, datetime.second)
    ti1  = sst_ds.get_index_by_date(date)
    if time < noon:
        # if the target time is less than noon, we take the current day and the day before.
        ti2 = ti1
        ti1 = ti2 - 1
    else:
        # we take the current day and tomorrow.
        ti2 = ti1 + 1

    num1 = (sst_ds.get_num_by_index(ti1))
    num2 = (sst_ds.get_num_by_index(ti2))
    num = (sst_ds.get_num_by_date(datetime))
    sst_at_ti1 = sst_ds.variables['tos'][ti1]
    sst_at_ti2 = sst_ds.variables['tos'][ti2]

    # linear interpolation
    w1 = (num2-num)/(num2-num1)
    w2 = (num-num1)/(num2-num1)
    return w1 * sst_at_ti1 + w2 * sst_at_ti2

    # scipy interp1d
    ##time_axis = np.array([num1, num2])
    ##sst_at_ti1 = sst_ds.variables['tos'][ti1]
    ##sst_at_ti2 = sst_ds.variables['tos'][ti2]
    ##sst_axis = [sst_at_ti1.flatten(), sst_at_ti2.flatten()]
    ##f = interp1d(time_axis, sst_axis, axis=0)
    ##sst_at_date = np.ma.masked_array(f(num).reshape(sst_at_ti1.shape), mask=sst_at_ti1.mask)


