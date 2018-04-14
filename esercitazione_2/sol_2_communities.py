#!/usr/bin/python

import networkx as nx
import itertools as it
import math
from joblib import Parallel, delayed
import random


#######STRONGLY CONNECTED COMPONENTS [Leskovec et al., Sect. 10.8.6]#######

# LINEAR IN THE SIZE OF THE GRAPH
# HARDER TO PARALLELIZE
def strongly(G):
    newG = G
    # If the graph is directed, then it considers a new graph in which the direction of the edges is reversed
    if type(G) is nx.DiGraph:
        newG = G.reverse(False)

    visited = set()
    components = []
    i = 0
    while len(visited) < len(G.nodes()):
        # Start from a node that has not been yet visited
        stack = [list(set(G.nodes()) - visited)[0]]
        components.append(set())
        # Run a DFS
        while len(stack) > 0:
            u = stack.pop()
            visited.add(u)
            components[i].add(u)
            for v in newG[u]:
                if v not in visited:
                    stack.append(v)
        # When the stack is empty, no other node can be added in the component, and we need to consider another component
        i += 1

    return components


# SLIGHTLY SLOWER
# EASIER TO PARALLELIZE
def strongly2(G):
    graph = G.copy()
    comp = dict()

    done = False
    while not done:
        changed = False
        # For each node left in the graph
        for node in graph.nodes():
            # Run a BFS to list all nodes reachable from "node"
            visited = set()
            queue = [node]
            while len(queue) > 0:
                u = queue.pop()
                for v in graph[u]:
                    if v not in visited:
                        queue.append(v)
                visited.add(u)

            # Run a BFS on the graph with the direction of edges reversed to list all nodes that can reach "node"
            igraph = graph.reverse(False)
            ivisited = set()
            queue = [node]
            while len(queue) > 0:
                u = queue.pop()
                for v in igraph[u]:
                    if v not in ivisited:
                        queue.append(v)
                ivisited.add(u)

            # The intersection of above sets is the strongly connected component at which "node" belongs
            if len(visited & ivisited) > 1:
                comp[node] = visited & ivisited
                # We modify the graph by substituting the strongly connected component at which "node" belongs with a single vertex labeled "node" that has all edges to and from the component and every other node in the graph
                mapping = {k: node for k in comp[node]}
                graph = nx.relabel_nodes(graph, mapping, copy=False)
                if graph.has_edge(node, node):
                    graph.remove_edge(node, node)
                # If the graph has been changed, we restart with the newly created graph
                changed = True
                break

        # If an iteration, no change is done, then all components have been found
        if not changed:
            done = True

    components = []
    # Each node left in the graph corresponds to a component
    for u in graph:
        if u in comp.keys():
            components.append(comp[u])
        else:
            components.append({u})

    return components


# EXERCISE: Modify function strongly2 in order to remove components in place of reducing the graph

#######DISCOVER COMPLETE BIPARTITE SUBGRAPH [Leskovec et al., Sect. 10.3, 6.2.6]#######

# Find a set of t items contained in at least s baskets
def apriori(B, N, s, t):
    cand = dict()
    not_excluded = set()

    # Incrementally finds a set of i+1 items contained in at least s baskets
    for i in range(t):
        cand = dict()
        for S in it.combinations(N, i + 1):
            done = True
            # A set of i+1 items can be contained in at least s baskets only if all its subsets of size i were contained in at least s baskets
            for T in it.combinations(S, i):
                if len(T) > 0 and frozenset(T) not in not_excluded:
                    done = False
                    break
            if done and len(S) > 0:
                cand[frozenset(S)] = set()

        # For each candidate set of i+1 items that can be contained in at least s baskets counts the number of basket in which it is contained
        for S in cand.keys():
            for i in B.keys():
                if S <= set(B[i]):
                    cand[S].add(i)

        # Remove all candidate sets of i+1 items that are not contained in at least s baskets
        not_excluded = set()
        for S in cand.keys():
            if len(cand[S]) >= s:
                not_excluded.add(S)

    sol = dict()
    for S in not_excluded:
        sol[S] = cand[S]
    return sol


# Finding complete (s,t)-bipartite subgraphs
def Kst(G, s, t):
    B = dict()
    for i in G.nodes():
        B[i] = set(G[i])

    sol = apriori(B, set(B.keys()), s, t)

    community = set()
    for S in sol.keys():
        community.add(S | sol[S])

    return community


# HOW TO CHOOSE s AND t? GIVEN A GRAPH WITH n NODES AND AVERAGE DEGREE d, IF WE TAKE s,t SUCH THAT n(d/n)^t >= s, THEN A K_s,t SUBGRAPH EXISTS WITH LARGE PROBABILITY

def chunks(data, SIZE=10000):
    idata = iter(data)
    for i in range(0, len(data), SIZE):
        yield {k: data[k] for k in it.islice(idata, SIZE)}


def count_cand(B, cand):
    count = {S: set() for S in cand}
    for i in B.keys():
        for S in cand:
            if S <= set(B[i]):
                count[S].add(i)
    return count


# Parallel implementation of a priori algorithm
def par_apriori(B, N, s, t, j):
    p = 1. / j
    with Parallel(n_jobs=j) as parallel:
        # Split the baskets in j chunks and assign each chunk to a different job
        # The job runs the apriori algorithm on its chunk
        # Since it works on a subset of baskets it also looks only for just a fraction of s occurrences
        results = parallel(delayed(apriori)(i, N, max(1, math.floor(p * s)), t) for i in chunks(B, int(p * len(B))))

        # The set of candidates consists of every subset of t items that is returned by at least one job
        cand = set()
        for i in range(len(results)):
            for k in results[i].keys():
                cand.add(k)

        # To avoid false positive we count again the occurrences of these candidates
        # Each job counts the occurrences only in its chink of baskets
        results = parallel(delayed(count_cand)(i, cand) for i in chunks(B, int(p * len(B))))

        # Combine the results of jobs
        count = {S: set() for S in cand}
        for i in range(len(results)):
            for S in cand:
                count[S] = count[S] | results[i][S]

        # Keep only the candidates whose combined count is at least s
        sol = dict()
        for S in cand:
            if len(count[S]) >= s:
                sol[S] = count[S]

        return sol


def par_Kst(G, s, t, j):
    B = dict()
    for i in G.nodes():
        B[i] = set(G[i])

    sol = par_apriori(B, set(B.keys()), s, t, j)

    community = set()
    for S in sol.keys():
        community.add(S | sol[S])

    return community


# TO HANDLE LARGE GRAPHS: SAMPLE ONLY A FRACTION p OF BASKETS (NODES) AND FINDS SETS OF t BASKETS THAT CONTAINS AT LEAST ps ITEMS

# EXERCISE: Implement parallel versions of algorithms to find strongly connected components (see above), to count the number of triangles (previous lesson), to count/approximate the diameter (previous lesson)

###############################################

if __name__ == '__main__':

    G = nx.DiGraph()
    G.add_edge(1, 2)
    G.add_edge(2, 3)
    G.add_edge(2, 4)
    G.add_edge(2, 5)
    G.add_edge(3, 6)
    G.add_edge(4, 5)
    G.add_edge(4, 7)
    G.add_edge(5, 2)
    G.add_edge(5, 7)
    G.add_edge(6, 3)
    G.add_edge(6, 8)
    G.add_edge(7, 8)
    G.add_edge(7, 10)
    G.add_edge(8, 7)
    G.add_edge(9, 7)
    G.add_edge(10, 9)
    G.add_edge(10, 11)
    G.add_edge(11, 12)
    G.add_edge(12, 10)
    print "strongly:"
    print(strongly(G))
    print "\nstrongly2"
    print(strongly2(G))

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
    print "\ncliques:"
    print(list(nx.find_cliques(G)))
    print(Kst(G, 1, 3))
    print(Kst(G, 2, 2))
    print(Kst(G, 2, 3))
    print(par_Kst(G, 1, 3, 2))
    print(par_Kst(G, 2, 2, 2))
    print(par_Kst(G, 2, 3, 2))