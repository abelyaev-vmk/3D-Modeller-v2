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
        self.walls = restructure_array(np.array(ip.objects['Walls']))
        self.sky = restructure_array(ip.objects['Sky'])
        self.motion = restructure_array(ip.objects['Motion'])

        self.project = project
        self.image_path = image_path
        self.xml = get_data_from_xml(source=self.project + '.xml')
        self.image_size = get_image_size(image_path)

        # Set camera parameters
        self.camera = camera.Camera()
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

        # Set planes we'll working on
        self.ground_plane = (0, 0, 1, 0)
        self.walls_planes = [self.define_wall_plane(wall) for wall in self.walls]
        self.sky_plane = self.define_sky_plane()

    def change_y_coordinate(self):
        change_y_in_lines = lambda lines: map(lambda line:
                                              map(lambda point: [point[0], self.image_size[1] - point[1] - 1],
                                                  line),
                                              lines)
        self.ground = change_y_in_lines(self.ground)
        self.walls = map(lambda wall: change_y_in_lines(wall), self.walls)

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

    # TODO add other xml types
    # @property
    def get_external_calibration_v2(self):
        # TODO !! REIMPORTED !!
        if self.xml.type == 'IE':
            return self.get_GL_model_view_matrix()
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

    # TODO import from old project
    def get_internal_calibration(self):
        pass

    # TODO import from old project
    # TODO ??????????
    def get_internal_parameters(self):
        pass

    # TODO import from old project
    def get_GL_projection_matrix(self):
        pass

    # TODO import from old project
    def get_GL_model_view_matrix(self):
        pass

    # TODO import from old project
    def get_calibration_matrix_v2(self):
        pass

    # TODO import from old project
    def img2world(self, point=(0, 0), plane=(0, 0, 1, 0)):
        return []

    # TODO import from old project
    def world2img(self, point=(0, 0, 0)):
        pass

    # TODO import from old project
    def interpolate(self, in_point=(0, 0)):
        pass

    # TODO import from old project
    def image2plane_v2(self, max_size=750, plane=(0, 0, 1, 0)):
        pass

    def calculate(self):
        pass
