

import filemanager as fm
import dataset as ds
import logging

from constants import GVars

from cache_deco import cached
from cdo import Cdo

import ecmwf as era

##class DataStore():
##    """Static class to handle dataset selection
##    from a file collection.
##    """
##    dataset = None
##
##    @classmethod
##    def __getitem__(cls, key):
##        return cls.dataset[key]
##
##    @classmethod
##    def __setitem__(cls, key, item):
##        cls.dataset[key] = item
##
##    @classmethod
##    def __iter__(cls):
##        return iter(cls.dataset)
##
##    @classmethod
##    def load_datasets(cls, gcm_var_attrs):
##        cls.dataset = fm.get_dataset_dict(gcm_var_attrs)
##        cal.check_calendar(cls.dataset)
##
##    @classmethod
##    def get_dataset(cls, varname):
##        return cls.dataset[varname]
##
##    @classmethod
##    def ref_ds(cls):
##        return cls.dataset[next(iter(cls.dataset))]


class DataStore():
    """Class to handle dataset selection
    """

    def __init__(self, tables, ds_type='NC4Dataset'):
        self.storage = {}
        self._init_datasets(tables, ds_type)

    def _init_datasets(self, tables, ds_type):
        for varname, table in tables.items():
            files = list(table['path'])
            for filename in files:
                logging.info('found: {}'.format(filename))
            self.storage[varname] = ds.get_dataset(files, ds_type)

    @property
    def dataset(self):
        return self.storage

    def __getitem__(self, key):
        return self.get_dataset(key)

    def __setitem__(self, key, item):
        self.set_dataset(key, item)

    def __iter__(self):
        return iter(self.storage)

    def threeD(self, varname):
        return self.get_dataset(varname).threeD(varname)

    def positive_down(self, varname):
        return self.get_dataset(varname).positive_down

    def get_dataset(self, varname):
        return self.storage[varname]

    def set_dataset(self, varname, dataset):
        self.storage[varname] = dataset

    def get_vc(self, varname):
        return self.get_dataset(varname).get_vc()

    def global_coordinates(self, varname):
        return self.get_dataset(varname).global_coordinates()

    def data_by_date(self, varname, datetime):
        return self.get_dataset(varname).data_by_date(varname, datetime)

    def timestep(self, varname, timestep):
        return self.get_dataset(varname).timestep(varname, timestep)

    def ref_ds(self):
        return self.storage[next(iter(self.storage))]


class ECMWF(DataStore):
    """class to store an ECMWF dataset.

    This class will handle derivation of variables from
    other variables, e.g., the computation of wind vectors
    from vorticity and divergence.
    """

    codemap   = {130: 'ta', 134: 'ps', 131: 'ua', 132: 'va',
                 133: 'hus',  34 : 'tos',  31 :'sic',  129 : 'orog',
                 172: 'sftlf', 139: 'tsl1', 170: 'tsl2', 183: 'tsl3',
                 238: 'tsn', 236: 'tsl4', 246: 'clw', 141: 'snw', 198: 'src' }

    def __init__(self, tables):
        self.cdo = Cdo(logging=True, tempdir=GVars.scratch)
        self.FM = era.FileManager
        DataStore.__init__(self, tables, 'ECMWF')

    def _init_datasets(self, tables, ds_type):
        for varname, table in tables.items():
            #fm = self.FM(table)
            self.storage[varname] = ds.get_dataset(table, ds_type)

    def get_dataset(self, varname):
        if varname == 'ua':
            return self.u_component()
        elif varname == 'va':
            return self.v_component()
        else:
            return self.storage[varname]

    @cached
    def uv(self, datetime=None):
        if datetime is None:
            print(type(self.storage['svo']))
            vorticity_tmp = self.storage['svo']._ref_file(nc=False)
            divergence_tmp = self.storage['sd']._ref_file(nc=False)
        else:
            vorticity_tmp = self.storage['svo']._tmp_file_by_date(datetime, nc=False)
            divergence_tmp = self.storage['sd']._tmp_file_by_date(datetime, nc=False)
        merge = self.cdo.merge(input=[vorticity_tmp, divergence_tmp])
        uv = self.cdo.dv2uvl(options='-f nc', input = merge)
        uv = self.cdo.invertlat(input=uv)
        u = self.cdo.selcode(131, input=uv)
        v = self.cdo.selcode(132, input=uv)
        return self.cdo.setname('ua', input = u), self.cdo.setname('va', input = v)

    def ws(self, datetime=None):
        pass

    def u_component(self, datetime=None):
        return ds.get_dataset(self.uv(datetime)[0], 'NC4Dataset')

    def v_component(self, datetime=None):
        return ds.get_dataset(self.uv(datetime)[1], 'NC4Dataset')

    def data_by_date(self, varname, datetime):
        logging.info('calling data_by_date for {}'.format(varname))
        if varname == 'ua':
            return self.u_component(datetime).data_by_date('ua', datetime)
        elif varname == 'va':
            return self.v_component(datetime).data_by_date('va', datetime)
        else:
            return self.storage[varname].data_by_date(varname, datetime)

    def get_vc(self, varname):
        """Reads the vertical hybrid coordinate from a dataset.
        """
        return self.get_dataset(varname).variables['hyai'], self.get_dataset(varname).variables['hybi']

    def positive_down(self, varname):
        """ERA5 data has the correct layer numbering for REMO.
        """
        return False


def create_datastore(tables, ds_type):
    if ds_type == 'ECMWF':
        datastore = ECMWF(tables)
    else:
        datastore = DataStore(tables, ds_type)
    #for varname, table in tables.items():
    #    if ds_type == 'ECMWF':
    #        files = table
    #        print(files)
    #    else:
    #        files = list(table['path'])
    #        for filename in files:
    #            logging.info('found: {}'.format(filename))
    #    datastore[varname] = ds.get_dataset(files, ds_type)
    return datastore


datastore = None
