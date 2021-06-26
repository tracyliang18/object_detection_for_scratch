#!/usr/bin/python2
# -*- coding:utf-8 -*-
# Created Time: Sat 26 Jun 2021 04:16:02 PM HKT
# Purpose: TODO
# Mail: tracyliang18@gmail.com

import utils.webcv2 as cv2
import numpy as np
from utils.logconf import get_logger

if __name__ == "__main__":
    logger = get_logger(__name__)
    logger.info('this is a test')
    img = np.zeros((160, 160), dtype='uint8')
    cv2.imshow('test', img)
    cv2.waitKey(0)
