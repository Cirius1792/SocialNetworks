import networkx as nx
import random
from Esercitazioni.esercitazione_4.Centrality import *
from util.utility import *
from util.priorityq import *

def best_resp(graph, act, nact):

    TRESHOLD = 'threshold'
    ACTIVE = 'active'
    ACT_NEIGH = 'act_neigh'

    thresholds = nx.get_node_attributes(graph, TRESHOLD)
    if len(thresholds) == 0:
        for i in graph.nodes():
            graph.node[i][TRESHOLD] = random.random() * len(graph[i])

    if len(act) > 0 or len(nact) > 0:
        for i in act:
            if ACTIVE not in graph.node[i] or not graph.node[i][ACTIVE]:
                graph.node[i][ACTIVE] = True
                for j in graph[i]:
                    if ACT_NEIGH in graph.node[j]:
                        graph.node[j][ACT_NEIGH] += 1
                    else:
                        graph.node[j][ACT_NEIGH] = 1
        for i in nact:
            if ACTIVE not in graph.node[i] or graph.node[i][ACTIVE]:
                graph.node[i][ACTIVE] = False
                for j in graph[i]:
                    if ACT_NEIGH in graph.node[j]:
                        graph.node[j][ACT_NEIGH] -= 1
                    else:
                        graph.node[j][ACT_NEIGH] = 0

        for i in graph.nodes():
            if ACT_NEIGH in graph.node[i] and graph.node[i][ACT_NEIGH] >= graph.node[i][TRESHOLD] and (
                    ACTIVE not in graph.node[i] or not graph.node[i][ACTIVE]):
                best_resp(graph, {i}, {})
                break
            if (ACT_NEIGH not in graph.node[i] or graph.node[i][ACT_NEIGH] < graph.node[i][TRESHOLD]) and (
                    ACTIVE in graph.node[i] and graph.node[i][ACTIVE]):
                best_resp(graph, {}, {i})
                break

    return graph

def test():
    path = "./generated_networks/random_2500_0.5.txt"
    G = nx.read_edgelist(path)
    seed = set(top(G,degree,10))
    active = nx.get_node_attributes(best_resp(G, seed, {}), 'active')
    print([i for i in active.keys() if active[i]])

if __name__ == '__main__':
    test()