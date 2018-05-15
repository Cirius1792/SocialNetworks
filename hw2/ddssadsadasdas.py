import numpy

from util.priorityq import PriorityQueue
from util.utility import *
from joblib import Parallel, delayed
import networkx as nx
import math

def pageRank(G, s=0.85, step=75, confidence=0, flag=False):
    pq = PriorityQueue()

    n = nx.number_of_nodes(G)
    done = False
    time = 0
    rank = {i: float(1) / n for i in G.nodes()}

    source = list(G.nodes())[:int(n / 2) - 1]
    dest = list(G.nodes())[int(n / 2):]

    l = []
    l.append([source, source])
    l.append([source, dest])
    l.append([dest, source])
    l.append([dest, dest])

    while not done and time < step:
        time += 1
        tmp = {i: float(1 - s) / n for i in G.nodes()}

        # UPDATE OPERATION
        results = Parallel(n_jobs=4)(
            delayed(aux_PageRank)(G, i[0], i[1], s, rank) for i in l)

        for i in G.nodes():
            tmp[i] += results[0][i] + results[1][i] + results[2][i] + results[3][i]

        diff = 0
        for i in G.nodes():
            diff += abs(rank[i] - tmp[i])
            rank[i] = tmp[i]

        if diff <= confidence:
            done = True
    if flag:
        return rank

    for u in G.nodes():
        pq.add(u, -rank[u])
    return pq


def aux_PageRank(G, source, dest, s, rank):
    tmp = {i: 0 for i in G.nodes()}

    for i in source:
        for j in set(G[i]) & set(dest):
            tmp[j] += float(s * rank[i]) / len(G[i])

    return tmp

if __name__ == '__main__':
    G = nx.DiGraph()

    G.add_edge('A', 'B')
    G.add_edge('A', 'C')
    G.add_edge('A', 'D')
    G.add_edge('B', 'A')
    G.add_edge('B', 'D')
    G.add_edge('C', 'A')
    G.add_edge('D', 'B')
    G.add_edge('D', 'C')
    graph = "./g_test.txt"
    G=load_graph(graph,True)
    print("\nParallelo")
    pq = pageRank(G, flag=False)
    for i in range(3):
        el, rank = pq.pop(with_priority=True)
        print(str(el) + "\t=\t " + str(rank))
