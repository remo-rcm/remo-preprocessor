
import numpy as np
import logging

def print_data(name, data):
    logging.debug('{}: shape {}, min {}, max {}'.format( name, data.shape,
            np.min(data), np.max(data)))
