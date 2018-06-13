import math
import time
from operator import itemgetter, attrgetter
from statistics import mean, stdev
from joblib import Parallel, delayed

import networkx as nx
from util.priorityq import PriorityQueue
from Project.BSDM import *
from Esercitazioni.esercitazione_4.CentralityGT import *
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.mlab as mlab
import itertools as it

def random_seed1(g):
    seeds = {random.choice(list(g.nodes())) for i in range(int(g.number_of_nodes() / 10))}
    return seeds

def random_monitor(g, seed1):
    monitor = set()
    while len(monitor) < g.number_of_nodes()/4:
        node = random.choice(list(g.nodes()))
        if node not in seed1:
            monitor.add(node)

    return monitor


def random_seed2(g, seed1, monitor):
    seeds= set()
    while len(seeds) < g.number_of_nodes() / 10:
        node = random.choice(list(g.nodes()))
        if node not in seed1 and node not in monitor:
            seeds.add(node)

    return seeds

def overlapping_neighborouds(graph, n1, n2, normalized = True):
    (a,b) = (n1,n2) if len(graph[n1]) > len(graph[n2]) else (n2,n1)
    cnt = 0
    for v in graph[b]:
        cnt += 1 if v in graph[a] else 0
    return cnt/len(graph[a]) if normalized else cnt

def choose_seed_fake2(g, seed_fake1=set(), monitor=set()):
    graph = nx.subgraph(g, set(g.nodes()) - (seed_fake1 | monitor))
    n_nodes = round(g.number_of_nodes() / 10)
    pq = PriorityQueue()
    # btw = nx.betweenness_centrality(graph)
    # for n in btw:
    #     pq.add(n,-btw[n])
    ###Degree
    for n in graph.nodes():
        pq.add(n, -graph.degree[n])
    top = []
    for i in range(int(g.number_of_nodes() / 4)):
        top.append(pq.pop())
    pq = PriorityQueue()
    for n in top:
        overlap = []
        for v in seed_fake1:
            overlap.append(overlapping_neighborouds(g, n, v))
        pq.add(n,mean(overlap)+stdev(overlap))

    seeds = set()
    ######SEMPLICE
    while len(pq) > 0 and len(seeds) < n_nodes:
        seeds.add(pq.pop())

    print(str(len(seeds)/n_nodes))
    return seeds




def choose_seed_fake2_fail(g, seed_fake1=set(), monitor=set()):
    #nodes_degree = [(n,graph.degree[n]) for n in graph.nodes()]
    # sorted_by_degree = sorted(nodes_degree, key=itemgetter(1))
    # print(sorted_by_degree)
    #Non considero i nodi usati come seed o monitor
    graph = nx.subgraph(g, set(g.nodes()) - (seed_fake1 | monitor))
    n_nodes = round(g.number_of_nodes()/10)
    pq = PriorityQueue()
    ###SV Degree
    # measure = shapley_degree(graph)
    # for n in measure:
    #     pq.add(n, -measure[n])
    ###Degree
    for n in graph.nodes():
        pq.add(n, -graph.degree[n])
    top = []
    neigh_sorted = PriorityQueue()
    for i in range(int(g.number_of_nodes()/4)):
        top.append(pq.pop())
    # for n in top:
    #     # L'idea e' quella di prendere come seed i nodi con grado piu' alto i cui vicini hanno grado più basso,
    #     # in questo modo mi assicuro di influenzare un grande numero di nodi facilmente influenzabili
    #     neigh_degree = []
    #     for v in graph[n]:
    #         neigh_degree.append(graph.degree[v])
    #     neigh_sorted.add(n, -mean(neigh_degree)) if len(neigh_degree) > 0 else 0
    # top = []
    # while len(neigh_sorted) > 0:
    #     top.append(neigh_sorted.pop())
    # neigh_sorted = PriorityQueue()
    for tuple in it.combinations(top, 2):
        overlapping = overlapping_neighborouds(graph, tuple[0], tuple[1])
        #if overlapping >= 0.5:
        neigh_sorted.add(tuple,-overlapping)
    # print("nodi con embedness >= 0.5: "+str(len(neigh_sorted)*2))
    seeds = set()
    # ######SEMPLICE
    # while len(neigh_sorted)>0 and len(seeds)< n_nodes:
    #     seeds.add(neigh_sorted.pop())
    ###NUOVA VERSIONE
    while len(neigh_sorted) > 0 and len(seeds) < n_nodes:
        tuple = neigh_sorted.pop()
        seeds.add(tuple[0])
        seeds.add(tuple[1])

    #print(str(len(seeds)/n_nodes))
    return seeds


def get_opinion_stats_bestresponse(g, output=False):
    active = nx.get_node_attributes(g, 'active')
    diffusion = 0
    n_nodes = g.number_of_nodes()
    for i in active:
        diffusion += 1 if g.node[i]['active'] else 0
    diffusion = diffusion/n_nodes
    if output:
        print("opinion 1: "+"{0:.2f}".format(diffusion*100))
    return diffusion

def plot_res(x):
    fig, ax = plt.subplots()
    num_bins = 50
    n, bins, patches = ax.hist(x, num_bins, density=1)
    y = mlab.normpdf(bins, mean(x), stdev(x))
    ax.plot(bins,y)
    fig.tight_layout()
    plt.show()

def par_test_bsdm():
    #path = "./generated_networks/WS2DGrid_0_1000_r5_k6.txt"
    path = "./net3/net_3"
    n_test = 2
    diff_fake1 = []
    diff_fake2 = []
    diff_noop = []
    start = time.time()
    with Parallel(n_jobs=4) as parallel:
        res = parallel(delayed(par_test)(path, n_it=20) for i in range(n_test))
        for i in range(n_test):
            diff_fake1.append(res[i][0])
            diff_fake2.append(res[i][1])
            diff_noop.append(res[i][2])
    stop = time.time() - start
    print("\ntime: "+"{0:.4f}".format(stop))
    print("fake 1:", end="")
    print("\tmean:\t "+"{0:.4f}".format(mean(diff_fake1)))
    print("fake 2:", end="")
    print("\tmean:\t "+"{0:.4f}".format(mean(diff_fake2)))
    print("no op:", end="")
    print("\tmean:\t "+"{0:.4f}".format(mean(diff_noop)))

def par_test(path, n_it = 10):
    g = nx.read_edgelist(path, create_using=nx.Graph())
    diff_fake1 =[]
    diff_fake2 =[]
    diff_noop = []
    seed_f1 = random_seed1(g)
    monitor = random_monitor(g, seed_f1)
    seed_f2 = choose_seed_fake2(g, seed_f1, monitor)
    #seed_f2 = random_seed2(g, seed_f1, monitor)
    for i in range(n_it):
        out = get_opinion_stats(bsdm(g, seed_f1, seed_f2, monitor), output=False)
        g = nx.read_edgelist(path, create_using=nx.Graph())
        diff_fake1.append(out[0] * 100)
        diff_fake2.append(out[1] * 100)
        diff_noop.append(out[2] * 100)
    return [mean(diff_fake1), mean(diff_fake2), mean(diff_noop)]


def test_bsdm():
    path = "./generated_networks/WS2DGrid_0_1000_r5_k6.txt"
    g = nx.read_edgelist(path, create_using=nx.Graph())
    n_it = 9
    diff_fake1 =[]
    diff_fake2 =[]
    diff_noop = []
    start = time.time()
    for i in range(2):
        seed_f1 = random_seed1(g)
        monitor = random_monitor(g, seed_f1)
        seed_f2 = choose_seed_fake2_fail(g, seed_f1, monitor)
        for i in range(10):
            #print("\r" + "{0:.2f}".format(i / n_it * 100), end="")
            out = get_opinion_stats(bsdm(g, seed_f1, seed_f2, monitor),output=False)
            g = nx.read_edgelist(path, create_using=nx.Graph())
            diff_fake1.append(out[0] * 100)
            diff_fake2.append(out[1] * 100)
            diff_noop.append(out[2] * 100)
    stop = time.time()-start
    print("\ntime: "+"{0:.4f}".format(stop))
    #plot_res(res1)
    print("fake1:", end="")
    print("\tmean:\t "+str(mean(diff_fake1)), end="")
    print("\tdev:\t "+str(stdev(diff_fake1)/100))
    print("fake 2:", end="")
    print("\tmean:\t "+str(mean(diff_fake2)), end="")
    print("\tdev:\t "+str(stdev(diff_fake2)/100))

def test_best_response():
    path = "./generated_networks/WS2DGrid_0_1000_r5_k6.txt"
    g = nx.read_edgelist(path, create_using=nx.Graph())
    #seed_f1 = {random.choice(list(g.nodes())) for i in range(int(g.number_of_nodes()/10))}
    #seed_f2 = {random.choice(list(g.nodes())) for i in range(int(g.number_of_nodes()/10))}
    #seed_f1 = choose_seed_fake2(g)
    #monitor = {random.choice(list(g.nodes())) for i in range(int(g.number_of_nodes()/4))}

    n_it = 100
    res =[]
    start = time.time()
    for i in range(n_it):
        print("\r" + "{0:.2f}".format(i / n_it * 100), end="")
        #out2 = get_opinion_stats(bsdm(g, seed_f1, seed_f2, monitor),output=True)
        out = get_opinion_stats_bestresponse(best_resp_seq(g, seed_f1, {}),output=False)
        g = nx.read_edgelist(path, create_using=nx.Graph())
        res.append(out * 100)
    stop = time.time()-start
    print("\ntime: "+"{0:.4f}".format(stop))
    plot_res(res)
    print("mean: "+str(mean(res)))
    print("dev: "+str(stdev(res)/100))




def test0():
    path = "./generated_networks/config_powerlaw_2500_3.txt"
    g = nx.read_edgelist(path, create_using=nx.Graph())
    seed = choose_seed_fake2(g)
    res = []
    res2 = []
    n_it = 100
    start = time.time()
    for i in range(n_it):
        print("\r" + "{0:.2f}".format(i / n_it * 100), end="")
        out = get_opinion_stats(bsdm_recursive(g, seed, {}, seed_f1=seed, seed_f2={}, monitor={}), output=True)
        g = nx.read_edgelist(path, create_using=nx.Graph())
        out2 = get_opinion_stats(bsdm(g, seed, {}, {}), output=True)
        # print(out)
        res.append(out * 100)
        res2.append(out2 * 100)
        g = nx.read_edgelist(path, create_using=nx.Graph())
    stop = time.time() - start
    # print("time: "+"{0:.4f}".format(stop))
    # print("mean: "+str(mean(res)))
    # print("dev: "+str(stdev(res)/100))
    # print("mean: "+str(mean(res2)))
    # print("dev: "+str(stdev(res2)/100))

    plot_res(res)
if __name__ == '__main__':
   par_test_bsdm()
