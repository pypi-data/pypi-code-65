from polka.tools import *
import time

# Tests simple example
LOGGER = create_logger()


def test_simple_example():
    LOGGER.debug("Running")
    print("############Test Simple Example############")

    starting = time.time()
    # List of servers
    s1 = [1, 1]
    s2 = [1, 1, 1]
    s3 = [1, 0, 1, 1]
    s = []
    s.append(s1)
    s.append(s2)
    s.append(s3)
    ns = len(s)

    # List of ports in the path
    o1 = [1]
    o2 = [1, 0]
    o3 = [1, 1, 0]
    o = []
    o.append(o1)
    o.append(o2)
    o.append(o3)

    r = calculate_routeid(s, o)
    print("RouteID: {}".format(r))

    end = time.time()
    print("Finished: %0.3fms" % ((end - starting)))
    print("###########################################")


# Tests multicast example
def test_multicast_example():
    LOGGER.debug("Running")
    print("############Test Multicast Example############")

    starting = time.time()
    # List of servers
    s1 = [1, 1, 1]
    s2 = [1, 0, 0, 1, 1]
    s3 = [1, 0, 0, 0, 1, 1, 0, 1, 1]
    s = []
    s.append(s1)
    s.append(s2)
    s.append(s3)
    ns = len(s)

    # List of ports in the path
    o1 = [1, 0]
    o2 = [1, 1, 0]
    o3 = [1, 0, 0, 1, 0, 1, 0, 0]
    o = []
    o.append(o1)
    o.append(o2)
    o.append(o3)

    r = calculate_routeid(s, o)
    print("RouteID: ", r)

    end = time.time()
    print(("Finished: %0.3fms" % ((end - starting))))
    print("###########################################")


# Tests p4 example
def test_p4_example():
    LOGGER.debug("Running")
    print("############Test P4 Example ############")

    starting = time.time()
    # List of servers
    s1 = [
        1,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        1,
        0,
        0,
        0,
        1,
        1,
        0,
        1,
    ]
    s2 = [
        1,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        1,
        0,
        1,
        0,
        1,
        1,
        1,
        1,
    ]
    s3 = [
        1,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        1,
        1,
        0,
        0,
        0,
        1,
        0,
        1,
    ]

    s = []
    s.append(s1)
    # s.append(s3)
    s.append(s2)
    ns = len(s)

    # List of ports in the path
    # o1 = [1,1]
    o1 = [1, 0]
    o3 = [1, 1]
    o2 = [1]
    o = []
    o.append(o1)
    # o.append(o3)
    o.append(o2)

    r = calculate_routeid(s, o)

    print("S1: ", print_poly(s1))
    print("S2: ", print_poly(s2))
    # print "S3: ", print_poly(s3)

    print("O1: ", print_poly(o1))
    print("O2: ", print_poly(o2))
    # print "O3: ", print_poly(o3)

    print("RouteID: ", print_poly(r))

    end = time.time()
    print(("Finished: %0.3fms" % ((end - starting))))
    print("###########################################")


def test_p4_latency_example():
    LOGGER.debug("Running")
    print("############Test P4 Example ############")

    starting = time.time()
    # List of servers
    s = []
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1])

    ns = len(s)
    r = []

    # Path H0->H1
    o = []
    o.append([1, 0])
    sp = []
    sp.append(s[0])
    r.append(calculate_routeid(sp, o))
    print("RouteID[", 0, "]: ")
    print(print_poly(r[0]))
    print("###########################################")

    # Path H0->Hn
    for i in range(1, len(s)):
        sp = []
        o = []
        port = [1, 1]
        for j in range(0, i):
            sp.append(s[j])
            o.append(port)
        j = j + 1
        port = [1]
        o.append(port)
        sp.append(s[j])
        r.append(calculate_routeid(sp, o))
        print("RouteID[", i, "]: ")
        print(print_poly(r[i]))
        print("###########################################")

    end = time.time()
    print(("Finished: %0.3fms" % ((end - starting))))
    print("###########################################")


# This test considers that the first port was defined by a table entry
def test_p4_latency_2_example():
    LOGGER.debug("Running")
    print("############Test P4 Example ############")

    starting = time.time()
    # List of servers
    s = []
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1])

    ns = len(s)
    r = []

    print("Direction H0-H10: ")

    # Path H0->H1
    r.append([0])
    print("RouteID[", 0, "]: ")
    print(print_poly(r[0]))
    print("###########################################")

    # Path H0->Hn
    for i in range(1, len(s)):
        sp = []
        o = []
        port = [1, 1]
        tmp = i
        for j in range(1, i):
            sp.append(s[j])
            o.append(port)
            tmp = j + 1
        port = [1]
        o.append(port)
        sp.append(s[tmp])
        r.append(calculate_routeid(sp, o))
        print("RouteID[", i, "]: ")
        print(print_poly(r[i]))
        print("###########################################")

    end = time.time()
    print(("Finished: %0.3fms" % ((end - starting))))
    print("###########################################")

    print("Direction H10-H0: ")

    r = []

    # Path H1->H0
    r.append([0])
    print("RouteID[", 0, "]: ")
    print(print_poly(r[0]))
    print("###########################################")

    # Path Hn->H0
    for i in range(1, len(s)):
        sp = []
        o = []
        port = [1, 0]
        for j in range(i - 1, 0, -1):
            sp.append(s[j])
            o.append(port)
        port = [1]
        o.append(port)
        sp.append(s[0])
        r.append(calculate_routeid(sp, o))
        print("RouteID[", i, "]: ")
        print_poly(r[i])
        print("###########################################")

    end = time.time()
    print("Finished: %0.3fms" % ((end - starting)))
    print("###########################################")


# This test considers that the first port was defined by a table entry
def test_p4_latency_3_example():
    LOGGER.debug("Running")
    print("############Test P4 Example ############")

    starting = time.time()
    # List of servers
    s = []
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1])

    ns = len(s)
    r = []

    print("Direction H0-H10: ")

    # Path H0->H1
    r.append([0])
    print("RouteID[", 0, "]: ")
    print(print_poly(r[0]))
    print("###########################################")

    # Path H0->Hn
    for i in range(1, len(s)):
        sp = []
        o = []
        port = [1, 1]
        tmp = i
        for j in range(1, i):
            sp.append(s[j])
            o.append(port)
            tmp = j + 1
        port = [1]
        o.append(port)
        sp.append(s[tmp])
        r.append(calculate_routeid(sp, o))
        print("RouteID[", i, "]: ")
        print(print_poly(r[i]))
        print("###########################################")

    end = time.time()
    print(("Finished: %0.3fms" % ((end - starting))))
    print("###########################################")

    print("Direction H10-H0: ")

    r = []

    # Path H1->H0
    r.append([0])
    print("RouteID[", 0, "]: ")
    print(print_poly(r[0]))
    print("###########################################")

    # Path Hn->H0
    for i in range(1, len(s)):
        sp = []
        o = []
        port = [1, 0]
        for j in range(i - 1, 0, -1):
            sp.append(s[j])
            o.append(port)
        port = [1]
        o.append(port)
        sp.append(s[0])
        r.append(calculate_routeid(sp, o))
        print("RouteID[", i, "]: ")
        print(print_poly(r[i]))
        print("###########################################")

    end = time.time()
    print(("Finished: %0.3fms" % ((end - starting))))
    print("###########################################")


# Test for linear fabric topo
def test_p4_latency_fabric():
    LOGGER.debug("Running")
    print("############Test P4 Example ############")

    starting = time.time()
    # List of servers
    s = []
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1])

    ns = len(s)
    r = []

    print("Direction H0-H10: ")

    # Path H0->H1
    r.append([0])
    print("RouteID[", 0, "]: ")
    print(print_poly(r[0]))
    print("###########################################")

    # Path H0->Hn
    for i in range(1, len(s)):
        sp = []
        o = []
        port = [1, 0]
        o.append(port)
        sp.append(s[0])

        port = [1, 1]
        tmp = i
        for j in range(1, i):
            sp.append(s[j])
            o.append(port)
            tmp = j + 1
        port = [1]
        o.append(port)
        sp.append(s[tmp])
        r.append(calculate_routeid(sp, o))
        print("RouteID[", i, "]: ")
        print(print_poly(r[i]))
        print("###########################################")

    end = time.time()
    print(("Finished: %0.3fms" % ((end - starting))))
    print("###########################################")

    print("Direction H10-H0: ")

    r = []

    # Path H1->H0
    r.append([0])
    print("RouteID[", 0, "]: ")
    print(print_poly(r[0]))
    print("###########################################")

    # Path Hn->H0
    for i in range(1, len(s)):
        sp = []
        o = []
        port = [1, 0]
        for j in range(i, 0, -1):
            sp.append(s[j])
            o.append(port)
        port = [1]
        o.append(port)
        sp.append(s[0])
        r.append(calculate_routeid(sp, o))
        print("RouteID[", i, "]: ")
        print(print_poly(r[i]))
        print("###########################################")

    end = time.time()
    print(("Finished: %0.3fms" % ((end - starting))))
    print("###########################################")


# Test for sfc in linear fabric topo
def test_p4_sfc_fabric():
    LOGGER.debug("Running")
    print("############Test P4 Example ############")

    starting = time.time()
    # List of servers
    s = []
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 1, 1, 1])

    ns = len(s)
    r = []

    print("Direction H1-H12: ")

    # Path H1->H2: S1 S2 2 1
    o = []
    port = [1, 0]
    o.append(port)
    port = [1]
    o.append(port)
    sp = []
    sp.append(s[0])
    sp.append(s[1])
    r.append(calculate_routeid(sp, o))
    print("RouteID[", 0, "]: : h1 -->h2 - ports: ", o)
    print(print_poly(r[0]))
    print("###########################################")

    # Path Hn->Hn+1 Sn Sn+1 3 1
    for i in range(1, ns - 1):
        sp = []
        o = []
        port = [1, 1]
        o.append(port)
        port = [1]
        o.append(port)

        sp.append(s[i])
        sp.append(s[i + 1])

        r.append(calculate_routeid(sp, o))
        print("RouteID[", i, "]: h", i + 1, "-->h", i + 2, " - ports: ", o)
        print(print_poly(r[i]))
        print("###########################################")

    end = time.time()
    print(("Finished: %0.3fms" % ((end - starting))))
    print("###########################################")

    print("Direction H12-H1: ")

    r = []

    # Path Hn->H1
    for i in range(1, ns):
        sp = []
        o = []
        port = [1, 0]
        for j in range(i, 0, -1):
            sp.append(s[j])
            o.append(port)
        port = [1]
        o.append(port)
        sp.append(s[0])
        r.append(calculate_routeid(sp, o))
        print("RouteID[", i - 1, "]: h", i + 1, "-->h1 - ports", o)
        print(print_poly(r[i - 1]))
        print("###########################################")

    end = time.time()
    print(("Finished: %0.3fms" % ((end - starting))))
    print("###########################################")


# Test for sfc in linear fabric topo
def test_p4_sfc_fabric_2():
    LOGGER.debug("Running")
    print("############Test P4 Example ############")

    starting = time.time()
    # List of servers
    s = []
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 1, 1, 1])

    ns = len(s)
    r = []

    # SFC H1->VNF3->H5
    print("SFC : H1->VNF3->H5")
    # Path H1->VNF3: S1 S2 S3 2 3 1
    o = []
    port = [1, 0]
    o.append(port)
    port = [1, 1]
    o.append(port)
    port = [1]
    o.append(port)
    sp = []
    sp.append(s[0])
    sp.append(s[1])
    sp.append(s[2])
    r.append(calculate_routeid(sp, o))
    print("RouteID : H1->VNF3 - ports: ", o)
    print(print_poly(r[0]))
    # Path VNF3->H5: S3 S4 S5 3 3 1
    o = []
    port = [1, 1]
    o.append(port)
    port = [1, 1]
    o.append(port)
    port = [1]
    o.append(port)
    sp = []
    sp.append(s[2])
    sp.append(s[3])
    sp.append(s[4])
    r.append(calculate_routeid(sp, o))
    print("RouteID : VNF3->H5 - ports: ", o)
    print(print_poly(r[1]))
    print("###########################################")

    # SFC H1->VNF4->H7
    print("SFC : H1->VNF4->H7")
    # Path H1->VNF4: S1 S2 S3 S4 2 3 3 1
    o = []
    port = [1, 0]
    o.append(port)
    port = [1, 1]
    o.append(port)
    port = [1, 1]
    o.append(port)
    port = [1]
    o.append(port)
    sp = []
    sp.append(s[0])
    sp.append(s[1])
    sp.append(s[2])
    sp.append(s[3])
    r.append(calculate_routeid(sp, o))
    print("RouteID : H1->VNF4 - ports: ", o)
    print(print_poly(r[2]))
    # Path VNF4->H7: S4 S5 S6 S7 3 3 3 1
    o = []
    port = [1, 1]
    o.append(port)
    port = [1, 1]
    o.append(port)
    port = [1, 1]
    o.append(port)
    port = [1]
    o.append(port)
    sp = []
    sp.append(s[3])
    sp.append(s[4])
    sp.append(s[5])
    sp.append(s[6])
    r.append(calculate_routeid(sp, o))
    print("RouteID : VNF4->H7 - ports: ", o)
    print(print_poly(r[3]))
    print("###########################################")

    # SFC H1->VNF5->H9
    print("SFC : H1->VNF5->H9")
    # Path H1->VNF5: S1 S2 S3 S4 S5 2 3 3 3 1
    o = []
    port = [1, 0]
    o.append(port)
    port = [1, 1]
    o.append(port)
    port = [1, 1]
    o.append(port)
    port = [1, 1]
    o.append(port)
    port = [1]
    o.append(port)
    sp = []
    sp.append(s[0])
    sp.append(s[1])
    sp.append(s[2])
    sp.append(s[3])
    sp.append(s[4])
    r.append(calculate_routeid(sp, o))
    print("RouteID : H1->VNF5 - ports: ", o)
    print(print_poly(r[4]))
    # Path VNF5->H9: S5 S6 S7 S8 S9 3 3 3 3 1
    o = []
    port = [1, 1]
    o.append(port)
    port = [1, 1]
    o.append(port)
    port = [1, 1]
    o.append(port)
    port = [1, 1]
    o.append(port)
    port = [1]
    o.append(port)
    sp = []
    sp.append(s[4])
    sp.append(s[5])
    sp.append(s[6])
    sp.append(s[7])
    sp.append(s[8])
    r.append(calculate_routeid(sp, o))
    print("RouteID : VNF5->H9 - ports: ", o)
    print(print_poly(r[5]))
    print("###########################################")

    end = time.time()
    print(("Finished: %0.3fms" % ((end - starting))))
    print("###########################################")


# Test for sfc migration
def test_p4_sfc_migration():
    LOGGER.debug("Running")
    print("############Test SFC Migration ############")

    starting = time.time()
    # List of servers
    s = []
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 1, 1, 1])

    ns = len(s)
    r = []

    # SFC H1->VNF3->H7
    print("SFC : H1->VNF3->H7")
    # Path H1->VNF3: S1 S2 S3 2 3 1
    o = []
    port = [1, 0]
    o.append(port)
    port = [1, 1]
    o.append(port)
    port = [1]
    o.append(port)
    sp = []
    sp.append(s[0])
    sp.append(s[1])
    sp.append(s[2])
    r.append(calculate_routeid(sp, o))
    print("RouteID : H1->VNF3 - ports: ", o)
    print(print_poly(r[0]))
    # Path VNF3->H7: S3 S4 S5 S6 S7 3 3 3 3 1
    o = []
    port = [1, 1]
    o.append(port)
    port = [1, 1]
    o.append(port)
    port = [1, 1]
    o.append(port)
    port = [1, 1]
    o.append(port)
    port = [1]
    o.append(port)
    sp = []
    sp.append(s[2])
    sp.append(s[3])
    sp.append(s[4])
    sp.append(s[5])
    sp.append(s[6])
    r.append(calculate_routeid(sp, o))
    print("RouteID : VNF3->H7 - ports: ", o)
    print(print_poly(r[1]))
    print("###########################################")

    # SFC H1->VNF10->H7
    print("SFC : H1->VNF10->H7")
    # Path H1->VNF10: S1 S8 S9 S10 3 3 3 1
    o = []
    port = [1, 1]
    o.append(port)
    port = [1, 1]
    o.append(port)
    port = [1, 1]
    o.append(port)
    port = [1]
    o.append(port)
    sp = []
    sp.append(s[0])
    sp.append(s[7])
    sp.append(s[8])
    sp.append(s[9])
    r.append(calculate_routeid(sp, o))
    print("RouteID : H1->VNF10 - ports: ", o)
    print(print_poly(r[2]))
    # Path VNF10->H7: S10 S11 S6 S7 3 3 3 1
    o = []
    port = [1, 1]
    o.append(port)
    port = [1, 1]
    o.append(port)
    port = [1, 1]
    o.append(port)
    port = [1]
    o.append(port)
    sp = []
    sp.append(s[9])
    sp.append(s[10])
    sp.append(s[5])
    sp.append(s[6])
    r.append(calculate_routeid(sp, o))
    print("RouteID : VNF10->H7 - ports: ", o)
    print(print_poly(r[3]))
    print("###########################################")

    end = time.time()
    print(("Finished: %0.3fms" % ((end - starting))))
    print("###########################################")


# Test for sfc fast failure reaction (FFR)
def test_p4_sfc_failure():
    LOGGER.debug("Running")
    print("############Test SFC FFR ############")

    starting = time.time()
    # List of servers
    s = []
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1])
    s.append([1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 1, 1, 1])

    ns = len(s)
    r = []

    # SFC H1->VNF2->H6
    print("SFC : H1->VNF2->H6")
    # Path H1->VNF2: S1 S2 2 1
    o = []
    port = [1, 0]
    o.append(port)
    port = [1]
    o.append(port)
    sp = []
    sp.append(s[0])
    sp.append(s[1])
    r.append(calculate_routeid(sp, o))
    print("RouteID : H1->VNF2 - ports: ", o)
    print(print_poly(r[0]))
    # Path VNF2->H6: S2 S4 S6 4 5 1
    o = []
    port = [1, 0, 0]
    o.append(port)
    port = [1, 0, 1]
    o.append(port)
    port = [1]
    o.append(port)
    sp = []
    sp.append(s[1])
    sp.append(s[3])
    sp.append(s[5])
    r.append(calculate_routeid(sp, o))
    print("RouteID : VNF2->H6 - ports: ", o)
    print(print_poly(r[1]))
    print("###########################################")

    # SFC H1->VNF2->H6 + Protection
    print("SFC : H1->VNF2->H6 + Protection")
    # Path VNF2->H6 +Protection: S3 S5 S7 5 3 4
    port = [1, 0, 1]
    o.append(port)
    port = [1, 1]
    o.append(port)
    port = [1, 0, 0]
    o.append(port)
    sp.append(s[2])
    sp.append(s[4])
    sp.append(s[6])
    r.append(calculate_routeid(sp, o))
    print("RouteID : VNF2->H6 +Protection - ports: ", o)
    print(print_poly(r[2]))
    print("###########################################")

    # Return H6->H1
    print("Return H6->H1")
    # Path H6->H1: S6 S4 S2 S1 2 2 2 1
    o = []
    port = [1, 0]
    o.append(port)
    port = [1, 0]
    o.append(port)
    port = [1, 0]
    o.append(port)
    port = [1]
    o.append(port)
    sp = []
    sp.append(s[5])
    sp.append(s[3])
    sp.append(s[1])
    sp.append(s[0])
    r.append(calculate_routeid(sp, o))
    print("RouteID : H6->H1 - ports: ", o)
    print(print_poly(r[3]))
    print("###########################################")

    # Return H6->H1
    print("Return H6->H1 (through S5)")
    # Path H6->H1: S6 S5 S4 S2 S1 3 2 2 2 1
    o = []
    port = [1, 1]
    o.append(port)
    port = [1, 0]
    o.append(port)
    port = [1, 0]
    o.append(port)
    port = [1, 0]
    o.append(port)
    port = [1]
    o.append(port)
    sp = []
    sp.append(s[5])
    sp.append(s[4])
    sp.append(s[3])
    sp.append(s[1])
    sp.append(s[0])
    r.append(calculate_routeid(sp, o))
    print("RouteID : H6->H1 - ports: ", o)
    print(print_poly(r[4]))
    print("###########################################")

    end = time.time()
    print(("Finished: %0.3fms" % ((end - starting))))
    print("###########################################")


def test_p4_rllc_fabric():
    LOGGER.debug("Running")
    print("############Test P4 Example ############")

    starting = time.time()
    # List of switches

    # s1
    s1 = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1]
    # s2
    s2 = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1]
    # s3
    s3 = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1]
    # s4
    s4 = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1]
    # s5
    s5 = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1]
    # s6
    s6 = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1]
    # s7
    s7 = [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1]
    # s8
    s8 = [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1]
    # s9
    s9 = [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1]
    # s10
    s10 = [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1]

    print("###########################################")
    print("Path 1: h2->s2->s3->->s4->h4")

    s = []
    # Path 1: l1->s1->l2
    # s.append(s3)
    s.append(s3)
    s.append(s4)

    ns = len(s)

    # List of ports in the path
    o1 = [1, 1]
    o2 = [1]
    o = []
    # o.append(o1)
    o.append(o1)
    o.append(o2)

    r = calculate_routeid(s, o)
    print("RouteID Path 1: ", r)
    print(print_poly(r))

    print("###########################################")
    print("Path 2: h4->s4->s3->->s2->h2")

    s = []
    # Path 1: l1->s1->l2
    # s.append(s3)
    s.append(s3)
    s.append(s2)

    ns = len(s)

    # List of ports in the path
    o1 = [1, 0]
    o2 = [1]
    o = []
    # o.append(o1)
    o.append(o1)
    o.append(o2)

    r = calculate_routeid(s, o)
    print("RouteID Path 1: ", r)
    print(print_poly(r))

# Test for two tier topo


def test_p4_migration_fabric():
    LOGGER.debug("Running")
    print("############Test P4 Example ############")

    starting = time.time()
    # List of switches
    # s1
    s1 = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1]
    # s2
    s2 = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1]
    # l1
    l1 = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1]
    # l2
    l2 = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1]
    # l3
    l3 = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1]
    # l4
    l4 = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1]

    print(("###########################################"))
    print(("Path 1: l1->s1->l2"))
    s = []
    # Path 1: l1->s1->l2
    s.append(l1)
    s.append(s1)
    s.append(l2)

    ns = len(s)

    # List of ports in the path
    o1 = [1]
    o2 = [1, 0]
    o3 = [1, 1]
    o = []
    o.append(o1)
    o.append(o2)
    o.append(o3)

    r = calculate_routeid(s, o)
    print("RouteID Path 1: ", r)
    print(print_poly(r))

    print(("Path 1 Return: l2->s1->l1"))
    s = []
    # Path 1: l2->s1->l1
    s.append(l2)
    s.append(s1)
    s.append(l1)

    ns = len(s)

    # List of ports in the path
    o1 = [1]
    o2 = [1]
    o3 = [1, 1]
    o = []
    o.append(o1)
    o.append(o2)
    o.append(o3)

    r = calculate_routeid(s, o)
    print("RouteID Path 1 Return: ", r)
    print_poly(r)
    print("###########################################")

    print("###########################################")
    print("Path 2: l1->s1->l3")
    s = []
    # Path 2: l1->s1->l3
    s.append(l1)
    s.append(s1)
    s.append(l3)

    ns = len(s)

    # List of ports in the path
    o1 = [1]
    o2 = [1, 1]
    o3 = [1, 1]
    o = []
    o.append(o1)
    o.append(o2)
    o.append(o3)

    r = calculate_routeid(s, o)
    print("RouteID Path 2: ", r)
    print(print_poly(r))

    print("Path 2 Return: l3->s1->l1")
    s = []
    # Path 1: l3->s1->l1
    s.append(l3)
    s.append(s1)
    s.append(l1)

    ns = len(s)

    # List of ports in the path
    o1 = [1]
    o2 = [1]
    o3 = [1, 0, 0]
    o = []
    o.append(o1)
    o.append(o2)
    o.append(o3)

    r = calculate_routeid(s, o)
    print("RouteID Path 2 Return: ", r)
    print(print_poly(r))
    print("###########################################")

    print("###########################################")
    print("Path 3: l1->s2->l2")
    s = []
    # Path 1: l1->s2->l2
    s.append(l1)
    s.append(s2)
    s.append(l2)

    ns = len(s)

    # List of ports in the path
    o1 = [1, 0]
    o2 = [1, 0]
    o3 = [1, 1]
    o = []
    o.append(o1)
    o.append(o2)
    o.append(o3)

    r = calculate_routeid(s, o)
    print("RouteID Path 3: ", r)
    print(print_poly(r))

    print("Path 3 Return: l2->s2->l1")
    s = []
    # Path 1: l2->s2->l1
    s.append(l2)
    s.append(s2)
    s.append(l1)

    ns = len(s)

    # List of ports in the path
    o1 = [1, 0]
    o2 = [1]
    o3 = [1, 1]
    o = []
    o.append(o1)
    o.append(o2)
    o.append(o3)

    r = calculate_routeid(s, o)
    print("RouteID Path 3 Return: ", r)
    print(print_poly(r))
    print("###########################################")

    end = time.time()
    print(("Finished: %0.3fms" % ((end - starting))))
    print("###########################################")


def test_output_port():
    LOGGER.debug("Running")
    # Nodeids[ 8 ]:  [[1, 0, 1, 1], [1, 1, 0, 1], [1, 0, 0, 1, 1], [1, 1, 0, 0, 1], [1, 1, 1, 1, 1], [1, 0, 0, 1, 0, 1], [1, 0, 1, 0, 0, 1], [1, 0, 1, 1, 1, 1]]
    # Path[ 3 ]:  [[1, 0, 0, 1, 0, 1], [1, 0, 1, 0, 0, 1], [1, 0, 1, 1, 1, 1]] -->worst case: greatest nodeids are allocated in the diameter
    # Max Bitlength:  15 --> 5+5+5

    # S=  [[1, 0, 0, 1, 0, 1], [1, 0, 1, 0, 0, 1], [1, 0, 1, 1, 1, 1]]
    # O=  [[0, 1, 1, 1, 0], [1, 1, 0, 0, 1], [0, 0, 1, 0, 1]]
    print("############Output Port Example############")

    starting = time.time()
    # List of servers
    s1 = [1, 0, 0, 1, 0, 1]
    s2 = [1, 0, 1, 0, 0, 1]
    s3 = [1, 0, 1, 1, 1, 1]
    s = []
    s.append(s1)
    s.append(s2)
    s.append(s3)
    ns = len(s)

    # List of ports in the path
    o1 = [1, 1, 1, 0]
    o2 = [1, 1, 0, 0, 1]
    o3 = [1, 0, 1]
    o = []
    o.append(o1)
    o.append(o2)
    o.append(o3)

    r = calculate_routeid(s, o)
    print("RouteID: ", r)

    end = time.time()
    print("Finished: %0.3fms" % ((end - starting)))
    print("###########################################")


# Tests Ana
def test_ana():
    LOGGER.debug("Running")
    print("############Test R1############")

    starting = time.time()
    # List of servers
    s1 = [1, 1, 1]
    s2 = [1, 0, 0, 1, 1]
    s3 = [1, 0, 0, 0, 1, 1, 0, 1, 1]
    s = []
    s.append(s1)
    s.append(s2)
    s.append(s3)
    ns = len(s)

    # List of ports in the path
    o1 = [1, 0]
    o2 = [1, 0, 0]
    o3 = [1, 0, 1, 0, 0]
    o = []
    o.append(o1)
    o.append(o2)
    o.append(o3)

    r = calculate_routeid(s, o)
    print("RouteID 1: ", r)

    end = time.time()
    print(("Finished: %0.3fms" % ((end - starting))))
    print("###########################################")

    print("############Test R2############")

    starting = time.time()
    # List of servers
    s1 = [1, 1, 1]
    s2 = [1, 0, 0, 1, 1]
    s3 = [1, 0, 0, 0, 1, 1, 0, 1, 1]
    s = []
    s.append(s1)
    s.append(s2)
    s.append(s3)
    ns = len(s)

    # List of ports in the path
    o1 = [0]
    o2 = [0]
    o3 = [0]
    o = []
    o.append(o1)
    o.append(o2)
    o.append(o3)

    r = calculate_routeid(s, o)
    print("RouteID 2: ", r)

    end = time.time()
    print(("Finished: %0.3fms" % ((end - starting))))
    print("###########################################")

    print("############Test R3############")

    starting = time.time()
    # List of servers
    s1 = [1, 1, 1]
    s2 = [1, 0, 0, 1, 1]
    s3 = [1, 0, 0, 0, 1, 1, 0, 1, 1]
    s = []
    s.append(s1)
    s.append(s2)
    s.append(s3)
    ns = len(s)

    # List of ports in the path
    o1 = [1, 0]
    o2 = [1, 1, 0]
    o3 = [1, 0, 0, 1, 0, 0, 0, 0]
    o = []
    o.append(o1)
    o.append(o2)
    o.append(o3)

    r = calculate_routeid(s, o)
    print("RouteID 3: ", r)

    end = time.time()
    print(("Finished: %0.3fms" % ((end - starting))))
    print("###########################################")


# Main
def main():
    # Execute simple example
    # test_simple_example()

    # Execute multicast example
    # test_multicast_example()

    # Generate irreducible polynomials of degree n
    # n = 16
    # polyn = create_list_irrpoly_mod2 (n)
    # print "Number of polynomials of degree ", n, " : ", len(polyn)
    # number= 4080 for n=16
    # print polyn
    # Generate k irreducible polynomials of degree n
    # k = 12
    # polyn = create_irrpoly_mod2 (n, k)

    # Execute P4 examples
    # test_p4_example()
    # test_p4_latency_3_example()

    # Tests for thesis with polys of degree 16
    # test_p4_latency_fabric()
    test_p4_migration_fabric()
    # test_p4_sfc_fabric()
    # test_p4_sfc_fabric_2()
    # test_p4_sfc_migration()
    # test_p4_sfc_failure()

    # test_ana()


if __name__ == "__main__":
    main()
