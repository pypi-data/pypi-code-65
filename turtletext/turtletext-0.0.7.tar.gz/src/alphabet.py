import math
import random


class Alphabet():
    def __init__(self, t, x, y, size):
        self.x_start = x
        self.y_start = y
        self.t = t
        self.size = size
        self.t.color((random.random(), random.random(), random.random()))

    def toStart(self):
        self.t.up()
        self.rotate(self.x_start, self.y_start)
        self.goto(self.x_start, self.y_start)
        self.t.down()

    def rotate(self, x, y):
        angle = (360+(self.t.towards(x, y)-self.t.heading())) % 360
        if angle < 180:
            self.t.left(angle)
        else:
            self.t.right(360-angle)

    def goto(self, x, y):
        self.t.goto(x, y)

    def arc(self, r, angle, isRight=False, doDraw=True):
        if isRight:
            r *= -1
        if not doDraw:
            self.t.pu()
        self.t.circle(r, angle)
        if not doDraw:
            self.t.pd()

    def draw(self):
        pass


class A(Alphabet):
    def __init__(self, t, x, y, size):
        super().__init__(t, x, y, size)
        self.x_start += size/2
        self.y_start -= size/6

    def draw(self):

        self.toStart()
        self.rotate(self.x_start-self.size/4, self.y_start-self.size/6*4)
        self.goto(self.x_start-self.size/4, self.y_start-self.size/6*4)
        self.rotate(self.x_start-self.size/2, self.y_start-self.size/6*4)
        self.arc(self.size/3, 180, isRight=True, doDraw=False)
        self.toStart()
        self.rotate(self.x_start+self.size/4, self.y_start-self.size/6*4)
        self.goto(self.x_start+self.size/4, self.y_start-self.size/6*4)
        self.rotate(self.x_start+self.size/2, self.y_start-self.size/6*4)
        self.arc(self.size/6, 180, doDraw=False)
        self.t.up()
        self.t.forward(self.size/8)
        self.t.down()
        self.t.forward(self.size/4)


class B(Alphabet):
    def __init__(self, t, x, y, size):
        super().__init__(t, x, y, size)
        self.x_start += size/6
        self.y_start -= size/6

    def draw(self):
        self.toStart()
        self.rotate(self.x_start, self.y_start-self.size/6*4)
        self.goto(self.x_start, self.y_start-self.size/6*4)
        self.t.right(90)
        self.arc(self.size/3, 180, isRight=True, doDraw=False)
        self.goto(self.x_start+self.size/6*2, self.y_start)
        self.arc(self.size/6, 180, isRight=True)
        self.t.forward(self.size/3)
        self.t.left(180)
        self.t.forward(self.size/3)
        self.arc(self.size/6, 180, isRight=True)
        self.t.forward(self.size/3)


class C(Alphabet):
    def __init__(self, t, x, y, size):
        super().__init__(t, x, y, size)
        self.x_start += self.size/2+self.size/3*math.cos(math.pi/9)
        self.y_start = self.y_start-self.size/2+self.size/3*math.sin(math.pi/9)

    def draw(self):
        self.toStart()
        self.t.left(110-self.t.heading())
        self.arc(self.size/3, 320)


class D(Alphabet):
    def __init__(self, t, x, y, size):
        super().__init__(t, x, y, size)
        self.x_start += size/6
        self.y_start -= size/6

    def draw(self):
        self.toStart()
        self.rotate(self.x_start, self.y_start-self.size/6*4)
        self.goto(self.x_start, self.y_start-self.size/6*4)
        self.t.right(90)
        self.arc(self.size/3, 180, isRight=True, doDraw=False)
        self.t.forward(self.size/6)
        self.arc(self.size/3, 180, isRight=True)
        self.t.forward(self.size/6)


class E(Alphabet):
    def __init__(self, t, x, y, size):
        super().__init__(t, x, y, size)
        self.x_start += size/6
        self.y_start -= size/6

    def draw(self):
        self.toStart()
        self.rotate(self.x_start, self.y_start-self.size/6*4)
        self.goto(self.x_start, self.y_start-self.size/6*4)
        self.t.right(90)
        self.arc(self.size/3, 180, isRight=True, doDraw=False)
        self.goto(self.x_start+self.size/6*4, self.y_start)
        self.arc(self.size/6, 180, isRight=True, doDraw=False)
        self.t.up()
        self.t.forward(self.size/6)
        self.t.down()
        self.t.forward(self.size/2)
        self.arc(self.size/6, 180, isRight=False, doDraw=False)
        self.t.forward(self.size/6*4)


class F(Alphabet):
    def __init__(self, t, x, y, size):
        super().__init__(t, x, y, size)
        self.x_start += size/6
        self.y_start -= size/6

    def draw(self):
        self.toStart()
        self.rotate(self.x_start, self.y_start-self.size/6*4)
        self.goto(self.x_start, self.y_start-self.size/6*4)
        self.t.right(90)
        self.arc(self.size/3, 180, isRight=True, doDraw=False)
        self.goto(self.x_start+self.size/6*4, self.y_start)
        self.arc(self.size/6, 180, isRight=True, doDraw=False)
        self.t.up()
        self.t.forward(self.size/6)
        self.t.down()
        self.t.forward(self.size/2)


class G(Alphabet):
    def __init__(self, t, x, y, size):
        super().__init__(t, x, y, size)
        self.x_start += self.size/2+self.size/3*math.cos(math.pi/6)
        self.y_start = self.y_start-self.size / \
            2+self.size/3*math.sin(math.pi/6)

    def draw(self):
        self.toStart()
        self.t.left(110-self.t.heading())
        self.arc(self.size/3, 320)
        self.t.left(110)
        self.t.forward(self.size/4)
        self.t.left(180)
        self.t.forward(self.size/4)
        self.t.right(90)
        self.t.forward(self.size/4)


class H(Alphabet):
    def __init__(self, t, x, y, size):
        super().__init__(t, x, y, size)
        self.x_start += size/6
        self.y_start -= size/6

    def draw(self):
        self.toStart()
        self.rotate(self.x_start, self.y_start-self.size/6*4)
        self.goto(self.x_start, self.y_start-self.size/6*4)
        self.t.right(90)
        self.arc(self.size/6, 180, isRight=True, doDraw=False)
        self.goto(self.t.xcor()+self.size/6*4, self.t.ycor())
        self.arc(self.size/6, 180, doDraw=False)
        self.t.left(90)
        self.goto(self.t.xcor(), self.t.ycor()-self.size/6*4)


class I(Alphabet):
    def __init__(self, t, x, y, size):
        super().__init__(t, x, y, size)
        self.x_start += size/2
        self.y_start -= size/6

    def draw(self):
        self.toStart()
        self.rotate(self.x_start, self.y_start-self.size/6*4)
        self.goto(self.x_start, self.y_start-self.size/6*4)


class J(Alphabet):
    def __init__(self, t, x, y, size):
        super().__init__(t, x, y, size)
        self.x_start += size/3
        self.y_start -= size/6

    def draw(self):
        self.toStart()
        self.rotate(self.x_start, self.y_start-self.size/6*4)
        self.goto(self.x_start, self.y_start-self.size/2)
        self.arc(self.size/6, 180, isRight=True)


class K(Alphabet):
    def __init__(self, t, x, y, size):
        super().__init__(t, x, y, size)
        self.x_start += size/6
        self.y_start -= size/6

    def draw(self):
        self.toStart()
        self.rotate(self.x_start, self.y_start-self.size/6*4)
        self.goto(self.x_start, self.y_start-self.size/6*4)
        self.rotate(self.x_start+self.size/6*3, self.y_start)
        self.t.pu()
        self.goto(self.x_start+self.size/6*3, self.y_start)
        self.t.pd()
        self.rotate(self.x_start, self.y_start-self.size/12*5)
        self.goto(self.x_start, self.y_start-self.size/12*5)
        self.rotate(self.x_start+self.size/6*3, self.y_start)
        self.t.pu()
        self.t.forward(self.size/8)
        self.t.pd()
        self.rotate(self.x_start+self.size/6*3, self.y_start-self.size/6*4)
        self.goto(self.x_start+self.size/6*3, self.y_start-self.size/6*4)


class L(Alphabet):
    def __init__(self, t, x, y, size):
        super().__init__(t, x, y, size)
        self.x_start += size/6
        self.y_start -= size/6

    def draw(self):
        self.toStart()
        self.rotate(self.x_start, self.y_start-self.size/6*4)
        self.goto(self.x_start, self.y_start-self.size/6*4)
        self.rotate(self.x_start+self.size/6*4, self.y_start-self.size/6*4)
        self.goto(self.x_start+self.size/6*4, self.y_start-self.size/6*4)


class M(Alphabet):
    def __init__(self, t, x, y, size):
        super().__init__(t, x, y, size)
        self.x_start += size/6
        self.y_start -= size/6

    def draw(self):
        self.toStart()
        self.rotate(self.x_start, self.y_start-self.size/6*4)
        self.goto(self.x_start, self.y_start-self.size/6*4)
        self.t.right(90)
        self.arc(self.size/3, 180, isRight=True, doDraw=False)
        self.rotate(self.x_start+self.size/3, self.y_start-self.size/6*4)
        self.goto(self.x_start+self.size/3, self.y_start-self.size/6*4)
        self.rotate(self.x_start+self.size/6*4, self.y_start)
        self.goto(self.x_start+self.size/6*4, self.y_start)
        self.rotate(self.x_start+self.size/6*4, self.y_start-self.size/6*4)
        self.goto(self.x_start+self.size/6*4, self.y_start-self.size/6*4)


class N(Alphabet):
    def __init__(self, t, x, y, size):
        super().__init__(t, x, y, size)
        self.x_start += size/6
        self.y_start -= size/6

    def draw(self):
        self.toStart()
        self.rotate(self.x_start, self.y_start-self.size/6*4)
        self.goto(self.x_start, self.y_start-self.size/6*4)
        self.t.right(90)
        self.arc(self.size/3, 180, isRight=True, doDraw=False)
        self.rotate(self.x_start+self.size/6*4, self.y_start-self.size/6*4)
        self.goto(self.x_start+self.size/6*4, self.y_start-self.size/6*4)
        self.rotate(self.x_start+self.size/6*4, self.y_start)
        self.goto(self.x_start+self.size/6*4, self.y_start)


class O(Alphabet):
    def __init__(self, t, x, y, size):
        super().__init__(t, x, y, size)
        self.x_start += self.size/2+self.size/3*math.cos(math.pi/9)
        self.y_start = self.y_start-self.size/2+self.size/3*math.sin(math.pi/9)

    def draw(self):
        self.toStart()
        self.t.left(110-self.t.heading())
        self.arc(self.size/3, 360)


class P(Alphabet):
    def __init__(self, t, x, y, size):
        super().__init__(t, x, y, size)
        self.x_start += size/6
        self.y_start -= size/6

    def draw(self):
        self.toStart()
        self.rotate(self.x_start, self.y_start-self.size/6*4)
        self.goto(self.x_start, self.y_start-self.size/6*4)
        self.t.right(90)
        self.arc(self.size/3, 180, isRight=True, doDraw=False)
        self.goto(self.x_start+self.size/6*2, self.y_start)
        self.arc(self.size/6, 180, isRight=True)
        self.t.forward(self.size/3)


class Q(Alphabet):
    def __init__(self, t, x, y, size):
        super().__init__(t, x, y, size)
        self.x_start += self.size/2+self.size/3*math.cos(math.pi/9)
        self.y_start = self.y_start-self.size/2+self.size/3*math.sin(math.pi/9)

    def draw(self):
        self.toStart()
        self.t.left(110-self.t.heading())
        self.arc(self.size/3, 360)
        self.rotate(self.t.xcor()-self.size/6, self.t.ycor()-self.size/4)
        self.t.pu()
        self.goto(self.t.xcor()-self.size/6, self.t.ycor()-self.size/4)
        self.t.pd()
        self.rotate(self.t.xcor()+self.size/6, self.t.ycor()-self.size/6)
        self.goto(self.t.xcor()+self.size/6, self.t.ycor()-self.size/6)


class R(Alphabet):
    def __init__(self, t, x, y, size):
        super().__init__(t, x, y, size)
        self.x_start += size/6
        self.y_start -= size/6

    def draw(self):
        self.toStart()
        self.rotate(self.x_start, self.y_start-self.size/6*4)
        self.goto(self.x_start, self.y_start-self.size/6*4)
        self.t.right(90)
        self.arc(self.size/3, 180, isRight=True, doDraw=False)
        self.goto(self.x_start+self.size/6*2, self.y_start)
        self.arc(self.size/6, 180, isRight=True)
        self.t.forward(self.size/3)
        self.t.left(180)
        self.t.forward(self.size/6)
        self.rotate(self.x_start+self.size/2, self.y_start-self.size/6*4)
        self.goto(self.x_start+self.size/2, self.y_start-self.size/6*4)


class S(Alphabet):
    def __init__(self, t, x, y, size):
        super().__init__(t, x, y, size)

        self.x_start += self.size/6*5
        self.y_start -= self.size/3

    def draw(self):
        self.toStart()
        self.rotate(self.x_start, self.y_start+1)
        self.arc(self.size/6, 90)
        self.t.forward(self.size/3)
        self.arc(self.size/6, 180)
        self.t.forward(self.size/3)
        self.arc(self.size/6, 180, isRight=True)
        self.t.forward(self.size/3)
        self.arc(self.size/6, 90, isRight=True)


class T(Alphabet):
    def __init__(self, t, x, y, size):
        super().__init__(t, x, y, size)
        self.x_start += size/6
        self.y_start -= size/6

    def draw(self):
        self.toStart()
        self.rotate(self.x_start+self.size/6*4, self.y_start)
        self.goto(self.x_start+self.size/6*4, self.y_start)
        self.t.left(90)
        self.arc(self.size/6, 180, doDraw=False)
        self.goto(self.x_start+self.size/6*2, self.y_start-self.size/6*4)


class U(Alphabet):
    def __init__(self, t, x, y, size):
        super().__init__(t, x, y, size)
        self.x_start += self.size/4
        self.y_start -= self.size/6

    def draw(self):
        self.toStart()
        self.rotate(self.x_start, self.y_start-self.size/12*5)
        self.goto(self.x_start, self.y_start-self.size/12*5)
        self.arc(self.size/4, 180)
        self.goto(self.x_start+self.size/2, self.y_start)


class V(Alphabet):
    def __init__(self, t, x, y, size):
        super().__init__(t, x, y, size)
        self.x_start += size/6
        self.y_start -= size/6

    def draw(self):
        self.toStart()
        self.rotate(self.x_start+self.size/3, self.y_start-self.size/6*4)
        self.goto(self.x_start+self.size/3, self.y_start-self.size/6*4)
        self.rotate(self.x_start+self.size/6*4, self.y_start)
        self.goto(self.x_start+self.size/6*4, self.y_start)


class W(Alphabet):
    def __init__(self, t, x, y, size):
        super().__init__(t, x, y, size)
        self.x_start += size/6
        self.y_start -= size/6

    def draw(self):
        self.toStart()
        for i in range(1, 5):
            self.rotate(self.x_start+self.size/24*4*i,
                        self.y_start-self.size/6*4*(i % 2))
            self.goto(self.x_start+self.size/24*4 *
                      i, self.y_start-self.size/6*4*(i % 2))


class X(Alphabet):
    def __init__(self, t, x, y, size):
        super().__init__(t, x, y, size)
        self.x_start += size/6
        self.y_start -= size/6

    def draw(self):
        self.toStart()
        self.rotate(self.x_start+self.size/6*4, self.y_start-self.size/6*4)
        self.goto(self.x_start+self.size/6*4, self.y_start-self.size/6*4)
        self.rotate(self.x_start+self.size, self.y_start-self.size/6*4)
        self.arc(self.size/3, 180, doDraw=False)
        self.rotate(self.x_start, self.y_start-self.size/6*4)
        self.goto(self.x_start, self.y_start-self.size/6*4)


class Y(Alphabet):
    def __init__(self, t, x, y, size):
        super().__init__(t, x, y, size)
        self.x_start += size/6
        self.y_start -= size/6

    def draw(self):
        self.toStart()
        self.rotate(self.x_start+self.size/6*2, self.y_start-self.size/6*2)
        self.goto(self.x_start+self.size/6*2, self.y_start-self.size/6*2)
        self.rotate(self.x_start+self.size/6*4, self.y_start)
        self.goto(self.x_start+self.size/6*4, self.y_start)
        self.rotate(self.x_start+self.size/6*4, self.y_start+1)
        self.arc(self.size/6, 180, doDraw=False)
        self.t.pu()
        self.goto(self.x_start+self.size/6*2, self.y_start-self.size/6*2)
        self.t.pd()
        self.goto(self.x_start+self.size/6*2, self.y_start-self.size/6*4)


class Z(Alphabet):
    def __init__(self, t, x, y, size):
        super().__init__(t, x, y, size)
        self.x_start += size/6
        self.y_start -= size/6

    def draw(self):
        self.toStart()
        self.rotate(self.x_start+self.size/6*4, self.y_start)
        self.goto(self.x_start+self.size/6*4, self.y_start)
        self.rotate(self.x_start, self.y_start-self.size/6*4)
        self.goto(self.x_start, self.y_start-self.size/6*4)
        self.rotate(self.x_start+self.size/6*4, self.y_start-self.size/6*4)
        self.goto(self.x_start+self.size/6*4, self.y_start-self.size/6*4)


class Exclamation(Alphabet):
    def __init__(self, t, x, y, size):
        super().__init__(t, x, y, size)
        self.x_start += size/2
        self.y_start -= size/6

    def draw(self):
        self.toStart()
        self.rotate(self.x_start, self.y_start-self.size/3)
        self.goto(self.x_start, self.y_start-self.size/2)
        self.t.pu()
        self.t.forward(self.size/6)
        self.t.stamp()
        self.t.forward(self.size/6)


class Question(Alphabet):
    def __init__(self, t, x, y, size):
        super().__init__(t, x, y, size)

        self.x_start += self.size/6
        self.y_start -= self.size/3

    def draw(self):
        self.toStart()
        self.rotate(self.x_start, self.y_start+1)
        self.arc(self.size/6, 90, isRight=True)
        self.t.forward(self.size/3)
        self.arc(self.size/6, 180, isRight=True)
        self.arc(self.size/6, 90)
        self.t.pu()
        self.t.forward(self.size/6)
        self.t.stamp()
        self.arc(self.size/6, 90, isRight=True)
