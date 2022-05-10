import math
import json
from tkinter import E
import networkx as nx

class Spoluprace:
        def __init__(self, druhyVedec, miraSpoluprace):
                self.druhyVedec = druhyVedec.jmeno
                self.miraSpoluprace = miraSpoluprace

class Pracovnik:
        def __init__(self, jmeno):
                self.jmeno = jmeno
                self.spoluprace = []
                self.pozice = (0.0, 0.0)
        
        def pridejSpolupraci(self, druhyVedec, miraSpoluprace):
                self.spoluprace.append(Spoluprace(druhyVedec=druhyVedec, miraSpoluprace=miraSpoluprace))
                druhyVedec.pridejReciprocneSpolupraci(self, miraSpoluprace)

        def pridejReciprocneSpolupraci(self, druhyVedec, miraSpoluprace):
                self.spoluprace.append(Spoluprace(druhyVedec=druhyVedec, miraSpoluprace=miraSpoluprace))

##################################################################
# Nacteni vstupu a urceni inicialni pozice

input = "sourceData.gml"
output = "output.txt"


G = nx.read_gml(input)
pracovnikuMame = len(G.nodes)
pracovnici = {}
x,y = 0, 0

breakAfter = math.sqrt(pracovnikuMame)

for vrchol in G.nodes():
        pracovnici[vrchol] = Pracovnik(vrchol)
        pracovnici[vrchol].pozice = (y, x)
        x += 1
        if x >= breakAfter: 
                x = 0
                y += 1

for hrana in G.edges.data():
        pracovnici[hrana[0]].pridejSpolupraci(pracovnici[hrana[1]], int(hrana[2]['value']))

##################################################################
# vypocet pozice







##################################################################
# ulozeni do souboru
with open('data.json', 'w') as f:
    json.dump(pracovnici, f, default=vars)

