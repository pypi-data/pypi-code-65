#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2020/10/10 16:46
# @Author : 詹荣瑞
# @File : board.py
# @desc : 本代码未经授权禁止商用
import numpy as np


class Board(object):

    def __init__(self, height=7, width=7):
        self.map = np.zeros((height, width), np.int)

    def __str__(self):
        return str(self.map)

    def down(self, num, pos):
        """
        下子

        :param num: 下子编号
        :param pos: 下子位置
        :return:
        """
        self.map[tuple(pos)] = num
