import math
import numpy

import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
from Esercitazioni.esercitazione_6.NetworksModel1 import *
from Esercitazioni.esercitazione_6.NetworksModel2 import *

def degree_distribution_plot(g):
    nodes = g.number_of_nodes()

    fk = {n: g.degree[n] for n in g.nodes()}
    f_nodes = sorted(fk.values())
    degrees = Counter(f_nodes)
    x = [ n/nodes for n in sorted(set(f_nodes))]
    y = [degrees[n] for n in sorted(set(f_nodes))]
    fig, ax = plt.subplots()
    ax.plot(x, y,'o-')
    ax.set(xlabel='fraction of nodes', ylabel='degree',
           title='degree distribution')
    ax.grid()

    plt.show()

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


if __name__ == '__main__':

    paths = [
        "./net_3",
        "../graphs/ego-gplus/out.ego-gplus",
        "../graphs/data_fb/348.edges"
             ]
    #G = nx.read_adjlist(paths[1])
    #G = randomG(5000, 0.5)
    deg_list = power_law_degree(2500, 2)
    G = configurationG(deg_list)
    degree_distribution_plot(G)
    power_law_plot(G)
