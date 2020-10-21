
import os
import pkg_resources

import yaml

def get_yaml(filename):
    return yaml.load(open(filename), Loader=yaml.FullLoader)

def write_yaml(filename, dict):
    with open(filename, 'w') as file:
        return yaml.dump(dict, file)


def browse(input_dir):
    dirs = {}
    for dirname, dirnames, filenames in os.walk(input_dir):
        # print path to all subdirectories first.
        for subdirname in dirnames:
            print(os.path.join(dirname, subdirname))
        # print path to all filenames.
        for filename in filenames:
            print(filename)
            project = os.path.basename(dirname)
            input = filename
            filepath = os.path.join(dirname, filename)
            dirs[project] =  {input: filepath}
    return dirs
    

input_gcm_path = pkg_resources.resource_filename(__name__, os.path.join("input", "gcm"))

bodlib = get_yaml(pkg_resources.resource_filename(__name__, os.path.join("input", "bodlib", "bodlib.yaml")))


