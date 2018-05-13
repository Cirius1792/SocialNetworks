import matplotlib

from optimized_functions import *
import networkx as nx
import time

#g_test = ["../graphs/ego-gplus/out.ego-gplus", "../graphs/p2p-Gnutella25/p2p-Gnutella25.txt"]
g_test = ["../graphs/ego-gplus/gplus_combined.txt"]


def test_triangle(graph, j):
    print("Test Triangoli")
    u_graph = nx.Graph(graph)
    start = time.time()
    triang_par = par_triangles(u_graph, j)
    t_par = time.time() - start
    start = time.time()
    triang_ex = num_triangles(u_graph)
    t_n = time.time() - start

    print ("\tparallelo: \t\t" + str(triang_par) + "\t time: " + str(t_par))
    print ("\tnormale: \t\t" + str(triang_ex) + "\t time: " + str(t_n))


def test_scc(graph, j):
    print("Test Componenti Fortemente Connesse")
    start = time.time()
    scc_n = strongly2(graph)
    t = time.time() - start
    start = time.time()
    p = 0.85
    scc_o = SCC_p(graph, p)
    t_o = time.time() - start
    m_scc = scc_o[0]
    for c in scc_o:
        if len(c)>len(m_scc):
            m_scc = c

    m_scc_n = scc_n[0]
    for c in scc_n:
        if len(c)>len(m_scc_n):
            m_scc_n = c
    print("\tAlgoritmo standard:")
    print("\tnum SCC: \t" + str(len(scc_n)) + "\t t: \t" + str(t))
    #print ("\tSCC più grande: "+str(m_scc_n))
    print("\tAlgoritmo ottimizzato:\t valutazione del "+str(p*100)+"% dei nodi")
    print("\tnum SCC: \t" + str(len(scc_o)) + "\t t: \t" + str(t_o))
    #print("\tSCC più grande: " + str(m_scc))



def test_diam(graph):
    print("Test Diametro")
    scc = strongly2(graph)
    ms = scc[0]
    for s in scc:
        if len(s) > len(ms):
            ms = s
    start = time.time()
    diam = stream_diam(graph.subgraph(ms))
    t = time.time() - start
    print ("\tdiametro approssimato:"+str(diam)+"\tt: \t"+str(t))


def hw(j=2):
    i = 0
    for g in g_test:
        directed = False if i>1 else True
        graph = load_graph(g, directed)
        i +=1
        print ("Grafo: \t"+g)
        print ("\tnodi: \t" + str(graph.number_of_nodes()))
        print ("\tarchi: \t" + str(graph.number_of_edges()))
        test_triangle(graph, j)
        #test_scc(graph,j)
        #test_diam(graph)
        print ("\n\n")

def stats_triang():
    s = str(time.time())
    f = open("trn_"+s+".txt", "w")
    f.write("########TEST Triangles "+s+"###########\n")
    for g in g_test:
        graph = load_graph(g, True)
        f.write("\n"+g+"\n")
        start = time.time()
        n_trn = num_triangles(graph)
        t = time.time() - start
        f.write("tempo algoritmo sequenziale: \t"+str(t)+"\n\n")
        for j in range(2,10,2):
            print("n job = "+str(j))
            f.write("n_job = "+str(j)+"\n")
            for i in range(0,20):
                start = time.time()
                triang_par = par_triangles(
                    graph, j)
                stop = time.time() - start
                print (str(round(stop,3)))
                f.write(str(round(stop,3))+"\n")
            f.write("\n")


def stats_scc():
    s = str(time.time())
    f = open("scc_"+s+".txt", "w")
    f.write("########TEST SCC "+s+"###########\n")
    for g in g_test:
        graph = load_graph(g, True)
        f.write("Grafo: \t"+g+"\n")
        #Funzione classica (il tempo verrà usato come valore di riferimento)
        start = time.time()
        scc_n = strongly2(graph)
        t_n = time.time() - start
        f.write("algoritmo standard\n")
        f.write("\t\t num SCC: \t\t t\n")
        f.write("\t\t"+str(len(scc_n))+" \t\t "+str(t_n)+"\n")
        p = 0.25

        while p < 0.9:
            print("p:" + str(p))
            for i in range(0,20):
                print("run: "+str(i))
                start = time.time()
                scc_o = SCC_p(graph, p)
                t_o = time.time() - start
                f.write(str(round(p,2))+"\t"+str(len(scc_o)) + " \t\t " + str(t_o)+"\n")
            p += 0.1
    f.close()


if __name__ == '__main__':
    hw(4)
    #stats_scc()
    #stats_triang()