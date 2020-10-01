"""compute additional derived fields from interpolated data

python implementation of intorg.bodfld.
"""

import numpy as np

from .constants import *
from .utils import print_data



zds3 = (3.25 - 0.0)/(3.5 - 0.0)
zds4 = (19.2 - 17.5)/(64.0 - 17.5)
zds5 = (77.55 - 64.0)/(194.5 - 64.0)
zdtfak = 0.00065

#def prandtl_thickness(psge, psem):
#    pass
#    dpge = PSGe - (AKGm(:-2) + BKGm(:-2)*PSGe)
#    dpem = PSEm - (AKEm(:-2) + BKEm(:-2)*PSEm)
#    return dpge, dpem


def snow_depth(snge=None):
    pass


def surface_fields(tswge, tslge, blaem, fibge):
    #snem = snge
    #wsem = np.minimum(wsmxem, wsge*wsmxem)
    #wlem = wlge
    iland = np.rint(blaem*fakinf)
    zdts = zdtfak*(fibem - fibge)
    tswem = tswge
    #tslem = np.where( iland == 0, tswge, tslge - zdts)
    td3ge = 0.0
    td4ge = 0.0
    td5ge = 0.0
    tdge  = 0.0

    td3em  = np.where( iland == 0, tswge, tslge - (tslge - td3ge)*zds3 - zdts)
    tslem  = np.where( iland == 0, tswge, td3em)
    tsnem  = np.where( iland == 0, tswge, tslem)

    td4em  = np.where( iland == 0, tswge, td4ge - (td4ge - td5ge)*zds4 - zdts)
    td5em  = np.where( iland == 0, tswge, td5ge - (td5ge - tdge)*zds5 - zdts)
    tdem   = np.where( iland == 0, tswge, td5em)
    tdclem = np.where( iland == 0, tswge, td5em)


def ts_land(tswge, fibem, fibge):
    iland = np.rint(blaem*fakinf)
    zdts = zdtfak*(fibem - fibge)


def soil_layers(tswge, tslge, blaem, fibem, fibge, td3ge=None, td4ge=None, td5ge=None, tdge=None, tsnge=None):
    """derives soil and snow temperature.
    """

    iland = np.rint(blaem*fakinf)
    zdts = zdtfak*(fibem - fibge)

    # check for soil temperatures
    if td3ge is None:
        td3ge = 0.0
    if td4ge is None:
        td4ge = 0.0
    if td5ge is None:
        td5ge = 0.0
    if tdge is None:
        tdge = 0.0

    td3em  = np.where( iland == 0, tswge, tslge - (tslge - td3ge)*zds3 - zdts)
    tslem  = np.where( iland == 0, tswge, td3em)
    if tsnge: # e.g. ECMWF has snow temperatur
        tsnem  = np.where( iland == 0, tswge, tsnge - (tsnge - tslge) * 0.5)
    else:
        tsnem  = np.where( iland == 0, tswge, tslem)

    td4em  = np.where( iland == 0, tswge, td4ge - (td4ge - td5ge)*zds4 - zdts)
    td5em  = np.where( iland == 0, tswge, td5ge - (td5ge - tdge)*zds5 - zdts)
    tdem   = np.where( iland == 0, tswge, td5em)
    tdclem = np.where( iland == 0, tswge, td5em)

    return {'td3em': td3em, 'td4em': td4em, 'td5em': td5em, 'tdem': tdem, 'tdclem': tdclem, 'tsnem': tsnem}


def seaice(tswem):
    """Simple derivation of seaice fraction from SST.

    A simple linear approximation is done if the water temperature is
    between the freezing and the melting point.
    """
    freezing_range = melt - frozen
    seaem = np.ma.masked_array(np.zeros_like(tswem), mask=tswem.mask)
    seaem = np.ma.where( tswem > melt, 0.0, seaem)
    seaem = np.ma.where( tswem < frozen, 1.0, seaem)
    seaem = np.ma.where( (tswem >= frozen) & (tswem <= melt), (melt - tswem) / freezing_range, seaem )

    return seaem


def water_content(arfem, tem, psem, akem, bkem):
    """computes qd (specific humidity) and qw (liquid water) from relative humidty (arfem).

    Python implementation of original Fortran source in `addem`.
    """
    # pressure height?!
    #phem = 0.5*(AKEm(k) + AKEm(k + 1) + (BKEm(k) + BKEm(k + 1))*PSEm(ij))
    #IF ( TEM(ij, k)>=B3 ) THEN
    #  zgqd = FGQD(FGEW(TEM(ij, k)), phem)
    #ELSE
    #  zgqd = FGQD(FGEE(TEM(ij, k)), phem)
    #END IF
    #zqdwem = ARFem(ij, k)*zgqd
    #IF ( ARFem(ij, k)<1.0_DP ) THEN
    #  QDEm(ij, k) = zqdwem
    #  QWEm(ij, k) = 0.
    #ELSE
    #  QDEm(ij, k) = zgqd
    #  QWEm(ij, k) = zqdwem - zgqd
    #END IF
    qdem = np.zeros(arfem.shape, dtype=arfem.dtype)
    qwem = np.zeros(arfem.shape, dtype=arfem.dtype)
    print_data('arfem', arfem)
    print_data('qdem', qdem)
    print_data('qwem', qdem)
    for k in range(arfem.shape[2]):
        print(k, B3)
        phem = 0.5 * (akem[k] + akem[k+1] + (bkem[k]+bkem[k+1]) * psem)
        print_data('tem',tem[:,:,k])
        zgqd = np.where(tem[:,:,k] >= B3, fgqd( fgew(tem[:,:,k]), phem ), fgqd( fgee(tem[:,:,k]), phem) )
        zqdwem = arfem[:,:, k] * zgqd
        print_data('zqdwem',zqdwem)
        print_data('arfem',arfem[:,:,k])
        qdem[:,:,k] = np.where( arfem[:,:,k] < 1.0, zqdwem, zgqd )
        qwem[:,:,k] = np.where( arfem[:,:,k] < 1.0, 0.0, zqdwem - zgqd )

    print_data('qdem', qdem)
    print_data('qwem', qwem)

    return qdem, qwem


def tsw(tswge):
    tswem = np.ma.where( tswge < frozen, frozen, tswge)
    return tswem

def tsi(tswge):
    tsiem = np.ma.where( tswge > frozen, frozen, tswge)
    return tsiem



# STATEMENTFUNKTION FUER SAETTIGUNGSDAMPFDRUCK
def fgew(tx):
    """magnus formula
    """
    return B1 * np.exp(B2W*(tx - B3)/(tx - B4W))

def fgee(tx):
    """magnus formula
    """
    return B1 * np.exp(B2E*(tx - B3)/(tx - B4E))

def fgqd(ge, p):
    """magnus formula
    """
    return RDRd*ge / (p - EMRdrd*ge)
