#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2020/10/10 16:46
# @Author : 詹荣瑞
# @File : player.py
# @desc : 本代码未经授权禁止商用


class Player(object):

    def __init__(self, name, number, print_style="*"):
        self.name = name
        self.number = number

        self.print = print_style
