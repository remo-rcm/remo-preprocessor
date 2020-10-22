


from cdo import Cdo
from .cache_deco import cached
import pandas as pd


class Cmorizer():

    codemap   = {130: 'ta', 134: 'ps', 131: 'ua', 132: 'va',
                 133: 'hus',  34 : 'tos',  31 :'sic',  129 : 'orog',
                 172: 'sftlf', 139: 'tsl1', 170: 'tsl2', 183: 'tsl3',
                 238: 'tsn', 236: 'tsl4', 246: 'clw', 141: 'snw', 198: 'src' }

    def __init__(self):
        self.cdo = Cdo(logging=True)

    @cached
    def _to_regular(self, filename):
        """converts ecmwf spectral grib data to regular gaussian netcdf.

        cdo is used to convert ecmwf grid data to netcdf depending on the gridtype:
        For 'gaussian_reduced': cdo setgridtype,regular
            'spectral'        : cdo sp2gpl

        This follows the recommendation from the ECMWF Era5 Documentation.
        We also invert the latitudes to stick with cmor standard.

        """
        gridtype = self._gridtype(filename)
        if gridtype == 'gaussian_reduced':
            #return self.cdo.copy(options='-R -f nc', input=filename)
            gaussian = self.cdo.setgridtype('regular', options='-f nc', input=filename)
        elif gridtype == 'spectral':
            gaussian = self.cdo.sp2gpl(options='-f nc', input=filename)
        elif gridtype == 'gaussian':
            gaussian =  self.cdo.copy(options='-f nc', input=filename)
        else:
            raise Exception('unknown grid type for conversion to regular grid: {}'.format(gridtype))
        return self.cdo.invertlat(input=gaussian)

    @cached
    def _nc_convert(self, filename):
        regular = self._to_regular(filename)
        if self.code in self.codemap:
            return self.cdo.setname(self.codemap[self.code], input=regular)
        else:
            return regular

    def _gridtype(self, filename):
        griddes = self.cdo.griddes(input=filename)
        griddes = {entry.split('=')[0].strip():entry.split('=')[1].strip() for entry in griddes if '=' in entry}
        return griddes['gridtype']

    def _get_code(self, filename):
        showcode = self.cdo.showcode(input=filename)
        print(showcode)
        return showcode



class FileManager():

    date_fmt = "%Y-%m-%dT%H:%M:%S"

    def __init__(self, df):
        self.df = df
        self.df['startdate'] = pd.to_datetime(self.df['startdate'])
        self.df['enddate'] = pd.to_datetime(self.df['enddate'])
        self.cmor = Cmorizer()
        self.cdo = Cdo(logging=True)

    @property
    def file_list(self):
        return self.df['path'].values

    @property
    def code(self):
        """returns code from dataframe, should be unique
        """
        code = self.df['code'].unique()
        if len(code) == 1:
            return code[0]
        else:
            raise Exception('code is not unique in file list')

    @cached
    def tmp_file_by_date(self, datetime, nc=True):
        filename = self.get_file_by_date(datetime)
        date_str = datetime.strftime(self.date_fmt)
        logging.debug('selecting {} from {}'.format(date_str, filename))
        if nc:
            return self.cmor._nc_convert( self.cdo.seldate(date_str, input=filename ) )
        else:
            return self.cdo.seldate(date_str, input=filename )

    def get_file_by_date(self, datetime):
        """search for a file in the dataframe that should contain the datetime.
        """
        df = self.df[ (datetime >= self.df['startdate']) & (datetime <= self.df['enddate']) ]
        if len(df['path'].values) == 0:
            raise Exception('no files found for {}'.format(datetime))
        elif len(df['path'].values) > 1:
            raise Exception('date selection must be unique')
        else:
            return df['path'].values[0]

    def _ref_file(self, filename=None, nc=True):
        """the reference dataset is used to access dataset attributes.

        This is required to give the preprocessor acces to, e.g., grid
        and calendar information.
        """
        if filename is None:
            filename = self.file_list[0]
        logging.info('getting reference dataset from {}'.format(filename))
        if nc:
            return self._nc_convert( self._reftimestep( filename ) )
        else:
            return self._reftimestep( filename )
