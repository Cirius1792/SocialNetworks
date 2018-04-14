"""Vogliamo identificare delle comunità all'interno della rete,dove per comunità intendiamo un insieme di persone in
cui ogni nodo può raggiungere tutti gli altri. In pratica ci interessa una componente connessa o fortemente connessa"""
import math
import networkx as nx
import itertools as it
import joblib
from joblib import Parallel, delayed

"""Algoritmo di Tarjan: molto efficiente per trovare le componenti connesse.
Lavora contemporaneamente su due grafi, su G ed il suo inverso, effettua un DFS partendo da un nodo qualsiasi di G^-1. 
Ogni nodo visitato viene aggiunto ad una componente. Non ci si ferma quando finisce la visita in profondita', ma ricominciamo 
 da capo sull'insieme di nodi a cui abbiamo tolto quelli gia' visitati. Questo insieme corrisponde ad una nuova componente.
 
 Nonostante l'efficienza, e' difficile da parallelizzare, visto che devo comunque considerare un nodo alla volta."""

"""
se v appartiene alla lista dei nodi visitati nel grafo G a partire da u ed anche a quella dei nodi visitabili nel grafo G^-1
allora u e v sono nella stessa componente connessa. Posso usare questo risultato per mettere in piedi un algorirmo migliore del
precedente per la ricerca delle componenti connesse considerando l'intersezione degli insiemi di nodi raggiungibili da u in 
G e G^-1.

"""

def strongly2(G):
    graph = G.copy()
    comp = dict()
    done = False
    while not done:
        changed = False
        for node in graph.node():
            visited=set()
            queue = [node]
            while len(queue) > 0:
                u = queue.pop()
                for v in graph[u]:
                    queue.append(v)
                visited.add(u)

            igraph=graph.reverse(False)
            ivisited = set()
            queue = [node]
            while len(queue) > 0:
                u = queue.pop()
                for v in igraph[u]:
                    queue.append(v)
                ivisited.add(u)

            if len(visited&ivisited) > 1: #& intersezione degli insiemi
                comp[node] = visited&ivisited
                #ora che abbiamo trovato la componente connessa dobbiamo toglierla dal grafo e procedere con l'alogirtmo per
                #trovare le altre. La rimozione si fa rinominando tutti i nodi della componente con uno stesso nome e poi
                #utilizzeremo una specifica funzione di networkx per ristrutturare la rete
                mapping = {k:node for k in comp[node]}
                graph=nx.relabel_nodes(graph, mapping, copy=False)
                if graph.has_edge(node,node):
                    graph.remove_edge(node,node) #rimuovo un eventuale autociclo
                changed = True
                break
        if not changed :
            done = True
    """Parallelizzabile perche' posso far partire lo stesso algoritmo sullo stesso grafo ma da nodi diversi"""

    return comp

"""
una componente connessa non e' necessariamente una comunita', una clique sicuramente lo e' ma e' un concetto troppo strigente.
Possiamo considerare quindi un gruppo di S persone con almeno T amici in comune, in pratica stiamo rilassando il concetto di
clique, ottenendo un insieme comunque molto denso di nodi. Un algoritmo che fa questo si chiama Apriori, nato nell'ambito delle
indagini di mercato con lo scopo di trovare gruppi di prodotti che vengono comprati assieme. 
In un primo passaggio posso scartare tutti i prodotti comprati meno di s volte
poi considero tutte le coppie e scarto quelli comprati meno di s volte
poi tutte le triple etc

Per controllare tutti gli elementi ho O(n), mentre ci sono n^2 coppie, ma alla seconda iterazione non le controllo tutte,
ma sicuramente meno visto che ho gia' scartato un buon numero di prodotti. Stesso discorso vale per le triple e cosi' via.

Come si sceglgono s e t? dato un grafo di n nodi con grado medio d, scelti s e t secondo la formula che ti vai a vedere sullibro,
allora c'e' un'alta probabilita' che esista un grafo bipartito completo

Vediamo la versione parallelizzabile:
"""
def apriori(B,N,s,t):
    pass

def chunks(data, SIZE=10000):
    pass

def par_apriori(B,N,s,t,j):
    """dividiamo i basket per i processori che vogliamo utilizzare, quelli si fanno i conti e poi metto assieme quando hanno finito.
    j = numero di processori a disposizione"""

    p = 1./j
    with Parallel(n_jobs=j) as parallel:
        # eseugi in maniera parallela la funzione apriori con i parametri tot
        results = Parallel(delayed(apriori)(i, N, max(1,math.f(p*s)))  for i in chunks(B,int(p*len())))
