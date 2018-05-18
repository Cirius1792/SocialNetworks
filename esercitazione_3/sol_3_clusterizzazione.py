#!/usr/bin/python

import networkx as nx
from util.priorityq import PriorityQueue
import random
from scipy.sparse import linalg, coo_matrix
import numpy as np
from util.utility import load_graph


# CLUSTERING [Leskovec et al., 10.2, 10.4]

def hierarchical(G):
    # Create a priority queue with each pair of nodes indexed by distance
    pq = PriorityQueue()
    for u in G.nodes():
        for v in G.nodes():
            if u != v:
                if (u, v) in G.edges() or (v, u) in G.edges():
                    pq.add(frozenset([frozenset(u), frozenset(v)]), 0)
                else:
                    pq.add(frozenset([frozenset(u), frozenset(v)]), 1)

    # Start with a cluster for each node
    clusters = set(frozenset(u) for u in G.nodes())

    done = False
    while not done:
        # Merge closest clusters
        s = list(pq.pop())
        clusters.remove(s[0])
        clusters.remove(s[1])

        # Update the distance of other clusters from the merged cluster
        for w in clusters:
            e1 = pq.remove(frozenset([s[0], w]))
            e2 = pq.remove(frozenset([s[1], w]))
            if e1 == 0 or e2 == 0:
                pq.add(frozenset([s[0] | s[1], w]), 0)
            else:
                pq.add(frozenset([s[0] | s[1], w]), 1)

        clusters.add(s[0] | s[1])

        print(clusters)
        a = input("Do you want to continue? (y/n) ")
        if a == "n":
            done = True


def two_means(G):
    # Choose two clusters represented by edge that are not neighbors
    u = random.choice(G.nodes())
    v = random.choice(list(nx.non_neighbors(G, u)))
    cluster0 = {u}
    cluster1 = {v}

    done = False
    while not done:
        # Choose a node that is not yet in a cluster and add it to the closest cluster
        x = random.choice([el for el in G.nodes() if el not in cluster0 | cluster1 and len(
            set(G.neighbors(el)).intersection(cluster0)) != 0 or len(set(G.neighbors(el)).intersection(cluster1)) != 0])
        if len(set(G.neighbors(x)).intersection(cluster0)) != 0:
            cluster0.add(x);
        elif len(set(G.neighbors(x)).intersection(cluster1)) != 0:
            cluster1.add(x);

        print(cluster0, cluster1)
        a = input("Do you want to continue? (y/n) ")
        if a == "n":
            done = True


# Computes the betweenness of the graph in input
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
                 G.nodes()}  # it saves the number of shortest path from u to every other node that use vertex i (this number is at least 1, since there is there is at least the shortest path from s to i)

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
                eflow[frozenset({c, i})] = vflow[c] * (spnum[i] / float(spnum[
                                                                            c]))  # the number of shortest paths using vertex c is split among the edge to its parents proportionally to the number of shortest paths that the parents contributes
                vflow[i] += eflow[frozenset({c,
                                             i})]  # each shortest path that use an edge (i,c) where i is closest to s than c must use also vertex i
                betweenness[frozenset({c, i})] += eflow[frozenset({i,
                                                                   c})]  # betweenness of an edge is the sum over all s of the number of shortest paths from s to other nodes using that edge

    return betweenness


# How to speed up betweenness computation? Instead to consider all possible starting node, only consider a sample.
# EXERCISE: implement this optimization
# EXERCISE: try to implement parallel versions of above algorithms.

# remove edges of largest betweenness
def bwt_cluster(G):
    b1 = betweenness(G)


    done = False
    while not done:
        b = nx.edge_betweenness_centrality(G)
        graph = G.copy()
        pq = PriorityQueue()
        for x in b.keys():
            pq.add(x, -b[x])
        edge = tuple(sorted(pq.pop()))
        graph.remove_edges_from([edge])
        print(list(nx.connected_components(graph)))
        a = input("Do you want to continue? (y/n) ")
        if a == "n":
            done = True


# Spectral algorithm
def spectral(G):
    n = G.number_of_nodes()
    nodes = sorted(G.nodes())
    # Laplacian of a graph is a matrix, with diagonal entries being the degree of the corresponding node and off-diagonal entries being -1 if an edge between the corresponding nodes exists and 0 otherwise
    L = nx.laplacian_matrix(G,
                            nodes).asfptype()  # asfptype() convertes the laplacian matrix as returned by networkx to a sparse matrix as managed by scipy
    # print(L)
    # Compute eigenvalues and eigenvectors of the Laplacian matrix
    w, v = linalg.eigsh(L,
                        n - 1)  # the first input is the array of eigenvalues in increasing order. The second output contains eigenvectors: specifically, the eigenvector of the k-th eigenvalue is given by the k-th entry of each of the n vectors contained in v
    # print(w)
    # print(v)
    # print(v[:,0])
    # Partition in clusters based on the corresponding eigenvector value being positive or negative
    cluster0 = set()
    cluster1 = set()
    for i in range(n):
        if v[i, 0] < 0:
            cluster0.add(nodes[i])
        else:
            cluster1.add(nodes[i])
    print(cluster0, cluster1)


# How to achieve more than two clusters? Two options: (i) recursively split in clusters using the same approach on each of the two subgraphs; (ii) use other eigenvectors
# EXERCISE: implement both these generalizations.
if __name__ == '__main__':
    G = nx.Graph()
    G.add_edge('A', 'B')
    G.add_edge('A', 'C')
    G.add_edge('B', 'C')
    G.add_edge('B', 'D')
    G.add_edge('D', 'E')
    G.add_edge('D', 'F')
    G.add_edge('D', 'G')
    G.add_edge('E', 'F')
    G.add_edge('F', 'G')
    graph = [
        "../graphs/as-caida2007/as-caida20071105.txt",
        "../graphs/p2p-Gnutella25/p2p-Gnutella25.txt",
        "../graphs/ego-gplus/out.ego-gplus",
        "../graphs/Ca-AstroPh.txt"
    ]
    G = load_graph(graph[3], False)

    # hierarchical(G)
    two_means(G)
    #bwt_cluster(G)
    #spectral(G)