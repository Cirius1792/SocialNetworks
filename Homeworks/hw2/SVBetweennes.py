


# Computes the betweenness of the graph in input
import math
import random
import time
import os

from util.utility import *
from util.priorityq import PriorityQueue

def ShapleyBetweennes(G, k=None, enqueue=False):
    """ Implementa il calcolo della Shapley Betweennes (ref. Szczepa´nski, Michalak, Rahwan)
        Parametri:
            -   G:      grafo su cui effettuare le operazioni
            -   k:      percentuale dei nodi da considerare per il calcolo dell'SV, nel caso in cui se ne volesse solo una
                        misura approssimata
            -   enqueue:se True restituisce una PriorityQueue contenente i  nodi ed i relativi SV, altrimenti restituisce
                        la mappa nodo SV
    """
    if k is None:
        Nodes = G
    else:
        Nodes = random.sample(G.nodes(), int(math.ceil(G.number_of_nodes()*k)))
    sv = {i : 0 for i in G.nodes()}
    pq = PriorityQueue()
    n = len(Nodes)
    cnt = 1
    print("Work in Progress...")

    for s in Nodes:
        if cnt%50==0:
            print("\r"+"{0:.2f}".format((float(cnt)/n)*100)+"%", end="")
        cnt +=1
        pred = {v: [] for v in G.nodes()}
        distance = {v: float('inf') for v in G.nodes()}
        sigma_sv = {v: 0 for v in G.nodes()}

        queue = []
        S = []
        distance[s] = 1
        sigma_sv[s] = 1
        queue.append(s)
        while queue:
            v = queue.pop()
            S.append(v)
            for w in G[v]:
                if distance[w] == float('inf'):
                    distance[w] = distance[v] + 1
                    queue.append(w)
                if distance[w] == distance[v] + 1:
                    sigma_sv[w] += sigma_sv[v]
                    pred[w].append(v)

        delta_s = {v : 0 for v in G.nodes()}
        while S != []:
            w = S.pop()
            for v in pred[w]:
                delta_s[v] += sigma_sv[v]/sigma_sv[w]*(float(1)/distance[w]+delta_s[w])
            if w != s:
                sv[w] += delta_s[w]+(float(2)-distance[w])/float(distance[w])
    for v in Nodes:
        sv[v] = sv[v]/float(2)
        if enqueue:
            pq.add(v,sv[v])
    print("\rDone!", end="")

    return (sv, pq) if enqueue else sv


def stats_SVB(G, top, k=1):
    start = time.time()
    sv, pq=ShapleyBetweennes(G, k, enqueue=True)
    #sv, pq=ShapleyBetweennes(G, enqueue=True)
    stop = time.time() - start
    out=[]
    for i in range(top):
        res,pr = pq.pop(with_priority=True)
        out.append(""+str(res)+","+"{0:.4f}".format(pr)+"")
    print("Time:\t"+str(stop))
    print(out)
    return out

def test_SVB():
    graphs = {"../graphs/CA-AstroPh.txt":False,
              "../graphs/p2p-Gnutella25/p2p-Gnutella25.txt":True}
    cnt = 0
    for graph_name in graphs:
        cnt +=1
        G = load_graph(graph_name, graphs[graph_name])
        print("nodes: " + str(G.number_of_nodes()) + "\t edges: " + str(G.number_of_edges()))
        out = stats_SVB(G, 50)
        file = open("./results2/SVB_" + "g" + str(cnt) + "_REFERENCE.txt", 'w')
        for el in out:
            file.write(el + "\n")
        file.close()
        for p in range(70,100,10):
            pr = p/100.00
            out = stats_SVB(G,50,pr)
            file = open("./results2/SVB_"+"g"+str(cnt)+"_"+str(p)+".txt", 'w')
            for el in out:
                file.write(el+"\n")
            file.close()

def compare_results(path_res,path_ref):
    file = open(path_ref,'r')
    ref = set()
    for line in file:
        s = line.split(",")
        ref.add(s[0])
    to_compare = {filename : 0 for filename in os.listdir(path_res)}
    for filename in os.listdir(path_res):
        file = open(path_res+filename)
        tmp = set()
        for line in file:
            s = line.split(",")
            tmp.add(s[0])
            #to_compare[filename] += 1 if s[0] in ref else 0
        to_compare[filename] = len(ref) - len(ref-tmp)
    for el in to_compare:
        print("\t"+str(el)+"\t"+str(to_compare[el]))




if __name__ == '__main__':
    test_SVB()
    print("Astro")
    compare_results("./results2/astro/","./results2/SVB_g1_REFERENCE.txt")
    print("\n\nGnutella")
    compare_results("./results2/gnutella/","./results2/SVB_g2_REFERENCE.txt")

