#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# $File: misc.py
# $Date: Thu Apr 20 01:47:53 2017 +0800
# $Author: Xinyu Zhou <zxytim[at]gmail[dot]com>

import os
import re
import subprocess
from pathlib import Path

import hashlib

import cv2
import numpy as np

from .fs import change_dir


def stable_rng(self):
    '''reutrn a stable numpy random number generator using seed from
    stable_rand_seed
    '''
    return np.random.RandomState(stable_rand_seed(self))


def class_numbers_to_one_hot(class_numbers, nr_class):
    '''convert batch of class numbers to one-hot representation

    :param class_numbers: a list or numpy array of integers, where each
    integer lies within [0, nr_class)

    :param nr_class: number of classes

    :return: the one-hot representation of given class numbers
    :rtype: numpy.ndarray of dtype float32
    '''
    class_numbers = list2nparray(class_numbers).astype('int32')
    assert class_numbers.ndim == 1, class_numbers.shape

    n = class_numbers.shape[0]

    one_hot = np.zeros((n, nr_class), dtype='float32')
    one_hot[np.arange(n), class_numbers] = 1
    return one_hot


def img2ic01(img, nr_channel, shape):
    '''Convert image to tensor of axis (c, h, w) .

    .. note::

        1. If the size of the image is not the same as given in *shape*, it
            will be resized using cv2.resize.
        2. If the number of channels of image is different from *nr_channel*,
            it will be converted using cv2.cvtColor with flag in one of
            cv2.COLOR_GRAY2BGR and cv2.COLOR_BGR2GRAY
    '''
    if nr_channel == 3 and img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    elif nr_channel == 1 and img.ndim == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    assert img.ndim == 2 or img.shape[2] in {1, 3}, img.shape

    if img.shape[:2] != tuple(shape):
        img = cv2.resize(img, shape[::-1])

    if img.ndim == 2:
        img = img.reshape(img.shape + (1, ))

    return i01c_to_ic01(img)


def cvpause():
    while (cv2.waitKey(0) & 0xff) != ord('q'):
        print('press `q` to quit')


def get_receptive_field_and_stride(opr_list):
    pass
    #from .opr.all import (
    #    Pooling2D, Conv2D, Conv2DVanilla, UnsharedConv2D, Deconv2DVanilla,
    #)

    opr_info = {}
    stride_dict = {}
    receptive_field_dict = {}
    for opr in iter_dep_opr(*opr_list):
        if len(opr.inputs) == 0:
            stride_dict[opr] = (1, 1)
            receptive_field_dict[opr] = (1, 1)
            continue
        s = (max(stride_dict[input.owner_opr][0] for input in opr.inputs),
            max(stride_dict[input.owner_opr][1] for input in opr.inputs))
        r = (max(receptive_field_dict[input.owner_opr][0] for input in opr.inputs),
            max(receptive_field_dict[input.owner_opr][1] for input in opr.inputs))
        if isinstance(opr, (Conv2D, UnsharedConv2D,
                            Conv2DVanilla)):
            receptive_field_dict[opr] = (opr.kernel_shape[0] * s[0] + r[0] - s[0],
                                opr.kernel_shape[1] * s[1] + r[1] - s[1])
            stride_dict[opr] = (opr.stride[0] * s[0],
                        opr.stride[1] * s[1])
        elif isinstance(opr, Pooling2D):
            receptive_field_dict[opr] = (opr.window[0] * s[0] + r[0] - s[0],
                                opr.window[1] * s[1] + r[1] - s[1])
            stride_dict[opr] = (opr.stride[0] * s[0],
                        opr.stride[1] * s[1])
        else:
            receptive_field_dict[opr] = r
            stride_dict[opr] = s
            continue
        if isinstance(opr, (Conv2D, UnsharedConv2D, Pooling2D, Conv2DVanilla)):
            opr_info[opr] = (receptive_field_dict[opr], stride_dict[opr])
    return opr_info


def safe_filename(fname):
    s = fname.replace('/', '-')
    while len(s) and s[0] in {'-', '.'}:
        s = s[1:]
    return s


def md5sum(s):
    """md5 checksum of given string
    :return: md5 hex digest string
    """
    m = hashlib.md5()
    m.update(s)
    return m.hexdigest()


def get_project_name(base_dir: Path) -> str:
    with change_dir(base_dir):
        try:
            out = subprocess.check_output(
                ["git", "remote", "get-url", "origin"]
            )
        except Exception:
            return None

        url = out.decode("utf-8").strip()
        gitrepo = os.path.split(url)[-1]
        return re.sub(r'\.git$', '', gitrepo)

# vim: foldmethod=marker
