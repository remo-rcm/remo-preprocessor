
import numpy as np
import logging
import yaml


def print_data(name, data):
    logging.debug('{}: shape {}, min {}, max {}'.format( name, data.shape,
            np.min(data), np.max(data)))

def get_yaml(filename):
    return yaml.load(open(filename), Loader=yaml.FullLoader)

def write_yaml(dict, filename):
    with open(filename, 'w') as yaml_file:
        yaml.dump(dict, yaml_file, default_flow_style=False)