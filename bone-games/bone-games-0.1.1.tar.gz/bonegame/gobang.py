#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2020/10/10 16:47
# @Author : 詹荣瑞
# @File : gobang.py
# @desc : 本代码未经授权禁止商用
import numpy as np
import cv2
from .game import Game
from .core import Player, Board
from .renderers import Renderer


class GoBang(Game):

    def __init__(self, board=(7, 7), height=480, width=640):
        if isinstance(board, int):
            board = Board(board, board)
        elif not isinstance(board, Board):
            board = Board(*board)
        players = [Player(f"p{i}", i, f"{i}") for i in range(1, 3)]
        self.renderer = Renderer(height, width)
        self.win = None
        super(GoBang, self).__init__(board, players)

    def reset(self):
        self.board.map[:] = 0
        self.win = None
        return self

    def check_pos(self, pos, direct, number, repeat):
        if repeat < 5:
            return False
        m = self.board.map
        num = 0
        pos = np.array(pos)
        for i in range(repeat, 0, -1):
            if m[tuple(pos)] == number:
                num += 1
            else:
                num = 0
            if num == 5:
                return True
            pos += direct
            # elif num + i <= 5:
            #     return False
        return False

    def check(self, player):
        m = self.board.map
        h, w = m.shape
        for j in range(w):
            if (self.check_pos((0, j), (1, 0), player.number, w) or
                    self.check_pos((0, j), (1, 1), player.number, w - j) or
                    self.check_pos((0, j), (1, -1), player.number, j + 1) or
                    self.check_pos((h-1, j), (-1, 1), player.number, w - j)):
                return True
        for i in range(h):
            if (self.check_pos((i, 0), (0, 1), player.number, h) or
                    self.check_pos((i, 0), (1, 1), player.number, h - i)):
                return True
        return False

    def down(self, player, pos):
        if isinstance(player, int):
            player = self.players[player]
        super(GoBang, self).down(player, pos)
        if self.check(player):
            self.win = player.name
        return self

    def render(self, window_name="image"):
        self.renderer(self.board.map, window_name)
        return self

    def mouse_event(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.round += 1
            bh, bw = self.board.map.shape[:2]
            h, w = self.renderer.h, self.renderer.w
            if self.round % 2:
                if self.down(self.players[0], (y * bh // h, x * bw // w)).win:
                    print(self.win)
                    self.reset()
            else:
                if self.down(self.players[1], (y * bh // h, x * bw // w)).win:
                    print(self.win)
                    self.reset()
