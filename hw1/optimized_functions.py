
import networkx as nx
import math
import itertools as it
from joblib import Parallel, delayed
import time
import random


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


def less(G, edge):
    if G.degree(edge[0]) < G.degree(edge[1]):
        return 0
    if G.degree(edge[0]) == G.degree(edge[1]) and edge[0] < edge[1]:
        return 0
    return 1


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
    """funzione di supporto che controlla l'esistenza di triangoli fra gli Heavy Hitters"""
    num_triangles = 0
    t = time.time()
    for triple in triples:
        if G.has_edge(triple[0], triple[1]) and G.has_edge(triple[0], triple[2]) and G.has_edge(triple[1],
                                                                                                triple[2]):
            num_triangles += 1
    return num_triangles


def light_triangle(edges, G, heavy_hitters):
    """funzione di supprto che controlla l'esistenza di triangoli fra i nodi"""
    num_triangles = 0
    for edge in edges:  # They are m
        sel = less(G, edge)
        if edge[sel] not in heavy_hitters:
            for i in G[edge[sel]]:
                if less(G, [i, edge[1 - sel]]) and G.has_edge(i, edge[1 - sel]):
                    num_triangles += 1
    return num_triangles



def par_triangles(G, j):
    """Ottimizza le operazioni per l'esecuzione parallela dividendo le triple di heavy hitters e gli edge tra non heavy hitters
    in tanti set quanti sono i workers da utilizzare"""
    if type(G) is nx.DiGraph:
        Gr = nx.Graph(G)
    else:
        Gr = G

    m = nx.number_of_edges(Gr)
    #In seguito all'osservazione della struttura dei grafi è stato possibile osservare che il numero di nodi con
    #almeno sqrt(m) edge erano decisamente pochi rispetto al numero complessivo di noi, per aumentare la paralleleizzazione
    #dell'algoritmo si è deciso di diminuire la soglia entro la quale considerare un nodo heavy hitters
    rad_m = math.sqrt(m)/2
    # The set of heavy hitters
    start = time.time()
    heavy_hitters = set()
    for u in Gr.nodes():
        if Gr.degree(u) >= rad_m:
            heavy_hitters.add(u)
    #print ("num ht: \t"+str(len(heavy_hitters)))
    ht = [[] for k in range(0,j)]
    i = 0
    #creo una lista di triple per ogni worker
    for triple in it.combinations(heavy_hitters, 3):
        ht[i%j].append(triple)
        i += 1
    #creo un sottografo contenente solo gli heavy hitters per alleggerire il passaggio di dati ai worker
    subgraph_1 = Gr.subgraph(heavy_hitters)
    edges = [[] for k in range(0, j)]
    stop = time.time() - start
    i = 0
    #creo una lista di edge per ogni worker
    for edge in Gr.edges():
        edges[i % j].append(edge)
        i += 1

    with Parallel(n_jobs=j) as parallel:
        #Prima parallelizzo la ricerca dei triangoli fra heavy hitters e poi riutilizzo gli stessi worker per la parallelizzazione
        #della ricerca dei restanti triangoli
        #Triangoli fra Heavy Hitters
        start = time.time()
        heavy_res = parallel(delayed(heavy_triangle)(triples, subgraph_1.copy(as_view=True)) for triples in ht)
        stop = time.time() - start
        h_trn = sum(heavy_res)
        #print ("\th_trn: "+str(h_trn)+"\t t: "+str(stop))
        start = time.time()
        #Triangoli Rimanenti
        light_res = parallel(delayed(light_triangle)(edges[i], Gr.copy(as_view=True), heavy_hitters.copy()) for i in range(0, j))
        stop = time.time()-start
        l_trn = sum(light_res)
        #print ("\tl_trn: "+str(l_trn)+"\t t: "+str(stop))
    num_triangles = h_trn + l_trn

    return num_triangles


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


def SCC_p(G, p=1):
    """Trova le componenti connesse di un grafo. Il parametro p permette di scegliere
    quanta parte del grafo utilizare per la ricerca. Solo i p percento dei nodi verranno considerati, invece che tutti."""
    graph = G.copy()
    comp = dict()

    done = False

    while not done:
        changed = False
        # For each node left in the graph
        for node in graph.nodes():
            #(1-p) equivale alla probabiltià che un nodo venga considerato o meno
            q = random.random()
            if q > (1-p):
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
                if type(graph) is nx.DiGraph:
                    igraph = graph.reverse(False)
                else:
                    igraph = graph
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
