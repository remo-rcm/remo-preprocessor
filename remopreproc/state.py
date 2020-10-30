



class State():

    def __init__(self):
        self.variables = {}

    def __getitem__(self, key):
        return self.variables[key]

    def __setitem__(self, key, item):
        self.variables[key] = item

    def __iter__(self):
        return iter(self.variables)

    def get_data(self, varname):
        shape = self.variables[varname].shape
        if len(shape) == 3:
            return self.variables[varname][1:-1,1:-1,:]
        elif len(shape) == 2:
            return self.variables[varname][1:-1,1:-1]
        else:
            return None


def init_state(state, variables):
    return state
