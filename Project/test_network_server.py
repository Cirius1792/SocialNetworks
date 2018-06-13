import networkx as nx
from joblib import Parallel, delayed


def shapley_degree(G):
    SV = {v: 1 / (1 + G.degree(v)) for v in G.nodes()}
    for v in G.nodes():
        for u in G[v]:
            SV[v] += 1 / (1 + G.degree(u))
    return SV


def shapley_closeness(G):
    SV = {v: 0 for v in G.nodes()}
    for v in G.nodes():
        nodes = sorted(({'node': u, 'dist': nx.shortest_path_length(G, u, v)} for u in G.nodes()),
                       key=lambda x: x['dist'])
        somma = 0
        prev_dist = -1
        prev_SV = -1
        curr_SV = 0
        for i in range(G.number_of_nodes() - 1, 0, -1):
            # curr_SV must be the same for each node at the same distance from v. This motivates the following if-else
            if nodes[i]['dist'] == prev_dist:
                curr_SV = prev_SV
            else:
                curr_SV = nodes[i]['dist'] / (1 + i) - somma
            SV[nodes[i]['node']] += curr_SV
            somma += nodes[i]['dist'] / (i * (1 + i))
            prev_dist = nodes[i]['dist']
            prev_SV = curr_SV
        SV[v] -= somma
    return SV


def write(file_name, node_list):
    f = open(file_name, 'w')
    for t in node_list:
        f.write(str(t[0]) + ' ' + str(t[1]) + '\n')

    f.close()


def read(file_name):
    f = open(file_name, 'r')
    l = list()
    for line in f.readlines():
        s = line.split(' ')
        l.append((int(s[0]), float(s[1].split('\n')[0])))
    f.close()
    return l


if __name__ == '__main__':
    G = nx.read_edgelist('./generated_networks/WS2DGrid_0_5000_r5_k6.txt', create_using=nx.Graph(), nodetype=int)
    func = [nx.degree_centrality,nx.closeness_centrality, nx.betweenness_centrality, shapley_degree, shapley_closeness]
    with Parallel(n_jobs=4) as parallel:
        res = parallel(delayed(func[i])(G.copy(as_view=True)) for i in range(len(func)))
    print("Done!")
    # d = nx.degree_centrality(G)
    # write('degree', sorted(d.items(), key=lambda x: x[1], reverse=True))
    # print('degree done!')
    #
    # d = nx.closeness_centrality(G)
    # write('closeness', sorted(d.items(), key=lambda x: x[1], reverse=True))
    # print('closeness done!')
    #
    # d = nx.betweenness_centrality(G)
    # write('betweenness', sorted(d.items(), key=lambda x: x[1], reverse=True))
    # print('betweenness done!')
    #
    # d = shapley_degree(G)
    # write('S_degree', sorted(d.items(), key=lambda x: x[1], reverse=True))
    # print('S_degree done!')
    #
    # d = shapley_closeness(G)
    # write('S_closeness', sorted(d.items(), key=lambda x: x[1], reverse=True))
    # print('S_closeness done!')
    #
    # f = open('END', 'w')
    # f.close()
