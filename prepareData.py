import math
import json
import networkx as nx
from random import random
import matplotlib.pyplot as plt

import scipy
import numpy

minD = 0.05
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

    def __getitem__(self, item):
        return self.pozice
    def __setitem__(self, key, value):
        self.pozice=value





##################################################################
# Nacteni vstupu a urceni inicialni pozice

input = "sourceData.gml"
output = "output.txt"

G = nx.read_gml(input)
pracovnikuMame = len(G.nodes)
pracovnici = {}
x, y = 0, 0

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
# attractive force
def f_a(d, k):
    force = d*d / k
    return force


# repulsive force
def f_r(d, k):
    force = k*k / d
    return force


def fruchterman_reingold(G, iteration=50, cnt=0):
    W = 1
    L = 1
    area = W * L
    k = (area / len(pracovnici))*10

    # initial position
    for v in G.nodes():
        G._node[v]['x'] = W * random()
        G._node[v]['y'] = L * random()

    t = W / 5
    dt = t / (iteration + 1)

    print("area:{0}".format(area))
    print("k:{0}".format(k))
    print("t:{0}, dt:{1}".format(t, dt))

    for i in range(iteration):
        print("iter {0} t: {1}".format(i, t))

        pos = {}
        for v in G.nodes():
            pos[v] = [G._node[v]['x'], G._node[v]['y']]
        plt.close()
        plt.ylim([-0.1, 1.1])
        plt.xlim([-0.1, 1.1])
        plt.axis('off')
        nx.draw_networkx(G, pos=pos, node_size=10, width=0.1, with_labels=False)
        if i % 5 == 0:
            plt.savefig("fig/{0}.png".format(i))

        # calculate repulsive forces
        for v in G.nodes():
            G._node[v]['dx'] = 0
            G._node[v]['dy'] = 0
            for u in G.nodes():
                if v != u:
                    dx = G._node[v]['x'] - G._node[u]['x']
                    dy = G._node[v]['y'] - G._node[u]['y']
                    delta = math.sqrt(dx * dx + dy * dy)
                    if delta != 0:
                        d = f_r(delta, k) / delta
                        G._node[v]['dx'] += dx * d
                        G._node[v]['dy'] += dy * d

        # calculate attractive forces
        for v, u in G.edges():
            dx = G._node[v]['x'] - G._node[u]['x']
            dy = G._node[v]['y'] - G._node[u]['y']
            delta = math.sqrt(dx * dx + dy * dy)
            if delta < minD: delta = 0
            if delta != 0:
                d = f_a(delta, k) / delta
                ddx = dx * d
                ddy = dy * d
                G._node[v]['dx'] += -ddx
                G._node[u]['dx'] += +ddx
                G._node[v]['dy'] += -ddy
                G._node[u]['dy'] += +ddy

        # limit the maximum displacement to the temperature t
        # and then prevent from being displace outside frame
        for v in G.nodes():
            dx = G._node[v]['dx']
            dy = G._node[v]['dy']
            disp = math.sqrt(dx * dx + dy * dy)
            if disp != 0:
                cnt += 1
                d = min(disp, t) / disp
                x = G._node[v]['x'] + dx * d
                y = G._node[v]['y'] + dy * d
                x = min(W, max(0, x)) - W / 2
                y = min(L, max(0, y)) - L / 2
                G._node[v]['x'] = min(math.sqrt(W * W / 4 - y * y), max(-math.sqrt(W * W / 4 - y * y), x)) + W / 2
                G._node[v]['y'] = min(math.sqrt(L * L / 4 - x * x), max(-math.sqrt(L * L / 4 - x * x), y)) + L / 2

        # cooling
        t -= dt

    pos = {}
    for v in G.nodes():
        pos[v] = [G._node[v]['x'], G._node[v]['y']]
    plt.close()
    plt.ylim([-0.1, 1.1])
    plt.xlim([-0.1, 1.1])
    plt.axis('off')
    nx.draw_networkx(G, pos=pos, node_size=10, width=0.1, with_labels=False)
    if i % 5 == 0:
        plt.savefig("fig/{0}.png".format(i + 1))

    return pos


def main():
    G = nx.read_gml(input)

    pos = fruchterman_reingold(G)
    i=0
    for pracovnik in pracovnici:
        positioneee=pos[pracovnik]
        postx=float(positioneee[0])
        posty = float(positioneee[1])
        newpos=(postx,posty)
        pracovnici[pracovnik]["pozice"]=newpos

    plt.close()
    plt.ylim([-0.1, 1.1])
    plt.xlim([-0.1, 1.1])
    plt.axis('off')
    nx.draw_networkx(G, pos=nx.spring_layout(G), node_size=10, width=0.1, with_labels=False)
    plt.savefig("fig/orig.png")


if __name__ == "__main__":
    main()

##################################################################
# ulozeni do souboru
with open('data.json', 'w') as f:
    json.dump(pracovnici, f, default=vars)
