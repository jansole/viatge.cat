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

########## COMARQUES
dfcomarq = {}

with open('fitxers\divisions-administratives-v2r1-comarques-250000-20240705.json', 'r', encoding='utf-8') as f:
    dades_fronteres = json.load(f)

for comarca in dades_fronteres['features']:
    
    codi_municipi = comarca['properties']['CODICOMAR']
    delimitacio = shape(comarca['geometry']) # tenim en compte totes les formes

    dfcomarq[codi_municipi] = {
        'frontera': delimitacio,
        'nom': comarca['properties']['NOMCOMAR'],
        'capital': comarca['properties']['CAPCOMAR'],
        'area': comarca['properties']['AREAC5000']
    }

G = nx.Graph()

# Afegim els nodes amb les característiques
for comarca in dfcomarq.items():
    codi_comarca = comarca[0]
    _x = dfcomarq[codi_comarca]['frontera'].centroid.x
    _y = dfcomarq[codi_comarca]['frontera'].centroid.y
    
    # agafem la posició central del municipi, ho traiem del diccionari de csv --> passat a int
    G.add_node(dfcomarq[codi_comarca]['nom'], x = _x*500, y = _y*500,
               codi=codi_comarca, 
               capital=comarca[1]['capital'],
               area = comarca[1]['area'])
    
# Afegim arestes segons si les fronteres mostren adjacència

print("Nombre de comarques detectades:", len(list(G.nodes)))

fnt = 0
for node1, node2 in combinations(G.nodes, 2):  #totes les combinacions possibles
    poly1 = dfcomarq[G.nodes[node1]['codi']]['frontera']
    poly2 = dfcomarq[G.nodes[node2]['codi']]['frontera']

    # comprovem si fa frontera amb una mica de tolerancia
    tolerancia = 0.0001
    if poly1.buffer(tolerancia).intersects(poly2.buffer(tolerancia)):
        G.add_edge(node1, node2)
        fnt += 1

print("Nombre de fronteres:", fnt)
pos = {node: (data['x'], data['y']) for node, data in G.nodes(data=True)}
nx.write_graphml(G, './grafs/comarques.graphml')