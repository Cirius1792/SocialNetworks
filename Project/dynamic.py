import random
from statistics import mean
import matplotlib.pyplot as plt
import networkx as nx
import math

THRESHOLD1 = 'threshold1'
THRESHOLD2 = 'threshold2'
TYPE = 'type'  # 0 = Monitor, 1 = seed_fake1, 2= seed_fake2
ACT_FAKE = 'act_fake'  # 1 = fake1, 2= fake2
ACT_FAKE1_NEIGH = 'act_fake1_neigh'
ACT_FAKE2_NEIGH = 'act_fake2_neigh'
FAKE1_COLOR = 'red'
FAKE2_COLOR = 'aquamarine'
MONITOR_COLOR = 'white'

class BSDM:



    def __init__(self, th1=0.5, th2=0.5, name='graph', out_path=None):
        self._f1_over_f2 = []
        self._th1 = th1
        self._th2 = th2
        self._iteration = 0
        self._nodes_colors = None
        self._seed_f1 = None
        self._seed_f2 = None
        self._name = name
        self._out_path=out_path
        
    def bsdm(self, graph, seed_f1, seed_f2, monitor, plot_steps=False, save_plots=False):
        self._seed_f1 = seed_f1
        self._seed_f2 = seed_f2
        self._monitor = monitor
        stable = False  # parametro usato per fermare la dinamica
        thresholds = nx.get_node_attributes(graph, THRESHOLD1)
        if len(thresholds) == 0:
            for i in graph.nodes():
                graph.node[i][THRESHOLD1] = random.random() * self._th1 * len(graph[i])
                graph.node[i][THRESHOLD2] = random.random() * self._th1 * len(graph[i])
                if i in seed_f1:
                    graph.node[i][TYPE] = 1
                elif i in monitor:
                    graph.node[i][TYPE] = 0
                elif i in seed_f2:
                    graph.node[i][TYPE] = 2

        fake1 = seed_f1
        fake2 = seed_f2
        self._iteration = 0
        self._f1f2_tmp = 0
        while not stable:
            if len(fake1) > 0 or len(fake2) > 0:
                fake1, fake2 = self.evolve(graph, fake1, fake2)
                if plot_steps:
                    self._plot_step(graph, save_plots)
                if len(fake1) == 0 and len(fake2) == 0:
                    stable = True
                self._iteration += 1
                #Salvo lo stato attuale di diffusione per il plot

        f1_over_f2 = self._f1f2_tmp/ self._iteration
        self._f1_over_f2.append(f1_over_f2)
        self._graph = graph
        return graph

    def evolve(self, graph, fake1, fake2):
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
                if ACT_FAKE1_NEIGH in graph.node[i] and graph.node[i][ACT_FAKE1_NEIGH] > graph.node[i][
                    THRESHOLD1] and (ACT_FAKE not in graph.node[i] or (
                        ACT_FAKE in graph.node[i] and graph.node[i][ACT_FAKE] == 2)):
                    if (ACT_FAKE1_NEIGH in graph.node[i] and ACT_FAKE2_NEIGH in graph.node[i]):
                        if graph.node[i][ACT_FAKE1_NEIGH] > graph.node[i][THRESHOLD1] and graph.node[i][
                            ACT_FAKE2_NEIGH] > graph.node[i][THRESHOLD2]:
                            self._f1f2_tmp += 1
                    fake1 = {i}
                    break
                if ACT_FAKE2_NEIGH in graph.node[i] and graph.node[i][ACT_FAKE2_NEIGH] > graph.node[i][
                    THRESHOLD2] and (ACT_FAKE1_NEIGH not in graph.node[i] or (
                        ACT_FAKE1_NEIGH in graph.node[i] and graph.node[i][ACT_FAKE1_NEIGH] < graph.node[i][
                    THRESHOLD1])) and (
                        ACT_FAKE not in graph.node[i] or (
                        ACT_FAKE in graph.node[i] and graph.node[i][ACT_FAKE] == 1)):
                    fake2 = {i}
                    break
        return fake1, fake2

    def mean_f1_over_f2(self):
        return mean(self._f1_over_f2) if self._f1_over_f2 else -1

    def get_iteration(self):
        return self._iteration

    def show_opinions(self):
        active = nx.get_node_attributes(self._graph, 'act_fake')
        print(["nodo: " + str(i) + " op:" + str(self._graph.node[i]['act_fake']) for i in active.keys() if active[i]])

    def get_diffusion_stats(self, output=False):
        active = nx.get_node_attributes(self._graph, 'act_fake')
        diffusion = [0, 0, 0]  # diffusion[0] = % opinioni fake1, diffusion[1] = % opinioni fake2
        n_nodes = self._graph.number_of_nodes()
        for i in active:
            if self._graph.node[i]['act_fake'] == 1:
                diffusion[0] += 1
            else:
                diffusion[1] += 1
        diffusion[0] = diffusion[0] / n_nodes
        diffusion[1] = diffusion[1] / n_nodes
        diffusion[2] = (n_nodes - len(active)) / n_nodes
        if output:
            print("iterations:\t "+str(self._iteration))
            print("f1 over f2: \t" + "{0:.4f}".format(mean(self._f1_over_f2)))
            print("opinion 1: " + "{0:.2f}".format(diffusion[0]) + "\t opinion 2:" + "{0:.2f}".format(
                diffusion[1]) + "\t no opinion:" + "{0:.2f}".format(diffusion[2]))
        return diffusion

    def rest_plot(self):
        self._nodes_colors = None

    def _plot_step(self, graph, save_plots):
        if not self._nodes_colors:
            self._layout = nx.kamada_kawai_layout(graph)
            self._nodes_colors = dict()
            for n in graph.nodes():
                if n in self._seed_f1:
                    self._nodes_colors[n] = FAKE1_COLOR
                elif n in self._seed_f2:
                    self._nodes_colors[n] = FAKE2_COLOR
                elif n in self._monitor:
                    self._nodes_colors[n] = MONITOR_COLOR
                else:
                    self._nodes_colors[n] = 'gray'

        active = nx.get_node_attributes(graph, 'act_fake')
        for node in active:
            self._nodes_colors[node] = 'red' if graph.nodes[node][ACT_FAKE] == 1 else 'blue'
        nx.draw_networkx(graph, self._layout,nodelist=sorted(self._nodes_colors.keys()),node_color=[self._nodes_colors[node] for node in sorted(self._nodes_colors)] )
        plt.title("setp "+str(self._iteration))
        plt.axis('off')
        if save_plots:
            if self._out_path:
                dest = self._out_path + self._name + "step" + str(self._iteration) + ".png"
            else:
                dest = self._name+"step"+str(self._iteration)+".png"
            plt.savefig(dest)
        plt.show()

    def bsdm_random(self, graph, plot_steps=False, save_plots=False):
        seed1 = self.random_seed1(graph)
        monitor = self.random_monitor(graph, seed1)
        seed2 = self.random_seed2(graph, seed1, monitor)
        return self.bsdm(graph, seed1, seed2, monitor, plot_steps=plot_steps, save_plots=save_plots)

    def random_seed1(self, g):
        seeds = {random.choice(list(g.nodes())) for i in range(int(g.number_of_nodes() / 10))}
        return seeds

    def random_monitor(self, g, seed1):
        monitor = set()
        while len(monitor) < g.number_of_nodes() / 4:
            node = random.choice(list(g.nodes()))
            if node not in seed1:
                monitor.add(node)

        return monitor

    def random_seed2(self, g, seed1, monitor):
        seeds = set()
        while len(seeds) < g.number_of_nodes() / 10:
            node = random.choice(list(g.nodes()))
            if node not in seed1 and node not in monitor:
                seeds.add(node)

        return seeds



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

    d = BSDM(name="test", out_path="./plot_steps/")
    d.bsdm(g,{7},{1},{6}, plot_steps=True, save_plots=True)
    d.get_diffusion_stats(True)
    d.show_opinions()

def test_powerlaw():
    g = nx.read_adjlist("./generated_networks/config_power_law.txt")
    d = BSDM(name="test", out_path="./plot_steps/power_law/")
    d.bsdm_random(g, plot_steps=True, save_plots=True)
    d.get_diffusion_stats(True)
    d.show_opinions()
def test_ws2dgrid():
    g = nx.read_adjlist("./generated_networks/ws2dg_20_2_1.txt")
    d = BSDM(name="test", out_path="./plot_steps/WS2DGrid/")
    d.bsdm_random(g, plot_steps=True, save_plots=True)
    d.get_diffusion_stats(True)
    d.show_opinions()

if __name__ == '__main__':
    test_ws2dgrid()
    test_powerlaw()