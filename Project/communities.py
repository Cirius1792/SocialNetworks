import time
from joblib import Parallel, delayed
from os import listdir
import networkx as nx
from networkx.algorithms import community
from os.path import isfile, join
import matplotlib.pyplot as plt


base_path = "./WS2DGrid5000_r5_k6/"


def _eval_net(filename):
    g = nx.read_edgelist(base_path + filename, create_using=nx.Graph())
    f = open(filename + "_communities.txt", 'w')
    start = time.time()
    coms = community.asyn_lpa_communities(g)
    stop = time.time()-start
    print(filename + "\n\ttime: " + "{0:.4f}".format(stop))
    #print("communities founded: "+str(len(coms)))
    for com in coms:
        out = ""
        for i in com:
            out += str(i)+", "
        out +="\n"
    f.write(out)
    f.close()


def save_com():
    files = [f for f in listdir(base_path) if isfile(join(base_path, f))]
    with Parallel (n_jobs=4) as parallel:
        res = parallel(delayed(_eval_net)(f) for f in files)
    print("Done!")
def test():
    path = "./generated_networks/WS2DGrid_0_5000_r5_k6.txt"
    #g = nx.read_edgelist(path, create_using=nx.Graph())
    g = nx.Graph()
    g.add_edge(1,2)
    g.add_edge(1,3)
    g.add_edge(2,3)
    g.add_edge(2,5)
    g.add_edge(3,4)
    g.add_edge(4,5)
    g.add_edge(4,7)
    g.add_edge(5,6)
    g.add_edge(6,7)
    g.add_edge(7,8)
    g.add_edge(8,6)
    print(path)
    print("\tNodes: " + str(g.number_of_nodes()))
    print("\tEdges: " + str(g.number_of_edges()))
    start = time.time()
    coms = community.asyn_lpa_communities(g)
    stop = time.time()-start
    print("time: "+"{0:.4f}".format(stop))
    #print("communities founded: "+str(len(coms)))
    for com in coms:
        out = ""
        for i in com:
            out += str(i)+", "
        print(out)

if __name__ == '__main__':
    #save_com()
    path = "./generated_networks/WS2DGrid_0_100_r2_k3.txt"
    g = nx.read_edgelist(path, create_using=nx.Graph())

    nx.draw_networkx(g,nx.kamada_kawai_layout(g, scale=100))
    plt.show()
