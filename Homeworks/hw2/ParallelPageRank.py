import time

import numpy

from util.priorityq import PriorityQueue
from util.utility import *
from joblib import Parallel, delayed
import networkx as nx
import math


def _evaluate(G, rank, degree, s, n):
    """Funzione ausiliaria che effettua il calcolo del rank di un nodo nel sottografo G"""
    tmp = {i: 0 for i in G.nodes()}
    for i in G.nodes():
        for j in G[i]:
            tmp[j] += float(s * rank[i]) / degree[i]
    return tmp

def _update(nodes, res, s, n, old=None):
    """Funzione ausiliaria che effettua il merge dei risultati per il calcolo parallelo del rank di un nodo"""
    rank = {v: float(1 - s) / n for v in nodes}
    diff = 0
    for node in nodes:
        for r in res:
            rank[node] += r[node] if node in r else 0
        #diff += abs(rank[node]- old[node]) if old else 0
    return rank


def parallelPageRank2(G, s=0.85, step=75, n_subsets=4, n_jobs=4, flag=False):
    """Implementazione parallela di page rank, in cui sia la fase di calcolo del nuovo rank per ogni nodo, sia la fase di
    aggiornamento del rank sono parallelizzate.
        Parametri:
            -   n_subset:   numero di sottoinsiemi in cui si vogliono dividere i nodi del grafo G
            -   n_jobs:     numero di workers da utilizzare per la parallelizzazione. In questa implementazione il numero
                            di workers è indipendente dal numero di subset utilizzati
            -   flag:       se abilitato, la funzione restituisce direttamente la mappa di nodo : rank, invece di una PQ
        N.B. In questa implementazione non è pessibile utilizzare un confidence level per arrestare l'algoritmo, la scelta
        di eliminare il controllo sul raggiungimento della stabilità dei risultati ottenuti fra un'iterazione e l'altra ha
        permesso di velocizzare i tempi di merging dei risultati degli aggiornamenti paralleli dei singoli sotto vettori
        di rank.
    """
    pq = PriorityQueue()
    start = time.time()
    subsets, subgraphs, degree, jobs_mapping, res_mapping = _split_graph(G, n_subsets)
    stop = time.time()-start
    print("precomputazione = \t"+"{0:.4f}".format(stop))
    n = nx.number_of_nodes(G)
    curr_step = 0
    rank = {i: ((float(1)) / n) for i in G.nodes()}
    start = time.time()
    with Parallel (n_jobs=n_jobs) as parallel:
        while  curr_step < step:
            curr_step += 1
            rank_s = [{i: rank[i] for i in subsets[k]} for k in range(n_subsets)]
            res = parallel(delayed(_evaluate)(subgraphs[i], rank_s[jobs_mapping[i]], degree[i], s, n) for i in range(n_subsets**2))
            diff = 0
            #########################COMBINAZIONE DEI RISULTATI PARALLELA###############################################
            to_combine = [[res[i] for i in res_mapping[job]] for job in range(len(subsets))]
            n_ranks = parallel(delayed(_update)(subsets[i],to_combine[i], s, n) for i in range(len(subsets)))
            for d in n_ranks:
                rank = {    ** rank, ** d}
    if flag:
        return rank
    for u in G.nodes():
        pq.add(u, -rank[u])
    stop = time.time()-start
    print("pagerank parallelo:\t"+str(stop))
    return pq


def parallelPageRank(G, s=0.85, step=75, confidence=0, n_subsets=4,n_jobs=4 , flag=False):
    """Implementazione parallela di page rank.
            Parametri:
                -   n_subset:   numero di sottoinsiemi in cui si vogliono dividere i nodi del grafo G
                -   n_jobs:     numero di workers da utilizzare per la parallelizzazione. In questa implementazione il numero
                                di workers è indipendente dal numero di subset utilizzati
                -   flag:       se abilitato, la funzione restituisce direttamente la mappa di nodo : rank, invece di una PQ
        """
    pq = PriorityQueue()
    start = time.time()
    subsets, subgraphs, degree, jobs_mapping, res_mapping = _split_graph(G, n_subsets)
    stop = time.time()-start
    print("preparazione sottostrutture. t = \t"+"{0:.4f}".format(stop)+" s")
    n = nx.number_of_nodes(G)
    done = False
    curr_step = 0
    rank = {i: ((float(1)) / n) for i in G.nodes()}
    start = time.time()
    with Parallel (n_jobs=n_jobs) as parallel:
        while not done and curr_step < step:
            curr_step += 1
            rank_s = [{i: rank[i] for i in subsets[k]} for k in range(n_subsets)]
            res = parallel(delayed(_evaluate)(subgraphs[i], rank_s[jobs_mapping[i]], degree[i], s, n) for i in range(n_subsets**2))
            diff = 0
            for nodes in G.nodes():
                new = float(1 - s) / n
                for r in res:
                    new += r[nodes] if nodes in r else 0
                diff += abs(new - rank[nodes])
                rank[nodes] = new

            if confidence != 0 and diff <= confidence:
                done = True
    if flag:
        return rank
    for u in G.nodes():
        pq.add(u, -rank[u])
    stop = time.time()-start
    print("page rank parallelo: "+"{0:.4f}".format(stop)+" s")
    return pq



def _split_graph(G, n_sets):
    """Effettua la scomposizione in sottografi del grafo in ingressi G, utilizzando n_sets sottoinsiemi dei nodi
        output:
            - subsets:      lista di set in cui i nodi sono stati divisi
            - subgraphs:    lista di sottografi in cui il grafo è stato diviso
            - degree:       mappa in cui ad ogni nodo viene fatto corrispondere il suo grado nel grafo originale
            - jobs_mapping: mappa utilizzata per far corrispondere ad ogni grafo il worker corretto
            - res_mapping:  mappa utilizzata per far corrispondere ad ogni sottoinsieme di nodi il worker corretto
    """
    n_subgraphs = n_sets**2
    subsets = [[] for i in range(n_sets)]
    subgraphs = [nx.DiGraph() for i in range(n_subgraphs)]
    i = 0
    #costruisco i set
    for u in G.nodes():
        subsets[i%n_sets].append(u)
        i += 1

    #costruisco i sottografi
    jobs_mapping = {i: set() for i in range(math.ceil(math.sqrt(n_subgraphs)))}
    res_mapping = {i: set() for i in range(math.ceil(math.sqrt(n_subgraphs)))}
    ng = 0
    start = time.time()
    for i in range(n_sets ):
        for j in range(n_sets):
            for node in subsets[i]:
                for v in G[node]:
                    if v in subsets[j]:
                        subgraphs[ng].add_edge(node, v)
            jobs_mapping[i].add(ng)
            res_mapping[j].add(ng)
            ng += 1
    stop = time.time() - start
    #print("tempo di tutto sto ciclo enorme: "+"{0:.4f}".format(stop))
    mapping = dict()
    for s in jobs_mapping:
        for job in jobs_mapping[s]:
            mapping[job] = s
    jobs_mapping = mapping
    degree = [{n : G.degree(n) for n in subgraphs[i].nodes()} for i in range(n_subgraphs)]

    return subsets, subgraphs, degree, jobs_mapping, res_mapping

def pageRank(G, s=0.85, step=75, confidence=0, flag=False):
    pq = PriorityQueue();

    n = nx.number_of_nodes(G)
    done = False
    time = 0
    # At the beginning, I choose the starting node uniformly at the random. Hence, every node has the same probability
    # of being verified at the beginning.
    rank = {i: float(1) / n for i in G.nodes()}
    while not done and time < step:
        time += 1
        # tmp contains the new rank
        # with probability 1-s, I restart the random walk. Hence, each node is visited at the next step at least with
        # probability (1-s)*1/n
        tmp = {i: float(1 - s) / n for i in G.nodes()}
        # UPDATE OPERATION
        for i in G.nodes():
            for j in G[i]:
                # with probability s, I follow one of the link on the current page. So, if I am on page i with probability
                # rank[i], at the next step I would be on page j at which i links with probability s*rank[i]*probability
                # of following link (i,j) that is 1/out_degree(i)
                tmp[j] += float(s * rank[i]) / len(G[i])
                # computes the difference between the old rank and the new rank and updates rank to contain the new rank
        diff = 0
        for i in G.nodes():
            # difference is computed in L1 norm. Alternatives are L2 norm (Euclidean Distance) and L_infinity norm
            # (maximum pointwise distance)
            diff += abs(rank[i] - tmp[i])
            rank[i] = tmp[i]

        if diff <= confidence:
            done = True
    if flag:
        return rank

    for u in G.nodes():
        pq.add(u, -rank[u])
    return pq

def test_split(G, n_sets):
    start = time.time()
    subsets, subgraphs, degree, jobs_mapping, res_mapping = _split_graph(G,n_sets=n_sets)
    stop = time.time() - start
    print("split: "+str(stop))



def test():

    graph = {
            "../graphs/as-caida2007/as-caida20071105.txt": False,
            "../graphs/p2p-Gnutella25/p2p-Gnutella25.txt":True,
             "../graphs/ego-gplus/out.ego-gplus":True,
             "../graphs/Ca-AstroPh.txt":False
             }
    for g in graph:
        print(g)
        G=load_graph(g,graph[g])
        print("\tnodes: \t"+str(G.number_of_nodes()))
        start = time.time()
        pq_s = pageRank(G)
        stop = time.time()-start
        print("pagerank:\t"+"{0:.4f}".format(stop)+" s")
        pq = parallelPageRank2(G, n_subsets=8)
        print("")


if __name__ == '__main__':
    test()
