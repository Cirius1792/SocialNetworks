import random
import networkx as nx

def bsdm(graph, seed_f1, seed_f2, monitor):
    THRESHOLD1 = 'threshold1'
    THRESHOLD2 = 'threshold2'
    TYPE = 'type' # 0 = Monitor, 1 = seed_fake1, 2= seed_fake2
    ACT_FAKE = 'act_fake'   # 1 = fake1, 2= fake2
    ACT_FAKE1_NEIGH = 'act_fake1_neigh'
    ACT_FAKE2_NEIGH = 'act_fake2_neigh'
    stable = False # parametro usato per fermare la dinamica

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
    fake1 = seed_f1
    fake2 = seed_f2
    while not stable:
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
                        fake1 = {i}
                        break
                    if ACT_FAKE2_NEIGH in graph.node[i] and graph.node[i][ACT_FAKE2_NEIGH] > graph.node[i][THRESHOLD2] and (ACT_FAKE1_NEIGH not in graph.node[i] or (ACT_FAKE1_NEIGH in graph.node[i] and graph.node[i][ACT_FAKE1_NEIGH] < graph.node[i][THRESHOLD1])) and (
                            ACT_FAKE not in graph.node[i] or (ACT_FAKE in graph.node[i] and graph.node[i][ACT_FAKE] == 1)):
                        fake2 = {i}
                        break
            if len(fake1) == 0 and len(fake2) == 0:
                stable = True

    return graph

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


def random_seed1(g):
    seeds = {random.choice(list(g.nodes())) for i in range(int(g.number_of_nodes() / 10))}
    return seeds

def random_monitor(g, seed1):
    monitor = set()
    while len(monitor) < g.number_of_nodes()/4:
        node = random.choice(list(g.nodes()))
        if node not in seed1:
            monitor.add(node)

    return monitor


def random_seed2(g, seed1, monitor):
    seeds= set()
    while len(seeds) < g.number_of_nodes() / 10:
        node = random.choice(list(g.nodes()))
        if node not in seed1 and node not in monitor:
            seeds.add(node)

    return seeds


def test_bsdm():
    path = "./WS2DGrid_0_1000_r5_k6.txt"
    g = nx.read_edgelist(path, create_using=nx.Graph())
    seed_f1 = random_seed1(g)
    monitor = random_monitor(g, seed_f1)
    seed_f2 = random_seed2(g, seed_f1, monitor)
    n_it = 10
    res1 =[]
    res2 =[]
    for i in range(n_it):
        #print("\r" + "{0:.2f}".format(i / n_it * 100), end="")
        out = get_opinion_stats(bsdm(g, seed_f1, seed_f2, monitor),output=True)
        print("tot: "+str(sum(out)))
        g = nx.read_edgelist(path, create_using=nx.Graph())

if __name__ == '__main__':
    test_bsdm()