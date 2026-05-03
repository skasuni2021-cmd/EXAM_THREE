#region imports
from Truss_GUI import Ui_TrussStructuralDesign
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from Truss_Classes import TrussController
import sys
#endregion


#region class definitions
class MainWindow(Ui_TrussStructuralDesign, qtw.QWidget):
    def __init__(self):
        """
        Main GUI window for the truss design program.
        The App only communicates directly with the Controller.
        """
        super().__init__()
        self.setupUi(self)

        self.btn_Open.clicked.connect(self.OpenFile)
        self.spnd_Zoom.valueChanged.connect(self.setZoom)

        self.controller = TrussController()

        self.controller.setDisplayWidgets((
            self.te_DesignReport,
            self.le_LinkName,
            self.le_Node1Name,
            self.le_Node2Name,
            self.le_LinkLength,
            self.gv_Main
        ))

        # MVC fix: App asks controller to install scene event filter
        self.controller.installSceneEventFilter(self)

        self.gv_Main.setMouseTracking(True)

        self.show()

    def setZoom(self):
        """
        Updates graphics view zoom.
        """
        self.gv_Main.resetTransform()
        self.gv_Main.scale(self.spnd_Zoom.value(), self.spnd_Zoom.value())

    def eventFilter(self, obj, event):
        """
        Handles mouse movement and mouse wheel zoom for the graphics scene.
        The App does not directly access controller.view.
        """

        if self.controller.isSceneObject(obj):

            if event.type() == qtc.QEvent.GraphicsSceneMouseMove:
                scenePos = event.scenePos()

                strScene = "Mouse Position:  x = {}, y = {}".format(
                    round(scenePos.x(), 2),
                    round(-scenePos.y(), 2)
                )

                item = self.controller.getItemAt(
                    scenePos,
                    self.gv_Main.transform()
                )

                if item is not None and item.data(0) is not None:
                    strScene += " (" + item.data(0) + ")"

                items = self.controller.getItemsAt(scenePos)

                item_names = [
                    item.name if hasattr(item, "name") else None
                    for item in items
                ]

                for name in item_names:
                    strScene += ", " + (name if name is not None else "none")

                self.lbl_MousePos.setText(strScene)

            elif event.type() == qtc.QEvent.GraphicsSceneWheel:
                # PyQt5 safer wheel event syntax
                if event.angleDelta().y() > 0:
                    self.spnd_Zoom.stepUp()
                else:
                    self.spnd_Zoom.stepDown()

                return True

        return super(MainWindow, self).eventFilter(obj, event)

    def OpenFile(self):
        """
        Opens a truss input file and passes the file data to the controller.
        """
        filename = qtw.QFileDialog.getOpenFileName()[0]

        if len(filename) == 0:
            return

        self.te_Path.setText(filename)

        with open(filename, "r") as file:
            data = file.readlines()

        self.controller.ImportFromFile(data)
#endregion


#region function definitions
def Main():
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())
#endregion


#region function calls
if __name__ == "__main__":
    Main()
#endregion