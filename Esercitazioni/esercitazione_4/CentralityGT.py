#!/usr/bin/python

from util.priorityq import PriorityQueue
import networkx as nx
from math import factorial
from scipy.special import binom 

# Compute the Shapley value for a characteristic function that extends degree centrality to coalitions
# Specifically, the characteristic function is value(C) = |C| + |N(C)|, where N(C) is the set of nodes outside C with at least one neighbor in C
# It has been proved that the Shapley value of node v in this case is SV[v] = 1/(1+deg(v)) + sum_{u \in N(v), u != v} 1/(1+deg(u))
# For more information, see Michalack et al. (JAIR 2013) sec. 4.1
def shapley_degree(G):
    SV={v:1/(1+G.degree(v)) for v in G.nodes()}
    for v in G.nodes():
        for u in G[v]:
            SV[v]+=1/(1+G.degree(u))
    return SV

# Consider another extension of degree centrality
# Specifically, we assume that to influence a node outside a coalition is necessary that at least k of its neighbors are
#  within the coalition. That, the characteristic function is value(C) = |C| + |N(C,k)|, where N(C,k) is the set of nodes
# outside C with at least k neighbors in C It has been proved that the Shapley value of node v in this case is
# SV[v] = min(1,k/(1+deg(v))) + sum_{u \in N(v), u != v} max(O,(deg(u)-k+1)/(deg(u)*(1+deg(u)))
# For more information, see Michalack et al. (JAIR 2013) sec. 4.2
def shapley_threshold(G,k=10):
    SV={v:min(1,k/(1+G.degree(v))) for v in G.nodes()}
    for v in G.nodes():
        for u in G[v]:
            SV[v]+=max(0,(G.degree(u)-k+1)/(G.degree(u)*(1+G.degree(u))))
    return SV
# NOTE: shapley_threshold works even with node-specific threshold values

# Compute the Shapley value for a characteristic function that extends closeness centrality to coalitions
# Specifically, the characteristic function is value(C) = sum_u dist(u,C), where dist(u,C) is the minimum distance between u and a node of C
# It has been proved that the Shapley value of node v in this case is:
# SV[v] = - sum_{k=0}^{|V|- 2} d_{k+1}/((k+1)(k+2)) + sum_{u != v} (d(u,v)/(k_uv + 2) - sum_{k = k_uv+1})^{|V|-2} d_{k+1}/((k+1)(k+2)))
# where D[v] = {d_1, ..., d_{|V|-1}} is the set of distances from v in increasing order,
# and k_uv is the number of nodes different from u and v whose distance from v is at most d(u,v)
# For more information, see Michalack et al. (JAIR 2013) sec. 4.4
def shapley_closeness(G):
    SV={v:0 for v in G.nodes()}
    cnt = 1
    n_nodes = G.number_of_nodes()
    print("\r" + "{0:.2f}".format((float(cnt) / n_nodes) * 100) + "%", end="")
    for v in G.nodes():
        if cnt%50==0:
            print("\r"+"{0:.2f}".format((float(cnt)/n_nodes)*100)+"%", end="")
        cnt +=1
        #nodes=sorted(({'node':u,'dist':nx.shortest_path_length(G,u,v)} for u in G.nodes()),key=lambda x:x['dist'])
        nodes = list()
        for u in G.nodes():
            dist = nx.shortest_path_length(G,u,v) if nx.has_path(G,u,v) else float('inf')
            nodes.append({'node':u,'dist':dist})
        nodes = sorted(nodes,key=lambda x:x['dist'])
        somma=0
        prev_dist=-1
        prev_SV=-1
        curr_SV=0
        for i in range(G.number_of_nodes()-1,0,-1):
            #curr_SV must be the same for each node at the same distance from v. This motivates the following if-else
            if nodes[i]['dist'] == prev_dist:
                curr_SV=prev_SV
            else:
                curr_SV=nodes[i]['dist']/(1+i) - somma
            SV[nodes[i]['node']] += curr_SV
            somma += nodes[i]['dist']/(i*(1+i))
            prev_dist=nodes[i]['dist']
            prev_SV = curr_SV
        SV[v] -= somma
    print("\r",end="")
    return SV

# The following measure assumes that the importance of a node does not depend only on its own (topological) properties,
# but also on the importance of the community in which it is community.
# E.g., a node in a community that is linked with many other community is more important than an equivalent node in an isolated community.
# This measure assumes that the community structure is given (e.g., computed by a community detection algorithm).
# The value of each node cannot computed with the Shapley value (that do not assume a community structure),
# but with a similar measure that uses the given community structure, called Owen value
# As for Shapley value, the Owen value can be computed for every characteristic function
# However, as for Shapley value, the naive implementation takes exponential time
# Here, we present a polynomial time algorithm for the Owen value when the characteristic function is value(C) = |N(C)| = \sum_{u \in N(C)} 1
# For more information, see Szczepanski et al. (ECAI 2014) sec. 5.3
def community_degree(G,communities):
    comm={v:com for com in communities for v in com}
    value={v:0 for v in G.nodes()}
    # Number of different communities in which there is at least a neighbor of u
    neigh_comm={u:len([c for c in communities if c != comm[u] and len(c.intersection(set(G[u]))) > 0]) for u in G.nodes()}
    M=len(communities)
    for v in G.nodes():
        #Number of neighbors of u in the community of v
        neigh_node={u:len(comm[v].intersection(set(G[u]))) for u in G.nodes()}
        C=len(comm[v])
        for k in range(M):
            for l in range(C):
                tmp=-1
                for u in set(G[v]).intersection(comm[v]):
                    tmp += (binom(M-1-neigh_comm[u],k)*binom(C-1-neigh_node[u],l))/(binom(M-1,k)*binom(C-1,l))
                for u in set(G[v]).difference(comm[v]):
                    tmp += (binom(M-1-neigh_comm[u],k)*binom(C-neigh_node[u],l))/(binom(M-1,k)*binom(C-1,l))
                tmp += (binom(M-1-neigh_comm[v],k)*binom(C-1-neigh_node[v],l))/(binom(M-1,k)*binom(C-1,l))
                value[v] += tmp/(M*C)
    return value
# NOTE: community degree can be extended to work for every characteristic function value(C) = sum_{u in N(C)} f(u) for some function f
# EXERCISE: test with different community structures

# All above measures assume that all coalitions are feasible
# Next, we consider that the feasibility of coalition is constrained from the graph G
# Specifically, a coalition C is feasible only if for every pair of nodes u,v in C there is a path in G that:
#   (i) consists only of nodes in C;
#   (ii) connects u and v.
# E.g., in the graph G={(1,2),(2,3)}, the coalition {1,3} is not feasible, whereas the coalition {1,2,3} is feasible
# Clearly, the value of each node cannot computed with the Shapley value (that assume all coalitions are feasible),
# but with a similar measure, named Myerson value
# As for Shapley value, the Myerson value can be computed for every characteristic function
# Moreover the Myerson value can always be computed in polynomial time in the number of feasible coalition (and the size of the graph)
#
# The algorithm simply generate all possible feasible coalitions, through a DFS visit of the graph, and add the contribution
# of this coalition to the Myerson value of each node. Be careful, that, in many setting, the number of coalitions allowed
# by the graph can be exponentially large (in particular, if G is a clique, all coalitions are feasible and we are just
# implementing the exponential-time naive algorithm for the Shapley value). In order to use the Myerson value as a
# centrality measure it makes sense to consider superadditive characteristic functions, that is characteristic functions
# that increase as new node are added to the coalition. In this way, a node is more important when it enables big coalitions.
# Below, we show an implementation when the characteristic function is value(C) = |C|^2
# For more information, see Skibski et al. (AAMAS 2014) sec. 5
def myerson(G):
    nodes=sorted(G.nodes(),key= lambda x:G.degree(x), reverse=True)
    neighbors={i:sorted(G[i], key = lambda x:G.degree(x), reverse = True) for i in nodes}
    myerson={i:0 for i in nodes}
    for i in nodes:
        #generate all coalition in which i is the node with most neighbors
        myerson_rec(nodes,neighbors,myerson,[i],{i},set(nodes[0:nodes.index(i)]),set(),0)
        
    return myerson
        
# nodes = list of nodes ordered by degree
# neighbors = for each node list neighbors ordered by degree
# myerson = myerson value of nodes
# path = denoted the path of visited nodes in a DFS visit. A node is added to the path as soon as it is visited for the first time, and it is removed from the path only when all neighbors have been visited
# subgraph = the current subgraph
# forbidden = nodes that are not in the current subgraph
# subneigh = neighbors of the current subgraph
# start = index of the next neighbor to process
def myerson_rec(nodes,neighbors,myerson,path,subgraph,forbidden,subneigh,start):
    v=path[len(path) - 1]
    for u in neighbors[v][start:len(neighbors[v])]:
        if u not in subgraph and u not in forbidden:
            #generate all coalitions that contain u
            #To this aim we create a copy of the variables
            newpath=list(path)
            newpath.append(u)
            newsub=set(subgraph)
            newsub.add(u)
            newforb=set(forbidden)
            newneigh=set(subneigh)
            myerson_rec(nodes,neighbors,myerson,newpath,newsub,newforb,newneigh,0)
            
            #generate all coalitions that do not contain u
            forbidden.add(u)
            subneigh.add(u)
        elif u in forbidden:
            subneigh.add(u)
    path.pop()
    #if there are other nodes to visit
    if len(path)>0:
        myerson_rec(nodes,neighbors,myerson,path,subgraph,forbidden,subneigh,neighbors[path[len(path)-1]].index(v)+1)
    else:
        #if there are no node to visit, we add the contribution og the current coalition to the Myerson value of nodes
        for i in subgraph:
            myerson[i] += len(subgraph)**2*factorial(len(subgraph)-1)*factorial(len(subneigh))/factorial(len(subgraph)+len(subneigh)) #for using a different characteristic function V, simply substitute len(subgraph)**2 with V(subgraph)
        for i in subneigh:
            myerson[i] -= len(subgraph)**2*factorial(len(subgraph))*factorial(len(subneigh)-1)/factorial(len(subgraph)+len(subneigh)) #for using a different characteristic function V, simply substitute len(subgraph)**2 with V(subgraph)
# EXERCISE: Test with different characteristic function
if __name__ == '__main__':

    G=nx.Graph()
    G.add_edge(1,2)
    G.add_edge(2,3)
    G.add_edge(3,4)
    G.add_edge(3,5)
    print(shapley_degree(G))
    print(shapley_threshold(G,2))
    print(shapley_closeness(G))
    print(community_degree(G,[{1,2},{3,4,5}]))
    print(myerson(G))








