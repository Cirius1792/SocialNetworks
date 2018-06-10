import math
import networkx as nx
import random


def randomG_opt(n, p, file="tmp.txt"):
    #G = nx.Graph()

    for i in range(n):
        for j in range(i+1,n):
            r=random.random()
            if r <= p:
                #G.add_edge(i,j)
                file.write(str(i)+" "+str(j)+"\n")
    file.close()
    return True


def WSGridG_opt(n, r, k, file=None, ret=None):
    G = nx.Graph()
    line = int(math.sqrt(n))

    for i in range(line):
        for j in range(line):

            for x in range(r + 1):
                for y in range(r + 1 - x):
                    if x + y > 0:
                        if i + x < line and j + y < line:
                           #G.add_edge(i * line + j, (i + x) * line + (j + y))
                            file.write(str(i * line + j)+" "+str((i + x) * line + (j + y))+"\n")
                            # G.add_edge((i,j),(i+x,j+y))ù

            for h in range(k):
                s = random.randint(0, n - 1)
                # s1 = random.randint(0,line-1)
                # s2 = random.randint(0,line-1)
                if s != i * line + j:
                    #G.add_edge(i * line + j, s)
                    file.write(str(i * line + j)+" "+str(s)+"\n")
    file.close()
    if ret:
        G = nx.read_edgelist(file)
    return G


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

    return True
