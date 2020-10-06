from sympy.polys.domains import ZZ
from sympy.polys.domains import GF
from sympy.polys.galoistools import gf_rem, gf_quo, gf_mul, gf_add
from sympy.polys.galoistools import gf_sub, gf_degree, gf_irreducible_p
from sympy.ntheory.modular import solve_congruence
import time
import math
import numpy as np
import logging
import itertools
import ast
import os
import pickle
import glob
import shutil
import networkx as nx
import matplotlib.pyplot as plt
import json
import time

try:
    # Python 2
    xrange
except NameError:
    # Python 3, xrange is now named range
    xrange = range

# https://stackoverflow.com/questions/44522676/including-the-current-method-name-when-printing-in-python
# LOGGER.info("Running %d", 1)
# LOGGER.error("Running %s", 2)
# LOGGER.debug("Running %03d", 0)


def create_logger(app_name=None):
    logger = logging.getLogger(app_name or __name__)
    # logger.setLevel(logging.DEBUG)
    logger.setLevel(logging.ERROR)
    log_format = "[%(asctime)-15s] [%(levelname)08s] (%(funcName)s %(message)s)"
    logging.basicConfig(format=log_format)
    return logger


LOGGER = create_logger()

# https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm
# function inverse(a, p)
# t := 0;     newt := 1;
# r := p;     newr := a;
# while newr != 0
# quotient := r div newr
# (r, newr) := (newr, r - quotient * newr)
# (t, newt) := (newt, t - quotient * newt)
# if degree(r) > 0 then
# return "Either p is not irreducible or a is a multiple of p"
# return (1/r) * t
# Calculates de multiplicative inverse of a mod p for GF using Extended Euclidean algorithm


def inverse(a, p, gfp):
    t = []
    newt = [1]
    r = p
    newr = a

    while newr != []:
        # >> quotient = r div newr
        quotient = gf_quo(ZZ.map(r), ZZ.map(newr), gfp, ZZ)
        # >> newr = r - quotient * newr
        tmp = newr
        multr = gf_mul(quotient, newr, gfp, ZZ)
        newr = gf_sub(r, multr, gfp, ZZ)
        r = tmp
        # >> newt = t - quotient * newt
        temp = newt
        multt = gf_mul(quotient, newt, gfp, ZZ)
        newt = gf_sub(t, multt, gfp, ZZ)
        t = temp

    if gf_degree(newr) > 0:
        print("Either p is not irreducible or a is a multiple of p")
    # >> print (1/r) * t
    res = gf_quo(t, r, gfp, ZZ)
    # print "Inverse: ", res
    return res


# Calculates RouteID using CRT for GF2
def calculate_routeid(s, o, debug=False):
    LOGGER.debug("Running")
    print("S= ", s)
    print("O= ", o)

    # Calculate Ti
    t = []
    for i in range(len(s)):
        current = s[i]
        elem = [1]
        for j in s:
            factor = ZZ.map(j)
            if factor != current:
                elem = gf_mul(ZZ.map(elem), ZZ.map(factor), 2, ZZ)
        t.append(elem)
    if debug:
        print("T= ", t)

    # Calculate Ni
    n = []
    for i in range(len(s)):
        elem = inverse(t[i], s[i], 2)
        n.append(elem)

    if debug:
        print("N= ", n)

    # Calculate Xi
    xx = []
    for i in range(len(s)):
        elem = gf_mul(ZZ.map(o[i]), ZZ.map(n[i]), 2, ZZ)
        elem = gf_mul(ZZ.map(elem), ZZ.map(t[i]), 2, ZZ)
        xx.append(elem)

    if debug:
        print("XX= ", xx)

    # Calculate X = SUM Xi
    x = []
    for i in range(len(s)):
        x = gf_add(x, xx[i], 2, ZZ)
    if debug:
        print("X: ", x)

    # Calculate M
    m = [1]
    for i in range(len(s)):
        m = gf_mul(ZZ.map(m), ZZ.map(s[i]), 2, ZZ)
    if debug:
        print("M: ", m)

    # Calculate F
    f = gf_rem(ZZ.map(x), ZZ.map(m), 2, ZZ)
    if debug:
        print("F: ", f)

    # Check
    for i in range(len(s)):
        if debug:
            print(
                "Check[", i, "] == ", gf_rem(ZZ.map(f), ZZ.map(s[i]), 2, ZZ) == o[i],
            )

    return f


def print_poly(p):
    print("Len: ", len(p))
    print("Poly (list): ", p)
    intp = shifting(p)
    print("Poly (int): ", intp)
    print("Poly (bin): ", bin(intp))
    print("Poly (hex): ", hex(intp))


def shifting(bitlist):
    out = 0
    for bit in bitlist:
        out = (out << 1) | bit
    return out


def increment_helper(lst, carry):
    if not carry:
        return lst

    if not lst:
        return [1]

    if lst[0]:
        return [0] + increment_helper(lst[1:], True)

    return [1] + lst[1:]


# https://stackoverflow.com/questions/49139939/how-to-recursively-increment-a-binary-number-in-list-form-without-converting-t
def increment(lst):
    # long but really just reverse input and output
    return increment_helper(lst[::-1], True)[::-1]


# Returns List of Irreducible Polynomials Mod2 for degree n
def create_list_irrpoly_mod2(n):
    p = 2
    # degree of polynomials
    K = ZZ

    f = []
    total = pow(2, n)
    poly = [K.one] + [K(0) for i in xrange(0, n)]
    for j in range(total):
        if gf_irreducible_p(poly, p, K):
            f.append(poly)
            # print_poly(poly)
        poly = increment(poly)
    return f


# Returns List of Irreducible Polynomials Mod2 for degree n
def create_irrpoly_mod2(degree, npoly, debug=False):
    p = 2
    # degree of polynomials
    K = ZZ

    f = []
    total = pow(2, degree)
    poly = [K.one] + [K(0) for i in xrange(0, degree)]
    x = 1
    for j in range(total):
        if x > npoly:
            break
        if gf_irreducible_p(poly, p, K):
            f.append(poly)
            if debug:
                print(x)
                print_poly(poly)
            x = x + 1
        poly = increment(poly)

    return f


def generate_coprimes_table(mindegree, maxdegree):

    f = []
    for n in range(mindegree, maxdegree + 1):
        f = f + create_list_irrpoly_mod2(n)
    return f


def generate_coprimes_table_print(mindegree, maxdegree):

    print("Generating table...")
    f = []
    lst = []
    for n in range(mindegree, maxdegree + 1):
        p = create_list_irrpoly_mod2(n)
        f = f + p
        lst.append(str(n) + ";" + str(len(p)) + ";" + str(p))

    filename = "irr_poly_table" + str(mindegree) + "_" + str(maxdegree) + ".csv"
    # Export to csv file
    arr = np.array(lst)
    np.savetxt(filename, arr, delimiter=",", fmt="%s")

    return f


def generate_coprimes_table_pickle(mindegree, maxdegree, directory):

    print("Generating table with pickle...")
    f = []
    lst = []

    if os.path.exists(directory):
        shutil.rmtree(directory)

    os.makedirs(directory)
    os.chdir(directory)

    for n in range(mindegree, maxdegree + 1):
        p = create_list_irrpoly_mod2(n)
        f = f + p
        filename = str(n) + "_" + str(len(p))
        with open(filename, "wb") as filehandle:
            pickle.dump(p, filehandle)

    return f


def get_coprimes_table_pickle(mindegree, maxdegree, filepath):
    print("Reading table with pickle...")

    table = []

    for i in range(mindegree, maxdegree + 1):
        directory = filepath + "/" + str(i) + "_*"
        print(directory)
        for filename in glob.glob(directory):
            with open(filename, "rb") as f:
                lst = pickle.load(f)
                table += lst

    return table


def read_coprimes_table(filename):
    print("Reading table...")

    lst = pd.read_csv(filename, delimiter=";")

    table = []

    for i, elrow in lst.iterrows():
        print(i)
        x = ast.literal_eval(elrow[2])
        table = table + x
        # print elrow[2]

    # Export to txt file
    arr = np.array(table)
    np.savetxt("teste.txt", arr, delimiter="/", fmt="%s")

    return table


def save_list2file(filepath, my_list):
    with open(filepath, "w") as f:
        for item in my_list:
            f.write("%s\n" % item)


def generate_nodeids(mindegree, n):
    nodeids = []
    table = generate_coprimes_table(int(mindegree), int(13))

    if len(table) < n:
        print(
            "Error: Table of Irreducible Polynomials was not generated for this degree."
        )
        return -1

    for i in range(0, n):
        nodeids.append(table[i])

    return nodeids


def generate_nodeids_table(mindegree, n, directory):
    nodeids = []

    maxdeg = 24
    table = get_coprimes_table_pickle(mindegree, maxdeg, directory)

    if len(table) < n:
        print(
            "Error: Table of Irreducible Polynomials was not generated for this degree."
        )
        return -1

    for i in range(0, n):
        nodeids.append(table[i])

    return nodeids


def _add_edge_port(G, **kwargs):
    node_list = [kwargs["name"], kwargs["switch"]["name"]]
    port_list = [kwargs["port"], kwargs["switch"]["port"]]

    edge_ports = {}

    for idx in range(0, 2):
        node_idx = node_list[idx]
        port_idx = port_list[idx]

        # Sanity check to see if the nodes and ports are present in Graph
        if G.nodes().get(node_idx, None) is None:
            print("Node : {} is not present in Graph".format(node_idx))
            return

        if port_idx not in G.nodes(data=True)[node_idx]["ports"]:
            print(
                "Port ID :{} is incorrect for Node ID : {}!".format(node_idx, port_idx)
            )
            return

        # edge_ports.append("{}.{}".format(node_idx, port_idx))
        # edge_ports.append(port_idx)
        edge_ports[str(node_idx)] = port_idx

    # Add the anchor points as edge attributes
    G.add_edge(kwargs["name"], kwargs["switch"]["name"], anchors=edge_ports)


def create_topology_json(json_data=None, plot=False, debug=False):
    # Creating new Graph by using the topology defined on JSON file
    G = nx.Graph()
    # Loading the data from JSON file
    degree = 0
    irpoly = None
    data = None
    try:
        data = json.load(json_data)
    except Exception as ex:
        raise ex

    if data:
        # Adding switches
        if data.get("switches", None) and data.get("hosts", None):
            for node in data.get("switches"):
                if len(node["ports"]) > degree:
                    degree = math.ceil(len(node["ports"]))
            # Irr Polynomious
            irpoly = create_irrpoly_mod2(degree, len(data.get("switches")))

            for node in data.get("switches"):
                G.add_node(node["name"], nodeID=irpoly.pop(), ports=node["ports"])

            # Adding hosts
            for node in data.get("hosts"):
                G.add_node(node["name"], ports=node["ports"])
        else:
            raise "Missing swicthes and hosts configuration"

        if data.get("links", None):
            # Adding links
            for link in data["links"]["switches"]:
                _add_edge_port(G, link)
            for link in data["links"]["hosts"]:
                _add_edge_port(G, link)
        else:
            raise "Missing links configuration"

        if data.get("links", None):
            for route in data["routes"]:
                #  Calculate the route
                path = nx.dijkstra_path(G, route["from"], route["to"])[2:]

                # Generating the routeID
                if debug:
                    print("{} -> {}".format(route["from"], route["to"]))
                s = []
                o = []
                for x, _ in enumerate(path):
                    if (x + 1) == len(path):
                        break
                    else:
                        # print(G.get_edge_data(path[x], path[x+1]))
                        s.append(G.nodes().get(path[x])["nodeID"])
                        aux = format(
                            G.get_edge_data(path[x], path[x + 1])["anchors"][path[x]],
                            "b",
                        )
                        o.append([int(a) for a in aux])
                if debug:
                    print("RouteID: {}".format(calculate_routeid(s, o)))
                # print(G.edges(data=True))

        else:
            raise "Missing links configuration"

    if plot:
        nx.draw_networkx(G, node_size=1000)
        plt.show()
