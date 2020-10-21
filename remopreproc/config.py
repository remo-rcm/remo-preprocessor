

import yaml

import pkg_resources


def get_yaml(filename):
    return yaml.load(open(filename), Loader=yaml.FullLoader)


user_config_default_yaml = pkg_resources.resource_filename(__name__, "user-config.yaml")
user_config_default = get_yaml(user_config_default_yaml)

LOG_DIR = 'log'
DFLT_EXPID = '000000'