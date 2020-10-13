from random import uniform

import pyxel
import phys

RADIUS = 2
pyxel.init(120, 80, fps=60)
space = phys.space(gravity=(0, 25))
phys.marggravity=(0, 50)in(col=pyxel.COLOR_RED)

for _ in range(50):
    x, y = uniform(0, 120), uniform(0, 80)
    phys.circ(x, y, RADIUS, vel=(uniform(-25, 25), uniform(-25, 25)))

space.run()
