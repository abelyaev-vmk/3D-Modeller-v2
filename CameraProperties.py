from ImageProperties import ImageProperties
from XMLParser import get_data_from_xml, XML
import camera
from PIL import Image
import numpy as np
from CommonFunctions import *


class CameraProperties:
    def __init__(self, ip, project, image_path):
        self.ip = ip
        self.ground = restructure_array(ip.objects['Ground'])
        self.walls = restructure_array(ip.objects['Walls'])
        self.sky = restructure_array(ip.objects['Sky'])
        self.motion = restructure_array(ip.objects['Motion'])

        self.project = project
        self.image_path = image_path
        self.xml = get_data_from_xml(source=self.project + '.xml')  # type: XML
        self.image_size = get_image_size(image_path)

        # Set camera parameters
        self.camera = camera.Camera()
        print self.xml
        if self.xml.type == 'IE':
            self.camera.UseNonGL()
            self.camera.SetLocation(self.xml['pos'])
            self.camera.SetQuaternion(self.xml['rot'])
        if self.xml.type == 'IGE':
            self.camera.UseGL()
            self.camera.SetLocation(self.xml['pos'])
            pass  # TODO need to calculate camera properties for this type! after reimport

        # # It have to be with kivy usage!
        self.change_y_coordinate()
        # # # # # # # # # # # # # # # # #

        self.debug_info()
        # # Set planes we'll working on
        # self.ground_plane = (0, 0, 1, 0)
        # self.walls_planes = [self.define_wall_plane(wall) for wall in self.walls]
        # self.sky_plane = self.define_sky_plane()
        #
        # self.__img2world_dict = {}

    def change_y_coordinate(self):
        change_y_in_lines = lambda lines: map(lambda line:
                                              map(lambda point: [point[0], self.image_size[1] - point[1] - 1],
                                                  line),
                                              lines)
        self.ground = change_y_in_lines(self.ground)
        self.walls = change_y_in_lines(self.walls)

    def define_wall_plane(self, wall):
        points = []
        for line in wall:
            points.append(line[0])
        distances = np.zeros((len(points), len(self.ground)))
        for p, point in enumerate(points):
            for l, line in enumerate(self.ground):
                distances[p, l] = dist(point, line[0])
        min_indexes = np.argsort(distances, axis=1)
        min_values = [[distances[i][min_indexes[i, 0]], (i, min_indexes[i, 0])] for i in range(distances.shape[0])]
        min_values.sort(key=lambda m: m[0])
        min_dist_points = [min_values[i][1] for i in (0, 1)]
        points_on_plane = [self.ground[min_dist_points[i][1]][0] for i in (0, 1)]
        x0, y0, z0 = map(float, self.img2world(point=points_on_plane[0],
                                               plane=self.ground_plane))
        x1, y1, z1 = map(float, self.img2world(point=points_on_plane[1],
                                               plane=self.ground_plane))
        x2, y2, z2 = x0, y0, 5.0
        p1, p2, p3 = np.array([x0, y0, z0]), np.array([x1, y1, z1]), np.array([x2, y2, z2])
        v1, v2 = p3 - p1, p2 - p1
        cp = np.cross(v1, v2)
        a, b, c = cp
        d = -np.dot(cp, p3)
        return a, b, c, d

    # TODO do after reimport
    def define_sky_plane(self):
        return 0

    @property
    def external_calibration(self):
        if not hasattr(self, '__ext_cal'):
            self.__ext_cal = self.__compute_external_calibration()
        return self.__ext_cal

    @property
    def internal_calibration(self):
        if not hasattr(self, '__int_cal'):
            self.__int_cal = self.__compute_internal_calibration()
        return self.__int_cal

    @property
    def internal_parameters(self):
        if not hasattr(self, '__int_params'):
            self.__int_params = self.__compute_internal_parameters()
        return self.__int_params

    @property
    def GL_projection_matrix(self):
        if not hasattr(self, '__gl_proj_matr'):
            self.__gl_proj_matr = self.__compute_GL_projection_matrix()
        return self.__gl_proj_matr

    @property
    def GL_model_view_matrix(self):
        if not hasattr(self, '__gl_model_view_matr'):
            self.__gl_model_view_matr = self.__compute_GL_model_view_matrix()
        return self.__gl_model_view_matr

    @property
    def calibration_matrix(self):
        if not hasattr(self, '__cal_matr'):
            self.__cal_matr = self.__compute_calibration_matrix()
        return self.__cal_matr

    def img2world(self, point=(0, 0), plane=(0, 0, 1, 0)):
        point = [point[0], point[1], 1]
        if plane.__str__() in self.__img2world_dict:
            A = self.__img2world_dict[plane.__str__()]
        else:
            A = np.zeros((4, 4))
            A[:3, :] = self.calibration_matrix[:, :]
            self.__img2world_dict[plane.__str__()] = A
        b = np.array([[p] for p in point + [0]])
        new_point = np.dot(np.linalg.inv(A), b)
        return new_point[:-1] / new_point[-1]

    def world2img(self, point=(0, 0, 0, 1)):
        ip = self.calibration_matrix.dot(point)
        return ip[0, 0] / ip[0, 2], ip[0, 1] / ip[0, 2]

    # TODO import from old project
    def interpolate(self, in_point=(0, 0)):
        pass

    # TODO import from old project
    @debug_time
    def image2plane(self, max_size=750, plane=(0, 0, 1, 0), points=None):
        if points is None:
            points = ((0, 0),
                      (self.image_size[0] - 1, 0),
                      (0, self.image_size[1] - 1),
                      (self.image_size[0] - 1, self.image_size[1] - 1))
        corners = map(lambda p: self.img2world(p, plane), points)
        min_coord, max_coord = corners[0], corners[0]
        for corner in corners:
            max_coord = map(max, max_coord, corner)
            min_coord = map(min, min_coord, corner)
        offset = map(float, min_coord)

    def calculate(self):
        pass

    # TODO add other xml types
    # # return matrix3x4, previous = 4x4, see GL_model_view
    def __compute_external_calibration(self):
        if self.xml.type == 'IE':
            return self.camera.GetViewMatrix()
            # return np.asarray(np.vstack((self.camera.GetViewMatrix(), np.array([0, 0, 0, 1]))), np.float32, order='F')
        if self.xml.type == 'IGE':
            rx, ry, rz = self.xml['rot']
            tx, ty, tz = self.xml['pos']
            sx, cx, sy, cy, sz, cz = sin(rx), cos(rx), sin(ry), cos(ry), sin(rz), cos(rz)
            Rx = np.matrix([[1, 0, 0, 0], [0, cx, sx, 0], [0, -sx, cx, 0], [0, 0, 0, 1]])
            Ry = np.matrix([[cy, 0, sy, 0], [0, 1, 0, 0], [-sy, 0, cy, 0], [0, 0, 0, 1]])
            Rz = np.matrix([[cz, sz, 0, 0], [-sz, cz, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
            R = Rx * Ry * Rz
            matr = np.matrix(np.zeros((4, 4)))
            matr[:3, :3] = R[:3, :3]
            matr[0, 3] = tx
            matr[1, 3] = ty
            matr[2, 3] = tz
            matr[3, 3] = 1
            return matr

    # TODO add other xml types
    def __compute_internal_calibration(self):
        if self.xml.type == 'IE':
            fl, pp, s = self.xml['fl'], self.xml['pp'], self.xml['s']
            return np.array([[fl[0], tan(s) * fl[1], pp[0]],
                             [0, fl[1], pp[1]],
                             [0, 0, 1]])
        if self.xml.type == 'IGE':
            matr = np.zeros((3, 3))
            matr[0, 0] = self.xml['sx'] / self.xml['dp'][0]
            matr[0, 2] = self.xml['c'][0]
            matr[1, 1] = 1 / self.xml['dp'][1]
            matr[1, 2] = self.xml['c'][1]
            matr[2, 2] = 1
            return np.dot(matr, np.array([[self.xml['focal'], 0, 0],
                                          [0, self.xml['focal'], 0],
                                          [0, 0, 1]]))
        return 1

    def __compute_internal_parameters(self):
        f = np.mean(self.xml['fl'] if self.xml['fl'] is not None else self.xml['focal'])
        cx, cy = self.xml['pp'] if self.xml['pp'] is not None else self.xml['c']
        pixel_center_offset = 0.5
        near = 1.0
        far = 1e2
        width, height = self.image_size
        right = (width - (cx + pixel_center_offset)) * (near / f)
        left = - (cx + pixel_center_offset) * (near / f)
        top = - (height - (cy + pixel_center_offset)) * (near / f)
        bottom = (cy + pixel_center_offset) * (near / f)
        return left, right, bottom, top, near, far

    def __compute_GL_projection_matrix(self):
        l, r, b, t, n, f = self.internal_parameters
        return np.matrix([[2 * n / (r - l), 0, (r + l) / (r - l), 0],
                          [0, 2 * n / (t - b), (t + b) / (t - b), 0],
                          [0, 0, -(f + n) / (f - n), -2 * f * n / (f - n)],
                          [0, 0, -1, 0]])

    def __compute_GL_model_view_matrix(self):
        view_matrix = self.external_calibration
        # view_matrix = self.camera.GetViewMatrix()
        gl_view_matrix = np.asarray(np.vstack((view_matrix, np.array([0, 0, 0, 1]))), np.float32, order='F')
        return gl_view_matrix

    def __compute_calibration_matrix(self):
        return np.matrix(self.internal_calibration) * np.matrix(self.external_calibration)

    def debug_info(self):
        for i, p in enumerate((self.internal_calibration, self.external_calibration, self.internal_parameters,
                               self.calibration_matrix, self.GL_model_view_matrix, self.GL_projection_matrix)):
            print '{0}: {1}'.format(i, p)
        print 'wall: ', self.walls
        print 'wall_plane: ', self.walls[0]
