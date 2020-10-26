

import pytest

from remopreproc import exp
from remopreproc import catalog as cat


test_config = "test-config.yaml"



def test_catalog(var):
    exp.load_config(test_config)
    url = exp.ExpVars.config_input_project_data['catalog']['url']
    catalog = cat.Intake(url)
    print(catalog)
    attrs = exp.ExpVars.gcm_var_attrs[var] 
    sel = catalog.select(**attrs)
    print(sel.df)
    da = sel.to_dataset_dict()['CMIP.MPI-M.MPI-ESM1-2-HR.historical.6hrLev.gn'][var]
    print(da)
    da_t = da.sel(time="2000-01-01T06:00:00")
    print(da_t.shape)
    return da_t






if __name__ == "__main__":
   var_t = test_catalog('ta')
