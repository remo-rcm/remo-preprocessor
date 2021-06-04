#!/usr/bin/env python
#SBATCH --job-name=@job_name                 # Specify job name
#SBATCH --partition=@partition               # Specify partition name
#SBATCH --ntasks=1                           # Specify max. number of tasks to be invoked
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=@mem_per_cpu           # Specify real memory required per CPU in MegaBytes
#SBATCH --time=@time                         # Set a limit on the total run time
#SBATCH --mail-type=FAIL                     # Notify user by email in case of job failure
#SBATCH --account=@account                   # Charge resources on this project account
#SBATCH --output=@{log_dir}/@{job_name}.o%j    # File name for standard output
#SBATCH --error=@{log_dir}/@{job_name}.o%j     # File name for standard error output

# own template

import sys
import logging

from remopreproc.exp import ExpVars
from remopreproc.process import run_dynamic
from remopreproc.common import parse_date


# logger configuration
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s | %(levelname)8s | %(module)10s | %(funcName)20s | %(message)s')


configfile = "@configfile"
startdate = parse_date("@startdate")
enddate = parse_date("@enddate")

timerange = (startdate, enddate)

ExpVars.init(configfile)

run_dynamic(timerange)


