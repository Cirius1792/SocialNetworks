#!/usr/bin/python

from util.priorityq import PriorityQueue
import networkx as nx

#Each of the following functions returns a PriorityQueue containing all nodes with priority equivalent to their centrality measure.

# DEGREE CENTRALITY
def degree(G):
    pq=PriorityQueue()
    for u in G.nodes():
        pq.add(u,-G.degree(u)) #We use negative value because PriorityQueue returns first values whose priority value is lower
    return pq

# CLOSENESS CENTRALITY    
def closeness(G):
    pq=PriorityQueue()
    
    for u in G.nodes():
        visited=set()
        queue=[u]
        visited.add(u)
        dist=dict()
        dist[u]=0
        
        while len(queue) > 0:
            v = queue.pop()
            for w in G[v]:
                if w not in visited:
                    dist[w]=dist[v]+1
                    visited.add(u)
        pq.add(u,sum(dist.values())) #This is not the closeness value. However, it gives the same rank as right closeness
        
    return pq
    
#BETWEENNESS CENTRALITY
def betweenness(G):
    pq=PriorityQueue()
    
    betweenness = {i:0 for i in G.nodes()}
    
    #Compute the number of shortest paths from s to every other node
    for s in G.nodes():
        #INITIALIZATION
        tree = []
        parents = {i:[] for i in G.nodes()} #it saves the nodes the parents of i in all shortest paths from s to i
        spnum = {i:0 for i in G.nodes()} #it saves the number of shortest paths from s to i
        distance = {i:-1 for i in G.nodes()} #it saves the length of the shortest path from s to i.
        eflow = {frozenset(e):0 for e in G.edges()} #it saves the number of shortest path from u to every other node that use edge e
        vflow = {i:1 for i in G.nodes()} #it saves the number of shortest path from u to every other node that use vertex i (this number is at least 1, since there is there is at least the shortest path from s to i)
        
        #BFS
        queue=[s]
        spnum[s]=1
        distance[s]=0
        while queue != []:
            c=queue.pop(0)
            tree.append(c)
            for i in G[c]:
                if distance[i] == -1: #if vertex i has not been visited
                    queue.append(i)
                    distance[i] = distance[c] +1
                if distance[i] == distance[c] + 1: #if we found another shortest path from s to i
                    spnum[i] += 1
                    parents[i].append(c)
                    
        #BOTTOM-UP PHASE
        while tree != []:
            c=tree.pop()
            for i in parents[c]:
                eflow[frozenset({c,i})] = vflow[c] * (spnum[i]/float(spnum[c])) #the number of shortest paths using vertex c is split among the edge to its parents proportionally to the number of shortest paths that the parents contributes
                vflow[i] += eflow[frozenset({c,i})] #each shortest path that use an edge (i,c) where i is closest to s than c must use also vertex i
                betweenness[i] += vflow[i] #betweenness of a vertex is the sum over all s of the number of shortest paths from s to other nodes using that node
    
    for u in G.nodes():
        pq.add(u, -betweenness[u])
    return pq
    
#PAGE RANK CENTRALITY
#s is the probability of selecting a neighbor. The probability of a restart is 1-s
#step is the maximum number of steps in which the process is repeated
#confidence is the maximum difference allowed in the rank between two consecutive step. When this difference is below or equal to confidence, we assume that the rank we assume that computation is terminated.
def pageRank(G,s=0.85,step=75,confidence=0):
    pq=PriorityQueue();
    
    n = nx.number_of_nodes(G)
    done = False
    time = 0
    # At the beginning, I choose the starting node uniformly at the random. Hence, every node has the same probability
    # of being verified at the beginning.
    rank = {i:float(1)/n for i in G.nodes()}
    while not done and time < step:
        time += 1
        #tmp contains the new rank
        # with probability 1-s, I restart the random walk. Hence, each node is visited at the next step at least with
        # probability (1-s)*1/n
        tmp = {i:float(1-s)/n for i in G.nodes()}
        #UPDATE OPERATION
        for i in G.nodes():
            for j in G[i]:
                # with probability s, I follow one of the link on the current page. So, if I am on page i with probability
                # rank[i], at the next step I would be on page j at which i links with probability s*rank[i]*probability
                # of following link (i,j) that is 1/out_degree(i)
                tmp[j] += float(s*rank[i])/len(G[i])
        #computes the difference between the old rank and the new rank and updates rank to contain the new rank
        diff = 0
        for i in G.nodes():
            # difference is computed in L1 norm. Alternatives are L2 norm (Euclidean Distance) and L_infinity norm
            # (maximum pointwise distance)
            diff += abs(rank[i]-tmp[i])
            rank[i] = tmp[i]
            
        if diff <= confidence:
            done = True
        
    for u in G.nodes():
        pq.add(u, -rank[u])
    return pq
    
#EXERCISE: Test how the computation time and the quality of the solution change as one changes s, step, confidence, and the norm used for computing the difference between ranks. (Suggestion: use larger graphs than the one below in order to appreciate differences)

#A parallel version of page rank can be achieved by dividing the graph in num_jobs different directed subgraphs.
# By assuming that num_jobs is a perfect square (4, 9, 16, 25, ...) this can be done dividing the set of nodes in
# sqrt(num_jobs) subsets, and having subgraph 0 containing only edges from the first subset to itself, subgraph 1
# containing only edges from the first subset to the second subset, ..., subgraph sqrt(num_jobs) containing only edges
#  from the second subset to the first subset, and so on. The update operation can be then executed in parallel for each
# subgraph. Results can be easily combined since the new page rank of a node i in the j-th subset is given by the rank
# coming from nodes in the first subset (contained in the j-th result) + the rank coming from nodes in the second subset
#  (contained in the sqrt(num_jobs)+j-th result) + ... + (1-s)/n. This combine operation also can be parallelized with
# each job taking care of combining the ranks of a different subset of nodes.
    
# HITS CENTRALITY
def hits(G, s=0.85,step=75,confidence=0):
    pq=PriorityQueue();
    
    H=nx.DiGraph(G) #It is more convenient to work with directed graph. Hence we convert the graph in input to a direct graph.
    
    n = nx.number_of_nodes(H)
    done = False
    time = 0
    
    hub = {i:float(1)/n for i in H.nodes()} #This contains the hub rank of each node.
    auth = {i:float(1)/n for i in H.nodes()} #This contains the authority rank of each node.
    
    while not done and time < step:
        time += 1
        
        #tauth contains the new authority rank
        tauth = {i:0 for i in H.nodes()}
        atot=0
        for i in H.nodes():
            for e in H.in_edges(i):
                #The authority level increases as better hubs are pointing to him
                tauth[i] += hub[e[0]] #the authority value of a node is the sum over all nodes pointing to him of their hubbiness value
                atot += hub[e[0]] #computes the sum of tauth[i] over all i. It serves only for normalization (each rank is done so that all values always sum to 1)
            
        #thub contains the new hub rank
        thub = {i:0 for i in H.nodes()}
        htot=0
        for i in H.nodes():
            for e in H.out_edges(i):
                #The hubbiness level increases as it points to better authorities
                thub[i] += auth[e[1]] #the hubbiness value of a node is the sum over all nodes at which it points of their authority value
                htot += auth[e[1]] #computes the sum of thub[i] over all i. It serves only for normalization (each rank is done so that all values always sum to 1)
            
        diff_a = 0
        diff_h = 0
        for i in H.nodes():
            diff_a += abs(auth[i]-tauth[i]/atot)
            diff_h += abs(hub[i]-thub[i]/htot)
            auth[i] = tauth[i]/atot
            hub[i] = thub[i]/htot
            
        if diff_a <= confidence and diff_h <= confidence:
            done = True
        
    for u in G.nodes():
        pq.add(u, -auth[u]) #Here we have different choices. Rank by authority level, by hubbiness level, by a combinations of these two levels. The best choice depends on the application at the hand
    return pq

#EXERCISE: Test how the solution changes as the ranking choice changes
    
#Returns the top k nodes of G according to the centrality measure "measure"
def top(G,measure,k):
    pq=measure(G)
    out=[]
    for i in range(k):
        out.append(pq.pop())
    return out
    
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
print(top(G,degree,3))
print(top(G,closeness,3))
print(top(G,betweenness,3))
print(top(G,pageRank,3))
print(top(G,hits,3))
