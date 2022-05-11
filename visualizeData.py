# Copyright (c) 2021 Ladislav Čmolík
#
# Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is 
# hereby granted.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE 
# INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE 
# FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS 
# OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING 
# OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import sys, random, math
from turtle import Pen
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QSizePolicy, QWidget, QHBoxLayout, QListWidget
from PySide6.QtGui import QBrush, QPen, QTransform, QPainter, QColor

import json

SELECTED = QBrush(Qt.red)
NEIGHBOUR_SELECTED = QBrush(Qt.green)
NOT_SELECTED = QBrush(Qt.gray)
ITEM_NOT_SELECTED = QBrush(Qt.white)

OUTLINE = QPen(Qt.black, 1)
BLACK_PEN = QPen(NOT_SELECTED, 3)
CONNECTION_HIGHLIGHT = QPen(NEIGHBOUR_SELECTED, 5)
BOTH_CONNECTED = QPen(SELECTED, 15)
NO_PEN = QPen(Qt.NoPen)

class Connection():
    def __init__(self, edge, otherName) -> None:
        self.otherName = otherName
        self.edge = edge
        self.elipse = None
    def elipse(self, elipse):
        self.elipse = elipse

class VisualObjects():
            
    selected = []
    selectedNames = []
    namesOfElipses = {} # elipse : name
    scientistDetails = {} #name : connections
    listOfNames = None

    def init(scientists):
        for key in scientists.keys():
            VisualObjects.scientistDetails[key] = []

    def selectScientist(jmeno):
        for elipse in VisualObjects.namesOfElipses.keys():
            if VisualObjects.namesOfElipses[elipse]["name"] is jmeno:
                VisualObjects.selectElipse(elipse)

    def selectElipse(elipse):
        item = VisualObjects.findItem(elipse)
        name = VisualObjects.namesOfElipses[elipse]
        VisualObjects.listOfNames.scrollToItem(item)        
        
        if elipse in VisualObjects.selected:
            VisualObjects.selected.remove(elipse)
            
            VisualObjects.selectedNames.remove(name)
            
            if VisualObjects.deselectEdges(elipse):
                elipse.setBrush(NEIGHBOUR_SELECTED)
                item.setBackground(NEIGHBOUR_SELECTED)
            else:
                elipse.setBrush(NOT_SELECTED)
                item.setBackground(ITEM_NOT_SELECTED)      
        else:
            VisualObjects.selected.append(elipse)
            VisualObjects.selectedNames.append(name)

            elipse.setBrush(SELECTED)
            item.setBackground(SELECTED)
            VisualObjects.selectEdges(elipse)

    def selectEdges(elipse):
            edges = VisualObjects.scientistDetails[VisualObjects.namesOfElipses[elipse]]
            isSomeOfNeighboursConnected = False
            for edge in edges:
                if edge.otherName in VisualObjects.selectedNames:
                    edge.edge.setPen(BOTH_CONNECTED)   
                    isSomeOfNeighboursConnected = True     
                else:
                    edge.elipse.setBrush(NEIGHBOUR_SELECTED)
                    VisualObjects.findItem(edge.elipse).setBackground(NEIGHBOUR_SELECTED)
                    edge.edge.setPen(CONNECTION_HIGHLIGHT)
            return isSomeOfNeighboursConnected
    
    def deselectEdges(elipse):
            edges = VisualObjects.scientistDetails[VisualObjects.namesOfElipses[elipse]]
            isSomeOfNeighboursConnected = False
            for edge in edges:
                if edge.otherName in VisualObjects.selectedNames:
                    isSomeOfNeighboursConnected = True
                    edge.edge.setPen(CONNECTION_HIGHLIGHT)
                else:
                    edge.edge.setPen(BLACK_PEN)
                VisualObjects.checkNeighboursSelected(edge.elipse)
            return isSomeOfNeighboursConnected
    
    def checkNeighboursSelected(elipse):
        if elipse not in VisualObjects.selected:
            edges = VisualObjects.scientistDetails[VisualObjects.namesOfElipses[elipse]]
            for edge in edges:
                if edge.otherName in VisualObjects.selectedNames:
                    return
            elipse.setBrush(NOT_SELECTED)
            VisualObjects.findItem(elipse).setBackground(ITEM_NOT_SELECTED)

    def computeMissingElipses():
        for scientist in VisualObjects.scientistDetails:
            for edge in VisualObjects.scientistDetails[scientist]:
                edge.elipse = VisualObjects.findElipseByName(edge.otherName)

    def findItem(elipse):
        name = VisualObjects.namesOfElipses[elipse]
        return VisualObjects.listOfNames.findItems(name, Qt.MatchExactly)[0]
        
    def findElipseByName(name):
        for e in VisualObjects.namesOfElipses:
                if VisualObjects.namesOfElipses[e] == name: return e
class VisGraphicsScene(QGraphicsScene):
    def __init__(self):
        super(VisGraphicsScene, self).__init__()
        self.selection = None
        self.wasDragg = False
        self.pen = QPen(Qt.black)

    def mouseReleaseEvent(self, event): 
        if(self.wasDragg):
            return
        item = self.itemAt(event.scenePos(), QTransform())
        if item: VisualObjects.selectElipse(item)

class VisGraphicsView(QGraphicsView):
    def __init__(self, scene, parent):
        super(VisGraphicsView, self).__init__(scene, parent)
        self.startX = 0.0
        self.startY = 0.0
        self.distance = 0.0
        self.myScene = scene

        self.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)

    def wheelEvent(self, event):
        zoom = 1 + event.angleDelta().y()*0.001;
        self.scale(zoom, zoom)
        
    def mousePressEvent(self, event):
        self.startX = event.pos().x()
        self.startY = event.pos().y()
        self.myScene.wasDragg = False
        super().mousePressEvent(event)


    def mouseReleaseEvent(self, event):
        endX = event.pos().x()
        endY = event.pos().y()
        deltaX = endX - self.startX
        deltaY = endY - self.startY
        distance = math.sqrt(deltaX*deltaX + deltaY*deltaY)
        if(distance > 5):
            self.myScene.wasDragg = True
        super().mouseReleaseEvent(event)

               

class MainWindow(QMainWindow):
    
    def __init__(self, data):
        super(MainWindow, self).__init__()
        self.setWindowTitle('Colaboration on scientific papers')
        
        self.data = data
        VisualObjects.init(data)

        self.createGraphicView()
        self.generateAndMapData()
        self.listWidget.sortItems()

        self.setMinimumSize(1080, 720)
        self.show()

    def createGraphicView(self):
        self.scene = VisGraphicsScene()
        layout = QHBoxLayout()
        
        self.listWidget = QListWidget()
        self.listWidget.setMinimumWidth(200)
        self.listWidget.itemClicked.connect(self.Clicked)
        VisualObjects.listOfNames = self.listWidget

        layout.addWidget(self.listWidget)
        layout.addWidget(VisGraphicsView(self.scene, self))


        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        centralWidget.setGeometry(400, 400, 800, 800)
        self.setCentralWidget(centralWidget)

    def Clicked(self, item):
        elipse = VisualObjects.findElipseByName(item.text())
        VisualObjects.selectElipse(elipse)
        

    def generateAndMapData(self):
        #Map data to graphical elements
        POSITION_SCALE = 8000
        SIZE_SCALE = 5

        # vykreslíme hrany a až poté vědce, aby nedocházelo k překrývání    
        for name in self.data.keys():
            x1 = self.data[name]["pozice"][1]
            y1 = self.data[name]["pozice"][0]
            for spojeni in self.data[name]["spoluprace"]:
                        otherScientist = spojeni["druhyVedec"]
                        sila = spojeni["miraSpoluprace"] * SIZE_SCALE
                        if self.data[otherScientist]["pozice"][0] >= y1:
                                    line = self.scene.addLine(POSITION_SCALE*x1, POSITION_SCALE*y1, POSITION_SCALE*self.data[otherScientist]["pozice"][1], POSITION_SCALE*self.data[otherScientist]["pozice"][0], 
                                    QPen(NOT_SELECTED, sila))
                                    if not VisualObjects.scientistDetails[name]: VisualObjects.scientistDetails[name] = []
                                    if not VisualObjects.scientistDetails[otherScientist]: VisualObjects.scientistDetails[otherScientist] = []

                                    VisualObjects.scientistDetails[name].append(Connection(line, otherScientist))
                                    VisualObjects.scientistDetails[otherScientist].append(Connection(line, name))
        for name in self.data.keys():
            degree = len(self.data[name]["spoluprace"])

            brush = NOT_SELECTED
            pen = OUTLINE
            d = SIZE_SCALE*(degree+2)

            if degree > 10:
                    d = SIZE_SCALE*12
            elipse = self.scene.addEllipse(POSITION_SCALE*self.data[name]["pozice"][1]-d/2, POSITION_SCALE*self.data[name]["pozice"][0]-d/2, d, d, pen, brush)
            VisualObjects.namesOfElipses[elipse] = name
            self.listWidget.addItem(name)

        VisualObjects.computeMissingElipses()

def main():
            
    # načíst slovník z data.json
    with open('data.json') as json_file:
        data = json.load(json_file)

    app = QApplication(sys.argv)
    ex = MainWindow(data)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
