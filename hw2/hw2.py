from ParallelPageRank import pageRank
from util.utility import load_graph
import time
if __name__ == '__main__':
    g = "../graphs/ego-gplus/out.ego-gplus"
    graph = load_graph(g,True)
    print("n nodes: \t"+str(graph.number_of_nodes())+"\tn edges: \t"+str(graph.number_of_edges()))
    start = time.time()
    rank = pageRank(graph)
    stop = time.time() - start
    print("time:\t "+str(stop))