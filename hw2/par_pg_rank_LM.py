import time

import numpy

from util.priorityq import PriorityQueue
from util.utility import *
from joblib import Parallel, delayed
import networkx as nx
import math

def splitGraph(G):
    n = nx.number_of_nodes(G)
    sub1 = list(G.nodes())[:int(n / 2)]
    sub2 = list(G.nodes())[int(n / 2):]

    G1 = nx.subgraph(G, sub1).copy()
    G2 = nx.subgraph(G, sub2).copy()

    Gaux = nx.difference(G, nx.union(G1, G2)).copy()

    if nx.is_directed(G):
        G3 = nx.DiGraph()
        G4 = nx.DiGraph()

        for e in Gaux.edges():
            if e[0] in sub1:
                G3.add_edge(e[0], e[1])
            else:
                G4.add_edge(e[0], e[1])
        return G1, G2, G3, G4
    else:
        return G1, G2, Gaux, Gaux


def parPageRank(G):
    pq = PriorityQueue()

    subgraphs = splitGraph(G)

    results = Parallel(n_jobs=4)(
        delayed(pageRank)(graph) for graph in subgraphs)

    rank = {v: 0 for v in G.nodes()}

    for v in G.nodes():
        for i in range(3):
            if v in results[i]:
                rank[v] += results[i][v]
        pq.add(v, -rank[v])

    return pq