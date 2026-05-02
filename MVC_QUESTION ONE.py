#region imports
import sys
import numpy as np
from scipy.integrate import quad
from PyQt5 import QtWidgets as qtw
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
#endregion


#region model
class TakeoffModel:
    """
    Model class for takeoff distance calculation.
    ChatGPT helped write this function.

    The model calculates aircraft takeoff distance using:
    Vstall, VTO, A, B, and STO integral.
    """

    def __init__(self):
        self.rho = 0.002377
        self.S = 1000.0
        self.CLmax = 2.4
        self.CD = 0.0279
        self.gc = 32.174

    def calc_sto(self, weight, thrust):
        """
        Calculate takeoff distance for a given weight and thrust.

        :param weight: aircraft weight, lb
        :param thrust: engine thrust, lbf
        :return: takeoff distance, ft
        """
        v_stall = np.sqrt(weight / (0.5 * self.rho * self.S * self.CLmax))
        v_to = 1.2 * v_stall

        A = self.gc * thrust / weight
        B = (self.gc / weight) * (0.5 * self.rho * self.S * self.CD)

        def integrand(v):
            return v / (A - B * v ** 2)

        sto, error = quad(integrand, 0, v_to)
        return sto

    def generate_curve(self, weight, thrust_values):
        """
        Generate STO values over a range of thrust values.

        :param weight: aircraft weight
        :param thrust_values: array of thrust values
        :return: array of STO values
        """
        return np.array([self.calc_sto(weight, thrust) for thrust in thrust_values])
#endregion


#region view
class TakeoffView:
    """
    View class for GUI widgets and plotting.
    """

    def __init__(self):
        self.window = qtw.QWidget()
        self.window.setWindowTitle("Aircraft Takeoff Distance Calculator")

        self.main_layout = qtw.QVBoxLayout(self.window)

        self.input_group = qtw.QGroupBox("Input Parameters")
        self.input_layout = qtw.QGridLayout(self.input_group)

        self.lbl_weight = qtw.QLabel("Weight, W (lb):")
        self.le_weight = qtw.QLineEdit("56000")

        self.lbl_thrust = qtw.QLabel("Thrust, T (lbf):")
        self.le_thrust = qtw.QLineEdit("13000")

        self.btn_calc = qtw.QPushButton("Calculate and Plot")

        self.input_layout.addWidget(self.lbl_weight, 0, 0)
        self.input_layout.addWidget(self.le_weight, 0, 1)
        self.input_layout.addWidget(self.lbl_thrust, 1, 0)
        self.input_layout.addWidget(self.le_thrust, 1, 1)
        self.input_layout.addWidget(self.btn_calc, 2, 0, 1, 2)

        self.main_layout.addWidget(self.input_group)

        self.figure = Figure(figsize=(7, 5), tight_layout=True)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.ax = self.figure.add_subplot(111)

        self.main_layout.addWidget(self.canvas)

        self.output_label = qtw.QLabel("STO result will appear here.")
        self.main_layout.addWidget(self.output_label)

    def show(self):
        self.window.show()

    def get_inputs(self):
        """
        Read weight and thrust from line edits.
        """
        weight = float(self.le_weight.text())
        thrust = float(self.le_thrust.text())
        return weight, thrust

    def plot_results(self, thrust_values, curve_data, selected_thrust, selected_sto):
        """
        Plot the three STO curves and mark the selected point.
        """
        self.ax.clear()

        for label, sto_values in curve_data:
            self.ax.plot(thrust_values, sto_values, label=label)

        self.ax.plot(
            selected_thrust,
            selected_sto,
            marker="o",
            markersize=9,
            fillstyle="none",
            linestyle="None",
            label="Selected W and T"
        )

        self.ax.set_title("Takeoff Distance vs Thrust")
        self.ax.set_xlabel("Thrust (lbf)")
        self.ax.set_ylabel("Takeoff Distance, STO (ft)")
        self.ax.grid(True)
        self.ax.legend()

        self.canvas.draw()

    def update_output(self, sto):
        """
        Display calculated STO.
        """
        self.output_label.setText(f"Selected takeoff distance STO = {sto:0.2f} ft")
#endregion


#region controller
class TakeoffController:
    """
    Controller class connecting the model and view.
    """

    def __init__(self):
        self.model = TakeoffModel()
        self.view = TakeoffView()

        self.view.btn_calc.clicked.connect(self.calculate)

    def calculate(self):
        """
        Read inputs, calculate STO curves, and update plot.
        """
        weight, thrust = self.view.get_inputs()

        thrust_values = np.linspace(5000, 30000, 100)

        weights = [
            weight - 10000,
            weight,
            weight + 10000
        ]

        curve_data = []

        for w in weights:
            sto_values = self.model.generate_curve(w, thrust_values)

            if w == weight:
                label = f"W = {w:0.0f} lb"
            elif w < weight:
                label = f"W - 10000 = {w:0.0f} lb"
            else:
                label = f"W + 10000 = {w:0.0f} lb"

            curve_data.append((label, sto_values))

        selected_sto = self.model.calc_sto(weight, thrust)

        self.view.plot_results(
            thrust_values,
            curve_data,
            thrust,
            selected_sto
        )

        self.view.update_output(selected_sto)

    def show(self):
        self.view.show()
#endregion


#region main
if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)
    controller = TakeoffController()
    controller.show()
    sys.exit(app.exec())
#endregion