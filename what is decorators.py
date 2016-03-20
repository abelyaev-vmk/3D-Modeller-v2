def debug_time(func):
    def wrapper(*args, **kwargs):
        from time import clock
        t = clock()
        res = func(*args, **kwargs)
        print 'TIME {0}: {1}'.format(func.__name__, clock() - t)
        return res
    return wrapper


def debug_calls_count(func):
    def wrapper(*args, **kwargs):
        wrapper.count += 1
        res = func(*args, **kwargs)
        print '{0} called {1}x times'.format(func.__name__, wrapper.count)
        return res
    wrapper.count = 0
    return wrapper


def debug_args(func):
    def wrapper(*args, **kwargs):
        print 'Arguments = {0}'.format(args)
        for key in kwargs:
            print 'Argument {0} = {1}'.format(key, kwargs[key])
        res = func(*args, **kwargs)
        return res
    return wrapper


class A:
    def __init__(self):
        self._param = 1

    @property
    def param(self):
        return self._param

    @param.setter
    def param(self, val):
        self._param = val


a = A()
print a.param