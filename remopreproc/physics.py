"""compute additional fields dervived from interpolated fields
"""


from pyintorg import physics
from .exp import ExpVars
from . import common as cm
import logging
from . import static_data as sd


def soil_layers(state):
#    if 'TD' not in state:
    tswem = state['TSW']
    tslem = state['TSL']
    td3ge = state.get('TD3', None)
    td4ge = state.get('TD4', None)
    td5ge = state.get('TD5', None)
    tdge = state.get('TD', None)
    cm.print_datinfo('TSW', tswem)
    cm.print_datinfo('TSL', tslem)
    #cm.print_datinfo('td3ge', td3ge)
    #cm.print_datinfo('td4ge', td4ge)
    #cm.print_datinfo('td5ge', td5ge)
    #cm.print_datinfo('tdge', tdge)
    logging.info('adding soil layers')
    soil = physics.soil_layers(tswem, tslem, sd.bodlib.blaem, sd.bodlib.fibem, sd.bodlib.fibge, td3ge, td4ge, td5ge, tdge )
    for field, data in soil.items():
        cm.print_datinfo(field, data)
    state['TD3'] = soil['td3em']
    state['TD4'] = soil['td4em']
    state['TD5'] = soil['td5em']
    state['TD'] = soil['tdem']
    state['TDCL'] = soil['tdclem']
    return state


def ocean_physics(state):
    """derive additional data from sst.
    """
    #tswem  = physics.tsw(state['TSW'])
    #tslem  = physics.tsw(state['TSL'])
    tswem  = state['TSW']
    tslem  = state['TSL']
    if 'SEAICE' not in state:
        logging.info('deriving SEAICE from TSW...')
        #seaice = physics.seaice(state['TSW'])
        state['SEAICE'] = physics.seaice(state['TSW'])
    #state['TSW'] = tswem
    #state['TSL'] = tslem
    state['TSI'] = physics.tsi(state['TSW'])
    return state


def water_content(state):
    arfem  = state['RF']
    tem = state['T']
    psem = state['PS']
    ak = ExpVars.vc_table['ak'].values
    bk = ExpVars.vc_table['bk'].values
    qdem, qwem = physics.water_content(arfem, tem, psem, ak, bk)
    state['QD'] = qdem
    state['QW'] = qwem
    state['QDBL'] = qdem[:,:,-1] # last layer will be used for QDBL
    return state
