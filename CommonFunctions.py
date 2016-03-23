from sys import stderr, stdout
from math import *
import numpy as np
from MainConsts import *
import pickle
from PIL import Image


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
        if dist(ans[i][0], ans[i][-1]) < 5:
            ans[i].remove(ans[i][-1])
    return ans


# Make UnityUnderstand Path
def make_unity_path(path):
    new_path = ''
    for p in path:
        new_path += p if p != '\\' else '//'
    return new_path


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
            new_dictionary[key] = dictionary[key]
        return new_dictionary


class Image3D:
    def __init__(self, image=None, matrices=None, shape_reducing=1, project=G_start_project, key='ground'):
        self.image = image  # type: Image
        self.pixels = self.image.load()
        self.matrices = matrices
        self.shape_reducing = shape_reducing
        self.project = project
        self.key = key

    def save(self, path=None):
        path = path if path is not None else '%s_projection' % self.key
        self.image.save(path + '.jpg')
        with open(path + '.i3d', 'w') as f:
            pickle.dump([self.matrices, self.shape_reducing, self.project, self.key], f)
            f.close()

    def texture_coordinates(self, (x, y, z)):
        ip = self.matrices.transition() * np.matrix([x, y, z, 1]).transpose()
        x, y, _ = het2hom(map(float, np.array(ip).ravel()))
        return map(lambda a, s: a / s, (x, y), self.image.size)

    def __setitem__(self, (x, y), value):
        if not self.image:
            raise ValueError('There\'s no image here!')
        try:
            self.pixels[x, y] = value
        except IndexError:
            print self.image.size[1], self.image.size[0]
            print y, x
            print 'INDEX ERROR {0} not in {1}'.format((x, y), self.image.size)

    @staticmethod
    def load(key='ground'):
        try:
            with open('%s_projection.i3d' % key, 'r') as f:
                image = Image.open('%s_projection.jpg' % key)
                matr, sr, p, k = pickle.load(f)
                return Image3D(image, matr, sr, p, k)
        except IOError:
            print >> stderr, 'No such file or directory: %s_projection.i3d' % key
            return None

    def show(self):
        self.image.show()


def points_and_tex_info(polygon, image):
        points_info, tex_info = '%d\n' % len(polygon), ''
        for point in polygon:
            for c in point:
                points_info += '%f ' % float(c)
            points_info += '\n'
            for c in image.texture_coordinates(point):
                tex_info += '%f ' % float(c)
            tex_info += '\n'
        return points_info + tex_info


# # # # # # Matrix & Vectors # # # # # # # #

# Class with matrices to change world coordinate to image projection coordinates
class MatricesForImage:
    def __init__(self):
        self.translation_2D, self.translation_3D = ident(4), ident(4)
        self.scale_2D, self.scale_3D = ident(4), ident(4)
        self.rotation_2D, self.rotation_3D = ident(4), ident(4)
        self.__transition, self.__inv_transition = ident(4), ident(4)
        self.updated = True

    def transition(self):
        if self.updated:
            self.__transition = self.rotation_2D * self.scale_2D * self.translation_2D * \
                                self.rotation_3D * self.scale_3D * self.translation_3D
            self.updated = False
        return self.__transition

    def inv_transition(self):
        if self.updated:
            self.__inv_transition = np.linalg.inv(self.transition())
        return self.__inv_transition

    def scale(self, scl, scale_type='3D'):
        self.updated = True
        if scale_type == '3D':
            self.scale_3D = self.scale_3D * np.diag((scl, scl, scl, 1))
        else:
            self.scale_2D = self.scale_2D * np.diag((scl, scl, 1, 1))

    def translate(self, trn, translate_type='3D'):
        self.updated = True
        for i, t in enumerate(trn):
            if translate_type == '3D':
                self.translation_3D[i, 3] += t
            else:
                self.translation_2D[i, 3] += t

    def axis_rotate(self, axis, theta, rotate_type='3D'):
        if theta == 0:
            return
        self.updated = True
        if rotate_type == '3D':
            axis = np.asarray(axis, dtype='d')
            theta = np.asarray(theta, dtype='d')
            axis /= sqrt(np.dot(axis, axis))
            a = cos(theta / 2)
            b, c, d = -axis * sin(theta / 2)
            aa, bb, cc, dd = a ** 2, b ** 2, c ** 2, d ** 2
            bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
            M = np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac), 0],
                          [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab), 0],
                          [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc, 0],
                          [0, 0, 0, 1]])
            self.rotation_3D = self.rotation_3D * M
        else:
            pass


# Create identity numpy matrix NxN
def ident(n):
    return np.matrix(np.identity(n))


# Homogeneous to heterogeneous coordinates
def hom2het(vector=None, matrix=None):
    if vector is not None:
        return np.append(np.array(vector), 1)
    if matrix is not None:
        temp = np.zeros((4, 4))
        temp[:3, :3] = matrix[:, :]
        temp[3, 3] = 1
        return temp


# Heterogeneous to homogeneous coordinates
def het2hom(vector=None, matrix=None):
    if vector is not None:
        return np.array(vector[:-1]) / vector[-1]
    if matrix is not None:
        return matrix[:3, :3] / matrix[3, 3]


# Homogeneous row-vector to heterogeneous transposed column-vector
def vm_hom2het(vector):
    vec = [0, 0, 0, 1]
    for i, p in enumerate(vector):
        vec[i] = p
    return np.matrix(vec).transpose()


# Calculate plane equation from points
def plane_from_points(points=((1, 2, 3), (2, 3, 4), (5, 6, 7))):
    p = points[0]
    v, w = map(lambda p1, p2: p1 - p2, points[0], points[1]), map(lambda p1, p2: p1 - p2, points[0], points[2])
    dets = [(v[k[0]] * w[k[1]] - v[k[1]] * w[k[0]]) for k in ((1, 2), (0, 2), (0, 1))]
    return dets[0], -dets[1], dets[2], sum([(-1) ** (i + 1) * p[i] * dets[i] for i in (0, 1, 2)])


# L2 norm of vector
def vector_length(vec):
    return sqrt(sum([float(v) ** 2 for v in vec]))


# True, if given plane is a ground plane
def is_ground(plane=(1, 2, 0, 0)):
    eps = 0.1
    return 1 - abs(float(plane[2]) / vector_length(plane)) < eps


# Calculate axis and angle for given plane to ground rotation
def ground_axis(points):
    pln = plane_from_points(points)
    if is_ground(np.array(pln)):
        return (0, 0, 0), 0

    ground_points = []
    for point in points:
        ground_points.append(np.array(point))
    ground_points.sort(key=lambda p: abs(p[2]))
    ans = ground_points[:2]
    ans.sort(key=lambda p: sqrt(p[0] ** 2 + p[1] ** 2))
    return [float(ans[1][0] - ans[0][0]), float(ans[1][1] - ans[0][1]), 0], pi / 2


# Distance between two points
def dist(p1, p2):
    return sqrt(sum(map(lambda a, b: (a - b) ** 2, p1, p2)))


def point_inside(point, points):
    avr = map(lambda p1, p2: p1 + p2, points[0], map(lambda pp1, pp2: (pp2 - pp1) *.5, points[0], points[1]))
    minus = lambda a, b: a - b
    S, S_, l = 0, 0, len(points)
    for i in range(0, l):
        p1, p2 = points[i], points[(i + 1) % l]
        S += .5 * abs(np.cross(map(minus, avr, p1), map(minus, avr, p2)))
        S_ += .5 * abs(np.cross(map(minus, point, p1), map(minus, point, p2)))
    return abs(S - S_) < 1e-1


# # # # # # DECORATORS HERE!!! # # # # # # #
# Class with debug-decorators
class Debug:
    def __init__(self):
        pass

    @staticmethod
    class CachedProperty(object):
        def __init__(self, func):
            self.func = func
            self.name = func.__name__

        def __get__(self, instance, cls=None):
            result = instance.__dict__[self.name] = self.func(instance)
            return result

    @staticmethod
    def time(func):
        def wrapper(*args, **kwargs):
            from time import clock
            t = clock()
            res = func(*args, **kwargs)
            print 'TIME {0}: {1}'.format(func.__name__, clock() - t)
            return res

        return wrapper

    @staticmethod
    def calls_count(func):
        def wrapper(*args, **kwargs):
            wrapper.count += 1
            res = func(*args, **kwargs)
            print '{0} called {1}x times'.format(func.__name__, wrapper.count)
            return res

        wrapper.count = 0
        return wrapper

    @staticmethod
    def args(func):
        def wrapper(*args, **kwargs):
            print 'Arguments = {0}'.format(args)
            for key in kwargs:
                print 'Argument {0} = {1}'.format(key, kwargs[key])
            res = func(*args, **kwargs)
            return res

        return wrapper
