
import logging
import numpy as np
import numpy.ma as ma



from . import filemanager as fm
from . import variable as var
from . import grid as gd
from pyintorg import interface as intf

from .state import State
from cordex.dataset import NC4Dataset

from . import common as cm

class StaticData():

    grav = 1.0/0.10197

    c_fib   = 129
    c_bla   = 172
    # we should use the unit attribute to define
    # the scaling factor..
    # scaling factor for orography
    # scaling factor for land sea mask
    # fak_bal = 1.0 # if unit is 'm**2 s**-2'
    fak_fib = 1.0 # era5
    fak_bla = 1.0 # era5

    #fak_fib = 1.0/0.10197 # = gravitational constant if unit is 'm'
    #fak_bla = 0.01 # if unit is '%'

    def __init__(self):
        pass

    def __getitem__(self, key):
        return self.dataset[key]

    def __setitem__(self, key, item):
        self.dataset[key] = item

    def __iter__(self):
        return iter(self.dataset)

    def load_bodlib(self, bodlib):
        logging.info('loading bodlib: {}'.format(bodlib))
        self.bodlib = NC4Dataset(ds = fm.get_bodlib(bodlib))
        #self.fibem  = self.bodlib.variables['var{}'.format(self.c_fib)]
        self.fibem = var.create_variable('var{}'.format(self.c_fib), self.bodlib).timestep(0)*1.0/0.10197
        self.blaem = var.create_variable('var{}'.format(self.c_bla), self.bodlib).timestep(0)


    def load_static(self, datasets):
        logging.info('loading static data from input data...')
        self.dataset = datasets
        self.fibgm_var = var.create_variable('orog', datasets, fak=self.fak_fib)
        self.fibgm = self.fibgm_var.timestep(0)
        cm.print_datinfo('fibgm', self.fibgm)
        self.blagm_var = var.create_variable('sftlf', datasets, fak=self.fak_bla)
        self.blagm = np.around(self.blagm_var.timestep(0))
        cm.print_datinfo('blagm', self.blagm)
        # additional land sea maks of the ocean model
        #self.blagm_sst_var = var.create_variable('sftof', datasets['sftof'])
        #self.blagm_sst_var = var.create_variable('sftlf', datasets['sftlf'])
        #self.blagm_sst = 1.0 - 0.01 * self.blagm_sst_var.timestep(0)
        #self.blagm_sst.set_fill_value(1.0)
        #self.blagm_sst = np.around(ma.getdata(self.blagm_sst))

    def field_by_code(self, code):
        for varname, ncvar in self.bodlib.variables.items():
            if 'code' in ncvar.ncattrs():
                return ncvar
            elif str(code).zfill(3) in varname:
                return ncvar




def interpolate_static(static_data, domain, igr=1):
    lamem, phiem = intf.geo_coords(*gd.get_info(domain))
    lamgm = static_data.fibgm_var.lam
    phigm = static_data.fibgm_var.phi
    indii, indjj = intf.intersection_points(lamgm, phigm, lamem, phiem)

    lamem = lamem[:,:,igr-1]
    phiem = phiem[:,:,igr-1]
    indii = indii[:,:,igr-1]
    indjj = indjj[:,:,igr-1]

    cm.print_datinfo('lamgm', lamgm)
    cm.print_datinfo('phigm', phigm)
    cm.print_datinfo('lamem', lamem)
    cm.print_datinfo('phiem', phiem)
    cm.print_datinfo('indii', indii)
    cm.print_datinfo('indjj', indjj)
    cm.print_datinfo('fibgm', static_data.fibgm)
    varname = 'FIB'
    #fibgm = static_data.fibgm_var.timestep(0)
    static_data.fibge  = intf.interp_horiz_2d(static_data.fibgm, lamgm, phigm, lamem,
            phiem, indii, indjj, varname)
    static_data.blage  = intf.interp_horiz_2d(static_data.blagm, lamgm, phigm, lamem,
            phiem, indii, indjj, varname)
    cm.print_datinfo('fibge', static_data.fibge)
    cm.print_datinfo('blage', static_data.blage)

    return static_data




bodlib = StaticData()
static_state = {} #State()

