import networkx as nx
import matplotlib.pyplot as plt
from math import radians, cos, sin, asin, sqrt


import matplotlib.pyplot as plt
#import plotly.graph_objects as go
import networkx as nx
import scipy as sp
from random import seed
from random import randint
import networkx as nx


import networkx as nx
from random import seed, randint
import math
import xml.etree.ElementTree as ET


import networkx as nx
import matplotlib.pyplot as plt

# GML dosyasını oku
S = "/home/hilal/Documents/networks/TU DRESDEN2/TU_Dresden_Suedvorstadt_connected2.gml"
G = nx.read_gml(S)

# Node pozisyonlarını hesapla (örneğin spring layout kullanarak)
pos = nx.spring_layout(G, seed=42)

# Ağı çiz
plt.figure(figsize=(10, 8))
nx.draw(G, pos, with_labels=True, node_size=500, node_color='lightblue', font_size=10, edge_color='gray')

# Kenar etiketlerini hazırla
edge_labels = {}
for u, v, data in G.edges(data=True):
    label = data.get('distance_km')
    if label is not None:
        edge_labels[(u, v)] = f"{float(label):.2f} km"  # örn: "2.35 km"

# Kenar etiketlerini çiz
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red', font_size=8)

plt.title("Graph with Edge Distances")
plt.show()
