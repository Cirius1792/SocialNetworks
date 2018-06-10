#!/usr/bin/python

import networkx as nx
import random
import math

# INDEPENDENT CASCADE MODEL
# graph may have edge prob
def cascade(graph,active,prob):
    if len(active)>0:
        newactive=set()
        for i in active:
            graph.node[i]['active']=True
            for j in graph[i]:
                if 'active' not in graph.node[j]:
                    r=random.random()
                    if r <= prob:
                        newactive.add(j)
        cascade(graph,newactive,prob)
    return graph

# LINEAR THRESHOLD MODEL (a node can change only once)
def threshold(graph,active):
    thresholds = nx.get_node_attributes(graph,'threshold')
    if len(thresholds) == 0:
        for i in graph.nodes():
            graph.node[i]['threshold']=random.random()

    if len(active)>0:
        newactive=set()
        for i in active:
            graph.node[i]['active']=True
            for j in graph[i]:
                if 'active' not in graph.node[j]:
                    if 'act_neigh' in graph.node[j]:
                        graph.node[j]['act_neigh'] += 1/len(graph[j])
                    else:
                        graph.node[j]['act_neigh'] = 1/len(graph[j])
                    if graph.node[j]['act_neigh'] >= graph.node[j]['threshold']:
                        newactive.add(j)
        threshold(graph,newactive)
        
    return graph
    
# MAJORITY DYNAMICS (a node can change multiple time)
# result may depend on the order
# single update at each time (it may not converge otherwise)
def majority(graph,act,nact):
    if len(act)>0 or len(nact)>0:
        for i in act:
            if 'active' not in graph.node[i] or not graph.node[i]['active']:
                graph.node[i]['active']=True
                for j in graph[i]:
                    if 'act_neigh' in graph.node[j]:
                        graph.node[j]['act_neigh'] += 1
                    else:
                        graph.node[j]['act_neigh'] = 1
        for i in nact:
            if 'active' not in graph.node[i] or graph.node[i]['active']:
                graph.node[i]['active']=False
                for j in graph[i]:
                    if 'act_neigh' in graph.node[j]:
                        graph.node[j]['act_neigh'] -= 1
                    else:
                        graph.node[j]['act_neigh'] = 0
        
        for i in graph.nodes():
            if 'act_neigh' in graph.node[i] and graph.node[i]['act_neigh'] >= len(graph[i])/2 and ('active' not in graph.node[i] or not graph.node[i]['active']):
                majority(graph,{i},{})
                break
            if ('act_neigh' not in graph.node[i] or graph.node[i]['act_neigh'] < len(graph[i])/2) and ('active' in graph.node[i] and graph.node[i]['active']):
                majority(graph,{},{i})
                break
            
    return graph

# BEST RESPONSE DYNAMICS FOR NETWORK COORDINATION GAMES (a node can change multiple times)
def best_resp(graph,act,nact):
    thresholds = nx.get_node_attributes(graph,'threshold')
    if len(thresholds) == 0:
        for i in graph.nodes():
            graph.node[i]['threshold']=random.random()*len(graph[i])
            
    if len(act)>0 or len(nact)>0:
        for i in act:
            if 'active' not in graph.node[i] or not graph.node[i]['active']:
                graph.node[i]['active']=True
                for j in graph[i]:
                    if 'act_neigh' in graph.node[j]:
                        graph.node[j]['act_neigh'] += 1
                    else:
                        graph.node[j]['act_neigh'] = 1
        for i in nact:
            if 'active' not in graph.node[i] or graph.node[i]['active']:
                graph.node[i]['active']=False
                for j in graph[i]:
                    if 'act_neigh' in graph.node[j]:
                        graph.node[j]['act_neigh'] -= 1
                    else:
                        graph.node[j]['act_neigh'] = 0
        
        for i in graph.nodes():
            if 'act_neigh' in graph.node[i] and graph.node[i]['act_neigh'] >= graph.node[i]['threshold'] and ('active' not in graph.node[i] or not graph.node[i]['active']):
                best_resp(graph,{i},{})
                break
            if ('act_neigh' not in graph.node[i] or graph.node[i]['act_neigh'] < graph.node[i]['threshold']) and ('active' in graph.node[i] and graph.node[i]['active']):
                best_resp(graph,{},{i})
                break
            
    return graph

# VOTER MODEL
def voter(graph, seed, num_steps):
    for i in graph.nodes():
        if i in seed:
            graph.node[i]['active'] = True
        else:
            graph.node[i]['active'] = False
            
    for t in range(num_steps):
        u=random.choice(list(graph.nodes()))
        v=random.choice(list(graph[u]))
        graph.node[u]['active'] = graph.node[v]['active']
        
    return graph

G=nx.Graph()
G.add_edge('A','B')
G.add_edge('A','C')
G.add_edge('B','C')
G.add_edge('B','D')
G.add_edge('D','E')
G.add_edge('D','F')
G.add_edge('D','G')
G.add_edge('E','F')
G.add_edge('F','G')
seed={'B'}
#UNCOMMENT FOR TEST
#INDEPENDENT CASCADE
print(list(nx.get_node_attributes(cascade(G,seed,2/3),'active').keys()))

#LINEAR THRESHOLD
print(list(nx.get_node_attributes(threshold(G,seed),'active').keys()))

#MAJORITY
active = nx.get_node_attributes(majority(G,seed,{}),'active')
print([i for i in active.keys() if active[i]])

#BEST RESPONSE
# active = nx.get_node_attributes(best_resp(G,seed,{}),'active')
# print([i for i in active.keys() if active[i]])

#VOTER
#active = nx.get_node_attributes(voter(G,seed,10),'active')
#print([i for i in active.keys() if active[i]])
