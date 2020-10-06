import turtle
import argparse

import alphabet
from alphabet import *


CHAR = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def getArgs():
    parser = argparse.ArgumentParser(description='A turtle writes text. You can use "ABCDEFGHIJKLMNOPQRSTUVWXYZ \n!?"')
    parser.add_argument('text', help='text you want turtle to write.')
    parser.add_argument('-s', '--speed', help='speed of turtle.', default=1)
    parser.add_argument('-w', '--width', help='width of character.', default=2)
    parser.add_argument('--shape', help='shape of turtle. You can choose from "arrow", "turtle", "circle", "square", "triangle", "classic".', default='turtle')

    args = parser.parse_args()
    return args

class Frame():

    def __init__(self, cfg):
        self.speed = float(cfg.speed)
        self.shape = cfg.shape
        self.width = float(cfg.width)
        self.text = cfg.text
        self.char_size = 100
        self.screen_size = (800, 600)

        self.t = self.init_turtle()

        self.wn = turtle.Screen()
        self.wn.screensize(*self.screen_size)

        canvas = self.wn.getcanvas()
        root = canvas.winfo_toplevel()

        self.running = True
        def on_close():
            self.running = False

        root.protocol("WM_DELETE_WINDOW", on_close)

    def init_turtle(self):
        t = turtle.Turtle()
        t.speed(self.speed)
        t.shape(self.shape)
        t.width(self.width)
        t.color((1., 0., 0.))

        return t

    def main(self):
        line = self.text
        line = line.upper()
        pos = self.getPosition(line)

        for char, p in zip(line, pos):
            if char in CHAR:
                cls = globals()[char]
                alph = cls(self.t, *p, self.char_size)
                alph.draw()
            elif char in "!":
                alph = alphabet.Exclamation(self.t, *p, self.char_size)
                alph.draw()
            elif char in "?":
                alph = alphabet.Question(self.t, *p, self.char_size)
                alph.draw()
        self.t.pu()
        angle = (360+(self.t.towards(min(self.screen_size)/2, 0)-self.t.heading())) % 360
        if angle < 180:
            self.t.left(angle)
        else:
            self.t.right(360-angle)
        self.t.goto(min(self.screen_size)/2, 0)
        self.t.left(90-self.t.heading())
        while self.running:
            self.t.circle(min(self.screen_size)/2, 10)


    def getPosition(self, line):
        i = 0
        num_br = 0
        tmp = []
        for char in line:
            if char in CHAR or char in " !?":
                i += 1
            elif char == "\n":
                tmp.append(i)
                i = 0

                num_br += 1
        tmp.append(i)

        if max(tmp)*self.char_size > self.screen_size[0]:
            self.char_size = self.screen_size[0]/max(tmp)
        if len(tmp)*self.char_size > self.screen_size[1]:
            self.char_size = self.screen_size[1]/len(tmp)

        pos = []
        tmp_br = 0
        for idx_y, tmpy in enumerate(tmp):
            y = (len(tmp)*self.char_size)/2-self.char_size*idx_y
            for idx_x in range(tmpy):
                x = -(tmpy*self.char_size)/2+self.char_size*idx_x
                pos.append((x, y))
            if tmp_br < num_br:
                pos.append(((tmpy*self.char_size)/2, y))
                tmp_br += 1
        return pos

def main():
    cfg = getArgs()
    frame = Frame(cfg)
    frame.main()


if __name__ == "__main__":
    main()
