# -*- coding: utf-8 -*-
"""encode png bytestream"""

import numpy as np
import cv2
from time import sleep

def png_encode(input, compress_level=3):
    '''
    :param numpy.ndarray input: uint8 color image array
    :param int compress_level: compress level for PNG compression
    :return: encoded image data
    '''
    assert len(input.shape) == 3 and input.shape[2] in [3, 4]
    assert input.dtype == np.uint8
    assert isinstance(compress_level, int) and 0 <= compress_level <= 9
    enc = cv2.imencode('.png', input,
                       [int(cv2.IMWRITE_PNG_COMPRESSION), compress_level])
    return enc[1].tostring()
