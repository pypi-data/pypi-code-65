#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2020/9/27 13:05
# @Author : 詹荣瑞
# @File : game.py
# @desc : 本代码未经授权禁止商用
from .core import Player


class Game(object):

    def __init__(self, board, players):
        self.board = board
        self.players = players

        self.success = False
        self.round = 0

    def __str__(self):
        out = str(self.board)
        for p in self.players:
            out = out.replace(f"{p.number}", p.print)
        return out

    def down(self, player, pos):
        """
        判断位置是否有子，若无子则下子

        :param player: 下子玩家
        :param pos: 下子位置
        :return:
        """
        current_piece = self.board.map[pos]
        if current_piece == 0:
            self.success = True
            if isinstance(player, Player):
                self.board.map[pos] = player.number
            else:
                self.board.map[pos] = self.players[player].number
        else:
            self.success = False
            print(f"位置{pos}已有子")
        return self

    def render(self):
        raise NotImplementedError
