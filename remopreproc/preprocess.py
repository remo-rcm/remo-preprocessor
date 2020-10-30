#!/usr/bin/env python

from logging.config import fileConfig
import logging
import colored

import sys

import argparse
import os

import PyRemo.f90nml as f90nml
from   PyRemo.ScriptTools import text_from_tmplt

# global variables hold GVars
from constants import GVars
from configobj import ConfigObj
import constants

from process import process_parser
from check import check_parser
from driver import run_parser, init_constants
from input import input_parser

path = os.path.dirname(constants.__file__)
print(path)

# main
if __name__ == '__main__':

    """main program
    Main program to control all steps. It initializes global
    variables depending on the system and user, initializes
    the command line parser and calls the step chosen by the user.

    Written by Lars Buntemeyer

    """


    # create main and subparsers
    parser = argparse.ArgumentParser(description=constants.DESCRIPTION, epilog=constants.EPILOG)
    subparsers = parser.add_subparsers(dest='subparser', description='Available Sub-Commands.')
    parser.set_defaults(func=None)

    # init subparsers
    input_parser(subparsers)
    run_parser(subparsers)
#    process_parser(subparsers)
    check_parser(subparsers)
    #retrieve_parser(subparsers)
    #prepare_parser(subparsers)
    #cmorize_parser(subparsers)
    #check_parser(subparsers)

    # get arguments
    args = parser.parse_args()
    kwargs = vars(parser.parse_args())


    # runHomeDir is the parent of directory having cmor.py 
    runHomeDir = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
    init_constants(runHomeDir)
    ## runHomeDir is the parent of directory having cmor.py 
    #runHomeDir = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
    ## init constants and user specifics from environment
    #GVars.init(runHomeDir)
    sys.path.append(GVars.binDir)

    ## create some directories
    #if not os.path.exists(GVars.logDir):
    #  os.makedirs(GVars.logDir)
    #if not os.path.exists(GVars.scpDir):
    #  os.makedirs(GVars.scpDir)

    ## initialize logger
    #logPath  = runHomeDir
    #initialize_logger(logPath)
    #GVars.log()

    ## log python version
    #logging.info('Using Python version ' + sys.version)

    # execute (the function to call is part of the arguments)
    logging.info('Calling: ' + args.func.__name__)
    if args.func:
      args.func(args)











