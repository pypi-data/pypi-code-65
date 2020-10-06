from polka.tools import *
from polka.generate import *
from keyflow import *
import pandas as pd
import networkx as nx


def max_bitlength(nports, nnodes, lpath):

    mindegree = math.log(nports, 2)
    print ("Mindegree: ", mindegree)
    mindegree = np.ceil(mindegree)
    print ("Mindegree: ", mindegree)

    nodeids = generate_nodeids(mindegree, nnodes)
    # print "nodeids[", len(nodeids), "]: ", nodeids

    # Worst Case
    path = nodeids[(-1 * lpath) :]
    # print "path[", len(path), "]: ", path

    bitlength = 0
    for elem in path:
        bitlength = bitlength + gf_degree(elem)
    # print "Bitlength: ", bitlength

    return bitlength


def max_bitlength_table(nports, nnodes, lpath, directory, is_multicast):

    if is_multicast:
        # Multicast
        print ("Multicast")
        mindegree = nports
    else:
        # Unicast
        print ("Unicast")
        mindegree = math.log(nports, 2)
        mindegree = int(np.ceil(mindegree))

    print ("Mindegree: ", mindegree)

    nodeids = generate_nodeids_table(mindegree, nnodes, directory)
    # print "nodeids[", len(nodeids), "]: ", nodeids

    # Worst Case
    path = nodeids[(-1 * lpath) :]
    # print "path[", len(path), "]: ", path

    bitlength = 0
    for elem in path:
        bitlength = bitlength + gf_degree(elem)
    # print "Bitlength: ", bitlength

    return bitlength


def max_bitlength_list(nports, lpath):
    bitsport = math.log(nports, 2)
    bitsport = np.ceil(bitsport)
    nbits = bitsport * lpath
    return int(nbits)


def scalability_analysis_keyflow_paper():
    LOGGER.debug("Running")
    lst = []
    # Header
    lst.append("Topology,Path,Bits")

    # Graph from KeyFlow paper
    nports = 24
    switch_nodes = [15, 30, 45, 60]

    for nnodes in switch_nodes:
        for lpath in range(1, 16):
            topo_name = "N=" + str(nnodes)
            print ("######", topo_name)
            nbits = max_bitlength(nports, nnodes, lpath)
            lst.append("PolKA " + str(topo_name) + "," + str(lpath) + "," + str(nbits))
            nbits_keyflow = max_bitlength_keyflow(nports, nnodes, lpath, topo_name)
            lst.append(
                "KeyFlow "
                + str(topo_name)
                + ","
                + str(lpath)
                + ","
                + str(nbits_keyflow)
            )
            nbits_list = max_bitlength_list(nports, lpath)
            lst.append(
                "List " + str(topo_name) + "," + str(lpath) + "," + str(nbits_list)
            )

    # Export to csv file
    arr = np.array(lst)
    np.savetxt("keyflow_paper.csv", arr, delimiter=",", fmt="%s")


def scalability_analysis_polka_paper(directory):
    LOGGER.debug("Running")

    table_directory = directory + "/irrpolys"

    lst = []
    # Header
    lst.append(
        "Topology,Max.Ports,Diameter,Nr.Nodes,Nr.Servers,"
        + "Nr.Bits-Unicast,Nr.Bits-Multicast"
    )

    # 2-tier Topologies
    switch_ports = [24]
    spine_nodes = [6, 12, 16]
    lpath = 3
    for nspine in spine_nodes:
        nleaf = nspine
        nnodes = nspine + nleaf
        for nports in switch_ports:
            if nports > nspine:
                nservers = (nports - nspine) * nleaf
                # topo_name = "2-tier - spine: ", nspine, " - leaf: ", nleaf,
                #             "- switches: ", nnodes," - ports: ", nports,
                #             " - servers: ", nservers, " - lpath: ", lpath
                topo_name = "2-tier spine " + str(nspine) + " leaf " + str(nleaf)
                print ("######", topo_name)
                nbits_unicast = max_bitlength_table(
                    nports, nnodes, lpath, table_directory, 0
                )
                nbits_multicast = max_bitlength_table(
                    nports, nnodes, lpath, table_directory, 1
                )
                lst.append(
                    topo_name
                    + ","
                    + str(nports)
                    + ","
                    + str(lpath)
                    + ","
                    + str(nnodes)
                    + ","
                    + str(nservers)
                    + ","
                    + str(nbits_unicast)
                    + ","
                    + str(nbits_multicast)
                )

    # FatTree
    pods = [4, 8, 16, 24]
    # pods = [4,8,16]
    lpath = 5
    for k in pods:
        nservers = pow(k, 3) / 4
        nswitch_access = k / 2
        nswitch_agreg = k / 2
        nswitch_core = pow(k / 2, 2)
        nnodes = k * nswitch_access + k * nswitch_agreg + nswitch_core
        nports = k
        topo_name = "Fat Tree pod " + str(k)
        print ("######", topo_name)
        nbits_unicast = max_bitlength_table(nports, nnodes, lpath, table_directory, 0)
        nbits_multicast = max_bitlength_table(nports, nnodes, lpath, table_directory, 1)
        lst.append(
            topo_name
            + ","
            + str(nports)
            + ","
            + str(lpath)
            + ","
            + str(nnodes)
            + ","
            + str(nservers)
            + ","
            + str(nbits_unicast)
            + ","
            + str(nbits_multicast)
        )

    # Arpanet Backbone Topology (ARPANET)
    # nnodes = 20
    # nports = 4
    # lpath = 7
    topo_name = "ARPANET"
    print ("######", topo_name)
    filename = directory + "/graphs/21-arpanet.txt"
    g = create_graph_edgelist(filename)
    nports = get_graph_maxdegree(g)
    print ("Maximum node degree: ", nports)
    nnodes = g.order()
    print ("Number of nodes: ", nnodes)
    lpath = nx.diameter(g)
    print ("Diameter: ", lpath)
    nservers = 0
    nbits_unicast = max_bitlength_table(nports, nnodes, lpath, table_directory, 0)
    nbits_multicast = max_bitlength_table(nports, nnodes, lpath, table_directory, 1)
    lst.append(
        topo_name
        + ","
        + str(nports)
        + ","
        + str(lpath)
        + ","
        + str(nnodes)
        + ","
        + str(nservers)
        + ","
        + str(nbits_unicast)
        + ","
        + str(nbits_multicast)
    )

    # Geant Backbone Topology (GEANT2)
    # nnodes = 30
    # nports = 8
    # lpath = 7
    topo_name = "GEANT2"
    print ("######", topo_name)
    filename = directory + "/graphs/32-geant2-30N-48L.txt"
    g = create_graph_edgelist(filename)
    nports = get_graph_maxdegree(g)
    print ("Maximum node degree: ", nports)
    nnodes = g.order()
    print ("Number of nodes: ", nnodes)
    lpath = nx.diameter(g)
    print ("Diameter: ", lpath)
    nservers = 0
    nbits_unicast = max_bitlength_table(nports, nnodes, lpath, table_directory, 0)
    nbits_multicast = max_bitlength_table(nports, nnodes, lpath, table_directory, 1)
    lst.append(
        topo_name
        + ","
        + str(nports)
        + ","
        + str(lpath)
        + ","
        + str(nnodes)
        + ","
        + str(nservers)
        + ","
        + str(nbits_unicast)
        + ","
        + str(nbits_multicast)
    )

    # Internet2 Network (INTERNET2)
    # nnodes = 56
    # nports = 3
    # lpath = 21
    topo_name = "INTERNET2"
    print ("######", topo_name)
    filename = directory + "/graphs/38-internet2.txt"
    g = create_graph_edgelist(filename)
    nports = get_graph_maxdegree(g)
    print ("Maximum node degree: ", nports)
    nnodes = g.order()
    print ("Number of nodes: ", nnodes)
    lpath = nx.diameter(g)
    print ("Diameter: ", lpath)
    nservers = 0
    nbits_unicast = max_bitlength_table(nports, nnodes, lpath, table_directory, 0)
    nbits_multicast = max_bitlength_table(nports, nnodes, lpath, table_directory, 1)
    lst.append(
        topo_name
        + ","
        + str(nports)
        + ","
        + str(lpath)
        + ","
        + str(nnodes)
        + ","
        + str(nservers)
        + ","
        + str(nbits_unicast)
        + ","
        + str(nbits_multicast)
    )

    # Export to csv file
    arr = np.array(lst)
    np.savetxt("polka_paper_table.csv", arr, delimiter=",", fmt="%s")


def scalability_analysis_netsoft(directory):
    LOGGER.debug("Running")

    table_directory = directory + "/irrpolys"

    lst = []
    # Header
    lst.append(
        "Topology,Max.Ports,Diameter,Nr.Nodes,Nr.Servers,"
        + "Nr.Bits-PolKA,Nr.Bits-List"
    )

    # 2-tier Topologies
    switch_ports = [24]
    # spine_nodes = [6,12,16]
    spine_nodes = [16]
    lpath = 3
    for nspine in spine_nodes:
        nleaf = nspine
        nnodes = nspine + nleaf
        for nports in switch_ports:
            if nports > nspine:
                nservers = (nports - nspine) * nleaf
                # topo_name = "2-tier - spine: ", nspine, " - leaf: ", nleaf,
                #             "- switches: ", nnodes," - ports: ", nports,
                #             " - servers: ", nservers, " - lpath: ", lpath
                topo_name = "2-tier spine " + str(nspine) + " leaf " + str(nleaf)
                print ("######", topo_name)
                nbits_unicast = max_bitlength_table(
                    nports, nnodes, lpath, table_directory, 0
                )
                nbits_list = max_bitlength_list(nports, lpath)
                lst.append(
                    topo_name
                    + ","
                    + str(nports)
                    + ","
                    + str(lpath)
                    + ","
                    + str(nnodes)
                    + ","
                    + str(nservers)
                    + ","
                    + str(nbits_unicast)
                    + ","
                    + str(nbits_list)
                )

    # FatTree
    # pods = [4,8,16,24]
    pods = [16]
    lpath = 5
    for k in pods:
        nservers = pow(k, 3) / 4
        nswitch_access = k / 2
        nswitch_agreg = k / 2
        nswitch_core = pow(k / 2, 2)
        nnodes = k * nswitch_access + k * nswitch_agreg + nswitch_core
        nports = k
        topo_name = "Fat Tree pod " + str(k)
        print ("######", topo_name)
        nbits_unicast = max_bitlength_table(nports, nnodes, lpath, table_directory, 0)
        nbits_list = max_bitlength_list(nports, lpath)
        lst.append(
            topo_name
            + ","
            + str(nports)
            + ","
            + str(lpath)
            + ","
            + str(nnodes)
            + ","
            + str(nservers)
            + ","
            + str(nbits_unicast)
            + ","
            + str(nbits_list)
        )

    # Arpanet Backbone Topology (ARPANET)
    # nnodes = 20
    # nports = 4
    # lpath = 7
    topo_name = "ARPANET"
    print ("######", topo_name)
    filename = directory + "/graphs/21-arpanet.txt"
    g = create_graph_edgelist(filename)
    nports = get_graph_maxdegree(g)
    print ("Maximum node degree: ", nports)
    nnodes = g.order()
    print ("Number of nodes: ", nnodes)
    lpath = nx.diameter(g)
    print ("Diameter: ", lpath)
    nservers = 0
    nbits_unicast = max_bitlength_table(nports, nnodes, lpath, table_directory, 0)
    nbits_list = max_bitlength_list(nports, lpath)
    lst.append(
        topo_name
        + ","
        + str(nports)
        + ","
        + str(lpath)
        + ","
        + str(nnodes)
        + ","
        + str(nservers)
        + ","
        + str(nbits_unicast)
        + ","
        + str(nbits_list)
    )

    # Geant Backbone Topology (GEANT2)
    # nnodes = 30
    # nports = 8
    # lpath = 7
    topo_name = "GEANT2"
    print ("######", topo_name)
    filename = directory + "/graphs/32-geant2-30N-48L.txt"
    g = create_graph_edgelist(filename)
    nports = get_graph_maxdegree(g)
    print ("Maximum node degree: ", nports)
    nnodes = g.order()
    print ("Number of nodes: ", nnodes)
    lpath = nx.diameter(g)
    print ("Diameter: ", lpath)
    nservers = 0
    nbits_unicast = max_bitlength_table(nports, nnodes, lpath, table_directory, 0)
    nbits_list = max_bitlength_list(nports, lpath)
    lst.append(
        topo_name
        + ","
        + str(nports)
        + ","
        + str(lpath)
        + ","
        + str(nnodes)
        + ","
        + str(nservers)
        + ","
        + str(nbits_unicast)
        + ","
        + str(nbits_list)
    )

    # Internet2 Network (INTERNET2)
    # nnodes = 56
    # nports = 3
    # lpath = 21
    topo_name = "INTERNET2"
    print ("######", topo_name)
    filename = directory + "/graphs/38-internet2.txt"
    g = create_graph_edgelist(filename)
    nports = get_graph_maxdegree(g)
    print ("Maximum node degree: ", nports)
    nnodes = g.order()
    print ("Number of nodes: ", nnodes)
    lpath = nx.diameter(g)
    print ("Diameter: ", lpath)
    nservers = 0
    nbits_unicast = max_bitlength_table(nports, nnodes, lpath, table_directory, 0)
    nbits_list = max_bitlength_list(nports, lpath)
    lst.append(
        topo_name
        + ","
        + str(nports)
        + ","
        + str(lpath)
        + ","
        + str(nnodes)
        + ","
        + str(nservers)
        + ","
        + str(nbits_unicast)
        + ","
        + str(nbits_list)
    )

    # Export to csv file
    arr = np.array(lst)
    np.savetxt("polka_paper_netsoft.csv", arr, delimiter=",", fmt="%s")


def scalability_analysis_thesis(directory):
    LOGGER.debug("Running")

    table_directory = directory + "/irrpolys"

    lst = []
    # Header
    lst.append(
        "Topology,Max.Ports,Diameter,Nr.Nodes,Nr.Servers,Nr.Bits-Bin-Unicast,"
        + "Nr.Bits-Bin-Multicast,Nr.Bits-Int-Unicast,Nr.Bits-Int-Multicast"
    )
    # lst.append("Topology,Max.Ports,Diameter,Nr.Nodes,Nr.Servers,Nr.Bits-Unicast,Nr.Bits-Multicast")

    # 2-tier Topologies
    switch_ports = [24]
    spine_nodes = [6, 12, 16]
    lpath = 3
    for nspine in spine_nodes:
        nleaf = nspine
        nnodes = nspine + nleaf
        for nports in switch_ports:
            if nports > nspine:
                nservers = (nports - nspine) * nleaf
                # topo_name = "2-tier - spine: ", nspine, " - leaf: ", nleaf,
                #             "- switches: ", nnodes," - ports: ", nports,
                #             " - servers: ", nservers, " - lpath: ", lpath
                topo_name = "2-tier spine " + str(nspine) + " leaf " + str(nleaf)
                print ("######", topo_name)
                nbits_unicast = max_bitlength_table(
                    nports, nnodes, lpath, table_directory, 0
                )
                nbits_multicast = max_bitlength_table(
                    nports, nnodes, lpath, table_directory, 1
                )
                nbits_keyflow_unicast = max_bitlength_keyflow(
                    nports, nnodes, lpath, topo_name
                )
                nbits_keyflow_multicast = max_bitlength_keyflow_multicast(
                    nports, nnodes, lpath, topo_name, 1
                )
                lst.append(
                    topo_name
                    + ","
                    + str(nports)
                    + ","
                    + str(lpath)
                    + ","
                    + str(nnodes)
                    + ","
                    + str(nservers)
                    + ","
                    + str(nbits_unicast)
                    + ","
                    + str(nbits_multicast)
                    + ","
                    + str(nbits_keyflow_unicast)
                    + ","
                    + str(nbits_keyflow_multicast)
                )

    # FatTree
    pods = [4, 8, 16, 24]
    # pods = [4,8,16]
    lpath = 5
    for k in pods:
        nservers = pow(k, 3) / 4
        nswitch_access = k / 2
        nswitch_agreg = k / 2
        nswitch_core = pow(k / 2, 2)
        nnodes = k * nswitch_access + k * nswitch_agreg + nswitch_core
        nports = k
        topo_name = "Fat Tree pod " + str(k)
        print ("######", topo_name)
        nbits_unicast = max_bitlength_table(nports, nnodes, lpath, table_directory, 0)
        nbits_multicast = max_bitlength_table(nports, nnodes, lpath, table_directory, 1)
        nbits_keyflow_unicast = max_bitlength_keyflow(nports, nnodes, lpath, topo_name)
        nbits_keyflow_multicast = max_bitlength_keyflow_multicast(
            nports, nnodes, lpath, topo_name, 1
        )
        lst.append(
            topo_name
            + ","
            + str(nports)
            + ","
            + str(lpath)
            + ","
            + str(nnodes)
            + ","
            + str(nservers)
            + ","
            + str(nbits_unicast)
            + ","
            + str(nbits_multicast)
            + ","
            + str(nbits_keyflow_unicast)
            + ","
            + str(nbits_keyflow_multicast)
        )

    # Arpanet Backbone Topology (ARPANET)
    # nnodes = 20
    # nports = 4
    # lpath = 7
    topo_name = "ARPANET"
    print ("######", topo_name)
    filename = directory + "/graphs/21-arpanet.txt"
    g = create_graph_edgelist(filename)
    nports = get_graph_maxdegree(g)
    print ("Maximum node degree: ", nports)
    nnodes = g.order()
    print ("Number of nodes: ", nnodes)
    lpath = nx.diameter(g)
    print ("Diameter: ", lpath)
    nservers = 0
    nbits_unicast = max_bitlength_table(nports, nnodes, lpath, table_directory, 0)
    nbits_multicast = max_bitlength_table(nports, nnodes, lpath, table_directory, 1)
    nbits_keyflow_unicast = max_bitlength_keyflow(nports, nnodes, lpath, topo_name)
    nbits_keyflow_multicast = max_bitlength_keyflow_multicast(
        nports, nnodes, lpath, topo_name, 1
    )
    lst.append(
        topo_name
        + ","
        + str(nports)
        + ","
        + str(lpath)
        + ","
        + str(nnodes)
        + ","
        + str(nservers)
        + ","
        + str(nbits_unicast)
        + ","
        + str(nbits_multicast)
        + ","
        + str(nbits_keyflow_unicast)
        + ","
        + str(nbits_keyflow_multicast)
    )

    # Geant Backbone Topology (GEANT2)
    # nnodes = 30
    # nports = 8
    # lpath = 7
    topo_name = "GEANT2"
    print ("######", topo_name)
    filename = "/home/cristina/Dropbox/Cristina/UFES/doutorado/P4/code/graphs/32-geant2-30N-48L.txt"
    g = create_graph_edgelist(filename)
    nports = get_graph_maxdegree(g)
    print ("Maximum node degree: ", nports)
    nnodes = g.order()
    print ("Number of nodes: ", nnodes)
    lpath = nx.diameter(g)
    print ("Diameter: ", lpath)
    nservers = 0
    nbits_unicast = max_bitlength_table(nports, nnodes, lpath, table_directory, 0)
    nbits_multicast = max_bitlength_table(nports, nnodes, lpath, table_directory, 1)
    nbits_keyflow_unicast = max_bitlength_keyflow(nports, nnodes, lpath, topo_name)
    nbits_keyflow_multicast = max_bitlength_keyflow_multicast(
        nports, nnodes, lpath, topo_name, 1
    )
    lst.append(
        topo_name
        + ","
        + str(nports)
        + ","
        + str(lpath)
        + ","
        + str(nnodes)
        + ","
        + str(nservers)
        + ","
        + str(nbits_unicast)
        + ","
        + str(nbits_multicast)
        + ","
        + str(nbits_keyflow_unicast)
        + ","
        + str(nbits_keyflow_multicast)
    )

    # Internet2 Network (INTERNET2)
    # nnodes = 56
    # nports = 3
    # lpath = 21
    topo_name = "INTERNET2"
    print ("######", topo_name)
    filename = (
        "/home/cristina/Dropbox/Cristina/UFES/doutorado/P4/code/graphs/38-internet2.txt"
    )
    g = create_graph_edgelist(filename)
    nports = get_graph_maxdegree(g)
    print ("Maximum node degree: ", nports)
    nnodes = g.order()
    print ("Number of nodes: ", nnodes)
    lpath = nx.diameter(g)
    print ("Diameter: ", lpath)
    nservers = 0
    nbits_unicast = max_bitlength_table(nports, nnodes, lpath, table_directory, 0)
    nbits_multicast = max_bitlength_table(nports, nnodes, lpath, table_directory, 1)
    nbits_keyflow_unicast = max_bitlength_keyflow(nports, nnodes, lpath, topo_name)
    nbits_keyflow_multicast = max_bitlength_keyflow_multicast(
        nports, nnodes, lpath, topo_name, 1
    )
    lst.append(
        topo_name
        + ","
        + str(nports)
        + ","
        + str(lpath)
        + ","
        + str(nnodes)
        + ","
        + str(nservers)
        + ","
        + str(nbits_unicast)
        + ","
        + str(nbits_multicast)
        + ","
        + str(nbits_keyflow_unicast)
        + ","
        + str(nbits_keyflow_multicast)
    )

    # Export to csv file
    arr = np.array(lst)
    np.savetxt("polka_paper_table_2.csv", arr, delimiter=",", fmt="%s")


def create_graph_edgelist(filename):
    # Read edge list
    edgelist = pd.read_csv(filename, delim_whitespace=True)
    g = nx.Graph()
    # Add edges and edge attributes
    for i, elrow in edgelist.iterrows():
        g.add_edge(elrow[0], elrow[1])
    return g


def get_graph_maxdegree(g):
    degree_sequence = sorted([d for n, d in g.degree()], reverse=True)
    dmax = max(degree_sequence)
    return dmax


def scalability_analysis_unicast():
    LOGGER.debug("Running")
    lst = []
    # Header
    lst.append(
        "Topology,Max.Ports,Diameter,Nr.Nodes,Nr.Servers,Nr.Bits-Bin,"
        + "Nr.Bits-Int,Nr.Bits-List,Worse than Keyflow, Worse than List"
    )

    # 2-tier Topologies
    switch_ports = [24, 48, 96]
    spine_nodes = [6, 12, 16, 24, 36, 48]
    lpath = 3
    for nspine in spine_nodes:
        nleaf = nspine
        nnodes = nspine + nleaf
        for nports in switch_ports:
            if nports > nspine:
                nservers = (nports - nspine) * nleaf
                # topo_name = "2-tier - spine: ", nspine, " - leaf: ",
                #             nleaf, "- switches: ", nnodes," - ports: ",
                #             nports," - servers: ", nservers, " - lpath: ",
                #             lpath
                topo_name = "2-tier spine " + str(nspine) + " leaf " + str(nleaf)
                print ("######", topo_name)
                nbits = max_bitlength(nports, nnodes, lpath)
                nbits_keyflow = max_bitlength_keyflow(nports, nnodes, lpath, topo_name)
                nbits_list = max_bitlength_list(nports, lpath)
                print ("Bitlength:", nbits)
                result = str(nbits - nbits_keyflow) if nbits > nbits_keyflow else ""
                result2 = str(nbits - nbits_list) if nbits > nbits_list else ""
                lst.append(
                    topo_name
                    + ","
                    + str(nports)
                    + ","
                    + str(lpath)
                    + ","
                    + str(nnodes)
                    + ","
                    + str(nservers)
                    + ","
                    + str(nbits)
                    + ","
                    + str(nbits_keyflow)
                    + ","
                    + str(nbits_list)
                    + ","
                    + result
                    + ","
                    + result2
                )

    # FatTree
    pods = [4, 8, 16, 24, 32]
    lpath = 5
    for k in pods:
        nservers = pow(k, 3) / 4
        nswitch_access = k / 2
        nswitch_agreg = k / 2
        nswitch_core = pow(k / 2, 2)
        nnodes = k * nswitch_access + k * nswitch_agreg + nswitch_core
        nports = k
        topo_name = "Fat Tree pod " + str(k)
        print ("######", topo_name)
        nbits = max_bitlength(nports, nnodes, lpath)
        nbits_keyflow = max_bitlength_keyflow(nports, nnodes, lpath, topo_name)
        nbits_list = max_bitlength_list(nports, lpath)
        print ("Bitlength:", nbits)
        result = str(nbits - nbits_keyflow) if nbits > nbits_keyflow else ""
        result2 = str(nbits - nbits_list) if nbits > nbits_list else ""
        lst.append(
            topo_name
            + ","
            + str(nports)
            + ","
            + str(lpath)
            + ","
            + str(nnodes)
            + ","
            + str(nservers)
            + ","
            + str(nbits)
            + ","
            + str(nbits_keyflow)
            + ","
            + str(nbits_list)
            + ","
            + result
            + ","
            + result2
        )

    # Hypercube Topologies
    degree = [3, 4, 5, 6, 7, 8, 9, 10]
    for ndegree in degree:
        nservers = pow(2, ndegree)
        nnodes = nservers
        nports = ndegree
        lpath = ndegree
        # topo_name = "Hypercube - degree: ",
        #              ndegree, "- switches: ",
        #              nnodes," - ports: ", nports,
        #              " - servers: ", nservers, " - lpath: ", lpath
        topo_name = "Hypercube degree " + str(ndegree)
        print ("######", topo_name)
        nbits = max_bitlength(nports, nnodes, lpath)
        nbits_keyflow = max_bitlength_keyflow(nports, nnodes, lpath, topo_name)
        nbits_list = max_bitlength_list(nports, lpath)
        print ("Bitlength:", nbits)
        result = str(nbits - nbits_keyflow) if nbits > nbits_keyflow else ""
        result2 = str(nbits - nbits_list) if nbits > nbits_list else ""
        lst.append(
            topo_name
            + ","
            + str(nports)
            + ","
            + str(lpath)
            + ","
            + str(nnodes)
            + ","
            + str(nservers)
            + ","
            + str(nbits)
            + ","
            + str(nbits_keyflow)
            + ","
            + str(nbits_list)
            + ","
            + result
            + ","
            + result2
        )

    # DCell
    # k = [1,2]
    # n = [4,6,8,10,12]
    # tmp = (n+1)*n
    # nservers = (tmp+1)*tmp
    # nswitcheslevel = nservers/n
    # nportsservers = k+1
    # nportsswitches = n
    # nnodes =
    # nports =

    # Export to csv file
    arr = np.array(lst)
    np.savetxt("scalability_analysis_unicast.csv", arr, delimiter=",", fmt="%s")


def calculate_routeid_worst_case(nodeids, lpath, mindegree):
    LOGGER.debug("Running")
    path = nodeids[(-1 * lpath) :]
    print "Path[", len(path), "]: ", path

    bitlength = 0
    for elem in path:
        bitlength = bitlength + gf_degree(elem)
    print "Bitlength: ", bitlength

    print "############ All ones output ports############"
    o1 = []
    for elem in path:
        # o1.append([1] * gf_degree(elem))
        o1.append([1] * mindegree)
    # print "o[", len(o1), "]: ", o1

    r = calculate_routeid(path, o1)
    print "RouteID[", len(r), "] = ", r

    print "############ 1 + all zeros output ports############"
    o2 = []
    for elem in path:
        # o2.append([1] + [0] * (gf_degree(elem)-1))
        o2.append([1] + [0] * (mindegree - 1))
    # print "o[", len(o2), "]: ", o2

    r = calculate_routeid(path, o2)
    print "RouteID[", len(r), "] = ", r

    for i in range(0, 10):
        print "############ 1 + Random bits output ports############"
        o3 = []
        for elem in path:
            # o3.append
            #       ([1] + [ int(uniform(0, 2)) for i in xrange(0,
            #       gf_degree(elem)-1) ])
            o3.append([1] + [int(uniform(0, 2)) for i in xrange(0, mindegree - 1)])
        # print "o[", len(o3), "]: ", o3

        r = calculate_routeid(path, o3)
        print "RouteID[", len(r), "] = ", r


def test_routeid_worst_case():
    LOGGER.debug("Running")
    # 2-tier 4 leaf - 4 spine - 8 ports - 16 servers
    toponame = "2-tier 16 servers"
    nports = 8
    nnodes = 8
    lpath = 3
    mindegree = int(math.log(nports, 2))
    nodeids = generate_nodeids(mindegree, nnodes)
    print "nodeids[", len(nodeids), "]: ", nodeids
    calculate_routeid_worst_case(nodeids, lpath, mindegree)


# Main
def main():

    # Generate table with irreducible polynomials mod2
    # mindegree = 1
    # maxdegree = 7
    # table = generate_coprimes_table(1, 7)
    # print table

    # Execute scalability analysis for unicast
    # Comparison between
    # scalability_analysis_unicast()

    # Comparison with KeyFlow as done in KeyFlow paper
    # scalability_analysis_keyflow_paper()

    # Generate human readable poly table
    # mindeg = 1
    # maxdeg = 10
    # table = generate_coprimes_table_print(mindeg, maxdeg)

    # Generate pickle poly table (better performance)
    # mindeg = 1
    # maxdeg = 24
    # directory = \
    # '/home/cristina/Dropbox/Cristina/UFES/doutorado/P4_v2/git/control/irrpolys'
    # generate_coprimes_table_pickle(mindeg, maxdeg, directory)
    # table = get_coprimes_table_pickle(mindeg, maxdeg, directory)
    # print table

    # Comparison PolKA
    # scalability_analysis_polka_paper(directory)

    # Comparison PolKA with Sourcey
    scalability_analysis_netsoft(
        "/home/cristina/Dropbox/Cristina/UFES/doutorado/P4_v2/git/control"
    )

    # Test routeid in the worst case for
    #         2-tier 4 leaf - 4 spine - 8 ports - 16 servers
    # test_routeid_worst_case()


if __name__ == "__main__":
    main()
