


# Computes the betweenness of the graph in input
import math
import random
import time
import os

import networkx as nx
import itertools as it
from util.utility import *
from hw1.optimized_functions import strongly2
from util.priorityq import PriorityQueue

def betweenness(G):
    betweenness = {frozenset(i): 0 for i in G.edges()}

    # Compute the number of shortest paths from s to every other node
    for s in G.nodes():
        # INITIALIZATION
        tree = []
        parents = {i: [] for i in G.nodes()}  # it saves the nodes the parents of i in all shortest paths from s to i
        spnum = {i: 0 for i in G.nodes()}  # it saves the number of shortest paths from s to i
        distance = {i: -1 for i in G.nodes()}  # it saves the length of the shortest path from s to i.
        eflow = {frozenset(e): 0 for e in G.edges()}  # it saves the number of shortest path from u to every other node
                                                      # that use edge e
        vflow = {i: 1 for i in
                 G.nodes()}  # it saves the number of shortest path from u to every other node that use vertex i (this
                             # number is at least 1, since there is at least the shortest path from s to i)

        # BFS
        queue = [s]
        spnum[s] = 1
        distance[s] = 0
        while queue != []:
            c = queue.pop(0)
            tree.append(c)
            for i in G[c]:
                if distance[i] == -1:  # if vertex i has not been visited
                    queue.append(i)
                    distance[i] = distance[c] + 1
                if distance[i] == distance[c] + 1:  # if we found another shortest path from s to i
                    spnum[i] += 1
                    parents[i].append(c)

        # BOTTOM-UP PHASE
        while tree != []:
            c = tree.pop()
            for i in parents[c]:
                eflow[frozenset({c, i})] = vflow[c] * (spnum[i] / float(spnum[c]))  # the number of shortest paths using
                                                                                    # vertex c is split among the edge to
                                                                                    #its parents proportionally to the number
                                                                                    # of shortest paths that the parents contributes
                vflow[i] += eflow[frozenset({c,
                                             i})]  # each shortest path that use an edge (i,c) where i is closest to s than c must use also vertex i
                betweenness[frozenset({c, i})] += eflow[frozenset({i,
                                                                   c})]  # betweenness of an edge is the sum over all s of the number of shortest paths from s to other nodes using that edge

    return betweenness


def ShapleyBetweennes(G, k=None, enqueue=False):
    if k is None:
        Nodes = G
    else:
        Nodes = random.sample(G.nodes(), k)
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

def ShapleyBetweennes2(G):
    shortest_path = dict()
    sv = {v: 0 for v in G.nodes()}
    for s in G.nodes():
        for d in G.nodes():
            if s != d:
                shortest_path[(s,d)] = nx.all_shortest_paths(G,s,d) if nx.has_path(G,s,d) else None
                shortest_path[(d,s)] = nx.all_shortest_paths(G,d,s) if nx.has_path(G,d,s) else None
    sigma = {pair: 0 for pair in shortest_path}
    dist = {pair: float('inf') for pair in shortest_path}
    sigma_v = {pair: {v: 0 for v in G.nodes()} for pair in shortest_path}
    for pair in shortest_path:
        source, target = pair
        if shortest_path[pair] is not None:
            l = []
            for paths in shortest_path[pair]:
                s = set()
                for n in paths:
                    s.add(n)
                l.append(s)
            shortest_path[pair] = l
            sigma[pair] = len(l)
            dist[pair] = nx.shortest_path_length(G,source, target)
            #print("pair:"+str(pair)+"\t dist:"+str(dist[pair]))

    # print("sigma e dist")
    # for el in shortest_path:
    #     print("pair:"+str(el))
    #     print("\tv: "+str(sigma[el])+"\tdist:"+str(dist[el]))
    for v in G.nodes():
        for s in G.nodes():
            for t in G.nodes():
                if s!= v and t != v:
                    sv[v] = sigma_v[()]
    return shortest_path

def stats_SVB(G,top, k=1):
    start = time.time()
    sv, pq=ShapleyBetweennes(G, k=math.ceil(G.number_of_nodes()*k), enqueue=True)
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
    graphs = ["../graphs/ego-gplus/out.ego-gplus",
              "../graphs/p2p-Gnutella25/p2p-Gnutella25.txt"]
    cnt = 0
    for graph in graphs:
        cnt +=1
        G = load_graph(graph, True)
        print("nodes: " + str(G.number_of_nodes()) + "\t edges: " + str(G.number_of_edges()))
        for p in range(70,100,10):
            pr = p/100.00
            out = stats_SVB(G,100,pr)
            file = open("./results/SVB_"+"g"+str(cnt)+"_"+str(p)+".txt", 'w')
            for el in out:
                file.write(el+"\n")
            file.close()

def compare_results(path):
    file = open("Shapley_Betweennes_completo.txt",'r')
    ref = set()
    for line in file:
        s = line.split(",")
        ref.add(s[0])
    to_compare = {filename : 0 for filename in os.listdir(path)}
    for filename in os.listdir(path):
        file = open(path+filename)
        tmp = set()
        for line in file:
            s = line.split(",")
            tmp.add(s[0])
            #to_compare[filename] += 1 if s[0] in ref else 0
        to_compare[filename] = len(ref) - len(ref-tmp)
    for el in to_compare:
        print("\t"+str(el)+"\t"+str(to_compare[el]))




if __name__ == '__main__':
    #test_SVB()
    #compare_results("./results/")
    G = nx.DiGraph()
    G.add_edge('A', 'B')
    G.add_edge('A', 'C')
    G.add_edge('B', 'C')
    G.add_edge('B', 'D')
    G.add_edge('D', 'E')
    G.add_edge('D', 'F')
    G.add_edge('D', 'G')
    G.add_edge('E', 'F')
    G.add_edge('F', 'G')
    G.add_edge('B', 'F')
    stats_SVB(G,5)
    #dist = ShapleyBetweennes2(G)
