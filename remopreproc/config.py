

import yaml

import pkg_resources


def get_yaml(filename):
    return yaml.load(open(filename), Loader=yaml.FullLoader)


user_config_default_yaml = pkg_resources.resource_filename(__name__, "config/user-config.yaml")
user_config_default = get_yaml(user_config_default_yaml)

LOG_DIR = 'log'
INPUT_DIR = 'input'
DFLT_EXPID = '000000'


#logging = get_yaml(pkg_resources.resource_filename(__name__, "config/logging.yaml"))
scheduler = get_yaml(pkg_resources.resource_filename(__name__, "config/scheduler.yaml"))


job_tpl = pkg_resources.resource_filename(__name__, "config/compute_range.py.tpl")
