import networkx as nx


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
                source = (int(edges[0].strip()))
                destination = (int(edges[1].strip()))
                graph.add_edge(source, destination)
    else:
        print("Impossibile aprire il file richiesto!")

    return graph

#Returns the top k nodes of G according to the centrality measure "measure"
def top(G,measure,k):
    pq=measure(G)
    out=[]
    for i in range(k):
        res,pr = pq.pop(with_priority=True)
        out.append(res)
    return out

def top_tostring(G,measure,k):
    pq=measure(G)
    out=[]
    for i in range(k):
        res,pr = pq.pop(with_priority=True)
        out.append("("+str(res)+","+"{0:.3f}".format(pr)+")")
    return out
