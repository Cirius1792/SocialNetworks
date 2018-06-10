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
from os import listdir
from os.path import isfile, join
from joblib import Parallel, delayed
from Project.OptNetworkModels import *

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


def power_law_plot(g):
    nodes = g.number_of_nodes()
    nodes_degree = {n: g.degree[n] for n in g.nodes()}
    sorted_degrees = sorted(nodes_degree.values())
    #Creo una mappa in cui, per ogni degree, so quanti nod del grafo hanno quel degree
    degrees = Counter(sorted_degrees)
    fk = [ k/nodes for k in sorted(set(sorted_degrees))] #Frazione di nodi con degree k
    x = [ math.log(f_k) for f_k in fk]
    y = [ math.log(degrees[n]) for n in sorted(set(sorted_degrees))]
    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set(xlabel='number of links', ylabel='degree',
           title='power law')
    ax.grid()
    plt.show()
    plt.pause(0.5)


def avg_degree(G):
    degs = [G.degree[n] for n in G.nodes()]
    return numpy.mean(degs)

def build_test_graph():
    base_path = "./generated_networks/"

    n = 25000
    p = 0.5

    r = 88
    k = 4
    print("Generating WS Grid")
    G = WSGridG(n,r,k)
    nx.write_edgelist(G,base_path+"WSGrid_2500_20_4.txt")

    print("Generating WS C")
    G = WS2DG(n,r,k)
    nx.write_edgelist(G,base_path+"WS2DG_2500_20_4.txt")

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
    with Parallel (n_jobs=4) as parallel:
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
    if avg_degree(G) < 100:
        out +=("\tClustering: \t" + str(nx.average_clustering(G))+"\n")
        degree_distribution_plot(G, title=f, save=True)
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


def _sub_proof(n,p,i):
    # RANDOM GRAPH
    # base_path = "./proof_networks/"
    # file = open(base_path + "random_test_"+str(i)+".txt",'w')
    # file.write("#n = " + str(n) + "\n")
    # file.write("#p = " + str(p) + "\n")
    # G = randomG_opt(n, p, file)
    # file.close()


    base_path = "./proof_networks2/"
    file = open(base_path + "WS2DG_test_"+"r"+str(p)+"_k"+str(i)+".txt",'w')
    file.write("#n = " + str(n) + "\n")
    file.write("#k = " + str(p) + "\n")
    file.write("#i = " + str(i) + "\n")
    G = WS2DG_opt(n,p,i,file=file)
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



if __name__ == '__main__':
    #par_eval_stats("./proof_networks/")
    proof()
