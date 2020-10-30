

from pyintorg import interface as intf

import numpy as np

import logging
from . import filemanager as fm

#import ocean as sst



#UNIT_CONVERT = {'m': 1.0/0.10197} # = gravitational constant if unit is 'm'


class Variable():

    def __init__(self, name, ds=None, igr=None, fak=None):
        self.name          = name
        self.ds            = ds
        self.zflip         = False
        if fak is None:
            self.fak = 1.0
        else:
            self.fak = fak
        if igr is None:
            self.igr = 0
        else:
            self.igr = igr
        if self.threeD:
            self.zflip = ds.positive_down(self.name)

    @property
    def unit(self):
        try:
            return self.ds.variables[self.name].getncattr('unit')
        except:
            logging.warning('no unit info in variable: {}'.format(self.name))
            return None

    @property
    def threeD(self):
        return self.ds.threeD(self.name)

    @property
    def dynamic(self):
        return self.ds.dynamic(self.name)

    @property
    def vc(self):
#        ak_bnds, bk_bnds = self.ds.get_vc()
        ak, bk = self.ds.get_vc(self.name)
#        nlev = ak.shape[0]
#        ak = np.zeros([nlev+1], dtype=np.float64)
#        bk = np.ones([nlev+1], dtype=np.float64)
##        if self.zflip:
##            #ak[:-1] = np.flip(ak_bnds[:])
##            #bk[:-1] = np.flip(bk_bnds[:])
##            ak = np.flip(ak)
##            bk = np.flip(bk)
#        else:
#            ak[1:] = np.flip(ak_bnds[:])
#            bk[1:] = np.flip(bk_bnds[:])
        return ak[:], bk[:]

    @property
    def ak(self):
        return self.vc[0]

    @property
    def bk(self):
        return self.vc[1]

    @property
    def global_coordinates(self):
        #return fm.get_lonlat_2d(self.ds)
        return self.ds.global_coordinates(self.name)

    @property
    def lam(self):
        return self.global_coordinates[0]

    @property
    def phi(self):
        return self.global_coordinates[1]

    def timestep(self, timestep):
        if self.zflip:
            return np.flip(self.fak*self.ds.timestep(self.name, timestep),0).T
        else:
            return self.fak*self.ds.timestep(self.name, timestep).T

    def data_by_date(self, datetime):
        if self.zflip:
            return np.flip(self.fak*self.ds.data_by_date(self.name, datetime),0).T
        else:
            return self.fak*self.ds.data_by_date(self.name, datetime).T



def create_variable(name, ds, **kwargs):
    logging.debug('creating variable: {}'.format(name))
    var = Variable(name, ds, **kwargs)
    return var



##### dervied variables
##class RelativeHumidity(Variable):
##
##    def __init__(self, qd, t, ps):
##        logging.debug('creating relative humidity')
##        Variable.__init__(self, 'hus', qd.ds)
##        self.qd = qd
##        self.t  = t
##        self.ps = ps
##
##    def timestep(self, timestep):
##        qdgm   = self.qd.timestep(timestep)
##        tgm    = self.t.timestep(timestep)
##        psgm   = self.ps.timestep(timestep)
##        return intf.relative_humidity(qdgm, tgm, psgm, self.ak, self.bk)
##
##
##
##class Geopotential(Variable):
##
##    def __init__(self, fib, qd, t, ps):
##        logging.debug('creating geopotential variable')
##        Variable.__init__(self, 'ta', t.ds)
##        self.fib = fib
##        self.qd  = qd
##        self.t   = t
##        self.ps  = ps
##
##    def timestep(self, timestep):
##        fibgm  = self.fib.timestep(timestep)
##        qdgm   = self.qd.timestep(timestep)
##        tgm    = self.t.timestep(timestep)
##        psgm   = self.ps.timestep(timestep)
##        return intf.geopotential(fibgm, tgm, qdgm, psgm, self.ak, self.bk)


#class SST(Variable):
#
#    def __init__(self, name, ds, atmo_grid=None):
#        logging.debug('creating sst')
#        self.atmo_grid = atmo_grid
#        Variable.__init__(self, name, ds)
#        self.coords = fm.get_lonlat_2d(self.process(0))
#
#    @property
#    def lam(self):
#        return self.coords[0]
#
#    @property
#    def phi(self):
#        return self.coords[1]
#
#    @property
#    def ds(self):
#        return self.process(0)
#
#    @ds.setter
#    def ds(self, ds):
#        self.ds_sst = ds
#
#    def process(self, timestep):
#        # remap sst on the fly
#        logging.debug('processing sst')
#        if self.atmo_grid:
#            return fm.NC4Dataset(sst.sst_to_atm_grid(self.ds_sst, self.atmo_grid, timestep, 'ocean_tmp.nc'))
#        else:
#            return fm.NC4Dataset(sst.sst_to_regular(self.ds_sst, timestep, output='ocean_tmp_2.nc'))
#
#    def timestep(self, timestep):
#        return self.process(timestep).timestep(self.name, timestep=0).T
#
#    def data_by_date(self, datetime):
#        if self.zflip:
#            return np.flip(self.fak*self.ds.data_by_date(self.name, datetime),0).T
#        else:
#            return self.fak*self.ds.data_by_date(self.name, datetime).T


def compute_relative_humidity(qdgm, tgm, psgm, qwgm=None):
    """Computes relative humidity.
    """
    return intf.relative_humidity(qdgm.T, tgm.T, psgm.T)

