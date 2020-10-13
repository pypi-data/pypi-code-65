import numpy as np
def sequence_split(sequence,n):
  xs,ys=[],[]
  for i in range(len(sequence)):
    last=i+n
    if last > len(sequence)-1:
      break
    v,w=sequence[i:last],sequence[last]
    xs.append(v)
    ys.append(w)
  return np.array(xs),np.array(ys)