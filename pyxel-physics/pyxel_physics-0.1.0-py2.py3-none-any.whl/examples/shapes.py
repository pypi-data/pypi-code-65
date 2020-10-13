import pyxel
import phys

pyxel.init(240, 160, fps=60, caption='Physics demo')
space = phys.space(gravity=(0, 50))
phys.margin()

ball = phys.circ(160, 20, 15, vel=(50, 50))
line = phys.line(50, 50, 100, 0, vel=(0, 0))
tri = phys.tri(100, 100, 100, 50, 40, 50, vel=(0, 0))
rect = phys.rect(0, 10, 40, 45, vel=(10, -10))

space.run()
