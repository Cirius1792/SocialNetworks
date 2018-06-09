#!/usr/bin/python

import networkx as nx
import random
from scipy.special import zeta
import math
import numpy

#Random Graph (Newman, chap. 12)
def randomG(n, p):
    G = nx.Graph()
    for i in range(n):
        for j in range(i+1,n):
            r=random.random()
            if r <= p:
                G.add_edge(i,j)
    return G

#Configuration Model (Newman, chap. 13)
def configurationG(deg):
    G=nx.Graph()
    nodes=set(range(len(deg)))
    while len(nodes) > 1:
        rep = 0
        edge=random.sample(list(nodes),2)
        while G.has_edge(edge[0],edge[1]) and rep < 10:
            edge=random.sample(list(nodes),2)
            rep += 1
        G.add_edge(edge[0],edge[1])
        deg[edge[0]] -= 1
        if deg[edge[0]] == 0:
            nodes.remove(edge[0])
        deg[edge[1]] -= 1
        if deg[edge[1]] == 0:
            nodes.remove(edge[1])
    return G

def power_law_degree(n,power):
    deg_list=[]
    deg = 1
    z=zeta(power)
    while len(deg_list) < n:
        p = 1/((deg**power)*z)
        num=math.ceil(p*n)
        if deg%2 == 1 and num%2 == 1:
            num=num-1
        for i in range(num):
            if len(deg_list) < n:
                deg_list.append(deg)
        deg += 1
    return deg_list
    
#Preferential Attachment (EK 18)
def preferentialG(n,p):
    G=nx.Graph()
    nodes=[]
    for u in range(n):
        r=random.random()
        if r <= p and len(nodes) > 0:
            v=random.choice(nodes)
            G.add_edge(u,v)
            nodes.append(v)
            nodes.append(u)
        else:
            v=random.choice([x for x in range(n) if x != u])
            G.add_edge(u,v)
            nodes.append(v)
            nodes.append(u)
    return G

def preferentialGd(n,d,p):
    G=nx.Graph()
    nodes=[]
    for u in range(n):
        for i in range(d):
            r=random.random()
            if r <= p and len(nodes) > 0:
                v=random.choice([x for x in nodes if x != u])
                G.add_edge(u,v)
                nodes.append(v)
                nodes.append(u)
            else:
                v=random.choice([x for x in range(n) if x != u])
                G.add_edge(u,v)
                nodes.append(v)
                nodes.append(u)
    return G

def test1():
    print(randomG(9,0.5).edges())
    print(configurationG([5,3,3,2,2,1,1,1,1]).edges())
    deg_list=power_law_degree(9,2)
    print(deg_list)
    print(configurationG(deg_list).edges())
    print(preferentialG(9,0.5).edges())
    print(preferentialGd(9,2,0.5).edges())

if __name__ == '__main__':
    G = preferentialG(9,0.5)
    nx.write_adjlist(G,"test.txt")
