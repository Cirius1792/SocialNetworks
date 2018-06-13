#!/usr/bin/python


import math
import networkx as nx
import random
from joblib import Parallel, delayed


def WS2DG_opt(n, r, k, file=None):
    G = nx.Graph()
    line = int(math.sqrt(n))
    nodes = dict()

    for i in range(n):
        x = random.random()
        y = random.random()
        nodes[i] = (x * line, y * line)

    for i in range(n):
        for j in range(i + 1, n):
            dist = math.sqrt((nodes[i][0] - nodes[j][0]) ** 2 + (nodes[i][1] - nodes[j][1]) ** 2)
            if dist <= r:
                #G.add_edge(i, j)
                file.write(str(i)+" "+str(j)+"\n")

        for h in range(k):
            s = random.randint(0, n - 1)
            if s != i:
                #G.add_edge(i, s)
                file.write(str(i)+" "+str(s)+"\n")
    return nodes





def build_test_graph():
    base_path = "./generated_networks/"
    print("Generating WS Grid")
    n_net = 4
    r = 5
    k = 6
    n = 1000
    # for i in range(0,n_net):
    #     print("\rBuilding network "+str(i),end="")
    #     save_path = base_path+"WS2DGrid_"+str(i)+"_"+str(n)+"_r"+str(r)+"_k"+str(k)+".txt"
    #     f = open(save_path,'w')
    #     positions = WS2DG_opt(n,r,k, file=f)
    #     f.close()
    #     f = open(save_path+"pos.txt",'w')
    #     out = ""
    #     for i in positions:
    #         out += str(i)+" - "+str(positions[i][0])+" - "+str(positions[i][0])+"\n"
    #     f.write(out)
    # print("\rDone!", end="")
    # g = nx.read_edgelist(save_path, create_using=nx.Graph())
    # nx.draw_networkx(g,nx.kamada_kawai_layout(g))


    with Parallel(n_jobs=2) as parallel:
        res = parallel(delayed(_sub)(i) for i in range(n_net))
    print("\rDone!", end="")

def _sub(i):
    r = 2
    k = 3
    n = 100
    base_path = "./generated_networks/"
    f = open(base_path + "WS2DGrid_" + str(i) + "_" + str(n) + "_r" + str(r) + "_k" + str(k) + ".txt", 'w')
    WS2DG_opt(n, r, k, file=f)


if __name__ == '__main__':
    build_test_graph()