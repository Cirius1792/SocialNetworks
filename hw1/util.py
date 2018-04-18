
import networkx as nx
import math
import itertools as it
from joblib import Parallel, delayed
import time
from scipy.sparse import linalg

from copy import deepcopy

def load_graph(filename, directed=False):
    if directed:
        graph = nx.DiGraph()
    else:
        graph = nx.Graph()

    f = open(filename, 'r')
    if f is not None:
        for line in f:
            if len(line)>1 and line[0] != '%' and line[0] != '#':
                edges = line.split()
                source = (edges[0].strip())
                destination = (edges[1].strip())
                graph.add_edge(source, destination)
    else:
        print("Impossibile aprire il file richiesto!")

    return graph


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
            # At the i-th iteration, we want that R contains for each vertex v an approximation of the number of nodes
            # that can be reached from v in i+1 steps If there is edge (u,v), then v can reach in i+1 steps at least the
            # number of nodes that u can reach in i steps
            if R[edge[0]] != R[edge[1]]:
                R[edge[0]] = max(R[edge[0]], R[edge[1]])
                if type(G) is nx.Graph:
                    R[edge[1]] = max(R[edge[0]], R[edge[1]])
                done = False

    return step


def diam_approximation(G):
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
                if type(G) is nx.Graph:
                    R[edge[1]] = max(R[edge[0]], R[edge[1]])
                done = False

    return step


def less(G, edge):
    if G.degree(edge[0]) < G.degree(edge[1]):
        return 0
    if G.degree(edge[0]) == G.degree(edge[1]) and edge[0] < edge[1]:
        return 0
    return 1


# OPTIMIZATION2: It distinguishes between high-degree nodes (called heavy hitters) and low-degree nodes.
def num_triangles(Gr):
    if type(Gr) is nx.DiGraph:
        G = nx.Graph(Gr)
    else:
        G = Gr
    m = nx.number_of_edges(G)
    rad_m = math.sqrt(m)/2
    num_triangles = 0

    # The set of heavy hitters, that is nodes with degree at least sqrt(m)
    # Note: the set contains at most sqrt(m) nodes.
    heavy_hitters = set()
    for u in G.nodes():
        if G.degree(u) >= rad_m:
            heavy_hitters.add(u)

    # Number of triangles among heavy hitters.
    for triple in it.combinations(heavy_hitters, 3):
        if G.has_edge(triple[0], triple[1]) and G.has_edge(triple[0], triple[2]) and G.has_edge(triple[1], triple[2]):
            num_triangles += 1

    # Number of remaining triangles.
    for edge in G.edges():                  # They are m
        sel = less(G, edge)
        if edge[sel] not in heavy_hitters:  # If the minimum among the endpoint is an heavy hitter,
                                            # then also the other endpoint is an heavy hitter
            for i in G[edge[sel]]:          # They are less than sqrt(m)
                if less(G, [i, edge[1 - sel]]) and G.has_edge(i, edge[
                    1 - sel]):              # In this way we count the triangle only once
                    num_triangles += 1

    return num_triangles


def heavy_triangle(triples, G):
    num_triangles = 0
    # print "Triples: "+str(triples)
    t = time.time()
    for triple in triples:
        if G.has_edge(triple[0], triple[1]) and G.has_edge(triple[0], triple[2]) and G.has_edge(triple[1],
                                                                                                triple[2]):
            num_triangles += 1
    #print("Ho sprecato:", time.time()-t)
    return num_triangles

def heavy_2(triples, G, ret, i):
    ret[i] = heavy_triangle(triples, G)

def light_2(edges, G, heavy_hitters, ret,i):
    ret[i] = light_triangle(edges, G, heavy_hitters)

def light_triangle(edges, G, heavy_hitters):
    num_triangles = 0
    for edge in edges:  # They are m
        sel = less(G, edge)
        if edge[sel] not in heavy_hitters:
            for i in G[edge[sel]]:
                if less(G, [i, edge[1 - sel]]) and G.has_edge(i, edge[1 - sel]):
                    num_triangles += 1
    return num_triangles
#
# def par2_trn(G,j):
#     m = nx.number_of_edges(G)
#     rad_m = math.sqrt(m) / 2
#     # The set of heavy hitters
#     start = time.time()
#     heavy_hitters = set()
#     for u in G.nodes():
#         if G.degree(u) >= rad_m:
#             heavy_hitters.add(u)
#     print ("num ht: \t" + str(len(heavy_hitters)))
#     ht = [[] for k in range(0, j)]
#     i = 0
#     for triple in it.combinations(heavy_hitters, 3):
#         ht[i % j].append(triple)
#         i += 1
#     subgraph_1 = G.subgraph(heavy_hitters)
#     edges = [[] for k in range(0, j)]
#     stop = time.time() - start
#     # print"prep: \t"+str(stop)
#     i = 0
#     for edge in G.edges():
#         edges[i % j].append(edge)
#         i += 1
#
#     #Parallelizzazione
#     ret_h = [None for i in range(0,j)]
#     ret_l = [None for i in range(0,j)]
#     start = time.time()
#     for i in range(0,j):
#         heavy_res = thread.start_new_thread((heavy_2),(ht[i], subgraph_1.copy(), ret_h,i))
#     ready = False
#     while not ready:
#         kk = 0
#         for i in range(0,j):
#             if ret_h[i] is not None:
#                 kk +=1
#         ready = kk == j
#     stop = time.time() - start
#     h_trn = sum(ret_h)
#     print "\th_trn: " + str(h_trn) + "\t t: " + str(stop)
#     # Number of remaining triangles.
#     start = time.time()
#     for i in range(0, j):
#         light_res = thread.start_new_thread((light_2),(edges[i][:], G, heavy_hitters.copy(),ret_l,i) )
#     ready = False
#     while not ready:
#         kk = 0
#         for i in range(0, j):
#             if ret_l[i] is not None:
#                 kk += 1
#         ready = kk == j
#     stop = time.time() - start
#     l_trn = sum(ret_l)
#     print "\tl_trn: " + str(l_trn) + "\t t: " + str(stop)
#     return l_trn + h_trn


def par_triangles(G, j):
    m = nx.number_of_edges(G)
    rad_m = math.sqrt(m)/2
    #rad_m = math.sqrt(m)
    # The set of heavy hitters
    start = time.time()
    heavy_hitters = set()
    for u in G.nodes():
        if G.degree(u) >= rad_m:
            heavy_hitters.add(u)
    print ("num ht: \t"+str(len(heavy_hitters)))
    ht = [[] for k in range(0,j)]
    i = 0
    for triple in it.combinations(heavy_hitters, 3):
        ht[i%j].append(triple)
        i += 1
    subgraph_1 = G.subgraph(heavy_hitters)
    edges = [[] for k in range(0, j)]
    stop = time.time() - start
    #print"prep: \t"+str(stop)
    i = 0
    for edge in G.edges():
        edges[i % j].append(edge)
        i += 1

    with Parallel(n_jobs=j) as parallel:
        # Number of triangles among heavy hitters.
        start = time.time()
        heavy_res = parallel(delayed(heavy_triangle)(triples, subgraph_1.copy()) for triples in ht)
        stop = time.time() - start
        h_trn = sum(heavy_res)
        print ("\th_trn: "+str(h_trn)+"\t t: "+str(stop))
        # Number of remaining triangles.
        start = time.time()
        light_res = parallel(delayed(light_triangle)(edges[i], G.copy(as_view=True), heavy_hitters.copy()) for i in range(0,j))
        stop = time.time()-start
        l_trn = sum(light_res)
        print ("\tl_trn: "+str(l_trn)+"\t t: "+str(stop))
    num_triangles = h_trn + l_trn

    return num_triangles


def par_SCC(G, j=4):
    graph = G.copy()
    comp = dict()

    done = False
    if type(graph) is nx.DiGraph:
        igraph = graph.reverse(False)
    else:
        igraph = graph
    gr = [graph, igraph]
    node_lists = [[] for i in range(0,j)]
    i = 0
    for node in graph:
        node_lists[i%j].append(node)
        i +=1

    with Parallel(n_jobs=j) as parallel:
        while not done:
            changed = False

    components = []
    # Each node left in the graph corresponds to a component
    for u in graph:
        if u in comp.keys():
            components.append(comp[u])
        else:
            components.append({u})

    return components

def BFS(node, graph):
    visited = set()
    queue = [node]
    while len(queue) > 0:
        u = queue.pop()
        for v in graph[u]:
            if v not in visited:
                queue.append(v)
        visited.add(u)
    return visited

def strongly2(G):
    graph = G.copy()
    comp = dict()

    done = False
    if type(graph) is nx.DiGraph:
        igraph = graph.reverse(False)
    else:
        igraph = graph
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

def spectral(G):
    n = G.number_of_nodes()
    nodes = sorted(G.nodes())
    # Laplacian of a graph is a matrix, with diagonal entries being the degree of the corresponding node and
    # off-diagonal entries being -1 if an edge between the corresponding nodes exists and 0 otherwise
    L = nx.laplacian_matrix(G,nodes).asfptype() # asfptype() convertes the laplacian matrix as returned by networkx to
                                                # a sparse matrix as managed by scipy
    # Compute eigenvalues and eigenvectors of the Laplacian matrix
    w, v = linalg.eigsh(L,n - 1)  # the first input is the array of eigenvalues in increasing order. The second output
                                  # contains eigenvectors: specifically, the eigenvector of the k-th eigenvalue is given
                                  #by the k-th entry of each of the n vectors contained in v

    # Partition in clusters based on the corresponding eigenvector value being positive or negative
    cluster0 = set()
    cluster1 = set()
    for i in range(n):
        if v[i, 0] < 0:
            cluster0.add(nodes[i])
        else:
            cluster1.add(nodes[i])
    return(cluster0, cluster1)