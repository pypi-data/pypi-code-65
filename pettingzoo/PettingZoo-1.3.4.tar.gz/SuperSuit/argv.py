import numpy as np
import time

vals = [np.ones((4,32*4,32*4,4)) for i in range(100)]

start = time.time()
for val in vals:
    val.transpose((1,2,0,3)).reshape(32*4,32*4,4*4)
end  = time.time()
print(end - start)
