
# Stampare i top 50 nodi secondo tutte le misure di centrality implementate (degree, closeness, page_rank, hits,
# shapley_degree, shapley_treshold, shapley_closeness, shapley_betweennes, owen**, myerson) relativamente ai grafi
# usati nel primo homework.
import time

from ..esercitazione_4.Centrality import *
from ..esercitazione_4.CentralityGT import *
from ..util.utility import load_graph
from .SVBetweennes import ShapleyBetweennes

graph_paths = [{"../graphs/Brightkite/Brightkite_edges.txt": False},
               {"../graphs/CA-AstroPh.txt": False},
               {"../graphs/ego-gplus/out.ego-gplus": True}]

functions = [{"Degree Centrality": degree},
             {"Closeness Centrality": closeness},
             {"Betweennes Centrality": betweenness},
             {"Pagerank": pageRank},
             {"Hits": hits},
             {"Shapley Degree": shapley_degree},
             {"Shapley Threshold": shapley_threshold},
             {"Shapley Closeness": shapley_closeness},
             {"Myerson": myerson},
             {"Shapley Betweennes": ShapleyBetweennes}]

if __name__ == '__main__':
    fout = open("stats_top50.txt", 'w')
    for g in graph_paths:
        G = load_graph(g,graph_paths[g])
        fout.write("Graph:\t")
        fout.write(g)
        fout.write("\n")
        for func_name in functions:
            start = time.time()
            out = top(G,functions[func_name],50)
            stop = time.time()-start
            fout.write(func_name+"\t\tt: \t"+str(stop) + "\n")
            fout.write(out)
            fout.write("\n")
        fout.write("########################################################################\n")
        fout.write("########################################################################\n")
        fout.write("\n\n")
    fout.close()

