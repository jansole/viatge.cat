import networkx as nx
from networkx.readwrite import json_graph
import simplejson as json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import sqrt
import geopandas as gpd
from shapely.geometry import Polygon, shape
from itertools import combinations
import time
import random
import copy

def generacio_inici_desti(G, comarques, minim=3):

    lloc1 = comarques[0]  # node clau
    # print(lloc1)

    # agafem distancies i ens quedem amb les que estiguin a 3 o més, sino es massa fàcil
    distances = nx.single_source_shortest_path_length(G, lloc1)
    nodes_propers = [node for node, dist in distances.items() if dist <= minim]

    # traiem les opcions que no compleixin
    opcions = np.setdiff1d(comarques, [lloc1])
    opcions = np.setdiff1d(opcions, nodes_propers).tolist()
    random.shuffle(opcions)

    lloc2 = opcions[0] # destí

    camins = list(nx.all_shortest_paths(G, source=lloc1, target=lloc2))
    t1 = time.time()
    
    #print(camins) #Solucions
    print(f'Avui vull anar des de {lloc1} fins a {lloc2}...\n')
    return lloc1, lloc2, camins


def solucio_trobada(cami, camins):
    # Unió de tots els nodes presents en totes les solucions possibles
    nodes_valids = set(node for solucio in camins for node in solucio)
    
    # Filtrar el camí de l'usuari per només incloure nodes vàlids
    cami_filtrat = [node for node in cami if node in nodes_valids]
    
    # Comprovar si alguna solució és subconjunt del camí filtrat
    for solucio in camins:
        if set(solucio).issubset(cami_filtrat):
            return True
    
    return False