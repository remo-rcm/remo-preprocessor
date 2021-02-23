
import os
import logging
from .common import get_config
from . import constants
import subprocess
from .constants import GVars,Template
from configobj import ConfigObj
#from PyRemo.Scheduler import Scheduler
from hpc_scheduler import Scheduler
import pandas as pd
from . import exp
from .workspace import Workspace as ws

from . import config as cfg

# interface module to PyRemo.Scheduler

# use global logger by default
#logger = logging

SYS = 'SLURM'

# date format for jobscripts
date_fmt = '%Y-%m-%dT%H:%M:%S'

def create_scheduler(name):
    btc_cfg = cfg.scheduler #get_config(GVars.btc_cfg, silent=True)
    run_tpl = cfg.job_tpl #os.path.join(GVars.tplDir,btc_cfg['scheduler']['serial_template'])
    logfile = None #os.path.join(GVars.logDir,name+'.jobids.ini')
    scheduler = Scheduler(SYS,name=name,tpl=run_tpl,logfile=logfile)
    return scheduler


def add_job(sc,jobname,config,submit=False):
    btc_cfg = cfg.scheduler #get_config(GVars.btc_cfg, silent=True)
    fill    = btc_cfg['scheduler']
    fill['log_dir']  = ws.logdir
    fill['runHomeDir']  = 'None'  #GVars.runHomeDir
    fill['job_name'] = jobname
    fill = {**fill, **config}

    jobscript = os.path.join(ws.jobdir,jobname+'.py') 

    sc.create_job(jobname=jobname,jobscript=jobscript,
                  header_dict=fill,
                  write=True)



def chunk_ranges(timerange, chunks, freq='6h'):
    total_range = pd.date_range(timerange[0], timerange[1], freq=chunks)
    ranges = []
    for startdate in total_range:
        ranges.append(pd.date_range(startdate, periods=2, freq=chunks))
    #chunked_ranges = []
    #for date_range in ranges:
    #    chunked_ranges.append( pd.date_range(date_range.min(), date_range.max(), freq=freq) )
    return ranges


def create_jobscript(scheduler, timerange):
    configfile = exp.ExpVars.user_config
    config = {'configfile': configfile,
              'startdate' : str(timerange[0].strftime(date_fmt)),
              'enddate'   : str(timerange[1].strftime(date_fmt)),
              'path'      : 'path'}
    jobname = 'preprocess_{}-{}'.format(timerange[0].strftime(date_fmt), timerange[1].strftime(date_fmt))
    add_job(scheduler, jobname, config)

def create_jobscripts(sub_ranges):
    scheduler = create_scheduler('preprocess')
    for sub_range in sub_ranges:
        create_jobscript(scheduler, (sub_range.min(),sub_range.max()))

#def get_job(varname,commands,jobname,submit=False):
#    btc_cfg = get_config(GVars.btc_cfg, silent=True)
#    run_tpl = os.path.join(GVars.tplDir,btc_cfg['scheduler']['serial_template'])
#    fill    = btc_cfg['scheduler']
#    fill['log_dir'] = GVars.logDir
#
#    jobscript = os.path.join(GVars.scpDir,jobname+'.sh') 
#
#    user_fill = {'command':commands, 'job_name':jobname}
#    fill.update(user_fill)
#
#    job = Scheduler.Job(SYS,jobname=jobname,jobscript=jobscript,
#                        commands=commands,header_dict=fill)
#    job.write_jobscript() 
#    #job.submit()
#    return job 

    #sc.add_job(jobname,jobscript,commands,fill) 


