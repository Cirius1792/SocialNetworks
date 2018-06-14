import math
import time

import numpy

import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
from Esercitazioni.esercitazione_6.NetworksModel1 import *
from Esercitazioni.esercitazione_6.NetworksModel2 import *
from os.path import isfile, join
from joblib import Parallel, delayed
from os import listdir
from Project.OptNetworkModels import *
from Project.task_3 import find_weak_ties

#CONSTANTS
stats_path = "statistics/"



def degree_distribution_plot(g, title="degree distribution", save=False):
    nodes = g.number_of_nodes()

    fk = {n: g.degree[n] for n in g.nodes()}
    f_nodes = sorted(fk.values())
    degrees = Counter(f_nodes)
    x = [ n/nodes for n in sorted(set(f_nodes))]
    y = [degrees[n] for n in sorted(set(f_nodes))]
    fig, ax = plt.subplots()
    ax.plot(x, y,'o-')
    ax.set(xlabel='fraction of nodes', ylabel='degree',
           title=title)
    ax.grid()
    if save:
        fig.savefig(stats_path+title.strip()+".png")
    plt.show()
    plt.pause(0.5)

def degree_bar_diagram(g, title="degree distribution", save=False):
    nodes = g.number_of_nodes()
    fk = {n: g.degree[n] for n in g.nodes()}
    max_deg = max(fk.values())
    bin = {i:0 for i in range(101)}
    step = max_deg/100.0

    for n in g.nodes():
        bin[int((100.0*g.degree[n])/max_deg)] += 1
    print( bin)
    fig, ax = plt.subplots()
    dist = []
    for key in sorted(bin.keys()):
        dist.append(bin[key])
    print(dist)
    plt.bar(np.arange(101),dist)
    plt.xticks(np.arange(100,step=10),[int(max_deg*x/50) for x in np.arange(100,step=10)])
    plt.show()

def avg_degree(G):
    degs = [G.degree[n] for n in G.nodes()]
    return numpy.mean(degs)

def build_test_graph():
    base_path = "./WSGrid25000_r5_k6/"

    n = 2500
    p = 0.5

    r = 5
    k = 6
    print("Generating WS Grid")
    f = open(base_path+"WSGrid_"+str(n)+"_r"+str(r)+"_k"+str(k)+".txt",'w')
    G = WSGridG_opt(n,r,k, file=f)


def statistics(base_path):
    files = [f for f in listdir(base_path) if isfile(join(base_path, f))]
    for f in files:
        print(f)
        G = nx.read_edgelist(base_path+f)
        print("\tNodes: " + str(G.number_of_nodes()))
        print("\tEdges: " + str(G.number_of_edges()))
        print("\tGrado medio: \t" + str(avg_degree(G)))
        if avg_degree(G) <100:
            print("\tClustering: \t"+str(nx.average_clustering(G)))
            degree_distribution_plot(G,title=f,save=True)
        print("\n")

def par_eval_stats(base_path):
    files = [f for f in listdir(base_path) if isfile(join(base_path, f))]
    with Parallel (n_jobs=2) as parallel:
        res = parallel(delayed(_eval_stat)(base_path,f) for f in files)
        for out in res:
            print(out)

def _eval_stat(base_path, f):
    out = ""
    out += f+"\n"
    G = nx.read_edgelist(base_path + f)
    out += ("\tNodes: " + str(G.number_of_nodes())+"\n")
    out +=("\tEdges: " + str(G.number_of_edges())+"\n")
    out +=("\tGrado medio: \t" + str(avg_degree(G))+"\n")
    out +=("\tWeak Ties: \t"+"{0:.2f}".format(len(find_weak_ties(G))/G.number_of_edges())+"\n")
    #if avg_degree(G) < 100:
    out +=("\tClustering: \t" + str(nx.average_clustering(G))+"\n")
    #degree_distribution_plot(G, title=f, save=False)
    out+= ("\n")
    #print(out)
    return out

def proof():

    n = 25000
    #ps = [0.003547,0.004547, 0.002547 ]
    ps = [5+k  for k in range(5)]
    k = [k for k in range(3,10)]
    with Parallel (n_jobs=3) as parallel:
        for j in range(len(k)):
            res = parallel(delayed(_sub_proof) (n,ps[i],k[j]) for i in range(len(ps)))

    print("done!")
    print("\nEvaluating statistics...")
    par_eval_stats("./proof_networks2/")


def _sub_proof(n, r, k):
    # RANDOM GRAPH
    # base_path = "./proof_networks/"
    # file = open(base_path + "random_test_"+str(i)+".txt",'w')
    # file.write("#n = " + str(n) + "\n")
    # file.write("#p = " + str(p) + "\n")
    # G = randomG_opt(n, p, file)
    # file.close()


    base_path = "./proof_networks2/"
    file = open(base_path + "WS2DG_test_" +"r" + str(r) + "_k" + str(k) + ".txt", 'w')
    file.write("#n = " + str(n) + "\n")
    file.write("#r = " + str(r) + "\n")
    file.write("#k = " + str(k) + "\n")
    G = WS2DG_opt(n, r, k, file=file)
    file.close()


def test1():
    paths = [
        "./net_3",
        "../graphs/ego-gplus/out.ego-gplus",
        "../graphs/data_fb/348.edges",
        "network_random_25000_0.4.txt"
    ]
    G = nx.read_edgelist(paths[0])
    print("\tNodes: " + str(G.number_of_nodes()))
    print("\tEdges: " + str(G.number_of_edges()))
    # print("Building Model...")
    # n = 25000
    # p = 2.0/5.0
    # print("\tn = "+str(n)+"\t\tp = "+str(p) )
    # G = randomG_opt(n, p)
    # print("Saving Model...")
    # nx.write_adjlist(G,"network_"+"random_"+str(n)+"_"+str(p)+".txt")
    # deg_list = power_law_degree(2500, 2)
    # G = configurationG(deg_list)
    # degree_distribution_plot(G)
    # power_law_plot(G)

    print("Grado medio: \t" + str(avg_degree(G)))
    print("Diametro: " + str(nx.diameter(G)))


def testnn():
    path = "./net_3"
    g = nx.read_edgelist(path,create_using=nx.DiGraph())
    degree_bar_diagram(g)

if __name__ == '__main__':
    par_eval_stats("./WS2DGrid5000_r5_k6/")
    #proof()
    #build_test_graph()
    #testnn()