from ImageProperties import ImageProperties
from XMLParser import get_data_from_xml, XML
import camera
from PIL import Image
import numpy as np
from CommonFunctions import *
from os import getcwd


# TODO sky calculation! (CLASS-TODO)
class CameraProperties:
    def __init__(self, ip, project, image_path):
        self.ip = ip
        self.ground = restructure_array(ip.objects['Ground'])
        self.ground_image = None
        self.walls = restructure_array(ip.objects['Walls'])
        self.walls_images = [None for _ in self.walls]
        self.sky = restructure_array(ip.objects['Sky'])
        self.sky_image = None
        self.motion = restructure_array(ip.objects['Motion'])

        self.project = project
        self.image_path = image_path
        self.xml = get_data_from_xml()  # type: XML
        self.image = Image.open(image_path)
        self.image_pixels = self.image.load()
        self.image_size = self.image.size

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
        self.__img2world_dict = {}
        self.ground_plane = (0, 0, 1, 0)
        self.walls_planes = [self.define_wall_plane(wall) for wall in self.walls]
        self.sky_plane = self.define_sky_plane()
        self.calculated = False

    # TODO add sky
    def make_image_projections(self):
        for _ in self.ground:
            self.ground_image = Image3D.load('ground')
            if self.ground_image is None:
                self.ground_image = self.image2plane(plane=self.ground_plane, key='ground', points=self.ground[0])
        for i, wall_plane in enumerate(self.walls_planes):
            self.walls_images[i] = Image3D.load('wall%d' % i)
            if self.walls_images[i] is None:
                self.walls_images[i] = self.image2plane(plane=wall_plane, key='wall%d' % i, points=self.walls[i])
        for _ in self.sky:
            self.sky_image = Image3D.load('sky')
            if self.sky_image is None:
                self.sky_image = self.image2plane(plane=self.sky_plane, key='sky', points=self.sky[0])

    def change_y_coordinate(self):
        change_y_in_lines = lambda lines: map(lambda line:
                                              map(lambda point: [point[0], self.image_size[1] - point[1] - 1],
                                                  line),
                                              lines)
        self.ground = change_y_in_lines(self.ground)
        self.walls = change_y_in_lines(self.walls)
        self.sky = change_y_in_lines(self.sky)
        self.motion = change_y_in_lines(self.motion)

    def define_wall_plane(self, wall):
        points = []
        for point in wall:
            points.append(point)
        distances = np.zeros((len(points), len(self.ground[0])))
        for p, point in enumerate(points):
            for gp, gpoint in enumerate(self.ground[0]):
                distances[p, gp] = dist(point, gpoint)
        min_indexes = np.argsort(distances, axis=1)
        min_values = [[distances[i][min_indexes[i, 0]], (i, min_indexes[i, 0])] for i in range(distances.shape[0])]
        min_values.sort(key=lambda m: m[0])
        min_dist_points = [min_values[i][1] for i in (0, 1)]
        points_on_plane = [self.ground[0][min_dist_points[i][1]] for i in (0, 1)]
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
            A[3, :] = plane[:]
            self.__img2world_dict[plane.__str__()] = A
        b = np.array([[p] for p in point + [0]])
        new_point = np.dot(np.linalg.inv(A), b)
        return new_point[:-1] / new_point[-1]

    def world2img(self, point=(0, 0, 0, 1)):
        ip = self.calibration_matrix.dot(hom2het(vector=point))
        return ip[0, 0] / ip[0, 2], ip[0, 1] / ip[0, 2]

    # TODO import from old project
    def interpolate(self, in_point=(0, 0)):
        try:
            return self.image_pixels[in_point]
        except KeyError:
            pass
        except ValueError:
            pass
        return 0, 0, 0

    # TODO add sky
    @Debug.time
    def image2plane(self, max_size=G_projection_max_size, plane=(0, 0, 1, 0), points=None, key='ground'):
        matrices = MatricesForImage()

        # create limiting polygon
        if points is None:
            points = ((0, 0),
                      (self.image_size[0] - 1, 0),
                      (0, self.image_size[1] - 1),
                      (self.image_size[0] - 1, self.image_size[1] - 1))

        # find 3D offset
        corners = map(lambda p: self.img2world(p, plane), points)
        min_coord, max_coord = corners[0], corners[0]
        for corner in corners:
            max_coord = map(max, max_coord, corner)
            min_coord = map(min, min_coord, corner)
        offset = map(float, min_coord)
        matrices.translate((-offset[0], -offset[1], 0), '3D')

        # find rotation and axis in case of plane and ground are orthographic
        world_coords = np.array(map(lambda p: het2hom(vector=matrices.transition() * vm_hom2het(p)), corners))
        axis, theta = ground_axis(world_coords)
        matrices.axis_rotate(axis, theta, '3D')

        #
        plane_coords = map(lambda p: het2hom(vector=matrices.transition() * vm_hom2het(p))[:2], corners)
        min_coord, max_coord = plane_coords[0], plane_coords[0]
        for coord in plane_coords:
            min_coord, max_coord = map(min, min_coord, coord), map(max, max_coord, coord)
        offset = map(float, min_coord[:2])

        shape = map(lambda m, o: m - o, max_coord, offset)
        shape_reducing = float(max(shape[0] / max_size, shape[1] / max_size))
        shape = map(lambda s: int(s / shape_reducing), shape)

        matrices.translate((-offset[0], -offset[1]), '2D')
        matrices.scale(1 / shape_reducing, '2D')

        img = Image3D(image=Image.new('RGBA', shape, 'white'), key=key, matrices=matrices)
        for ix in range(shape[0]):
            for iy in range(shape[1]):
                wp = matrices.inv_transition() * vm_hom2het((ix, iy, 0))
                wx, wy, wz = np.array(het2hom(wp)).ravel()
                point = self.world2img((wx, wy, wz))
                if not all(0 <= point[i] < self.image_size[i] for i in (0, 1)):
                    continue
                img[ix, iy] = self.interpolate(point)
            if ix in (i * shape[0] / 20 for i in range(0, 20)):
                print "Done %d / %d" % (ix, shape[0])
        img.save()
        img.show()

    def calculate(self):
        self.make_image_projections()
        self.calculated = True

    def point2plane(self, point):
        for ground in self.ground:
            if point_inside(point, ground):
                return self.ground_plane
        for i, wall in enumerate(self.walls):
            if point_inside(point, wall):
                return self.walls_planes[i]
        for sky in self.sky:
            if point_inside(point, sky):
                return self.sky_plane
        return self.ground_plane

    def render(self):
        f = open(G_UnityPointsAndTex_path, 'w')
        f.write(points_and_tex_info([self.img2world(point=point, plane=self.ground_plane) for point in self.ground[0]],
                                    self.ground_image))
        walls = [[self.img2world(point=point, plane=self.walls_planes[i]) for point in wall]
                 for i, wall in enumerate(self.walls)]
        f.write('%d\n' % len(walls))
        for i, wall in enumerate(walls):
            f.write(points_and_tex_info(wall, self.walls_images[i]))
        # TODO sky
        f.write('0\n')
        f.write('%d\n' % len(self.motion))
        for motion in self.motion:
            motion_info = '%d\n' % len(motion)
            for point in motion:
                for c in self.img2world(point, self.point2plane(point)):
                    motion_info += '%f ' % float(c)
                motion_info += '\n'
            f.write(motion_info)
        f.close()

        f = open(G_UnityInfo_path, 'w')
        f.write('%s\n%s\n' % (make_unity_path(getcwd()) + '//', G_UnityPointsAndTex_path))
        f.write('%d\n%s_projection.jpg\n' % (len(self.ground), self.ground_image.key))
        f.write('%d\n' % len(self.walls))
        for wi in self.walls_images:
            f.write('%s_projection.jpg\n' % wi.key)
        f.write('%d\n' % len(self.sky) + ('%s_projection\n' % self.sky_image.key if self.sky else ''))
        f.write('%d\n' % len(self.motion))
        f.close()

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
