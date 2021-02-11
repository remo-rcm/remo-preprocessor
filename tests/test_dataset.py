

import os
import pytest

from remopreproc import dataset as rds

import datetime as dt

filenames = [
"output1/IPSL/IPSL-CM5A-MR/historical/6hr/atmos/6hrLev/r1i1p1/v20120114/ta/ta_6hrLev_IPSL-CM5A-MR_historical_r1i1p1_1850010103-1859123121.nc",
"output1/IPSL/IPSL-CM5A-MR/historical/6hr/atmos/6hrLev/r1i1p1/v20120114/ta/ta_6hrLev_IPSL-CM5A-MR_historical_r1i1p1_1860010103-1869123121.nc",
"output1/IPSL/IPSL-CM5A-MR/historical/6hr/atmos/6hrLev/r1i1p1/v20120114/ta/ta_6hrLev_IPSL-CM5A-MR_historical_r1i1p1_1870010103-1879123121.nc",
"output1/IPSL/IPSL-CM5A-MR/historical/6hr/atmos/6hrLev/r1i1p1/v20120114/ta/ta_6hrLev_IPSL-CM5A-MR_historical_r1i1p1_1880010103-1889123121.nc",
"output1/IPSL/IPSL-CM5A-MR/historical/6hr/atmos/6hrLev/r1i1p1/v20120114/ta/ta_6hrLev_IPSL-CM5A-MR_historical_r1i1p1_1890010103-1899123121.nc",
"output1/IPSL/IPSL-CM5A-MR/historical/6hr/atmos/6hrLev/r1i1p1/v20120114/ta/ta_6hrLev_IPSL-CM5A-MR_historical_r1i1p1_1900010103-1909123121.nc",
"output1/IPSL/IPSL-CM5A-MR/historical/6hr/atmos/6hrLev/r1i1p1/v20120114/ta/ta_6hrLev_IPSL-CM5A-MR_historical_r1i1p1_1910010103-1919123121.nc",
"output1/IPSL/IPSL-CM5A-MR/historical/6hr/atmos/6hrLev/r1i1p1/v20120114/ta/ta_6hrLev_IPSL-CM5A-MR_historical_r1i1p1_1920010103-1929123121.nc",
"output1/IPSL/IPSL-CM5A-MR/historical/6hr/atmos/6hrLev/r1i1p1/v20120114/ta/ta_6hrLev_IPSL-CM5A-MR_historical_r1i1p1_1930010103-1939123121.nc",
"output1/IPSL/IPSL-CM5A-MR/historical/6hr/atmos/6hrLev/r1i1p1/v20120114/ta/ta_6hrLev_IPSL-CM5A-MR_historical_r1i1p1_1940010103-1949123121.nc",
"output1/IPSL/IPSL-CM5A-MR/historical/6hr/atmos/6hrLev/r1i1p1/v20120114/ta/ta_6hrLev_IPSL-CM5A-MR_historical_r1i1p1_1950010103-1959123121.nc",
"output1/IPSL/IPSL-CM5A-MR/historical/6hr/atmos/6hrLev/r1i1p1/v20120114/ta/ta_6hrLev_IPSL-CM5A-MR_historical_r1i1p1_1960010103-1969123121.nc",
"output1/IPSL/IPSL-CM5A-MR/historical/6hr/atmos/6hrLev/r1i1p1/v20120114/ta/ta_6hrLev_IPSL-CM5A-MR_historical_r1i1p1_1970010103-1979123121.nc",
"output1/IPSL/IPSL-CM5A-MR/historical/6hr/atmos/6hrLev/r1i1p1/v20120114/ta/ta_6hrLev_IPSL-CM5A-MR_historical_r1i1p1_1980010103-1989123121.nc",
"output1/IPSL/IPSL-CM5A-MR/historical/6hr/atmos/6hrLev/r1i1p1/v20120114/ta/ta_6hrLev_IPSL-CM5A-MR_historical_r1i1p1_1990010103-1999123121.nc",
"output1/IPSL/IPSL-CM5A-MR/historical/6hr/atmos/6hrLev/r1i1p1/v20120114/ta/ta_6hrLev_IPSL-CM5A-MR_historical_r1i1p1_2000010103-2005123121.nc" ]


#root = '/work/kd0956/CMIP5/data/cmip5'
root = 'http://esgf1.dkrz.de/thredds/dodsC/cmip5/cmip5'

filenames = [ os.path.join(root, f) for f in filenames ]



def test_dataset():
    ds = rds.NC4Dataset(filenames)
    date = dt.datetime(1850,1,1,3,0,0)
    assert ds.get_index_by_date(date) == 0
    assert ds.dynamic('ta')


if __name__ == "__main__":
    test_dataset() 
