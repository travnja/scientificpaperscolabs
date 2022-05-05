from msilib.schema import File
import os
import networkx as nx
import numpy as np

class Spoluprace:
        def __init__(self, druhyVedec, miraSpoluprace):
                self.druhyVedec = druhyVedec.id
                self.miraSpoluprace = miraSpoluprace

class Pracovnik:
        def __init__(self, id, jmeno):
                self.id = id
                self.jmeno = jmeno
                self.spoluprace = []
                self.pozice = (0.0, 0.0)
        
        def pridejSpolupraci(self, druhyVedec, miraSpoluprace):
                self.spoluprace.append(Spoluprace(druhyVedec=druhyVedec, miraSpoluprace=miraSpoluprace))
                druhyVedec.pridejReciprocneSpolupraci(self, miraSpoluprace)

        def pridejReciprocneSpolupraci(self, druhyVedec, miraSpoluprace):
                self.spoluprace.append(Spoluprace(druhyVedec=druhyVedec, miraSpoluprace=miraSpoluprace))



input = "sourceData.gml"
output = "output.txt"


G = nx.read_gml(input)
pracovnikuMame = len(G.nodes)
pracovnici = [None] * pracovnikuMame
i = 0

for vrchol in G.nodes():
        print(vrchol)
        pracovnici[i] = Pracovnik(id=i, jmeno=vrchol[0])
        i += 1
print("->", pracovnikuMame)

# for hrana in G.edges.data():
        # print(hrana)
        # pracovnici[int(hrana[0])].pridejSpolupraci(pracovnici[int(hrana[1])], int(hrana[2]['weights']))

