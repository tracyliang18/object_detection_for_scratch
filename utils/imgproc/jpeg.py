# -*- coding: utf-8 -*-

"""encode/decode jpeg bytestream"""
import numpy as np
import cv2
from time import sleep

def jpeg_encode(img, quality=90):
    '''
    :param img: uint8 color image array
    :type img: :class:`numpy.ndarray`
    :param int quality: quality for JPEG compression
    :return: encoded image data
    '''
    return cv2.imencode('.jpg', img,
                        [int(cv2.IMWRITE_JPEG_QUALITY), quality])[1].tostring()

def jpeg_decode(input):
    """use :func:`.imdecode`"""
    from . import imdecode
    return imdecode(input)
