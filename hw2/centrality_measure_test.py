
# Stampare i top 50 nodi secondo tutte le misure di centrality implementate (degree, closeness, page_rank, hits,
# shapley_degree, shapley_treshold, shapley_closeness, shapley_betweennes, owen**, myerson) relativamente ai grafi
# usati nel primo homework.
import time
#http://snap.stanford.edu/data/as-caida.html
# Betweennes Centrality		 t: 	5504.773956775665
# [41060, 39242, 28942, 34541, 39324, 43098, 15950, 12384, 38956, 13243, 28726, 25475, 13177, 11619, 21902, 32461, 1347, 32664, 23359, 19039, 32110, 36784, 40328, 14738, 23465, 42368, 42517, 31922, 35097, 38720, 12798, 2634, 26197, 39940, 11931, 32401, 25816, 19674, 20145, 6260, 4017, 22704, 13957, 26727, 32185, 13334, 15152, 15356, 16670, 36636]

from esercitazione_4.Centrality import *
from esercitazione_4.CentralityGT import *
from util.utility import load_graph
from SVBetweennes import ShapleyBetweennes
from hw1.optimized_functions import strongly2

graph_paths = {#"../graphs/Brightkite/Brightkite_edges.txt": False,
                "../graphs/as-caida2007/as-caida20071105.txt":False,
                "../graphs/CA-AstroPh.txt": False,
                "../graphs/ego-gplus/out.ego-gplus": True}
#
# functions = {"Degree Centrality": degree,
#              "Closeness Centrality": closeness,
#              #"Betweennes Centrality": nx.betweenness_centrality,
#              "Pagerank": pageRank,
#              "Hits": hits,
#              "Shapley Degree": shapley_degree,
#              "Shapley Threshold": shapley_threshold,
#              #"Shapley Closeness": shapley_closeness,
#              "Myerson": myerson,
#              #"Shapley Betweennes": ShapleyBetweennes
#              }

functions = {
#              "Myerson": myerson,
#              #"Shapley Betweennes": ShapleyBetweennes
             "Shapley Closeness": shapley_closeness

              }


def get_stats():
    cnt = 0
    for g in graph_paths:
        fout = open("g"+str(cnt)+"_stats_top50.txt", 'w')
        cnt += 1
        G = load_graph(g, graph_paths[g])
        print("Graph:\t" + g)
        fout.write("Graph:\t")
        fout.write(g)
        fout.write("\n")
        print("\n")
        # ssc = strongly2(G)
        # max = ssc[0]
        # for s in ssc:
        #     if len(s)> len(max):
        #         max = s
        # G = G.subgraph(max)
        for func_name in functions:
            start = time.time()
            print("\r"+func_name, end="")
            try:
                out = top(G, functions[func_name], 50)
                stop = time.time() - start
                fout.write(func_name + "\t\tt: \t" + str(stop) + "\n")
                print("\t\t t: \t" + str(stop))
                fout.write(str(out))
                print(str(out))
                fout.write("\n")
            except:
                print("impossibile calcolare: \t"+func_name)
            fout.write("########################################################################\n")
        #fout.write("########################################################################\n")
        print("########################################################################\n")
        print("########################################################################\n")
        fout.write("\n\n")
        fout.close()


if __name__ == '__main__':
    get_stats()

