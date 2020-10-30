"""This module manages output files and functions.
"""

import os

from netCDF4 import Dataset

import datetime as dt
import logging

from .exp import ExpVars
from .constants import GVars
from . import filemanager as fm
from . import datastore as ds
import tarfile

from . import common as cm

current_file = None
output = None



def create_archive(archive, filelist):
    """create a tar archive from a file list.
    """
    tar = tarfile.open(archive, "w")
    for filename in filelist:
        tar.add(filename)
    tar.close()
    return archive



class ForcingFile():

    file_pattern = 'a{id}a{timerange}.nc'
    datetime_fmt = "%Y%m%d%H"

    def __init__(self, id, startdate, output_freq=6, file_freq=None):
        self.id          = id
        self.startdate   = startdate
        self.output_freq = output_freq
        self.filename    = None
        if file_freq is None:
            self.file_freq = self.output_freq
        else:
            self.file_freq = file_freq
        nsteps = self.file_freq // self.output_freq
        self.enddate     = startdate + dt.timedelta(hours=(nsteps-1)*self.output_freq)
        self.filename    = self._create_filename()

    def _create_filename(self):
        if self.enddate == self.startdate:
            timerange = str(self.startdate.strftime(self.datetime_fmt))
        else:
            timerange = '{}-{}'.format(self.startdate.strftime(self.datetime_fmt),
                    self.enddate.strftime(self.datetime_fmt))
        return self.file_pattern.format(id=self.id, timerange=timerange)



class Output():

    def __init__(self, path, file, cal=None):
        self.path = path
        self.file = file
        self.cal  = cal
        self.file_list = []
        self.fw   = self.create_file()
        self.define_variables()

    def create_file(self):
        ak = ExpVars.vc_table['ak'].values
        bk = ExpVars.vc_table['bk'].values
        self.filepath  = os.path.join(self.path, self.file.filename)
        self.file_list.append(self.filepath)
        ncattrs = {'driving_model_'+key : item for key, item in ds.datastore.ref_ds().ncattrs_dict().items()}
        fw   = fm.FileWriter(ds=create_dataset(self.filepath), ncattrs=ncattrs, cal=self.cal)
        fw.def_vc(ak, bk)
        return fw

    def define_variables(self):
        """define variables in the forcing file
        """
        for var in ExpVars.config['output']['variables']:
            items = GVars.var_attrs[var]
            fill_value = items.get('fill_value', False)
            attrs = items.get('attributes', None)
            self.fw.def_ncvar(var, dims=items['dims'], attrs=attrs, fill_value=fill_value)

    def add_date(self, date):
        """add a date to the time variable.
        """
        if not self.fw.date_in_time(date):
            self.fw.add_date(date)

    def write_date(self, date, state):
        """write data by date to current output file.
        """
        new_file = self._check_eof(date)
        self.add_date(date)
        for varname, data in state.items():
            crop = self.crop_data(data)
            cm.print_datinfo(varname, crop)
            logging.debug('writing: {}, {}'.format(varname, type(crop.T)))
            self.fw.write_date(varname, date, crop.T)

    def crop_data(self, data):
        """crops data for output to forcing files.
        """
        shape = data.shape
        if len(shape) == 3:
            return data[1:-1,1:-1,:]
        elif len(shape) == 2:
            return data[1:-1,1:-1]
        else:
            return None

    def _check_eof(self, date):
        """check if we have to create a new file.
        """
        if date > self.file.enddate:
            self.fw.close()
            self.file = init_forcing_file(self.file.id, date, file_freq=self.file.file_freq)
            self.fw = self.create_file()
            self.define_variables()
            return self.filepath
        else:
            return False

    def close(self):
        logging.info('closing file: {}'.format(self.ds.filepath()))
        return None

    def archive(self, date):
        archive_filename = 'a{id}a{date}.tar'.format(id=self.file.id, date=date.strftime("%Y%m") )
        filepath = os.path.join(self.path, archive_filename)
        logging.info('creating archive: {}'.format(filepath))
        create_archive(filepath, self.file_list)
        self.file_list = []




def init_forcing_file(id, startdate, file_freq=None):
    global current_file
    print('creating initial file')
    current_file = ForcingFile(id, startdate, file_freq=file_freq)
    return current_file


def current_forcing_file(datetime):
    global current_file
    if datetime > current_file.enddate:
        print('creating new file')
        id = current_file.id
        output_freq = current_file.output_freq
        file_freq   = current_file.file_freq
        current_file = ForcingFile(id, datetime, output_freq, file_freq)
    return current_file


def init_output(id, path, startdate, domain):
    global output
    logging.debug('output path: {}'.format(path))
    current_file = init_forcing_file(id, startdate, file_freq=6)
    output = Output(path, file=current_file)


def create_dataset(filename):
    logging.info('creating file: {}'.format(filename))
    return ExpVars.domain.get_dataset(filename, mode='w')


