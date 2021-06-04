


import pandas as pd
from pyremo import domain as dm


def domain_info(domain):
    return dm.domain_info(domain)

def get_info(domain_info):
    #bb = domain.grid_rotated.get_bounding_box()
    #domain_info = dm.domain_info(short_name)
    ll_lam = domain_info['ll_lon']
    ll_phi = domain_info['ll_lat']
    dlon = domain_info['dlon']
    dlat = domain_info['dlat']
    pollon = domain_info['pollon']
    pollat = domain_info['pollat']
    nlon = domain_info['nlon']
    nlat = domain_info['nlat']
    return (ll_lam, ll_phi, dlon, dlat, pollon,
            pollat, nlon+2, nlat+2)


def get_vc_table(filename):
    return pd.from_csv(filename)


def load_domain(short_name):
    return dm.remo_domain(short_name)
