import time
#http://snap.stanford.edu/data/as-caida.html
# Betweennes Centrality		 t: 	5504.773956775665
# [41060, 39242, 28942, 34541, 39324, 43098, 15950, 12384, 38956, 13243, 28726, 25475, 13177, 11619, 21902, 32461, 1347, 32664, 23359, 19039, 32110, 36784, 40328, 14738, 23465, 42368, 42517, 31922, 35097, 38720, 12798, 2634, 26197, 39940, 11931, 32401, 25816, 19674, 20145, 6260, 4017, 22704, 13957, 26727, 32185, 13334, 15152, 15356, 16670, 36636]

from Esercitazioni.esercitazione_4.Centrality import *
from Esercitazioni.esercitazione_4.CentralityGT import *
from util.utility import load_graph

metrics = {"degree": 0, "closeness": 1, "pagerank": 2, "hits": 3, "sdegree": 4, "sthreshold": 5}
#metrics = {"degree": 0, "closeness": 1, "pagerank": 2, "hits": 3, "sdegree": 4, "sthreshold": 5, "sbetweennes": 6}

graph_paths = { "../graphs/as-caida2007/as-caida20071105.txt":False,
                "../graphs/CA-AstroPh.txt": False,
                "../graphs/ego-gplus/out.ego-gplus": True}

functions = {
            "Degree Centrality": degree,
             "Closeness Centrality": closeness,
             #"Betweennes Centrality": nx.betweenness_centrality,
             "Pagerank": pageRank,
             "Hits": hits,
             "Shapley Degree": shapley_degree,
             "Shapley Threshold": shapley_threshold,
             #"Shapley Closeness": shapley_closeness,
             "Myerson": myerson,
             #"Shapley Betweennes": ShapleyBetweennes
             }


def load_SVB(path):
    file = open(path)
    for line in path:
        if line != '\n':
            s = line.split()

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


def compare(a, b):
    cnt = 0
    for el in a:
        cnt +=1 if el in b else 0
    return cnt

def compare_stats1(path):

    cm = [[0 for i in range(len(metrics))] for i in range(len(metrics))]
    values = {i:set() for i in metrics}
    file = open(path,'r')

    for line in file:
        if line != '\n':
            s = line.split(':')
            metric = s[0]
            vals = s[1].split(',')
            cnt = 0
            for val in vals:
                values[metric].add(val.strip())
                cnt += 1
    for i in metrics:
        for j in metrics:
            cm[metrics[i]][metrics[j]] += compare(values[i], values[j])
    return cm

def compare_stats(path):
    cm = [[0 for i in range(len(metrics))] for i in range(len(metrics))]
    values = {i:set() for i in metrics}
    file = open(path,'r')

    for line in file:
        if line != '\n':
            s = line.split(':')
            metric = s[0]
            vals = s[1].split(',')
            cnt = 0
            for val in vals:
                values[metric].add(val.strip())
                cnt += 1
    for i in metrics:
        for j in metrics:
            cm[metrics[i]][metrics[j]] += compare(values[i], values[j])
    return cm

def print_cm(cm):
    out = "\t"
    m = 0
    for label in metrics:
        out += str(metrics[label])+"\t "
    out += "\n"
    for row in metrics:
        #out += row+" \t\t\t  " #if len(row)> m/2 else row+" \t\t\t\t  "
        out += str(metrics[row])+"\t"
        for column in metrics:
            out += str(cm[metrics[row]][metrics[column]])+"\t"
        out += "\n"
    for label in metrics:
        out += str(metrics[label])+":"+label+"\n"
    print(out)
    return out


def eval_stats():
    res = ["as-caida20071105.txt", "AstroPh.txt", "gplus.txt"]
    for r in res:
        print(r)
        cm = compare_stats("./results/" + r)
        print_cm(cm)


if __name__ == '__main__':
    get_stats()
    #I file devono essere prima preparati per l'analisi
    eval_stats()


