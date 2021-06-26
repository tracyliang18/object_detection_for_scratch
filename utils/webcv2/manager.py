#!/usr/bin/env mdl
import base64
import numpy as np
from collections import OrderedDict


from .server import get_server
from ..web import get_free_port
from utils.imgproc import jpeg_encode as cv2_jpeg_encode


def jpeg_encode(img, quality=90):
    '''
    :param img: image array
    :type img: :class:`numpy.ndarray`
    :param int quality: quality for JPEG compression
    :return: encoded uint8 image data
    '''

    if img.dtype == 'uint8':
        pass
    elif img.dtype == 'uint16':
        img = np.clip(img.astype(np.float32) / 257 + 0.5, 0, 255.0).astype(np.uint8)
    elif img.dtype == 'float32' or img.dtype == 'float64':
        img = np.clip(img * 255 + 0.5, 0, 255.0).astype(np.uint8)
    elif img.dtype == 'bool':
        img = img.astype(np.uint8) * 255
    else:
        raise Exception(img.dtype + 'not yet supported by webcv2.')

    return cv2_jpeg_encode(img, quality=quality)


class Manager:
    def __init__(self, img_encode_method=jpeg_encode, rng=None):
        self._queue = OrderedDict()
        self._server = None
        self.img_encode_method = img_encode_method
        if rng is None:
            rng = np.random.RandomState(self.get_default_seed())
        self.rng = rng

    def get_default_seed(self):
        return 0

    def imshow(self, title, img):
        data = self.img_encode_method(img)
        data = base64.b64encode(data)
        data = data.decode('utf8')
        self._queue[title] = data

    def waitKey(self, delay=0):
        if self._server is None:
            self.port = get_free_port(self.rng)
            self._server, self._conn = get_server(port=self.port)
        self._conn.send([delay, list(self._queue.items())])
        # self._queue = OrderedDict()
        return self._conn.recv()


global_manager = Manager()
