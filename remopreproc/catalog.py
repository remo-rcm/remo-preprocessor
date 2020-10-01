
import logging


try:
    import intake
except:
    print('could not find intake')


class FileCollection():
    """class to manage input file collections.
    """

    def __init__(self):
        self.col = None

    def datasets(self, config):
        dataset_dict = {}
        for key, attrs in config.items():
            logging.debug('key: {}, attrs: {}'.format(key, attrs))
            dataset_dict[key] = self.select(**attrs)
            print(dataset_dict[key])
            print(dataset_dict[key].df)
        return dataset_dict

    def select(self, **kwargs):
        raise NotImplementedError

    def file_list(self, **kwargs):
        raise NotImplementedError



class Intake(FileCollection):
    """class to manage an intake file collection.
    """

    def __init__(self, url, path_col='path', sort_col=None):
        FileCollection.__init__(self)
        self.path_col = path_col
        self.sort_col = sort_col
        self.url = url
        self.col = self.get_collection(self.url)
        print(self.col.df)

    def get_collection(self, url):
        logging.info('reading catalog: {}'.format(url))
        return intake.open_esm_datastore(url)

    def select(self, **kwargs):
        """get a selection from the catalog.
        """
        return self.col.search(**kwargs)

    def file_list(self, **kwargs):
        """returns a sorted file list
        """
        df = self.select(**kwargs).df
        if self.sort_col:
            return list(df.sort_values(by=[self.sort_col])[self.path_col])
        else:
            return list(df[self.path_col])

    def df(self, **kwargs):
        """returns a sorted dataframe
        """
        df = self.select(**kwargs).df
        if self.sort_col:
            return df.sort_values(by=[self.sort_col])
        else:
            return df


class ERA5DRKZ(FileCollection):
    """class to manage ERA5 data at DKRZ.
    """
    def __init__(self):
        FileCollection.__init__(self)
        self.datasets = None



def get_dataset_dict(config, **kwargs):
    dataset_dict = {}
    for varname, attrs in config.items():
        dataset_dict[varname] = get_dataset_by_variable(attrs, varname, **kwargs)
    return dataset_dict
