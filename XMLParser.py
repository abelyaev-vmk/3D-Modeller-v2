import xml.etree.ElementTree as ET
import numpy as np
from CommonFunctions import stderr
from MainConsts import G_matrix_path


def define_type(root):
    for child in root:
        if child.tag == 'Intrinsic':
            return 'IGE'
    return 'IE'


class XML:
    def __init__(self, xml_type, internal, external, geometry):
        self.type = xml_type
        self.internal = internal
        self.external = external
        self.geometry = geometry

    def __getitem__(self, item):
        for mas in (self.internal, self.external, self.geometry):
            try:
                return mas[item]
            except KeyError:
                pass
        print >>stderr, "Can't find attribute=%s, try another xml_type (now='%s') attribute" % (item, self.type)
        return None


def get_data_from_xml(source=G_matrix_path):
    """
    XML Types:
    'IE' - Internal\External Calibration, example: TownCenter
    'IGE' - Intrinsic\Geometry\Extrinsic, example: Pets

    :param source: string
    :return: dict
    """
    if not source:
        return
    tree = ET.parse(source=source)
    root = tree.getroot()
    internal, external, geometry = {}, {}, {}
    xml_type = define_type(root)
    if xml_type == 'IE':
        for child in root:
            at = child.attrib
            if child.tag == 'InternalCalibration':
                internal['dk'] = np.array(map(float, [at['dk1'], at['dk2']]))
                internal['dp'] = np.array(map(float, [at['dp1'], at['dp2']]))
                internal['fl'] = np.array(map(float, [at['flx'], at['fly']]))
                internal['pp'] = np.array(map(float, [at['ppx'], at['ppy']]))
                internal['s'] = float(at['s'])
            if child.tag == 'ExternalCalibration':
                external['pos'] = np.array(map(float, [at['tx'], at['ty'], at['tz']]))
                external['rot'] = np.array(map(float, [at['rx'], at['ry'], at['rz'], at['rw']]))
    if xml_type == 'IGE':
        for child in root:
            at = child.attrib
            if child.tag == 'Intrinsic':
                internal['focal'] = float(at['focal'])
                internal['kappa'] = float(at['kappa1'])
                internal['c'] = np.array(map(float, [at['cx'], at['cy']]))
                internal['sx'] = float(at['sx'])
            if child.tag == 'Geometry':
                geometry['size'] = np.array(map(float, [at['width'], at['height']]))
                geometry['ncx'] = float(at['ncx'])
                geometry['nfx'] = float(at['nfx'])
                geometry['d'] = np.array(map(float, [at['dx'], at['dy']]))
                geometry['dp'] = np.array(map(float, [at['dpx'], at['dpy']]))
            if child.tag == 'Extrinsic':
                external['pos'] = np.array(map(float, [at['tx'], at['ty'], at['tz']]))
                external['rot'] = np.array(map(float, [at['rx'], at['ry'], at['rz']]))
    return XML(xml_type, internal, external, geometry)

