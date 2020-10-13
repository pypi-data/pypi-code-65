#!/usr/bin/env python3

import numpy as np

yValue = 81
uValue = 90
vValue = 240

r = yValue + (1.403 * (vValue-128))
g = yValue - (0.714 * (vValue-128)) - (0.344 * (uValue-128))
b = yValue + (1.77 * (uValue-128))

print("r: " + str(np.round(r, 2)))
print("g: " + str(np.round(g, 2)))
print("b: " + str(np.round(b, 2)))

print("mean: " + str(np.mean([r, g, b])))

# lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
lum = 0.299 * r + 0.587 * g + 0.114 * b

print("lum: " + str(np.round(lum, 2)))

# Y -= 16;
# U -= 128;
# V -= 128;
# R = 1.164 * Y             + 1.596 * V;
# G = 1.164 * Y - 0.392 * U - 0.813 * V;
# B = 1.164 * Y + 2.017 * U;