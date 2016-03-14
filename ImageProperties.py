import numpy as np
from CommonFunctions import MyDict
import pickle


class ImageObject:
    def __init__(self, points=None, type=""):
        self.points = np.array(points) if points is not None else None
        self.type = type

    def show(self):
        print self.type + ':', self.points


class ImageProperties:
    def __init__(self, project='image'):
        self.objects = MyDict()
        self.objects['Ground'] = []
        self.objects['Walls'] = []
        self.objects['Sky'] = []
        self.objects['Motion'] = []
        self.project = project

    def add(self, io):
        self.objects[io.type].append(io.points)

    def __str__(self):
        ans = ''
        for key in self.objects:
            ans += key + ' ' + self.objects[key].__str__() + '\n'

    def copy(self, ip):
        self.objects = ip.objects
        self.project = self.project

    def save(self, path=None):
        with open(path if path is not None else self.project, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load(path=None):
        if path:
            with open(path, 'wb') as f:
                return pickle.load(f)
