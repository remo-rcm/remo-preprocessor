
import numpy as np

from pyintorg import interface as intf
from . import grid as gd
from . import variable as var
from . import filemanager as fm
import logging
from .static_data import bodlib 
from .state import State

from .common import print_datinfo

import datetime as dt

from . import ocean as sst

from .exp import ExpVars

from .import datastore as ds

from .dataset import NC4Dataset

class Mapping():
    """Connects input variable with output data using mapping info.
    """

    def __init__(self, src, domain, igr=None, cressman=False, mask='sea'):
        self.src = src
        self.domain = domain
        if igr is None:
            self.igr = 1
        else:
            self.igr = igr
        self._create_grid_mapping()
        if self.src.threeD:
            self._create_vertical_mapping()
        self.cressman = cressman
        self.mask = mask

    def _create_grid_mapping(self):
        logging.info('grid info: {}'.format(self.domain))
        lamem, phiem = intf.geo_coords(*gd.get_info(self.domain))
        indii, indjj = intf.intersection_points(self.src.lam, self.src.phi, lamem, phiem)
        self.lamem = lamem[:,:,self.igr-1]
        self.phiem = phiem[:,:,self.igr-1]
        self.indii = indii[:,:,self.igr-1]
        self.indjj = indjj[:,:,self.igr-1]
        self.lamgm = self.src.lam
        self.phigm = self.src.phi
        print_datinfo('indii', self.indii)
        print(self.indii)
        print_datinfo('indjj', self.indjj)
        print(self.indjj)
        print_datinfo('lamem', self.lamem)
        print_datinfo('phiem', self.phiem)
        print_datinfo('lamgm', self.lamgm)
        print_datinfo('phigm', self.phigm)

    def _create_vertical_mapping(self):
        self.akem = ExpVars.vc_table['ak'].values
        self.bkem = ExpVars.vc_table['bk'].values
        self.akgm = self.src.ak
        self.bkgm = self.src.bk
        self.akhgm, self.bkhgm, self.dakgm, self.dbkgm = compute_vc(self.akgm, self.bkgm)
        self.akhem, self.bkhem, self.dakem, self.dbkem = compute_vc(self.akem, self.bkem)


def compute_vc(ak, bk):
    """Computes vertical coordinates.

    Computes vertical coordinates at full levels and the thickness of levels.

    """
    akh = np.array([  0.5 * ( ak[i] + ak[i+1] ) for i in range(ak.shape[0]-1)], dtype=np.float64)
    bkh = np.array([  0.5 * ( bk[i] + bk[i+1] ) for i in range(bk.shape[0]-1)], dtype=np.float64)
    dak = np.array([ ( ak[i+1] - ak[i] ) for i in range(ak.shape[0]-1)], dtype=np.float64)
    dbk = np.array([ ( bk[i+1] - bk[i] ) for i in range(bk.shape[0]-1)], dtype=np.float64)
    return akh, bkh, dak, dbk


def create_mapping(name, src, domain, igr=None):
    return Mapping(src, domain, igr)


def mapping_table_dynamic(datasets, table, domain):
    mapping_table = {}

    varname = 'T'
    source = table[varname]['src']
    src_t = var.create_variable(source, datasets )
    mapping_table[varname] = create_mapping(varname, src_t, domain)

    varname = 'PS'
    source = table[varname]['src']
    src_ps = var.create_variable(source, datasets )
    mapping_table[varname] = create_mapping(varname, src_ps, domain)

    varname = 'U'
    source = table[varname]['src']
    src_u = var.create_variable(source, datasets )
    mapping_table[varname] = create_mapping(varname, src_u, domain, 2)

    varname = 'V'
    source = table[varname]['src']
    src_v = var.create_variable(source, datasets )
    mapping_table[varname] = create_mapping(varname, src_v, domain, 3)

    #varname = 'RF'
    #source = table['QD']['src']
    #src_qd = var.create_variable(source, datasets[source] )
    #mapping_table[varname] = create_mapping(varname, src_rf, domain, fw)

    varname = 'QD'
    source = table[varname]['src']
    src_qd = var.create_variable(source, datasets )
    mapping_table[varname] = src_qd

    varname = 'QW'
    source = table[varname]['src']
    src_qw = var.create_variable(source, datasets )
    mapping_table[varname] = src_qw

    varname = 'SEAICE'
    source = table[varname]['src']
    if source in datasets.storage:
        src = var.create_variable(source, datasets )
        mapping_table[varname] = src

    #varname = 'TS'
    #source = table[varname]['src']
    ##src_ts = var.SST(source, datasets[source])
    #src_ts = var.SST(source, datasets[source], datasets['ta'])
    #mapping_table[varname] = create_mapping(varname, src_ts, domain, fw)

    return mapping_table


def get_remo_var(src, table):
    for remo_var, items in table.items():
        if src == items['src']:
            return remo_var


def mapping_table_aux(datasets, aux_vars, table, domain):
    mapping_table = {}
    for cf_var in aux_vars:
        remo_var = get_remo_var(cf_var, table)
        if not remo_var:
            logging.critical('could not find a mapping for {}'.format(cf_var))
        cressman = table[remo_var].get('cressman', False)
        mask = table[remo_var].get('mask', 'sea')
        logging.info('auxiliary variable: {} is mapped to {}'.format(cf_var, remo_var))
        source = cf_var
        src = var.create_variable(source, datasets)
        mapping_table[remo_var] = Mapping(src, domain, cressman=cressman, mask=mask)
    return mapping_table


def create_mapping_table(datasets, variables, table, domain):
    for remo_var in variables:
        if remo_var in table:
            cressman = table[remo_var].get('cressman', False)
            mask = table[remo_var].get('mask', None)
            source = table[remo_var]['src']
            src = var.create_variable(source, datasets)


def interpolate_horizontal(data, varmap, name):
    if len(data.shape)==3:
        return intf.interp_horiz_3d(data, varmap.lamgm, varmap.phigm, varmap.lamem,
            varmap.phiem, varmap.indii, varmap.indjj, name)
    elif len(data.shape)==2:
        return intf.interp_horiz_2d(data, varmap.lamgm, varmap.phigm, varmap.lamem,
            varmap.phiem, varmap.indii, varmap.indjj, name)


def remap_sst(varmap, datetime):
    state = {} #State()
    tsgm = varmap.src.data_by_date(datetime)

    fakinf = 10000

    print_datinfo('tsgm', tsgm)
    print_datinfo('tsgm.data', tsgm.filled(fill_value=1.e20))
    print_datinfo('tsgm.mask', tsgm.mask)
    blaem = bodlib.blaem
    blagm = bodlib.blagm #_sst
    print_datinfo('blagm', blagm)
    print_datinfo('blaem', blaem)
    print_datinfo('blaem.mask', blaem.mask)
    # the fortran routines can not work with masked arrays, so we have to set the data explicitly
    # fortran will assume 1.e20 as fill value
    tslge = intf.interp_horiz_2d_cm(tsgm.filled(fill_value=1.e20), blagm, blaem, varmap.lamgm, varmap.phigm, varmap.lamem,
            varmap.phiem, varmap.indii, varmap.indjj, 'TSL')
    tswge = intf.interp_horiz_2d_cm(tsgm.filled(fill_value=1.e20), blagm, blaem, varmap.lamgm, varmap.phigm, varmap.lamem,
            varmap.phiem, varmap.indii, varmap.indjj, 'TSW')
    #mask = np.where( blaem > 1.0 - 0.5/fakinf, True, False)
    mask = np.where( blaem == 1.0, True, False)
    #state['TSL'] = np.ma.masked_array(tslge, mask=mask, fill_value=1.e20)
    state['TSL'] = np.array(tslge)
    state['TSW'] = np.ma.masked_array(tswge, mask=mask, fill_value=1.e20)
    print_datinfo('state[\'TSL\']', state['TSL'])
    print_datinfo('state[\'TSW\']', state['TSW'])
    print_datinfo('tslge', tslge)
    print_datinfo('tswge', tswge)
    return state


def remap_ocean(datetime, domain, to_atmo=True):
    # sst.prepare_sst returns the sst interpolated to the
    # atmospheric grid and frequency so we can handle it like every
    # other atmospheric field
    if to_atmo:
        sst_prepared = sst.prepare_sst(datetime)
        sst_ds  = NC4Dataset(sst_prepared)
    else:
        sst_ds  = ds.datastore['tos']
    print_datinfo('sst_prepared', sst_ds.variables['tos'][0])
    src_sst = var.create_variable('tos', sst_ds )
    varmap = Mapping(src_sst, domain)
    return remap_sst(varmap, datetime)


def remap_dynamic(mapping_table, datetime):

    varmap = mapping_table['T']
    akgm = varmap.src.ak
    bkgm = varmap.src.bk
    kpbl = intf.pbl_index(akgm, bkgm)
    logging.debug('pbl index: {}'.format(kpbl))

    logging.info('horizontal interpolation')

    # interpolate basic dynamic variables horizontally
    varname = 'T'
    t_varmap = mapping_table[varname]
    tgm = t_varmap.src.data_by_date(datetime)
    print_datinfo('tgm', tgm)
    tge = interpolate_horizontal(tgm, t_varmap, varname)
    print_datinfo('tge', tge)

    varname = 'PS'
    ps_varmap = mapping_table[varname]
    psgm = ps_varmap.src.data_by_date(datetime)
    print_datinfo('psgm', psgm)
    psge = interpolate_horizontal(psgm, ps_varmap, varname)
    print_datinfo('psge', psge)

    varname = 'U'
    u_varmap = mapping_table[varname]
    ugm = u_varmap.src.data_by_date(datetime)
    print_datinfo('ugm', ugm)
    uge = interpolate_horizontal(ugm, u_varmap, varname)
    print_datinfo('uge', uge)

    varname = 'V'
    v_varmap = mapping_table[varname]
    vgm = v_varmap.src.data_by_date(datetime)
    print_datinfo('vgm', vgm)
    vge = interpolate_horizontal(vgm, v_varmap, varname)
    print_datinfo('vge', vge)

    # additional variables
    fibgm = bodlib.fibgm
    print_datinfo('fibgm', fibgm)
    qdgm  = mapping_table['QD'].data_by_date(datetime).clip(min=0.0)
    qwgm  = mapping_table['QW'].data_by_date(datetime).clip(min=0.0)

    qdgm_le_zero = np.where( qdgm <= 0.0, True, False)
    qdgm = np.where( qdgm_le_zero, 0.0, qdgm)
    qwgm = np.where( qdgm_le_zero, 0.0, qwgm)
    qdgm_or_qwgm_gt_one = np.where( (qdgm > 1.0) | (qwgm > 1.0), True, False)
    qdgm = np.where( qdgm_or_qwgm_gt_one, 0.0, qdgm)
    qwgm = np.where( qdgm_or_qwgm_gt_one, 0.0, qwgm)
    

    print_datinfo('qdgm', qdgm)
    print_datinfo('qwgm', qwgm)
    print_datinfo('akgm', akgm)
    print_datinfo('bkgm', bkgm)
    ficgm = intf.geopotential(fibgm, tgm, qdgm, psgm, akgm, bkgm)
    ficge = interpolate_horizontal(ficgm, t_varmap, 'FIC')
    arfgm = intf.relative_humidity(qdgm, tgm, psgm, akgm, bkgm, qwgm)
    print_datinfo('arfgm', bkgm)
    arfge = interpolate_horizontal(arfgm, t_varmap, 'AREL HUM')

    # additional wind vector for rotation
    uvge = interpolate_horizontal(ugm, v_varmap, 'U')
    vuge = interpolate_horizontal(vgm, u_varmap, 'V')

    # rotation
    logging.info('rotation of wind vector')
    uge_rot, vge_rot = intf.rotate_uv(uge, vge, uvge, vuge, u_varmap.lamem, u_varmap.phiem,
            v_varmap.lamem, v_varmap.phiem, u_varmap.domain['pollon'], u_varmap.domain['pollat'])
    print_datinfo('uge_rot', uge_rot)
    print_datinfo('vge_rot', vge_rot)


    fibem = bodlib.fibem
    fibge = bodlib.fibge
    print_datinfo('fibem', fibem)
    print_datinfo('fibge', fibge)

    # first pressure correction
    logging.info('first pressure correction')
    ps1em = intf.pressure_correction_em(psge, tge, arfge, fibge, fibem, akgm, bkgm, kpbl)
    print_datinfo('ps1em', ps1em)

    # interpolate vertically
    # temperature
    varname = 'T'
    varmap = mapping_table[varname]
    logging.info('vertical interpolation: {}'.format(varname))
    tem = intf.interp_vert(tge, psge, ps1em, varmap.akhgm, varmap.bkhgm, varmap.akhem, varmap.bkhem, varname, kpbl)
    print_datinfo('tem', tem)

    # humidity
    varname = 'RF'
    logging.info('vertical interpolation: {}'.format(varname))
    arfem = intf.interp_vert(arfge, psge, ps1em, t_varmap.akhgm, t_varmap.bkhgm, t_varmap.akhem, t_varmap.bkhem, varname, kpbl)
    print_datinfo('arfem', arfem)

    # second presure interpolation
    logging.info('second pressure correction')
    psem  = intf.pressure_correction_ge(ps1em, tem, arfem, ficge, fibem, t_varmap.akem, t_varmap.bkem)
    print_datinfo('psem', psem)

    # interpolate vertically
    # u-velocity
    varname = 'U'
    varmap = mapping_table[varname]
    logging.info('vertical interpolation: {}'.format(varname))
    uem = intf.interp_vert(uge_rot, psge, psem, varmap.akhgm, varmap.bkhgm, varmap.akhem, varmap.bkhem, varname, kpbl)
    print_datinfo('uem', uem)

    # v-velocity
    varname = 'V'
    varmap = mapping_table[varname]
    logging.info('vertical interpolation: {}'.format(varname))
    vem = intf.interp_vert(vge_rot, psge, psem, varmap.akhgm, varmap.bkhgm, varmap.akhem, varmap.bkhem, varname, kpbl)
    print_datinfo('vem', vem)

    # correction of wind vector
    grid_info = gd.get_info(u_varmap.domain)
    philuem = grid_info[1]
    dlamem  = grid_info[2]
    dphiem  = grid_info[3]
    logging.info('correction of wind vector')
    uem, vem = intf.correct_uv(uem, vem, psem, u_varmap.akem, u_varmap.bkem, philuem, dlamem, dphiem)
    print_datinfo('uem', uem)
    print_datinfo('vem', vem)


    # store results in the atmo state
    atmo = {}# State()
    atmo['T']    = tem
    atmo['U']    = uem
    atmo['V']    = vem
    atmo['PS']   = psem
    atmo['RF']   = arfem

    return atmo


def remap_aux_fields(mapping_table, datetime, mask=False):
    """
    """
    aux = {}#State()
    for remo_var, varmap in mapping_table.items():
        logging.info('horizontal interpolation of {}'.format(remo_var))
        aux[remo_var] = remap_horiz_2d(remo_var, varmap, datetime)
    return aux


def remap_horiz_2d(remo_var, varmap, datetime):
    """Remap a surface field horizontally.
    """
    blaem = bodlib.blaem
    blagm = bodlib.blagm #_sst
    logging.info('horizontal interpolation of {}'.format(remo_var))
    data  = varmap.src.data_by_date(datetime)
    if varmap.cressman:
        remap = intf.interp_horiz_2d_cm(data.filled(fill_value=1.e20), blagm, blaem, varmap.lamgm, varmap.phigm, varmap.lamem,
            varmap.phiem, varmap.indii, varmap.indjj, remo_var)
        print_datinfo(remo_var, remap)
        if varmap.mask == 'land':
            logging.debug('adding land mask')
            mask = np.where( blaem > 0.0, False, True)
            return np.ma.masked_array(remap, mask=mask, fill_value=1.e20)
        elif varmap.mask == 'sea':
            logging.debug('adding sea mask')
            mask = np.where( blaem < 1.0, False, True)
            return np.ma.masked_array(remap, mask=mask, fill_value=1.e20)
        else:
            return np.array(remap)
    else:
        data  = varmap.src.data_by_date(datetime)
        return interpolate_horizontal(data, varmap, remo_var)

