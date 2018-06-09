#!/usr/bin/python

import networkx as nx
import random
from scipy.special import zeta
import math
import numpy

#Watts Strogatz (EK 20)
# n is the number of nodes
# r is the radius of each node (a node u is connected with each other node at distance at most r) - strong ties
# k is the number of random edges for each node u - weak ties
def WSGridG(n, r, k):
    G=nx.Graph()
    line=int(math.sqrt(n))
    
    for i in range(line):
        for j in range(line):
            
            for x in range(r+1):
                for y in range(r+1-x):
                    if x + y > 0:
                        if i + x < line and j + y < line:
                            G.add_edge(i*line+j,(i+x)*line+(j+y))
                            #G.add_edge((i,j),(i+x,j+y))ù
                            
            for h in range(k):
                s = random.randint(0,n-1)
                #s1 = random.randint(0,line-1)
                #s2 = random.randint(0,line-1)
                if s != i*line+j:
                    G.add_edge(i*line+j,s)
    
    return G

def WS2DG(n, r, k):
    G=nx.Graph()
    line=int(math.sqrt(n))
    nodes=dict()
    
    for i in range(n):
        x=random.random()
        y=random.random()
        nodes[i]=(x*line,y*line)
        
    for i in range(n):
        for j in range(i+1,n):
            dist=math.sqrt((nodes[i][0]-nodes[j][0])**2 + (nodes[i][1]-nodes[j][1])**2)
            if dist <= r:
                G.add_edge(i,j)
                
        for h in range(k):
            s = random.randint(0,n-1)
            if s != i:
                G.add_edge(i,s)
        
    return G

# q determines the probability distribution of weak ties
def GenWS2DG(n, r, k, q):
    G=nx.Graph()
    line=int(math.sqrt(n))
    nodes=dict()
    prob=dict()
    
    for i in range(n):
        x=random.random()
        y=random.random()
        nodes[i]=(x*line,y*line)
        prob[i]=dict()
        
    for i in range(n):
        for j in range(i+1,n):
            dist=math.sqrt((nodes[i][0]-nodes[j][0])**2 + (nodes[i][1]-nodes[j][1])**2)
            prob[i][j]=1/(dist**q)
            prob[j][i]=prob[i][j]
            if dist <= r:
                G.add_edge(i,j)
                
        norm=sum(prob[i].values())
        for h in range(k):
            s = numpy.random.choice(list(prob[i].keys()), p = [x/norm for x in prob[i].values()])
            if s != i:
                G.add_edge(i,s)
                
    return G

#Affiliation Networks
#n = number of nodes
#m = number of communities
#q = probability of preferential affiliation
#p = probability of edge within community
#c = number max of communities at which a node participates
#s = number of out-of-community nodes
def affiliationG(n,m,q,p,c,s):
    G=nx.Graph()
    community=dict()
    comm_inv=dict()
    communities=[]
    nodes=[]
    
    for i in range(m):
        community[i]=set()
    for i in range(n):
        comm_inv[i]=set()
        
    for i in range(n):
        r = random.random()
        if len(communities) == 0 or r < q:
            num_com=random.randint(1,c)
            for k in range(num_com):
                comm=random.choice([x for x in range(m)])
                community[comm].add(i)
                if comm not in comm_inv[i]:
                    communities.append(i)
                    comm_inv[i].add(comm)
        else:
            prototype=random.choice(communities)
            for comm in comm_inv[prototype]:
                community[comm].add(i)
                if comm not in comm_inv[i]:
                    communities.append(i)
                    comm_inv[i].add(comm)
                    
        for comm in comm_inv[i]:
            for v in community[comm]:
                if v != i:
                    r=random.random()
                    if r < p:
                        if not G.has_edge(i,v):
                            G.add_edge(i,v)
                            nodes.append(i)
                            nodes.append(v)
                            
        for t in range(s):
            if len(nodes) == 0:
                v=random.choice([x for x in range(n) if x != i])
            else:
                v=random.choice([x for x in nodes if x != i])
            if not G.has_edge(i,v):
                G.add_edge(i,v)
                nodes.append(i)
                nodes.append(v)
    
    return G

if __name__ == '__main__':

    print(WSGridG(9,1,1).edges())
    print(WS2DG(9,1,1).edges())
    print(GenWS2DG(9,1,1,2).edges())
    print(affiliationG(9,4,0.5,0.8,3,2).edges())
