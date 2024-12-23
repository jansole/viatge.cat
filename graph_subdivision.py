"""Document on passarem de tenir un graf de municipis, a grafs de comarques/vegueries..."""

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

catalunya = nx.read_graphml('./grafs/catalunya.graphml')
nx.draw(catalunya)
plt.show()