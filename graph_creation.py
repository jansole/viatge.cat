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

df = {}

#diccionari on guardem les coordenades UTM dels municipis
posicions = pd.read_csv('./fitxers/Municipis_Catalunya_Geo.csv', encoding='utf-8')
posicions = {row['Codi']: (row['Longitud'], row['Latitud']) for _, row in posicions.iterrows()}

with open('fitxers\divisions-administratives-v2r1-municipis-250000-20240705.json', 'r', encoding='utf-8') as f:
    dades_fronteres = json.load(f)

for municipi in dades_fronteres['features']:
    
    codi_municipi = municipi['properties']['CODIMUNI']
    delimitacio = shape(municipi['geometry']) # tenim en compte totes les formes

    df[codi_municipi] = {
        'frontera': delimitacio,
        'nom': municipi['properties']['NOMMUNI'],
        'comarca': municipi['properties']['NOMCOMAR'],
        'capital': municipi['properties']['CAPCOMAR'],
        'vegueria': municipi['properties']['NOMVEGUE'],
        'provincia': municipi['properties']['NOMPROV']
    }

G = nx.Graph()

# Afegim els nodes amb les característiques
for municipi in df.items():
    codi_municipi = municipi[0]
    
    # agafem la posició central del municipi, ho traiem del diccionari de csv --> passat a int
    G.add_node(municipi[1]['nom'], x=posicions[int(codi_municipi)][0]*500, y = posicions[int(codi_municipi)][1]*500,
               codi=codi_municipi, 
               comarca=municipi[1]['comarca'], 
               capital=municipi[1]['capital'], 
               vegueria=municipi[1]['vegueria'], 
               provincia=municipi[1]['provincia'])
    
# Afegim arestes segons si les fronteres mostren adjacència

print("Nombre de municipis detectats:", len(list(G.nodes)))

fnt = 0
for node1, node2 in combinations(G.nodes, 2):  #totes les combinacions possibles
    poly1 = df[G.nodes[node1]['codi']]['frontera']
    poly2 = df[G.nodes[node2]['codi']]['frontera']

    # comprovem si fa frontera amb una mica de tolerancia
    tolerancia = 0.0001
    if poly1.buffer(tolerancia).intersects(poly2.buffer(tolerancia)):
        G.add_edge(node1, node2)
        fnt += 1

G.add_edge('Puigcerdà', 'Llívia') # Sino el graf ens quedava separat en dues components connexes. És el que té més sentit
fnt += 1
print("Nombre d'arestes (fronteres):", fnt)

pos = {node: (data['x'], data['y']) for node, data in G.nodes(data=True)}
nx.draw(G, pos, with_labels=True)
nx.write_graphml(G, 'catalunya.graphml')


