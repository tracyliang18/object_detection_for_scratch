#!/usr/bin/python mdl
# -*- coding:utf-8 -*-
# Created Time: Thu 19 Oct 2017 09:43:24 PM HKT
# Purpose:  draw bezier
# Mail: liangjiajun@megvii.com
import numpy as np
from functools import reduce
import operator as op
import utils.webcv2 as cv2
def ncr(n, r):
    r = min(r, n-r)
    if r == 0: return 1
    numer = reduce(op.mul, range(n, n-r, -1))
    denom = reduce(op.mul, range(1, r+1))
    return numer//denom

def get_bezier_curve_points(anchors, count, ret_int=False):
    xs = list(map(lambda x: x[0], anchors))
    ys = list(map(lambda x: x[1], anchors))
    ts = np.linspace(0, 1, count)
    l = len(anchors)
    n = l - 1
    cofs = []
    for ind in range(n+1):
        cofs.append(ncr(n, ind))

    def get_x(t):
        r = 0
        for ind in range(l):
            r += xs[ind] * cofs[ind] * ((1 - t)**(n-ind)) * (t**ind)
        return r

    def get_y(t):
        r = 0
        for ind in range(l):
            r += ys[ind] * cofs[ind] * ((1 - t)**(n-ind)) * (t**ind)
        return r

    ret_xs = [get_x(t) for t in ts]
    ret_ys = [get_y(t) for t in ts]

    if ret_int:
        ret_xs = list(map(int, ret_xs))
        ret_ys = list(map(int, ret_ys))

    return list(zip(ret_xs, ret_ys))

def draw_points(img, points):
    for p in points:
        cv2.circle(img, center=p, radius=2, color=(0, 255, 0), thickness=-1)
    return img

def draw_box(img, box):
    return cv2.rectangle(img, box[0], box[-1], (0, 255, 0), 1)


class BezierCurveGenerator(object):

    def __init__(self, max_ctrl_points=5, H=224, W=224):
        self.max_ctrl_points = max_ctrl_points
        self.height = H
        self.width = W

    def __iter__(self):
        while True:
            n = np.random.randint(2, high=self.max_ctrl_points)
            points = []
            for _ in range(n):
                points.append((np.random.randint(0, self.height), np.random.randint(0, self.width)))
            count = 400
            curve_points = get_bezier_curve_points(points, count, ret_int=True)
            canvas = np.ones((self.height, self.width), dtype='uint8')
            canvas *= 255
            canvas = draw_points(canvas, curve_points)
            canvas = canvas[:, :, np.newaxis]
            canvas = np.concatenate([canvas] * 3, axis=2)
            curve_points = np.array(curve_points)
            x_min, y_min = curve_points.min(axis=0)
            x_max, y_max = curve_points.max(axis=0)

            box = [(x_min, y_min), (x_min, y_max), (x_max, y_min), (x_max, y_max)]

            yield {
                'img': canvas,
                'box': box
            }

if __name__ == "__main__":
    #points = [(0, 0), (224,224)]
    beziercurve = BezierCurveGenerator()
    shows = []
    for data in beziercurve:
        img = data['img']
        box = data['box']
        img = draw_box(img, box)
        shows.append(img)
        if len(shows) == 64:
            rows = []
            for i in range(8):
                rows.append(np.concatenate(shows[i*8:(i+1)*8], axis=1))
            show = np.concatenate(rows, axis=0)
            cv2.imshow('show', show)
            cv2.waitKey(0)
            shows = []



