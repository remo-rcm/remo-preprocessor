

import pytest


from remopreproc import input 



test_config = "../remopreproc/user-config.yaml"
test_config = "test-config.yaml"


def get_input(configfile):
    input.get_input(configfile)



def test_datastore():
    pass


def test_input():
    get_input(test_config)
