"""this module handles relative (cf-standard) and absolute calendars (for a-files.)
"""

import cftime
import datetime as dt
import logging
import math

calendar = None

# roundTime from here:
# https://stackoverflow.com/questions/3463930/how-to-round-the-minute-of-a-datetime-object-python
def roundTime(datetime=None, roundTo=1):
   """Round a datetime object to any time lapse in seconds
   dt : datetime.datetime object, default now.
   roundTo : Closest number of seconds to round to, default 1 minute.
   Author: Thierry Husson 2012 - Use it as you want but don't blame me.
   """
   if datetime == None : datetime = dt.datetime.now()
   seconds = (datetime.replace(tzinfo=None) - datetime.min).seconds
   rounding = (seconds+roundTo/2) // roundTo * roundTo
   return datetime + dt.timedelta(0,rounding-seconds,-datetime.microsecond)



class Calendar():
    """Calendar class for handling relative CF-calendars.

    Units will need to contain the 'since' keyword and a startdate.
    These calendars can be handles usind the netCDF4 date2num, num2date, etc.
    """

    def __init__(self, ds):
        self.cal_ds = ds

    def index_by_datetime(self, datetime):
        return self.cal_ds.get_index_by_date(datetime)

    def datetime_by_index(self, index):
        return self.cal_ds.get_date_by_index(index)

    def get_first_date(self):
        return self.cal_ds.get_date_by_num(0)

    def ncattrs_dict(self):
        time = self.cal_ds.time_axis
        return self.cal_ds.ncattrs_dict(varname=time)

    def get_julian_day(self, date):
        return cftime.JulianDayFromDate(date, calendar=self.cal_ds.calendar)

    def convert_to_cftime(self, date):
        datetype = type(self.get_first_date())
        return datetype(date.year, date.month, date.day, date.hour, date.minute, date.second)



class AbsoluteCalendar():
    """Absolute calendar to handle absolute dates.

    Forcing Files will probably contain absolute dates. This is not cf-standard so
    we handle this manually (not using the netCDF4 num2date/date2num, those work only
    for cf-convetions.).
    """

    def __init__(self, units=None, calendar=None):
        if units is None:
            self.units = 'day as %Y%m%d.%f'
        if calendar is None:
            self.calendar = 'proleptic_gregorian'
        self.fmt = '%Y%m%d'#self.units.split()[2]

    def ncattrs_dict(self):
        return {'standard_name': 'time', 'units': self.units,
                'calendar':self.calendar, 'axis': 'T'}

    def date2num(self, datetime):
        """convert a datetime object to an absolute numeric date value.
        """
        delta = dt.timedelta(hours=datetime.hour, minutes=datetime.minute,
                seconds=datetime.second)
        frac = delta.total_seconds()/dt.timedelta(days=1).total_seconds()
        return float(datetime.strftime(self.fmt)) + frac

    def num2date(self, num):
        """convert a numeric absolute date value to a datetime object.
        """
        frac, whole = math.modf(num)
        date_str = str(whole)
        date = dt.datetime.strptime(date_str, self.fmt)
        return roundTime(date + dt.timedelta(seconds = dt.timedelta(days=1).total_seconds() * frac))


def check_calendar(dataset_dict):
    """Check if all calendars in the datasets are consistent.
    """
    units = []
    cals  = []
    for varname,ds in dataset_dict.items():
        logging.debug('variable: {}'.format(varname))
        logging.debug('units: {}'.format(ds.units))
        logging.debug('calendar: {}'.format(ds.calendar))
        if ds.units not in units:
            units.append(ds.units)
        if ds.calendar not in cals:
            cals.append(ds.calendar)
    if len(units) != 1 or len(cals) != 1:
        print('found units: {}'.format(units))
        print('found calendars: {}'.format(cals))
        raise Exception('different calendars in input datasets!')
    return units[0], cals[0]


def init_calendar(cal_ds, units='relative'):
    global calendar
    calendar = Calendar(cal_ds)
