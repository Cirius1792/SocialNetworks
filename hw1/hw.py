import matplotlib

from util import *
import networkx as nx
import time
from joblib import Parallel, delayed

import matplotlib.pyplot as plt


def test_triangle(graph, j):
    u_graph = nx.Graph(graph)
    start = time.time()
    #triang_par = par_triangles(u_graph, j)
    triang_par = par2_trn(u_graph, j)
    t_par = time.time() - start
    start = time.time()
    triang_ex = num_triangles(u_graph)
    t_n = time.time() - start

    print "parallelo: \t\t" + str(triang_par) + "\t time: " + str(t_par)
    print "normale: \t\t" + str(triang_ex) + "\t time: " + str(t_n)

def test_diam(graph, j):
    pass

def hw_mk2(j=2):
    g_test = ["./ego-gplus/out.ego-gplus", "./p2p-Gnutella25/p2p-Gnutella25.txt",
                "../data_fb/1684.edges", "../data_fb/107.edges", "../data_fb/348.edges"]
    i = 0
    for g in g_test:
        directed = False if i>1 else True
        graph = load_graph(g, directed)
        i +=1
        print "Graph loaded: \t"+g
        print "\tnodes: \t" + str(graph.number_of_nodes())
        print "\tedges: \t" + str(graph.number_of_edges())

        #scc = strongly2(graph)
        test_triangle(graph, j)
        print "\n\n"


def test2():
    g = ["./ego-gplus/out.ego-gplus", "./p2p-Gnutella25/p2p-Gnutella25.txt",
                "../data_fb/1684.edges", "../data_fb/107.edges", "../data_fb/348.edges"]
    graph = load_graph(g[1], True)
    u_graph = nx.Graph(graph)
    sccs = strongly2(graph)
    grt = sccs[0]
    diam = 0
    start = time.time()
    for scc in sccs:
        n_d = stream_diam(graph.subgraph(scc))
        if n_d > diam:
            diam = n_d
    print "diam:\t"+str(diam)
    stop = time.time() - start
    print "diam tot "+stream_diam(graph)


def test():
    g1 = "./ego-gplus/out.ego-gplus"
    g2 = "./p2p-Gnutella25/p2p-Gnutella25.txt"
    gt = "./g_test.txt"
    graph = load_graph(g2, True)
    print "nodes: \t" + str(graph.number_of_nodes())
    print "edges: \t" + str(graph.number_of_edges())

    triangles_app = num_triangles(nx.Graph(graph))
    print "num_triangles: \t" + str(triangles_app)

    diam_app = stream_diam(graph)
    print "diameter: \t" + str(diam_app)

    comp = strongly2(graph)
    max = len(comp[0])
    for c in comp:
        print c
        if len(c) > max:
            max = len(c)
    print "nodi nella componente connessa piu' grande: " + str(max)

if __name__ == '__main__':
    #test()
    hw_mk2(4)
    #test2()