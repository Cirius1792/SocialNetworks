import math
import networkx as nx
import itertools as it

# il probema delle tecniche basate su BFS con i grafi di nostri interesse è la memoria, visto che dobbiamo tenere traccia dei nodi
# visitati. possiamo risparmiare memoria memorizzando l'hash del nodo anzichè il nodo stesso, ad esempio. Posso fare di meglio,
# memorizzo solo il numero di zeri nella parte finale dell'hash, per evitare collisioni posso fare questa cosa per più funzioni
# hash e salvarmi il numero di zeri in ognuna.
"""


"""
def num_triangles(G):
    m = nx.number_of_edges(G)
    num_triangles = 0

    heavy_hitters = set()
    for u in G.nodes():
        if G.degree(u) >= math.sqrt(m):
            heavy_hitters.add(u)
            #k*sqrt(m) deve essere minore di m quindi k non può essere maggiore di sqrt(m)
            #dunque l'inisieme di heavi_hitters non puù essere molto grande. Posso quindi cercare i triangoli in questo insieme
            #sapendo che non sono molti. Poi contare i triangoli fuori questo insieme

    #CONTO TRIANGOLI in HEAVI_HITTERS
    for triple in it.combinations(heavy_hitters, 3):
        # has_edge funziona anche per grafi diretti, ma bisogna stare attenti all'ordine
        if G.has_edge(triple[0], triple[1]) and G.has_edge(triple[0], triple[2]) and G.has_edge(triple[1], triple[2]):
            num_triangles += 1
            #visto che l'insieme può contenere al più radice d n nodi, il tempo richiesto sarà al più radice di n al cubo

    #CONTO TRIANGOLI NEGLI ALTRI NODI
    #i cicli interni nel conto dei triangoli (funzione a lezione) sono molto pesanti, ma se consideriamo che abbiao già contato i triangoli
    #composti da soli heavy_itters, i triangoli rimasti saranno quelli composti da almeno un nodo che non è heavy_itters, ovvero
    #con basso grado. Facendo partire il conto da questi nodi alleggeriamo i cicli interni.
    #Una seconda ottimizzazione è quella di considerare i triangoli una sola volta, posso pensare di farlo considerando i
    #nodi in ordine, come ad esempio ordinati sul nome (la loro etichetta)
    #m^(3/2)
    for edge in G.edges():# m volte
        sel = less(G,edge)
        #se il secondo è un heavy itters lo sarà anche il primo
        if edge[sel] not in heavy_hitters:
            for i in G[edge[sel]]:#m^(1/2)
                if less (G,[i, edge[1-sel]]) and G.has_edge(i,edge[1-sel]):
                    num_triangles += 1
    return num_triangles


def less(G,edge):
    if G. degree(edge[0]) < G.degree(edge[1]):
        return 0
    if G. degree(edge[0]) == G.degree(edge[1]) and edge[0] < edge[1]:
        return 0
    return 1

#Funzioni di supporto da recuperare

"""
    G grafo
    K numero di hash funztion da usare
"""


def hash_function(i):
    pass


def trailing_zeros(param):
    pass

#modificare questa funzione per ottenereil numero di nodi che posso visitare in n step partendo da un nodo u
def stream_diam(G, K):
    #per ogni hash function salvo il suo valore per ogni nodo
    #R=[{v:trailing_zeros(hash_function(i)) for v in G.nodes()} for i in range(K)]
    R= {v:G.degree(v) for v in G.nodes()}
    step = 0
    done = False
    #consideriamo come stream la sequenza degli archi
    while not done:
        step +=1
        done = True
        for edge in G.edges():
            for i in range(K):
                if R[i][edge[0]] != R[i][edge[1]]:
                    #per grafi diretti devo aggiornarne solo 1
                    R[i][edge[0]] = max(R[i][edge[0]], R[i][edge[1]])
                    R[i][edge[1]] = max(R[i][edge[0]], R[i][edge[1]])
                    done = False
    return step




#SNAP per le reti
#