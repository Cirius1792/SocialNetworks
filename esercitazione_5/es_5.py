import networkx as nx
import random
import math
import numpy
from scipy.special import zeta
#Dobbiamo creare dei grafi su cui fare test, e' meglio crearli simili alla realta' quindi la costruzione segue un processo
# probabilistico di tipo preferential attachment
#Random Graph Newman cap 12
def randomG(n,p):
    #Drawback: un grafo così costruito ha un basso coefficiente di clustering, ovvero non ci sono molte comunita', quindi
    #non e' simile ai grafi reali rappresentanti reti sociali, che sono appunto ricche di comunita'
    G = nx.Graph()
    for i in range(n):
        for j in range(i+1,n):
            r = random.random()
            if r>= p:
                G.add_edge(i,j)
    return G

#Configuration Model, Newman cap 13
#In questo caso il grafo viene costruito utilizzando non una probabilita' ma il grado atteso per ogni nodo della rete. In
# pratica uso il grado dei nodi della rete originale per costruirne una nuova che abbia una struttura simile i.e. i cui
# nodi abbiano gli stessi gradi
def configurationG(deg):
    G = nx.Graph()
    nodes = set(range(len(deg)))
    while len(nodes) > 1:
        #ad ogni step prendo due nodi dalla lista, creo un arco fra di loro e riduco il valore corrispondente in deg.
        # Se alla fine nella lista rimane un nodo solo
        edge = random.sample(list(nodes),2)
        #non controllo se il vertice gia' esiste perchè potrebbe non essere possibile trovare un edge che ancora non esiste
        #data la configurazione della rete. E' un limite del modello, ma comunque su grafi grandi le probabilita' che ci
        # sia un problema del genere sono scarse
        G.add_edge(edge[0],edge[1])
        deg[edge[0]] -= 1
        if deg[edge[0]] == 0:
            nodes.remove[edge[0]]
        deg[edge[1]] -= 1
        if deg[edge[1]] == 0:
            nodes.remove[edge[1]]
    return G
    #Anche in questo caso il coefficiente di clustering è scarso ed i grafi risultanti tenderanno ad avere una componente
    # gigante e alcune componenti piccoline di contorno

def power_low_degree(n,power):
    deg_list=[]

    deg = 1
    z = zeta(power)
    while len(deg_list)<n:
        #probabilita' p che il grado sia deg
        p = 1/(deg**power)*z #frazionde dei nodi che avranno grado deg
        num = math.ceil(p*n)
        if deg%2 == 1 and num%2==1:
            num -=1
        for i in range(num):
            if len(de_list) < n :
                deg_list.append(deg)
        deg += 1

    return deg_list

#costruzione di grafi sul modello preferential attachment: mi collego con probabilita' p ad una persona in maniera
# proporzionale al suo degree
def preferentialG(n,p):
    G = nx.Graph()
    nodes = [0]
    for u in range(1,n):
        r = random.random()
        if r <= p:
            v = random.choice(node) #un nodo appare nella lista tante volte quando è il suo grado, questo metodo di scegliere
            #il nodo mi assicura che la probabilita' scelta sia dipendente dal grado del nodo
            G.add_edge(u,v)
            if len(nodes) > 1: #questo controllo mi serve per la prima iterazione, per evitare di riaggiungere lo stesso nodo
                #alla lista
                nodes.append(v)
            nodes.add(u)
        else:
            v = random.choice(x for x in range(n if x != u))
            G.add_edge(u, v)
            if len(nodes) > 1:
                nodes.append(v)
            nodes.add(u)