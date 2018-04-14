#!/usr/bin/python

import networkx as nx
import math
import itertools as it


# DIAMETER
# Classical algorithm: if uses a BFS
# It is has computational complexity O(n*m)
# It require to keep in memory the full set of nodes (it may huge)
def diameter(G):
    n = len(G.nodes())
    diam = 0

    for u in G.nodes():
        udiam = 0
        # clevel contains the nodes reachable from u with paths of length udiam
        clevel = [u]
        visited = set(u)
        while len(visited) < n:
            # nlevel contains the nodes reachable from u with paths of length udiam+1
            nlevel = []
            while (len(clevel) > 0):
                c = clevel.pop(0)
                for v in G[c]:
                    if v not in visited:
                        visited.add(v)
                        nlevel.append(v)
            clevel = nlevel
            udiam += 1
        if udiam > diam:
            diam = udiam

    return diam


# This algorithm only returns an approximation of the diameter.
# It explores all edges multiple times for a number of steps that is approximately the diameter of the graph.
# Thus, it has computational complexity O(diam*m), that is usually much faster than the complexity of previous algorithm.
#
# The algorithm need to keep in memory a number for each node.
# There is a version of the algorithm that reduce the amount of used memory.
# It does not save the degree (that may be a large number), but uses hash functions and it is able to save few bits for each vertex.
def stream_diam(G):
    # At the beginning, R contains for each vertex v the number of nodes that can be reached from v in one step
    R = {v: G.degree(v) for v in G.nodes()}

    step = 0
    done = False
    while not done:
        step += 1
        done = True
        for edge in G.edges():
            # At the i-th iteration, we want that R contains for each vertex v an approximation of the number of nodes that can be reached from v in i+1 steps
            # If there is edge (u,v), then v can reach in i+1 steps at least the number of nodes that u can reach in i steps
            if R[edge[0]] != R[edge[1]]:
                R[edge[0]] = max(R[edge[0]], R[edge[1]])
                R[edge[1]] = max(R[edge[0]], R[edge[1]])  # This line must be removed in a directed graph
                done = False

    return step


# Exercise: modify above algorithm in order to compute an approximation of the number of nodes that a given node v can visit in at most t steps

# TRIANGLES
# Classical algorithm
# The problems of this algorithm are twofold:
# - The same triangle is counted multiple times (six times)
# - For each node, it requires to visit its neighborhood twice (and the neighborhood can be large)
def triangles(G):
    triangles = 0

    for u in G.nodes():
        for v in G[u]:
            for w in G[u]:
                if w in G[v]:
                    triangles += 1

    return int(triangles / 6)


# Optimized algorithm
# There are two optimizations.
#
# OPTIMIZATION1: It consider an order among nodes. Specifically, nodes are ordered by degree. In case of nodes with the same degree, nodes are ordered by label.
def less(G, edge):
    if G.degree(edge[0]) < G.degree(edge[1]):
        return 0
    if G.degree(edge[0]) == G.degree(edge[1]) and edge[0] < edge[1]:
        return 0
    return 1


# OPTIMIZATION2: It distinguishes between high-degree nodes (called heavy hitters) and low-degree nodes.
def num_triangles(G):
    m = nx.number_of_edges(G)
    num_triangles = 0

    # The set of heavy hitters, that is nodes with degree at least sqrt(m)
    # Note: the set contains at most sqrt(m) nodes.
    heavy_hitters = set()
    for u in G.nodes():
        if G.degree(u) >= math.sqrt(m):
            heavy_hitters.add(u)

    # Number of triangles among heavy hitters.
    # It considers all possible triples of heavy hitters.
    # Hence, the complexity is O(sqrt(m)^3)
    for triple in it.combinations(heavy_hitters, 3):
        if G.has_edge(triple[0], triple[1]) and G.has_edge(triple[0], triple[2]) and G.has_edge(triple[1], triple[2]):
            num_triangles += 1

    # Number of remaining triangles.
    # For each edge, if one of the endpoints is not an heavy hitter, verifies if there is a node in its neighborhood that forms a triangle with the other endpoint.
    # Since the size of the neighborhood of a non heavy hitter is at most sqrt(m), the complexity is O(m*sqrt(m)) = O(sqrt(m)^3)
    for edge in G.edges():  # They are m
        sel = less(G, edge)
        if edge[
            sel] not in heavy_hitters:  # If the minimum among the endpoint is an heavy hitter, then also the other endpoint is an heavy hitter
            for i in G[edge[sel]]:  # They are less than sqrt(m)
                if less(G, [i, edge[1 - sel]]) and G.has_edge(i, edge[
                    1 - sel]):  # In this way we count the triangle only once
                    num_triangles += 1

    return num_triangles

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
    print(diameter(G))
    print(stream_diam(G))
    print(triangles(G))
    print(num_triangles(G))

# Exercise: test above algorithms on datasets from
# - SNAP (http://snap.stanford.edu/)
# - KONECT (http://konect.uni-koblenz.de/)