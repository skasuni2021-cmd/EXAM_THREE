#region imports
import math
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
# No external GraphicsView_App dependency – we define RigidLink and RigidPivotPoint here.
#endregion

#region simple graphics items (replaces import from GraphicsView_App)
class RigidLink(qtw.QGraphicsLineItem):
    def __init__(self, x1, y1, x2, y2, radius=3, pen=None, brush=None, name=""):
        super().__init__(x1, y1, x2, y2)
        self.pen = pen if pen else qtg.QPen(qtc.Qt.orange)
        self.pen.setWidth(2)
        self.setPen(self.pen)
        self.brush = brush if brush else qtg.QBrush(qtg.QColor(255, 165, 0, 64))
        self.name = name
        self.setData(0, name)
        # tooltip will be set later
    def setToolTip(self, tip):
        super().setToolTip(tip)

class RigidPivotPoint(qtw.QGraphicsEllipseItem):
    def __init__(self, x, y, radius=10, size=20, pen=None, brush=None, name=""):
        super().__init__(x - radius, y - radius, size, size)
        self.pen = pen if pen else qtg.QPen(qtc.Qt.darkBlue)
        self.setPen(self.pen)
        self.brush = brush if brush else qtg.QBrush(qtg.QColor(215, 215, 215, 128))
        self.setBrush(self.brush)
        self.name = name
        self.setData(0, name)
#endregion

#region Position class (same as before, but kept minimal)
class Position():
    def __init__(self, pos=None, x=None, y=None, z=None):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        if pos is not None:
            self.x, self.y, self.z = pos
        self.x = x if x is not None else self.x
        self.y = y if y is not None else self.y
        self.z = z if z is not None else self.z
    def __sub__(self, other):
        return Position((self.x - other.x, self.y - other.y, self.z - other.z))
    def mag(self):
        return (self.x**2 + self.y**2 + self.z**2)**0.5
    def getAngleRad(self):
        l = self.mag()
        if l <= 0.0:
            return 0
        if self.y >= 0.0:
            return math.acos(self.x / l)
        return 2.0 * math.pi - math.acos(self.x / l)
    def getTup(self):
        return (self.x, self.y, self.z)
#endregion

#region helper classes
class Rectangle():
    def __init__(self, top=None, left=None, bottom=None, right=None):
        self.top = 0 if top is None else top
        self.left = 0 if left is None else left
        self.bottom = 0 if bottom is None else bottom
        self.right = 0 if right is None else right
    def height(self):
        return self.top - self.bottom
    def width(self):
        return self.right - self.left
    def centerX(self):
        return self.left + self.width()/2.0
    def centerY(self):
        return self.bottom + self.height()/2.0

class Material():
    def __init__(self, uts=None, ys=None, modulus=None, staticFactor=None):
        self.uts = uts
        self.ys = ys
        self.E = modulus
        self.staticFactor = staticFactor

class Node():
    def __init__(self, name=None, position=None):
        self.name = name
        self.position = position if position is not None else Position()
        self.graphic = None

class Link():
    def __init__(self, name="", node1="1", node2="2", length=None, angleRad=None,
                 material="Steel", width=0.1, thickness=0.05):
        self.name = name
        self.node1_Name = node1
        self.node2_Name = node2
        self.length = length
        self.angleRad = angleRad
        self.material = material
        self.width = width
        self.thickness = thickness
        self.graphic = None
#endregion

#region Truss Model
class TrussModel():
    def __init__(self):
        self.title = None
        self.links = []
        self.nodes = []
        self.material = Material()
        self.rct = Rectangle()

    def getNode(self, name):
        for n in self.nodes:
            if n.name == name:
                return n
        return None

    def getCenterPt(self):
        if not self.nodes:
            return
        rct = Rectangle()
        rct.left = self.nodes[0].position.x
        rct.right = self.nodes[0].position.x
        rct.top = self.nodes[0].position.y
        rct.bottom = self.nodes[0].position.y
        for n in self.nodes:
            if rct.left > n.position.x:
                rct.left = n.position.x
            if rct.right < n.position.x:
                rct.right = n.position.x
            if rct.top < n.position.y:
                rct.top = n.position.y
            if rct.bottom > n.position.y:
                rct.bottom = n.position.y
        self.rct = rct
#endregion

#region Truss View
class TrussView():
    def __init__(self):
        # Create a persistent scene
        self.scene = qtw.QGraphicsScene()
        self.scene.setObjectName("TrussScene")

        # Widgets – will be set later by setDisplayWidgets
        self.te_Report = None
        self.le_LongLinkName = None
        self.le_LongLinkNode1 = None
        self.le_LongLinkNode2 = None
        self.le_LongLinkLength = None
        self.gv = None

        # Pens and brushes
        self.penLink = qtg.QPen(qtg.QColor("orange"))
        self.penLink.setWidth(2)
        self.penNode = qtg.QPen(qtc.Qt.darkBlue)
        self.penNode.setWidth(1)
        self.penLabel = qtg.QPen(qtc.Qt.darkMagenta)
        self.penLabel.setWidth(1)
        self.penGridLines = qtg.QPen(qtg.QColor.fromHsv(197, 144, 228, alpha=50))
        self.penGridLines.setWidth(1)
        self.brushLink = qtg.QBrush(qtg.QColor.fromHsv(35, 255, 255, 64))
        self.brushPivot = qtg.QBrush(qtg.QColor.fromRgb(215, 215, 215, alpha=128))
        self.brushNode = qtg.QBrush(qtg.QColor.fromCmyk(0, 0, 255, 0, alpha=100))
        self.brushGrid = qtg.QBrush(qtg.QColor.fromHsv(87, 98, 245, alpha=128))

    def setDisplayWidgets(self, args):
        self.te_Report = args[0]
        self.le_LongLinkName = args[1]
        self.le_LongLinkNode1 = args[2]
        self.le_LongLinkNode2 = args[3]
        self.le_LongLinkLength = args[4]
        self.gv = args[5]
        self.gv.setScene(self.scene)

    def displayReport(self, truss=None):
        if truss is None:
            return
        st = '\tTruss Design Report\n'
        st += 'Title:  {}\n'.format(truss.title if truss.title else 'N/A')
        st += 'Static Factor of Safety:  {:0.2f}\n'.format(truss.material.staticFactor if truss.material.staticFactor else 0)
        st += 'Ultimate Strength:  {:0.2f}\n'.format(truss.material.uts if truss.material.uts else 0)
        st += 'Yield Strength:  {:0.2f}\n'.format(truss.material.ys if truss.material.ys else 0)
        st += 'Modulus of Elasticity:  {:0.2f}\n'.format(truss.material.E if truss.material.E else 0)
        st += '_____________Link Summary________________\n'
        st += 'Link\t(1)\t(2)\tLength\tAngle\n'
        longest = None
        for l in truss.links:
            if longest is None or (l.length and longest.length and l.length > longest.length):
                longest = l
            st += '{}\t{}\t{}\t{:0.2f}\t{:0.2f}\n'.format(
                l.name, l.node1_Name, l.node2_Name,
                l.length if l.length else 0,
                l.angleRad if l.angleRad else 0)
        self.te_Report.setText(st)
        if longest:
            self.le_LongLinkName.setText(longest.name)
            self.le_LongLinkLength.setText("{:0.2f}".format(longest.length))
            self.le_LongLinkNode1.setText(longest.node1_Name)
            self.le_LongLinkNode2.setText(longest.node2_Name)

    def buildScene(self, truss=None):
        if truss is None or not truss.nodes:
            return
        self.scene.clear()
        truss.getCenterPt()
        rct = truss.rct
        # draw grid
        self.drawAGrid(DeltaX=10, DeltaY=10,
                       Height=abs(rct.height()), Width=abs(rct.width()),
                       CenterX=0, CenterY=0)
        # draw links then nodes
        self.drawLinks(truss)
        self.drawNodes(truss)

    def drawAGrid(self, DeltaX=10, DeltaY=10, Height=320, Width=180, CenterX=120, CenterY=60):
        # Grid is drawn relative to scene origin (0,0) – this is just a background
        left = -Width/2
        right = Width/2
        bottom = -Height/2
        top = Height/2
        pen = self.penGridLines
        brush = self.brushGrid
        rect = qtw.QGraphicsRectItem(left, bottom, Width, Height)
        rect.setBrush(brush)
        rect.setPen(pen)
        self.scene.addItem(rect)
        x = left
        while x <= right:
            line = qtw.QGraphicsLineItem(x, bottom, x, top)
            line.setPen(pen)
            self.scene.addItem(line)
            x += DeltaX
        y = bottom
        while y <= top:
            line = qtw.QGraphicsLineItem(left, y, right, y)
            line.setPen(pen)
            self.scene.addItem(line)
            y += DeltaY

    def drawLinks(self, truss):
        truss.getCenterPt()
        offset = Position(x=truss.rct.centerX(), y=truss.rct.centerY())
        for l in truss.links:
            n1 = truss.getNode(l.node1_Name)
            n2 = truss.getNode(l.node2_Name)
            if n1 is None or n2 is None:
                continue
            x1 = n1.position.x - offset.x
            y1 = -(n1.position.y - offset.y)
            x2 = n2.position.x - offset.x
            y2 = -(n2.position.y - offset.y)
            l.graphic = RigidLink(x1, y1, x2, y2, pen=self.penLink, brush=self.brushLink, name="link " + l.name)
            tip = "Link: " + l.name
            tip += "\nMaterial: " + l.material
            tip += "\nWidth: {:.2f}, Thick: {:.2f}".format(l.width, l.thickness)
            # compute weight (simplified)
            density = 7850 if l.material.lower() == 'steel' else 2700
            volume = l.length * l.width * l.thickness
            weight_N = volume * density * 9.81
            tip += "\nWeight: {:.1f} N".format(weight_N)
            l.graphic.setToolTip(tip)
            self.scene.addItem(l.graphic)

    def drawNodes(self, truss):
        truss.getCenterPt()
        offset = Position(x=truss.rct.centerX(), y=truss.rct.centerY())
        # compute vertical loads from self-weight
        loads = {}
        for n in truss.nodes:
            loads[n.name] = 0.0
        for l in truss.links:
            density = 7850 if l.material.lower() == 'steel' else 2700
            volume = l.length * l.width * l.thickness
            weight = volume * density * 9.81
            loads[l.node1_Name] += weight / 2.0
            loads[l.node2_Name] += weight / 2.0

        for n in truss.nodes:
            x = n.position.x - offset.x
            y = -(n.position.y - offset.y)
            tip = "Node: " + n.name
            tip += "\nVertical load (self-weight): {:.1f} N".format(loads[n.name])
            if n.name.lower() == 'right':
                # roller: circle + horizontal line
                circ = qtw.QGraphicsEllipseItem(x-8, y-8, 16, 16)
                circ.setPen(self.penNode)
                circ.setBrush(self.brushNode)
                circ.setData(0, n.name)
                circ.setToolTip(tip)
                self.scene.addItem(circ)
                line = qtw.QGraphicsLineItem(x-12, y+8, x+12, y+8)
                line.setPen(self.penNode)
                self.scene.addItem(line)
            else:
                n.graphic = RigidPivotPoint(x, y, radius=10, size=20, pen=self.penNode, brush=self.brushPivot, name=n.name)
                n.graphic.setToolTip(tip)
                self.scene.addItem(n.graphic)
            # add label
            lbl = qtw.QGraphicsTextItem(n.name)
            lbl.setDefaultTextColor(self.penLabel.color())
            lbl.setPos(x-10, y-20)
            self.scene.addItem(lbl)
#endregion

#region Truss Controller
class TrussController():
    def __init__(self):
        self.truss = TrussModel()
        self.view = TrussView()

    # ---- New methods for MVC event handling (fix crash) ----
    def installSceneEventFilter(self, filter_obj):
        self.view.scene.installEventFilter(filter_obj)

    def isSceneObject(self, obj):
        return obj == self.view.scene

    def getItemAt(self, scenePos, transform):
        return self.view.scene.itemAt(scenePos, transform)

    def getItemsAt(self, scenePos):
        return self.view.scene.items(scenePos)
    # -------------------------------------------------------

    def setDisplayWidgets(self, args):
        self.view.setDisplayWidgets(args)

    def ImportFromFile(self, data):
        self.truss = TrussModel()
        for line in data:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            cells = [c.strip() for c in line.split(',')]
            if len(cells) < 2:
                continue
            keyword = cells[0].lower()
            if keyword == 'title':
                self.truss.title = cells[1].strip("'\"")
            elif keyword == 'material':
                sut = float(cells[1])
                sy = float(cells[2])
                E = float(cells[3])
                self.truss.material = Material(uts=sut, ys=sy, modulus=E)
            elif keyword == 'static_factor':
                sf = float(cells[1])
                self.truss.material.staticFactor = sf
            elif keyword == 'node':
                name = cells[1]
                x = float(cells[2])
                y = float(cells[3])
                self.truss.nodes.append(Node(name=name, position=Position(x=x, y=y)))
            elif keyword == 'link':
                name = cells[1]
                n1 = cells[2]
                n2 = cells[3]
                # optional material, width, thickness
                mat = cells[4] if len(cells) > 4 else "Steel"
                w = float(cells[5]) if len(cells) > 5 else 0.1
                t = float(cells[6]) if len(cells) > 6 else 0.05
                self.truss.links.append(Link(name=name, node1=n1, node2=n2, material=mat, width=w, thickness=t))
        self.calcLinkVals()
        self.displayReport()
        self.drawTruss()

    def calcLinkVals(self):
        for l in self.truss.links:
            n1 = self.truss.getNode(l.node1_Name)
            n2 = self.truss.getNode(l.node2_Name)
            if n1 and n2:
                r = n2.position - n1.position
                l.length = r.mag()
                l.angleRad = r.getAngleRad()

    def displayReport(self):
        self.view.displayReport(truss=self.truss)

    def drawTruss(self):
        self.view.buildScene(truss=self.truss)
#endregion