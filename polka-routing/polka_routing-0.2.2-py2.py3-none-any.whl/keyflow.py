import time
import sympy
from mpmath import log
import numpy as np
import math

try:
    range = xrange
except Exception as ex:
    pass


def coeficiente(k, e, w):
    global lista
    c = 0
    l = k - 1
    for i in range(l, -1, -1):
        tmp = i * (k ** e)
        if w >= tmp:
            c = w - tmp
            break
    if c >= 0:
        lista.append(i)
    else:
        lista.append(0)

    return c


def gerar_primos(limite_min, limite_max, total):
    primos = []
    for numero in range(limite_min, limite_max + 1):
        max_div = int(math.floor(math.sqrt(numero)))
        for auxiliar in range(2, 1 + max_div):
            if numero % auxiliar == 0:
                break
        else:
            primos.append(numero)
            if len(primos) == total:
                break
    return primos


def mod_inverse(a, b):
    r = -1
    B = b
    A = a
    eq_set = []
    full_set = []
    mod_set = []

    # euclid's algorithm
    while r != 1 and r != 0:
        r = b % a
        q = b // a
        eq_set = [r, b, a, q * -1]
        b = a
        a = r
        full_set.append(eq_set)

    for i in range(0, 4):
        mod_set.append(full_set[-1][i])

    mod_set.insert(2, 1)
    counter = 0

    # extended euclid's algorithm
    for i in range(1, len(full_set)):
        if counter % 2 == 0:
            mod_set[2] = full_set[-1 * (i + 1)][3] * mod_set[4] + mod_set[2]
            mod_set[3] = full_set[-1 * (i + 1)][1]

        elif counter % 2 != 0:
            mod_set[4] = full_set[-1 * (i + 1)][3] * mod_set[2] + mod_set[4]
            mod_set[1] = full_set[-1 * (i + 1)][1]

        counter += 1

    if mod_set[3] == B:
        return mod_set[2] % B
    return mod_set[4] % B


def calculate_routeid(Midlist, pathlen, toponame, debug=False):
    if debug:
        print("{}".format(Midlist))
        print("Pathlen: {}".format(pathlen))

    mult = 1.0

    for i in range(len(Midlist) - 1, len(Midlist) - pathlen - 1, -1):
        if debug:
            print("Midlist[{}]: {}".format(i, Midlist[i]))
        mult = mult * Midlist[i]

    total = float(log(mult, 2))
    total = np.ceil(total)

    if debug:
        print("total: {}".format(total))
        print("[{}] Total of the bits to PRI: {}".format(toponame, total))

    return total


def max_bitlength_keyflow(nports, nnodes, lpath, toponame):
    Midlist = gerar_primos(nports, 1000000, nnodes)
    nbits = int(calculate_routeid(Midlist, lpath, toponame))
    return nbits


# def scalability_analysis():

# lst = []

## 2-tier Topologies
# switch_ports = [24,48,96]
# spine_nodes = [6,12,16,24,36,48]
# lpath = 3

# for nspine in spine_nodes:
# nleaf = nspine
# nnodes = nspine + nleaf

# for nports in switch_ports:
# if (nports>nspine):
# nservers = (nports-nspine) * nleaf
##topo_name = "2-tier - spine: ", nspine, " - leaf: ", nleaf, "- switches: ", nnodes," - ports: ", nports," - servers: ", nservers, " - lpath: ", lpath
# topo_name = "2-tier spine "+ str(nspine) +" leaf "+ str(nleaf)
# nbits = max_bitlength_keyflow(nports,nnodes,lpath,topo_name)
# print "######", topo_name
# print "Bitlength:", nbits
# lst.append(topo_name+","+str(nnodes)+","+str(nservers)+","+str(nbits))

##Hypercube Topologies
# degree = [3,4,5,6,7,8,9,10]

# for ndegree in degree:
# nservers = pow(2,ndegree)
# nnodes = nservers
# nports = ndegree
# lpath = ndegree

##topo_name = "Hypercube - degree: ", ndegree, "- switches: ", nnodes," - ports: ", nports," - servers: ", nservers, " - lpath: ", lpath
# topo_name = "Hypercube degree "+str(ndegree)

# nbits = max_bitlength_keyflow(nports,nnodes,lpath,topo_name)
# print "######", topo_name
# print "Bitlength:", nbits
# lst.append(topo_name+","+str(nnodes)+","+str(nservers)+","+str(nbits))

# arr = np.array(lst)
# np.savetxt('data_keyflow.csv', arr, delimiter=',', fmt="%s")
