from sliced_normals import scaled_sn, basic_sn
#from . import z_expand, z_expand_func
from timeit import timeit
import numpy as np
import matplotlib.pyplot as plt
setup = """\
from itertools import combinations_with_replacement as cwr
from itertools import chain
from functools import reduce
from operator import mul
import numpy as np

def z_expand_func(data, dof):
    return [
        reduce(mul, c) for c in
        chain.from_iterable([cwr(data, d) for d in range(1, dof + 1)])
        ]

zfun = lambda x, dof: [*map(pow, [x[0]]*dof, range(1,dof+1))]

test = np.random.multivariate_normal([1,2,3],[[1,0,0],[0,1,0],[0,0,1]],size=100)
q = np.cov(test)
"""
def pol2cart(phi, rho):
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return(x, y)

dlen = 100
DoF = 9

[datax,datay] = pol2cart(np.random.rand(1,dlen)*2*np.pi-1, np.random.rand(1,dlen)*0.2+2)
data1 = np.append(datax.T, datay.T,1)
data2 = np.random.multivariate_normal([0, 0], [[0.8, 0.793],[0.793, 0.8]], int(dlen/2))
data3 = np.random.multivariate_normal([0, 0], [[0.8, -0.793],[-0.793, 0.8]], int(dlen/2))
Phdata = np.append(data1, np.append(data2, data3, 0), 0)

def datadraw():
    r = np.random.rand()
    if r <=0.5:
        [x, y] = pol2cart(np.random.rand(1)*2*np.pi-1, np.random.rand(1)*0.2+2)
        return np.hstack([x, y])
    elif r <= 0.75:
        return np.random.multivariate_normal([0, 0], [[0.8, 0.793],[0.793, 0.8]], 1)[0]
    else:
        return np.random.multivariate_normal([0, 0], [[0.8, -0.793],[-0.793, 0.8]], 1)[0]

data = np.vstack([datadraw() for n in range(0,500)])
plt.hist(data[:,0], density=True, bins=40)
ax = plt.gca()
ax2 = ax.twinx()
x = np.linspace(min(data[:,0]),max(data[:,0]),1000)
sn = scaled_sn(np.vstack([datadraw() for n in range(0,20)]), 5, 1000)
sn.sn_phi(data[0:3])
sn = basic_sn(data, 3)
print(-sn.sn_phi(datadraw())[0])
for i in range(2,9):
    sn = scaled_sn(data[:,0], i, 100000)
    y = np.exp([-1*s for s in sn.sn_phi(x)])
    ax2.plot(x, y/max(y), label=i)
plt.legend()
sn = basic_sn(data[:,0], 3)
print(timeit("-(2*np.sum(np.log(np.diag(np.linalg.cholesky(np.eye(3))))))",setup,number=10000))
print(timeit("-np.log(np.linalg.det(np.eye(3)))",setup,number=10000))
#print(timeit("np.sum(np.array([[3, 2]]*100)**2, 1)**0.5",setup,number=10000))
#print(timeit("mapmean(data)",setup,number=10000))
print(-1*np.array([*sn.sn_phi(data[0,0])]))
plt.show()