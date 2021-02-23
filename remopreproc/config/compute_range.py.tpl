#!/usr/bin/env python
#SBATCH --job-name=@job_name                 # Specify job name
#SBATCH --partition=@partition               # Specify partition name
#SBATCH --ntasks=1                           # Specify max. number of tasks to be invoked
#SBATCH --cpus-per-task=1  
#SBATCH --mem-per-cpu=@mem_per_cpu           # Specify real memory required per CPU in MegaBytes
#SBATCH --time=@time                         # Set a limit on the total run time
#SBATCH --mail-type=FAIL                     # Notify user by email in case of job failure
#SBATCH --account=@account                   # Charge resources on this project account
#SBATCH --output=@{log_dir}/@{job_name}.o%j    # File name for standard output
#SBATCH --error=@{log_dir}/@{job_name}.o%j     # File name for standard error output

# own template

import sys

sys.path.append("@path")

from driver import init_constants
from exp import ExpVars
from process import run_dynamic
from common import parse_date

configfile = "@configfile"
startdate = parse_date("@startdate")
enddate = parse_date("@enddate")

timerange = (startdate, enddate)

init_constants("@runHomeDir")
ExpVars.init(configfile)

run_dynamic(timerange)


