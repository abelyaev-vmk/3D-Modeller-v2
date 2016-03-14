import numpy as np
import pickle


class ImageObject:
    def __init__(self, points=None, type=""):
        self.points = np.array(points) if points is not None else None
        self.type = type

    def show(self):
        print self.type + ':', self.points


class ImageProperties:
    def __init__(self, project='image'):
        self.objects = []
        self.project = project

    def add(self, io):
        self.objects.append(io)

    def save(self, path=None):
        with open(path if path is not None else self.project, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load(path=None):
        with open(path if path is not None else self.project, 'wb') as f:
            return pickle.load(f)
