import pickle
import os


import inspect

class key_memoized(object):
    def __init__(self, func):
       self.func = func
       self.cache = {}

    def __call__(self, *args, **kwargs):
        key = self.key(args, kwargs)
        if key not in self.cache:
            self.cache[key] = self.func(*args, **kwargs)
            print(self.cache)
        else:
            print('using cached value')
        return self.cache[key]

    def normalize_args(self, args, kwargs):
        spec = inspect.getargs(self.func.__code__).args
        return dict(**kwargs, **dict(zip(spec, args)))
        #return dict(kwargs.items() + zip(spec, args))

    def key(self, args, kwargs):
        a = self.normalize_args(args, kwargs)
        return tuple(sorted(a.items()))


def cached(func):
    """memorizer decorator function to cache temporary results.
    """
    cache = dict()

    def memoized_func(*args):
        if args in cache:
            return cache[args]
        result = func(*args)
        cache[args] = result
        return result

    return memoized_func


#def disk_cached(cachefile=False):
#    """memorizer decorator function to cache temporary results.
#    """
#    cache = dict()
#    if cachefile:
#        # load from file
#        if os.path.isfile(cachefile):
#            with open(cachefile, 'rb') as handle:
#                cache = pickle.load(handle)
#
#    def wrapper(func):
#
#        def memoized_func(*args):
#            if args in cache:
#                return cache[args]
#            result = func(*args)
#            cache[args] = result
#            if cachefile:
#                with open(cachefile, 'wb') as handle:
#                    pickle.dump(your_data, handle, protocol=pickle.HIGHEST_PROTOCOL)
#            return result
#        return memoized_func
#
#    return memorized_func


