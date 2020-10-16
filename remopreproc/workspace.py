

import os
import sys


def init_dir(expid, root='.'):
    runHomeDir = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
    workDir = os.path.abspath(os.getcwd())
    print(runHomeDir)
    print(workDir)

def init_workspace(expid, root):
    init_dir(expid, root)

