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
import funcions_joc as fj
import math

### CALAIX DE LES CONSTANTS
K = 1.25
G = nx.read_graphml('./grafs/comarques.graphml')
comarques = list(G.nodes()) # agafem les comarques i desordenem

### INICI DEL JOC
random.shuffle(comarques)
inici, desti, camins = fj.generacio_inici_desti(G, comarques) # generació de cami
cami = [inici, desti] #cami que omplirà l'usuari

minim_torns = len(camins[0])
torns_totals = math.ceil(minim_torns * K + 1)

torns = 0
inputs = []
while not fj.solucio_trobada(cami, camins) and torns < torns_totals: # mentre no trobi la solució i porti menys torns que el total
    print(f'Torn {torns} de {torns_totals}:')
    inp = input('Introdueix una comarca: ')
    print('\n')
    if inp in comarques and inp not in cami:
        cami.append(inp)
        inputs.append(inp + fj.calcul_proximitat(G, inp, camins))
        torns +=1
    print(inputs)

if fj.solucio_trobada(cami, camins):
    print('Has trobat la solució!')
    print(f"Llargada mínima: {minim_torns-2} - El teu intent: {torns}")
else: print('Has fallat :(')
