#EXERCISE: Test how the computation time and the quality of the solution change as one changes s, step, confidence, and
#  the norm used for computing the difference between ranks. (Suggestion: use larger graphs than the one below in order
# to appreciate differences)

#A PARALLEL VERSION OF PAGE RANK can be achieved by dividing the graph in num_jobs different directed subgraphs.
# By assuming that num_jobs is a perfect square (4, 9, 16, 25, ...) this can be done dividing the set of nodes in
# sqrt(num_jobs) subsets, and having subgraph 0 containing only edges from the first subset to itself, subgraph 1
# containing only edges from the first subset to the second subset, ..., subgraph sqrt(num_jobs) containing only edges
#  from the second subset to the first subset, and so on. The update operation can be then executed in parallel for each
# subgraph.
# Results can be easily combined since the new page rank of a node i in the j-th subset is given by the rank
# coming from nodes in the first subset (contained in the j-th result) + the rank coming from nodes in the second subset
#  (contained in the sqrt(num_jobs)+j-th result) + ... + (1-s)/n. This combine operation also can be parallelized with
# each job taking care of combining the ranks of a different subset of nodes.
import time

import numpy

from util.priorityq import PriorityQueue
from util.utility import *
from joblib import Parallel, delayed
import networkx as nx
import math


# PAGE RANK CENTRALITY
# s is the probability of selecting a neighbor. The probability of a restart is 1-s
# step is the maximum number of steps in which the process is repeated
# confidence is the maximum difference allowed in the rank between two consecutive step. When this difference is below or equal to confidence, we assume that the rank we assume that computation is terminated.
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

def _evaluate(G, rank, degree, s, n):
    tmp = {i: 0 for i in G.nodes()}
    for i in G.nodes():
        for j in G[i]:
            tmp[j] += float(s * rank[i]) / degree[i]
    return tmp

def _update(nodes, res, s, n, old=None):
    rank = {v: float(1 - s) / n for v in nodes}
    diff = 0
    for node in nodes:
        for r in res:
            rank[node] += r[node] if node in r else 0
        #diff += abs(rank[node]- old[node]) if old else 0
    return rank



def parallelPageRank(G, s=0.85, step=75, confidence=0, n_subsets=4, flag=False):
    pq = PriorityQueue()
    start = time.time()
    subsets, subgraphs, degree, jobs_mapping, res_mapping = _split_graph(G, n_subsets ** 2)
    stop = time.time()-start
    print("preparazione sottostrutture. t = \t"+"{0:.4f}".format(stop))
    n = nx.number_of_nodes(G)
    done = False
    curr_step = 0
    rank = {i: ((float(1)) / n) for i in G.nodes()}

    tmp = []
    with Parallel (n_jobs=4) as parallel:
        while not done and curr_step < step:
            curr_step += 1
            rank_s = [{i: rank[i] for i in subsets[k]} for k in range(n_subsets)]
            res = parallel(delayed(_evaluate)(subgraphs[i], rank_s[jobs_mapping[i]], degree[i], s, n) for i in range(n_subsets**2))
            diff = 0
            #########################COMBINAZIONE DEI RISULTATI PARALLELA###############################################
            to_combine = [[res[i] for i in res_mapping[job]] for job in range(len(subsets))]
            n_ranks = parallel(delayed(_update)(subsets[i],to_combine[i], s, n) for i in range(len(subsets)))
            for d in n_ranks:
                rank = {**rank, **d}
            ############################################################################################################
            #########################COMBINAZIONE DEI RISULTATI SEQUENZIALE#############################################
            # for nodes in G.nodes():
            #     new = float(1 - s) / n
            #     for r in res:
            #         new += r[nodes] if nodes in r else 0
            #     diff += abs(new - rank[nodes])
            #     rank[nodes] = new

            if confidence != 0 and diff <= confidence:
                done = True
    if flag:
        return rank
    for u in G.nodes():
        pq.add(u, -rank[u])

    return pq


def _split_graph(G, n_subgraphs):
    n_sets = int(math.sqrt(n_subgraphs))
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
    for i in range(n_sets ):
        for j in range(n_sets):
            for node in subsets[i]:
                for v in G[node]:
                    if v in subsets[j]:
                        subgraphs[ng].add_edge(node, v)
            jobs_mapping[i].add(ng)
            res_mapping[j].add(ng)
            ng += 1
    mapping = dict()
    for sets in jobs_mapping:
        for job in jobs_mapping[sets]:
            mapping[job] = sets
    jobs_mapping = mapping
    degree = [{n : G.degree(n) for n in subgraphs[i].nodes()} for i in range(n_subgraphs)]

    return subsets, subgraphs, degree, jobs_mapping, res_mapping


def test():
    G = nx.DiGraph()

    G.add_edge('A', 'B')
    G.add_edge('A', 'C')
    G.add_edge('A', 'D')
    G.add_edge('B', 'A')
    G.add_edge('B', 'D')
    G.add_edge('C', 'A')
    G.add_edge('D', 'B')
    G.add_edge('D', 'C')
    graph = ["../graphs/Brightkite/Brightkite_edges.txt",
             "../graphs/ego-gplus/out.ego-gplus",
             "./g_test.txt"]
    G=load_graph(graph[0],True)
    print("\tnodes: \t"+str(G.number_of_nodes()))


    el_to_print = 4
    print("\nNormale")
    start = time.time()
    pq_s = pageRank(G, flag=False)
    stop = time.time() - start
    print("\tt: \t" + "{0:.4f}".format(stop))
    for i in range(el_to_print):
        el, rank = pq_s.pop(with_priority=True)
        print(str(el) + "\t=\t " + str(rank))
    print("\nParallelo")
    start = time.time()
    pq = parallelPageRank(G, n_subsets=4
                          , flag=False)
    stop = time.time() - start
    print("\tt: \t" + "{0:.4f}".format(stop))
    for i in range(el_to_print):
        el, rank = pq.pop(with_priority=True)
        print(str(el) + "\t=\t " + str(rank))

# con parallelizzazione dell'aggiornamento di rank
# 	t: 	33.7364
# 8775	=	 -1.1781554686962033e-05
# 15597	=	 -7.702734696904458e-06
# 529	=	 -7.697435246317929e-06
# 530	=	 -7.697435246317929e-06
# parallelizzando solo update
# 	t: 	33.9227
# 8775	=	 -1.1781554686962033e-05
# 15597	=	 -7.702734696904458e-06
# 529	=	 -7.697435246317929e-06
# 530	=	 -7.697435246317929e-06
if __name__ == '__main__':
    test()
