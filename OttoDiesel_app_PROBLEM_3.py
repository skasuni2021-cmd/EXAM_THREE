#region imports
from OttoDiesel_GUI import Ui_Form
import sys
from PyQt5 import QtWidgets as qtw
from Otto import ottoCycleController
from Diesel import dieselCycleController

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
#endregion


class MainWindow(qtw.QWidget, Ui_Form):
    def __init__(self):
        """MainWindow constructor."""
        super().__init__()
        self.setupUi(self)
        self.calculated = False

        # Create matplotlib canvas
        self.figure = Figure(figsize=(8, 8), tight_layout=True, frameon=True, facecolor='none')
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.ax = self.figure.add_subplot()
        self.main_VerticalLayout.addWidget(self.canvas)

        # Signals and slots
        self.rdo_Metric.toggled.connect(self.setUnits)
        self.btn_Calculate.clicked.connect(self.calcCycle)
        self.cmb_Abcissa.currentIndexChanged.connect(self.doPlot)
        self.cmb_Ordinate.currentIndexChanged.connect(self.doPlot)
        self.chk_LogAbcissa.stateChanged.connect(self.doPlot)
        self.chk_LogOrdinate.stateChanged.connect(self.doPlot)
        self.cmb_OttoDiesel.currentIndexChanged.connect(self.selectCycle)

        # ChatGPT helped complete these controller connections.
        self.otto = ottoCycleController(ax=self.ax)
        self.diesel = dieselCycleController(ax=self.ax)
        self.controller = self.otto

        self.someWidgets = []
        self.someWidgets += [self.lbl_THigh, self.lbl_TLow, self.lbl_P0, self.lbl_V0, self.lbl_CR]
        self.someWidgets += [self.le_THigh, self.le_TLow, self.le_P0, self.le_V0, self.le_CR]
        self.someWidgets += [self.le_T1, self.le_T2, self.le_T3, self.le_T4]
        self.someWidgets += [self.lbl_T1Units, self.lbl_T2Units, self.lbl_T3Units, self.lbl_T4Units]
        self.someWidgets += [self.le_PowerStroke, self.le_CompressionStroke, self.le_HeatAdded, self.le_Efficiency]
        self.someWidgets += [self.lbl_PowerStrokeUnits, self.lbl_CompressionStrokeUnits, self.lbl_HeatInUnits]
        self.someWidgets += [self.rdo_Metric, self.cmb_Abcissa, self.cmb_Ordinate]
        self.someWidgets += [self.chk_LogAbcissa, self.chk_LogOrdinate, self.ax, self.canvas]

        self.otto.setWidgets(w=self.someWidgets)
        self.diesel.setWidgets(w=self.someWidgets)

        self.selectCycle()
        self.show()

    def clamp(self, val, low, high):
        """Clamp a numeric value between low and high."""
        if self.isfloat(val):
            val = float(val)
            if val > high:
                return float(high)
            if val < low:
                return float(low)
            return val
        return float(low)

    def isfloat(self, value):
        """Check whether a string can be converted to float."""
        if value == 'NaN':
            return False
        try:
            float(value)
            return True
        except ValueError:
            return False

    def doPlot(self):
        """Update plot when axis or log options change."""
        self.controller.updateView()

    def selectCycle(self):
        """Select Otto or Diesel cycle controller."""
        otto = self.cmb_OttoDiesel.currentIndex() == 0
        self.gb_Input.setTitle(
            'Input for Air Standard {} Cycle:'.format('Otto' if otto else 'Diesel')
        )
        self.controller = self.otto if otto else self.diesel
        self.controller.updateView()

    def setUnits(self):
        """Update view when units are changed."""
        self.controller.updateView()

    def calcCycle(self):
        """Calculate selected thermodynamic cycle."""
        self.controller.calc()
        self.calculated = True


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    mw.setWindowTitle('Otto/Diesel Cycle Calculator')
    sys.exit(app.exec())