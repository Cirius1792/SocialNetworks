import matplotlib

from util import *
import networkx as nx
import time
from joblib import Parallel, delayed

import matplotlib.pyplot as plt

def test_triangle(graph, j):

    u_graph = nx.Graph(graph)
    start = time.time()
    triang_par = par_triangles(u_graph, j)
    #triang_par = par2_trn(u_graph, j)
    t_par = time.time() - start
    start = time.time()
    triang_ex = num_triangles(u_graph)
    t_n = time.time() - start

    print ("parallelo: \t\t" + str(triang_par) + "\t time: " + str(t_par))
    print ("normale: \t\t" + str(triang_ex) + "\t time: " + str(t_n))



def hw_mk2(j=2):
    g_test = ["./ego-gplus/out.ego-gplus", "./p2p-Gnutella25/p2p-Gnutella25.txt",
                "../data_fb/1684.edges", "../data_fb/107.edges", "../data_fb/348.edges"]
    i = 0
    for g in g_test:
        directed = False if i>1 else True
        graph = load_graph(g, directed)
        i +=1
        print ("Graph loaded: \t"+g)
        print ("\tnodes: \t" + str(graph.number_of_nodes()))
        print ("\tedges: \t" + str(graph.number_of_edges()))
        start = time.time()
        #scc = strongly2(graph)
        #scc = par_SCC(graph)
        stop = time.time()-start
        test_triangle(graph, j)
        #print ("num SCC: \t"+str(len(scc))+"\t t: \t"+str(stop))
        print ("\n\n")




if __name__ == '__main__':
    #test()
    hw_mk2(4)
    #test2()