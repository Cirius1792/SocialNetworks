
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


def SCC_2(G):
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
                for n in comp[node]:
                    graph.remove_node(n)
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