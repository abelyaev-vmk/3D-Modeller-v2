import numpy as np
from CommonFunctions import MyDict, stderr
import pickle


class ImageObject:
    def __init__(self, points=None, kivy_touches = None, type=""):
        self.points = np.array(points) if points is not None else None
        self.touches = np.array(kivy_touches) if kivy_touches is not None else None
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

        self.kivy_objects = MyDict()
        self.kivy_objects['Ground'] = []
        self.kivy_objects['Walls'] = []
        self.kivy_objects['Sky'] = []
        self.kivy_objects['Motion'] = []

        self.project = project

    def add(self, io):
        self.objects[io.type].append(io.points)
        self.kivy_objects[io.type].append(io.touches)
        print >>stderr, self.kivy_objects['Ground']

    def __iter__(self):
        for key in ('Ground', 'Walls', 'Sky', 'Motion'):
            yield key, self.objects[key]

    def __str__(self):
        ans = ''
        for key in self.objects:
            ans += key + ' ' + self.objects[key].__str__() + '\n'
        print ans

    def copy(self, ip):
        if ip is not None:
            self.objects = ip.objects
            self.kivy_objects = ip.kivy_objects
            self.project = ip.project

    def save(self, path=None):
        with open(path if path is not None else self.project, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load(path=None):
        ans = None
        try:
            if path:
                with open(path, 'rb') as f:
                    ans = pickle.load(f)
            print "PRINTING ON LOAD", ans.__str__()
        except IOError:
            pass
        return ans
