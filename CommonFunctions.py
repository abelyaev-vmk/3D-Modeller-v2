from sys import stderr, stdout
from math import *
import numpy as np


# Get size of image
def get_image_size(source):
    from PIL import Image
    return Image.open(source).size


# Make right structure of array
def restructure_array(array):
    ans = [[] for _ in array]
    for i, _ in enumerate(array):
        ans[i] = [[] for _ in array[i]]
        for j, __ in enumerate(array[i]):
            ans[i][j] = [array[i][j][0], array[i][j][1]]
    return ans


def dist(p1, p2):
    return sqrt(sum(map(lambda a, b: (a - b) ** 2, p1, p2)))


# aka dictionary class
class MyDict(dict):
    def __init__(self, length=5):
        super(MyDict, self).__init__()
        self.dict = {}
        self.length = length

    def __setitem__(self, key, value):
        self.dict[key[:self.length]] = value

    def __getitem__(self, key):
        try:
            return self.dict[key[:self.length]]
        except KeyError:
            print >> stderr, 'Bad key %s' % key.__str__()
            return None

    def __iter__(self):
        for key in self.dict:
            yield key

    @staticmethod
    def from_dictionary(dictionary, length=3):
        new_dictionary = MyDict(length=length)
        for key in dictionary:
            print key, dictionary[key]
            new_dictionary[key] = dictionary[key]
            print key, new_dictionary[key]
        print new_dictionary['Wall']
        return new_dictionary


# # # # # # Matrix & Vectors # # # # # # # #
def hom2het(vector=None, matrix=None):
    if vector is not None:
        return np.append(np.array(vector), 1)
    if matrix is not None:
        temp = np.zeros((4, 4))
        temp[:3, :3] = matrix[:, :]
        temp[3, 3] = 1
        return temp


def het2hom(vector=None, matrix=None):
    if vector is not None:
        return np.array(vector[:-1]) / vector[-1]
    if matrix is not None:
        return matrix[:3, :3] / matrix[3, 3]


# # # # # # DECORATORS HERE!!! # # # # # # #
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
