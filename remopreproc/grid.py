


import pandas as pd


def get_info(domain):
    bb = domain.grid_rotated.get_bounding_box()
    ll_lam = bb[0][0]
    ll_phi = bb[0][1]
    return (ll_lam, ll_phi, domain.dlon, domain.dlat, domain.pollon,
            domain.pollat, domain.nlon+2, domain.nlat+2)

def get_vc_table(filename):
    return pd.from_csv(filename)

