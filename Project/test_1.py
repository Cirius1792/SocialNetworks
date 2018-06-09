from util.utility import load_graph

if __name__ == '__main__':
    path = "./net_3"
    G = load_graph(path, False)
    print("\t Nodes: \t"+str(G.number_of_nodes()))
    print("\t Edges: \t" + str(G.number_of_edges()))