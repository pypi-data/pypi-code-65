from random import uniform

import pyxel
import phys

pyxel.init(120, 80, fps=60)
space = phys.space(bg=0, col=1, gravity=(0, 10))
phys.margin()

for y in [15, 25, 35, 45, 55, 65]:
    balls = [
        phys.circ(10 * i + 15, y, 2,
                  col=pyxel.COLOR_RED,
                  vel=(0, uniform(0, 50)))
        for i in range(10)
    ]

space.run()
