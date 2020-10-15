
import os
import pkg_resources

import yaml

def get_yaml(filename):
    return yaml.load(open(filename), Loader=yaml.FullLoader)

bodlib = get_yaml(pkg_resources.resource_filename(__name__, "input/bodlib/bodlib.yaml"))


def browse(input_dir):
    for dirname, dirnames, filenames in os.walk(input_dir):
        # print path to all subdirectories first.
        for subdirname in dirnames:
            print(os.path.join(dirname, subdirname))
        # print path to all filenames.
        for filename in filenames:
            print(os.path.join(dirname, filename))




input_gcm_path = pkg_resources.resource_filename(__name__, "input/gcm")

