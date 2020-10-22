
"""Declares global symbols and constants for use in cmor modules"""

# Symbols exported to main namespace for those who want it
__all__ = ["GVars"]

import os
import sys
import socket
import logging
from string import Template
from configobj import ConfigObj


import yaml

### main constants
PROGNAME = 'preprocessor'

CDO      = 'cdo'

CUR_DIR = os.path.abspath(os.getcwd())


INF_TPL = 'cdocmorinfo.tpl.txt'
GLB_ATT = 'global-attributes.ini'

DATE_FMT = '%Y-%m-%dT%H:%M:%S'

# available definitions of time frequencies
TIME_FREQ = ['day','mon','sem','6hr','3hr','1hr','fx']

# constant directory names
MAP_DIR                = 'mapping'
USR_DIR                = 'user'
BIN_DIR                = 'bin'
CFG_DIR                = 'config'
TPL_DIR                = 'templates'
PRJ_DIR                = 'projects'
SCP_DIR                = 'scripts'
LOG_DIR                = 'log'
VCT_DIR                = 'vc-table'
CMR_DIR                = 'cmor-meta'
DMN_DIR                = 'domains'
DYN_DIR                = 'dynamic'
INP_DIR                = 'input'
OUT_DIR                = 'output'

MAP_DIR                = 'mapping'
MIP_DIR                = 'mip'
# REMO Mapping table default name
MT_TABLE               = 'mtREMO.txt'

# constant default configs
LOG_CFG                = 'logging.ini'
BTC_CFG                = 'scheduler.ini'
IO_CFG                 = 'io.ini'
CF_SPEC                = 'cf-variables.spec.ini'

EXP_TPL                = 'exp.tpl.ini'
DAT_REQ                = 'data-request.ini'
PRJ_CFG                = 'project.ini'
VAR_CFG                = 'variables.yaml'
BDL_CFG                = 'bodlib.yaml'

GCM_DIR                = os.path.join(INP_DIR,'gcm')
VCT_DIR                = os.path.join(INP_DIR,'vc_table')
BDL_DIR                = os.path.join(INP_DIR,'bodlib')
FRC_DIR                = os.path.join(OUT_DIR,'forcing')

GLB_DIR                = os.path.join(CMR_DIR,'global-attributes')
TBL_DIR                = os.path.join(CMR_DIR,'tables')

DM_DMN                 = os.path.join(GLB_DIR,'driving_model')
DE_DMN                 = os.path.join(GLB_DIR,'driving_experiment')
GR_DMN                 = os.path.join(GLB_DIR,'domain')
IN_DMN                 = os.path.join(GLB_DIR,'institute')
MO_DMN                 = os.path.join(GLB_DIR,'model')


######### Global Variables

class GVarsClass:
    """Stores Global variables (visible to most of the code)."""

    def init(self,runHomeDir):
        # we should always use absolute pathes, it's safer
        # constant directory names
        self.runHomeDir = runHomeDir
        self.binDir = os.path.join(self.runHomeDir, BIN_DIR)
        self.usrDir = os.path.join(self.runHomeDir, USR_DIR)
        self.mapDir = os.path.join(self.runHomeDir, MAP_DIR)
        self.dmnDir = os.path.join(self.runHomeDir, DMN_DIR)
        self.cfgDir = os.path.join(self.runHomeDir, CFG_DIR)
        self.tplDir = os.path.join(self.runHomeDir, TPL_DIR)
        self.scpDir = os.path.join(self.runHomeDir, SCP_DIR)
        self.logDir = os.path.join(self.runHomeDir, LOG_DIR)
        self.cmrDir = os.path.join(self.runHomeDir, CMR_DIR)
        self.prjDir = os.path.join(self.runHomeDir, PRJ_DIR)
        self.glbDir = os.path.join(self.runHomeDir, GLB_DIR)
        self.tblDir = os.path.join(self.runHomeDir, TBL_DIR)
        self.tblDir = os.path.join(self.runHomeDir, TBL_DIR)
        self.tblDir = os.path.join(self.runHomeDir, TBL_DIR)
        self.gcmDir = os.path.join(self.runHomeDir, GCM_DIR)
        self.vctDir = os.path.join(self.runHomeDir, VCT_DIR)
        self.frcDir = os.path.join(self.runHomeDir, FRC_DIR)
        self.bdlDir = os.path.join(self.runHomeDir, BDL_DIR)

        self.dmDmnDir = os.path.join(self.runHomeDir, DM_DMN)
        self.deDmnDir = os.path.join(self.runHomeDir, DE_DMN)
        self.grDmnDir = os.path.join(self.runHomeDir, GR_DMN)
        self.inDmnDir = os.path.join(self.runHomeDir, IN_DMN)
        self.moDmnDir = os.path.join(self.runHomeDir, MO_DMN)

        # constant default configs
        self.log_cfg = os.path.join(self.cfgDir, LOG_CFG)
        self.btc_cfg = os.path.join(self.cfgDir, BTC_CFG)
        self.var_cfg = os.path.join(self.frcDir, VAR_CFG)
        self.stc_cfg = os.path.join(self.bdlDir, BDL_CFG)

        self.userid  = os.getenv('USER')
        self.scratch = os.getenv('SCRATCH')
        self.work    = os.getenv('WORK')
        self.home    = os.getenv('HOME')
        self.host    = socket.gethostname()

        self.scheduler = ConfigObj(self.btc_cfg)
        #self.dynvars   = ConfigObj(self.dyn_cfg)
        self.var_attrs = yaml.load(open(self.var_cfg), Loader=yaml.FullLoader)
        self.stcvars   = yaml.load(open(self.stc_cfg), Loader=yaml.FullLoader)

        cwd = os.getcwd()
        os.chdir(cwd)

    def log(self):
        logging.info("USERID  : "+str(self.userid))
        logging.info("SCRATCH : "+str(self.scratch))
        logging.info("WORK    : "+str(self.work))
        logging.info("HOME    : "+str(self.home))
        logging.info("HOST    : "+str(self.host))
        logging.info("variables    : "+str(self.var_attrs))



class Template(Template):
     delimiter = '@'



DESCRIPTION = "The preprocessor for remapping gcm data to REMO forcing files."

EPILOG      = " In case of problems, contact: lars.buntemeyer@hzg.de"

############################################################################# 
##################### initialization code   ################################# 
############################################################################# 

GVars = GVarsClass()

