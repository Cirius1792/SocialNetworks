import networkx as nx
import random
from Esercitazioni.esercitazione_4.Centrality import *
from util.utility import *
from util.priorityq import *


# BEST RESPONSE DYNAMICS FOR NETWORK COORDINATION GAMES (a node can change multiple times)
def best_resp(graph, act, nact):
    thresholds = nx.get_node_attributes(graph, 'threshold')
    if len(thresholds) == 0:
        for i in graph.nodes():
            graph.node[i]['threshold'] = random.random() * len(graph[i])

    if len(act) > 0 or len(nact) > 0:
        for i in act:
            if 'active' not in graph.node[i] or not graph.node[i]['active']:
                graph.node[i]['active'] = True
                for j in graph[i]:
                    if 'act_neigh' in graph.node[j]:
                        graph.node[j]['act_neigh'] += 1
                    else:
                        graph.node[j]['act_neigh'] = 1
        for i in nact:
            if 'active' not in graph.node[i] or graph.node[i]['active']:
                graph.node[i]['active'] = False
                for j in graph[i]:
                    if 'act_neigh' in graph.node[j]:
                        graph.node[j]['act_neigh'] -= 1
                    else:
                        graph.node[j]['act_neigh'] = 0

        for i in graph.nodes():
            if 'act_neigh' in graph.node[i] and graph.node[i]['act_neigh'] >= graph.node[i]['threshold'] and (
                    'active' not in graph.node[i] or not graph.node[i]['active']):
                best_resp(graph, {i}, {})
                break
            if ('act_neigh' not in graph.node[i] or graph.node[i]['act_neigh'] < graph.node[i]['threshold']) and (
                    'active' in graph.node[i] and graph.node[i]['active']):
                best_resp(graph, {}, {i})
                break

    return graph


def best_resp_seq(graph, act, nact):
    thresholds = nx.get_node_attributes(graph, 'threshold')
    if len(thresholds) == 0:
        for i in graph.nodes():
            graph.node[i]['threshold'] = random.random() * len(graph[i])
    stable = False
    while not stable:
        if len(act) > 0 or len(nact) > 0:
            for i in act:
                if 'active' not in graph.node[i] or not graph.node[i]['active']:
                    graph.node[i]['active'] = True
                    for j in graph[i]:
                        if 'act_neigh' in graph.node[j]:
                            graph.node[j]['act_neigh'] += 1
                        else:
                            graph.node[j]['act_neigh'] = 1
            for i in nact:
                if 'active' not in graph.node[i] or graph.node[i]['active']:
                    graph.node[i]['active'] = False
                    for j in graph[i]:
                        if 'act_neigh' in graph.node[j]:
                            graph.node[j]['act_neigh'] -= 1
                        else:
                            graph.node[j]['act_neigh'] = 0
            act = {}
            nact = {}
            for i in graph.nodes():
                if 'act_neigh' in graph.node[i] and graph.node[i]['act_neigh'] >= graph.node[i]['threshold'] and (
                        'active' not in graph.node[i] or not graph.node[i]['active']):
                    act = {i}
                    break
                if ('act_neigh' not in graph.node[i] or graph.node[i]['act_neigh'] < graph.node[i]['threshold']) and (
                        'active' in graph.node[i] and graph.node[i]['active']):
                    nact = {i}
                    break
            if len(act) == 0 and len(nact) == 0:
                stable = True

    return graph


def bsdm_recursive (graph,fake1, fake2, seed_f1=None, seed_f2=None, monitor=None):
    THRESHOLD1 = 'threshold1'
    THRESHOLD2 = 'threshold2'
    TYPE = 'type' # 0 = Monitor, 1 = seed_fake1, 2= seed_fake2
    ACT_FAKE = 'act_fake'   # 1 = fake1, 2= fake2
    ACT_FAKE1_NEIGH = 'act_fake1_neigh'
    ACT_FAKE2_NEIGH = 'act_fake2_neigh'
    stable = False # parametro usato per fermare la dinamica
    iterations = 0
    thresholds = nx.get_node_attributes(graph, THRESHOLD1)
    if len(thresholds) == 0:
        for i in graph.nodes():
            graph.node[i][THRESHOLD1] = random.random()/2.0 * len(graph[i])
            graph.node[i][THRESHOLD2] = random.random()/2.0 * len(graph[i])
            # print("\nNodo:\t"+str(i))
            # print("\t t1 = "+str(graph.node[i][THRESHOLD1]))
            # print("\t t2 = "+str(graph.node[i][THRESHOLD2]))
            if i in seed_f1:
                graph.node[i][TYPE] = 1
            elif i in monitor:
                graph.node[i][TYPE] = 0
            elif i in seed_f2:
                graph.node[i][TYPE] = 2

    if len(fake1) > 0 or len(fake2) > 0:
        iterations += 1
        for i in fake1:
            if ACT_FAKE not in graph.node[i] or graph.node[i][ACT_FAKE] == 2:
                if ACT_FAKE in graph.node[i]:
                    change = True
                else:
                    change = False
                graph.node[i][ACT_FAKE] = 1
                for j in graph[i]:
                    if ACT_FAKE1_NEIGH in graph.node[j]:
                        graph.node[j][ACT_FAKE1_NEIGH] += 1
                        if change and ACT_FAKE2_NEIGH in graph.node[j]:
                            graph.node[j][ACT_FAKE2_NEIGH] -= 1
                    else:
                        graph.node[j][ACT_FAKE1_NEIGH] = 1
                        if change and ACT_FAKE2_NEIGH in graph.node[j]:
                            graph.node[j][ACT_FAKE2_NEIGH] -= 1

        for i in fake2:
            if ACT_FAKE not in graph.node[i] or graph.node[i][ACT_FAKE] == 1:
                if ACT_FAKE in graph.node[i]:
                    change = True
                else:
                    change = False
                graph.node[i][ACT_FAKE] = 2
                for j in graph[i]:
                    if ACT_FAKE2_NEIGH in graph.node[j]:
                        graph.node[j][ACT_FAKE2_NEIGH] += 1
                        if change and ACT_FAKE1_NEIGH in graph.node[j]:
                            graph.node[j][ACT_FAKE1_NEIGH] -= 1
                    else:
                        graph.node[j][ACT_FAKE2_NEIGH] = 1
                        if change and ACT_FAKE1_NEIGH in graph.node[j]:
                            graph.node[j][ACT_FAKE1_NEIGH] -= 1


        for i in graph.nodes():
            if TYPE not in graph.node[i]:
                if ACT_FAKE1_NEIGH in graph.node[i] and graph.node[i][ACT_FAKE1_NEIGH] > graph.node[i][THRESHOLD1] and (ACT_FAKE not in graph.node[i] or (ACT_FAKE in graph.node[i] and graph.node[i][ACT_FAKE] == 2)):
                    bsdm_recursive(graph, {i},{})
                    break
                if ACT_FAKE2_NEIGH in graph.node[i] and graph.node[i][ACT_FAKE2_NEIGH] > graph.node[i][THRESHOLD2] and (ACT_FAKE1_NEIGH not in graph.node[i] or (ACT_FAKE1_NEIGH in graph.node[i] and graph.node[i][ACT_FAKE1_NEIGH] < graph.node[i][THRESHOLD1])) and (
                        ACT_FAKE not in graph.node[i] or (ACT_FAKE in graph.node[i] and graph.node[i][ACT_FAKE] == 1)):
                    bsdm_recursive(graph, {}, {i})
                    break


    return graph

def bsdm(graph, seed_f1, seed_f2, monitor):
    THRESHOLD1 = 'threshold1'
    THRESHOLD2 = 'threshold2'
    TYPE = 'type' # 0 = Monitor, 1 = seed_fake1, 2= seed_fake2
    ACT_FAKE = 'act_fake'   # 1 = fake1, 2= fake2
    ACT_FAKE1_NEIGH = 'act_fake1_neigh'
    ACT_FAKE2_NEIGH = 'act_fake2_neigh'
    stable = False # parametro usato per fermare la dinamica
    #fake1Tofake2 = -(len(seed_f1)+ len(seed_f2))
    f1_over_f2 = 0
    n_seeds = len(seed_f2) + len(seed_f2)
    thresholds = nx.get_node_attributes(graph, THRESHOLD1)
    if len(thresholds) == 0:
        for i in graph.nodes():
            graph.node[i][THRESHOLD1] = random.random()*0.5 * len(graph[i])
            graph.node[i][THRESHOLD2] = random.random()*0.5 * len(graph[i])
            # print("\nNodo:\t"+str(i))
            # print("\t t1 = "+str(graph.node[i][THRESHOLD1]))
            # print("\t t2 = "+str(graph.node[i][THRESHOLD2]))
            if i in seed_f1:
                graph.node[i][TYPE] = 1
            elif i in monitor:
                graph.node[i][TYPE] = 0
            elif i in seed_f2:
                graph.node[i][TYPE] = 2
    fake1 = seed_f1
    fake2 = seed_f2
    iteration = 0
    while not stable:
        iteration += 1
        if len(fake1) > 0 or len(fake2) > 0:
            for i in fake1:
                if ACT_FAKE not in graph.node[i] or graph.node[i][ACT_FAKE] == 2:
                    if ACT_FAKE in graph.node[i]:
                        change = True
                    else:
                        change = False
                    graph.node[i][ACT_FAKE] = 1
                    for j in graph[i]:
                        if ACT_FAKE1_NEIGH in graph.node[j]:
                            graph.node[j][ACT_FAKE1_NEIGH] += 1
                            if change and ACT_FAKE2_NEIGH in graph.node[j]:
                                graph.node[j][ACT_FAKE2_NEIGH] -= 1
                        else:
                            graph.node[j][ACT_FAKE1_NEIGH] = 1
                            if change and ACT_FAKE2_NEIGH in graph.node[j]:
                                graph.node[j][ACT_FAKE2_NEIGH] -= 1

            for i in fake2:
                if ACT_FAKE not in graph.node[i] or graph.node[i][ACT_FAKE] == 1:
                    if ACT_FAKE in graph.node[i]:
                        change = True
                    else:
                        change = False
                    graph.node[i][ACT_FAKE] = 2
                    for j in graph[i]:
                        if ACT_FAKE2_NEIGH in graph.node[j]:
                            graph.node[j][ACT_FAKE2_NEIGH] += 1
                            if change and ACT_FAKE1_NEIGH in graph.node[j]:
                                graph.node[j][ACT_FAKE1_NEIGH] -= 1
                        else:
                            graph.node[j][ACT_FAKE2_NEIGH] = 1
                            if change and ACT_FAKE1_NEIGH in graph.node[j]:
                                graph.node[j][ACT_FAKE1_NEIGH] -= 1

            fake1 = {}
            fake2 = {}
            for i in graph.nodes():
                if TYPE not in graph.node[i]:
                    if ACT_FAKE1_NEIGH in graph.node[i] and graph.node[i][ACT_FAKE1_NEIGH] > graph.node[i][THRESHOLD1] and (ACT_FAKE not in graph.node[i] or (ACT_FAKE in graph.node[i] and graph.node[i][ACT_FAKE] == 2)):
                        if (ACT_FAKE1_NEIGH in graph.node[i] and ACT_FAKE2_NEIGH in graph.node[i]):
                            if graph.node[i][ACT_FAKE1_NEIGH] > graph.node[i][THRESHOLD1] and graph.node[i][ACT_FAKE2_NEIGH] > graph.node[i][THRESHOLD2]:
                                f1_over_f2 += 1
                        fake1 = {i}
                        break
                    if ACT_FAKE2_NEIGH in graph.node[i] and graph.node[i][ACT_FAKE2_NEIGH] > graph.node[i][THRESHOLD2] and (ACT_FAKE1_NEIGH not in graph.node[i] or (ACT_FAKE1_NEIGH in graph.node[i] and graph.node[i][ACT_FAKE1_NEIGH] < graph.node[i][THRESHOLD1])) and (
                            ACT_FAKE not in graph.node[i] or (ACT_FAKE in graph.node[i] and graph.node[i][ACT_FAKE] == 1)):
                        fake2 = {i}
                        break
            if len(fake1) == 0 and len(fake2) == 0:
                stable = True
    f1_over_f2 = f1_over_f2/(iteration - n_seeds)
    print("f1 over f2: \t"+"{0:.4f}".format(f1_over_f2))
    return graph


def test_locale():
    g = nx.Graph()
    g.add_edge(1, 2)
    g.add_edge(1, 3)
    g.add_edge(2, 3)
    g.add_edge(2, 5)
    g.add_edge(3, 4)
    g.add_edge(4, 5)
    g.add_edge(4, 7)
    g.add_edge(5, 6)
    g.add_edge(6, 7)
    g.add_edge(7, 8)
    g.add_edge(8, 6)

    fake1 = {random.choice(list(g.nodes()))}
    fake2 = {random.choice(list(g.nodes()))}
    monitor = {random.choice(list(g.nodes()))}
    g = bsdm_recursive(g, fake1, fake2, seed_f1=fake1, seed_f2=fake2, monitor=monitor)
    active = nx.get_node_attributes(g, 'act_fake')
    print(["nodo: " + str(i) + " op:" + str(g.node[i]['act_fake']) for i in active.keys() if active[i]])
    sts = get_opinion_stats(g)
    print("\nResoconto Diffusione:")
    print("\tfake1: " + "{0:.4f}".format(sts[0]) + "\t fake2: " + "{0:.2f}".format(sts[1]))


def testBSDM():
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

    # path = "./generated_networks/WSGrid_2500_r5_k6.txt"
    # g = nx.read_edgelist(path)
    # print("Rete: "+path)
    # print("\tNodes: "+str(g.number_of_nodes()))
    # print("\tEdges: "+str(g.number_of_edges()))
    # fake1 = { random.choice(list(g.nodes())),random.choice(list(g.nodes())),random.choice(list(g.nodes())),random.choice(list(g.nodes()))}
    # monitor = { random.choice(list(g.nodes())),random.choice(list(g.nodes())),random.choice(list(g.nodes())),random.choice(list(g.nodes()))}
    # fake2 = { random.choice(list(g.nodes())),random.choice(list(g.nodes())),random.choice(list(g.nodes())),random.choice(list(g.nodes()))}
    fake1 = {7}
    fake2 = {1}
    monitor = {6}
    g = bsdm_recursive(g, fake1, fake2, seed_f1=fake1, seed_f2= fake2, monitor=monitor)
    active = nx.get_node_attributes(g, 'act_fake')
    print(["nodo: "+str(i)+" op:"+str(g.node[i]['act_fake']) for i in active.keys() if active[i]])
    sts = get_opinion_stats(g)
    print("\nResoconto Diffusione:")
    print("\tfake1: "+"{0:.4f}".format(sts[0])+"\t fake2: "+"{0:.2f}".format(sts[1]))
    sts2 = g._stats
    sts2 = [sts[0]/g.number_of_nodes(), sts[1]/g.number_of_nodes()]
    print("\tfake1: "+"{0:.2f}".format(sts2[0])+"\t fake2: "+"{0:.2f}".format(sts2[1]))
    # g = bsdm(g, fake1, fake2, monitor)
    # active = nx.get_node_attributes(g, 'act_fake')
    # print(["nodo: "+str(i)+" op:"+str(g.node[i]['act_fake']) for i in active.keys() if active[i]])

def get_opinion_stats(g, output=False):
    active = nx.get_node_attributes(g, 'act_fake')
    diffusion = [0,0,0] #diffusion[0] = % opinioni fake1, diffusion[1] = % opinioni fake2
    n_nodes = g.number_of_nodes()
    for i in active:
        if g.node[i]['act_fake'] == 1:
            diffusion[0] += 1
        else:
            diffusion[1] += 1
    diffusion[0] = diffusion[0]/n_nodes
    diffusion[1] = diffusion[1]/n_nodes
    diffusion[2] = (n_nodes - len(active))/n_nodes
    if output:
        print("opinion 1: "+"{0:.2f}".format(diffusion[0])+"\t opinion 2:"+"{0:.2f}".format(diffusion[1])+"\t no opinion:"+"{0:.2f}".format(diffusion[2]))
    return diffusion



def test():
    path = "./generated_networks/WS2DGrid_0_100_r2_k3.txt"
    G = nx.read_edgelist(path)
    fake1 = set(top(G,degree,10))
    fake2 = {random.choice(list(G.nodes())) for i in range(10) }
    monitor = {random.choice(list(G.nodes()))for i in range(10) }

    G = bsdm(G, fake2, fake1, monitor)
    #print([i for i in active.keys() if active[i]])
    get_opinion_stats(G, output=True)

if __name__ == '__main__':
    for i in range(5):
        test()
        print("\n\n###### "+str(i)+" <######")