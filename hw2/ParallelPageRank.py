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

def update(G,rank, degree, s,n):
    tmp = {i: (float(1) - s) / n for i in G.nodes()}

    for i in G.nodes():
        for j in G[i]:
            tmp[j] += float(s * rank[i] / degree[i])
    diff = 0
    # for i in G.nodes():
    #     diff += abs(rank[i] - tmp[i])
    #     rank[i] = tmp[i]
    #return {'rank': tmp, 'diff': diff}
    return tmp

def parallelPageRank(G, s=0.85, step=75, confidence=0, n_jobs=4,flag=False):
    pq = PriorityQueue()
    subsets, subgraphs, degree, mp = split_graph(G, n_jobs)
    n = nx.number_of_nodes(G)
    done = False
    time = 0
    rank = {i: ((float(1)) / n) for i in G.nodes()}
    #rank_s = [{i: rank[i] for i in subgraphs[k].nodes()} for k in range(n_jobs)]
    mapping = dict()
    #inv_map = {v: k for k, v in mp.items()}
    for sets in mp:
        for job in mp[sets]:
            mapping[job] = sets
    with Parallel (n_jobs=n_jobs) as parallel:
        while not done and time < step:
            time += 1
            rank_s = [{i: rank[i] for i in subsets[k]} for k in range(math.ceil(math.sqrt(n_jobs)))]
            res = parallel(delayed(update)(subgraphs[i], rank_s[mapping[i]], degree[i], s, n) for i in range(n_jobs))
            #res = parallel(delayed(update)(subgraphs[i], rank, degree[i], s, n) for i in range(n_jobs))
            diff = 0
            for k in range(math.ceil(math.sqrt(n_jobs))):
                for nodes in subsets[k]:
                    new = 0
                    for i in mp[k]:
                        new += res[i][nodes]
                    diff += abs(new - rank[nodes])
                    rank[nodes] = new
            if diff <= confidence:
                done = True
    if flag:
        return rank
    for u in G.nodes():
        pq.add(u, -rank[u])
    return pq


def split_graph(G, n_jobs):
    n_sets = int(math.sqrt(n_jobs))
    subsets = [[] for i in range(n_sets)]
    subgraphs = [nx.DiGraph() for i in range(n_jobs)]
    i = 0
    #costruisco i set
    for u in G.nodes():
        subsets[i%n_sets].append(u)
        i +=1

    #costruisco i sottografi
    mp = { i: set() for i in range(math.ceil(math.sqrt(n_jobs)))}
    ng = 0
    for i in range(n_sets ):
        for j in range(n_sets ):
            for node in subsets[i]:
                for v in G[node]:
                    #subgraphs[ng].add_edge(node, v) if v in subsets[j] else 0
                    if v in subsets[j]:
                        subgraphs[ng].add_edge(node, v)
                        mp[j].add(ng)
            ng += 1
    degree = [{n : G.degree(n) for n in subgraphs[i].nodes()} for i in range(n_jobs)]

    return subsets, subgraphs, degree, mp



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
    graph = "../graphs/Brightkite/Brightkite_edges.txt"
    G=load_graph(graph,True)
    #s, g, degree = split_graph(G, 9)
    # print("sets:")
    # for ss in s:
    #     print(ss)
    # print("subgraphs:")
    # for gg in g:
    #     for n in gg:
    #         for neig in gg[n]:
    #             print("("+str(n)+","+str(neig)+") ")
    #     print("\n")
    print("\nNormale")
    pq_s = pageRank(G,flag=False)
    for i in range(3):
        el, rank = pq_s.pop(with_priority=True)
        print(str(el)+"\t=\t "+str(rank))
    print("\nParallelo")
    pq = parallelPageRank(G, flag=False)
    for i in range(3):
        el, rank = pq.pop(with_priority=True)
        print(str(el)+"\t=\t "+str(rank))


