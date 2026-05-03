# region imports
import math
import numpy as np
from scipy.integrate import quad
from scipy.optimize import fsolve
from copy import deepcopy as dc
# endregion


# region class definitions
class StateDataForPlotting:
    """
    Storage class for thermodynamic plotting data.
    """

    def __init__(self):
        self.T = []
        self.P = []
        self.h = []
        self.u = []
        self.s = []
        self.v = []

    def clear(self):
        self.T.clear()
        self.P.clear()
        self.h.clear()
        self.u.clear()
        self.s.clear()
        self.v.clear()

    def add(self, vals):
        T, P, u, h, s, v = vals
        self.T.append(T)
        self.P.append(P)
        self.h.append(h)
        self.u.append(u)
        self.s.append(s)
        self.v.append(v)

    def getAxisLabel(self, W='T', Units=None):
        Units = Units if Units is not None else units()
        w = W.lower()

        if w == 't':
            return Units.TPlotUnits
        if w == 'h':
            return Units.hPlotUnits
        if w == 'u':
            return Units.uPlotUnits
        if w == 's':
            return Units.sPlotUnits
        if w == 'v':
            return Units.vPlotUnits
        if w == 'p':
            return Units.PPlotUnits

    def getDataCol(self, W='T'):
        w = W.lower()

        if w == 't':
            return self.T
        if w == 'h':
            return self.h
        if w == 'u':
            return self.u
        if w == 's':
            return self.s
        if w == 'v':
            return self.v
        if w == 'p':
            return self.P


class stateProps:
    """
    Storage class for a thermodynamic state:
    T, P, u, h, s, v.
    """

    def __init__(self):
        self.name = None
        self.T = None
        self.P = None
        self.h = None
        self.u = None
        self.s = None
        self.v = None

    def __mul__(self, other):
        """
        Multiply state properties by a scalar.
        ChatGPT helped fix this function.
        """
        if type(other) in (float, int):
            b = stateProps()
            b.name = self.name
            b.T = self.T
            b.P = self.P
            b.h = self.h * other if self.h is not None else None
            b.u = self.u * other if self.u is not None else None
            b.s = self.s * other if self.s is not None else None
            b.v = self.v * other if self.v is not None else None
            return b

        raise TypeError("stateProps can only be multiplied by a float or int.")

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        """
        Divide state properties by a scalar.
        ChatGPT helped fix this function.
        """
        if type(other) in (float, int):
            b = stateProps()
            b.name = self.name
            b.T = self.T
            b.P = self.P
            b.h = self.h / other if self.h is not None else None
            b.u = self.u / other if self.u is not None else None
            b.s = self.s / other if self.s is not None else None
            b.v = self.v / other if self.v is not None else None
            return b

        raise TypeError("stateProps can only be divided by a float or int.")

    def ConvertStateData(self, SI=True, mass=False, total=False, n=1.0, MW=1.0, Units=None):
        UC = Units if Units is not None else units()
        UC.set(SI=SI, mass=mass, total=total)

        TCF = 1.0 if SI else UC.CF_T
        PCF = 1.0 if SI else UC.CF_P
        vCF = 1.0 if SI else UC.CF_v
        uCF = 1.0 if SI else UC.CF_e
        hCF = 1.0 if SI else UC.CF_e
        sCF = 1.0 if SI else UC.CF_s
        nCF = 1.0 if SI else UC.CF_n

        if mass:
            vCF /= MW
            uCF /= MW
            hCF /= MW
            sCF /= MW
        elif total:
            vCF *= n * nCF
            uCF *= n * nCF
            hCF *= n * nCF
            sCF *= n * nCF

        if self.P is not None:
            self.P *= PCF
        if self.T is not None:
            self.T *= TCF
        if self.h is not None:
            self.h *= hCF
        if self.u is not None:
            self.u *= uCF
        if self.v is not None:
            self.v *= vCF
        if self.s is not None:
            self.s *= sCF

    def getVal(self, name='T'):
        n = name.lower()

        if n == 't':
            return self.T
        if n == 'h':
            return self.h
        if n == 'u':
            return self.u
        if n == 's':
            return self.s
        if n == 'v':
            return self.v
        if n == 'p':
            return self.P

    def print(self, Units=None):
        UC = Units if Units is not None else units()

        if self.name is not None:
            print(self.name)

        print('T={:0.4f} {}'.format(self.T, UC.TUnits))
        print('P={:0.4f} {}'.format(self.P, UC.PUnits))
        print('v={:0.4f} {}'.format(self.v, UC.vUnits))
        print('u={:0.4f} {}'.format(self.u, UC.uUnits))
        print('h={:0.4f} {}'.format(self.h, UC.hUnits))
        print('s={:0.4f} {}'.format(self.s, UC.sUnits))


class units:
    """
    Unit conversion helper class for air properties.
    """

    def __init__(self):
        self.SI = True

        self.sUnits = 'J/mol*K'
        self.uUnits = 'J/mol'
        self.vUnits = 'm^3/mol'
        self.VUnits = 'm^3'
        self.hUnits = self.uUnits
        self.mUnits = 'kg'
        self.TUnits = 'K'
        self.PUnits = 'Pa'
        self.EUnits = 'J'

        self.CF_E = 1.0 / 1055.06
        self.CF_Length = 3.28084
        self.CF_V = self.CF_Length ** 3.0
        self.CF_P = 1.0 / 101325.0
        self.CF_Mass = 2.20462
        self.CF_T = 9.0 / 5.0
        self.CF_n = 1.0 / 453.59
        self.CF_v = self.CF_V / self.CF_n
        self.CF_e = self.CF_E / self.CF_n
        self.CF_s = self.CF_e / self.CF_T

        self.setPlotUnits()

    def set(self, SI=True, mass=False, total=False):
        self.changed = not self.SI == SI
        self.SI = SI

        if SI:
            self.sUnits = 'J/{}K'.format('' if total else ('kg*' if mass else 'mol*'))
            self.uUnits = 'J{}'.format('' if total else ('/kg' if mass else '/mol'))
            self.vUnits = 'm^3{}'.format('' if total else ('/kg' if mass else '/mol'))
            self.VUnits = 'm^3'
            self.hUnits = self.uUnits
            self.mUnits = 'kg'
            self.TUnits = 'K'
            self.PUnits = 'Pa'
            self.EUnits = 'J'
        else:
            self.sUnits = 'Btu/{}R'.format('' if total else ('lb*' if mass else 'lbmol*'))
            self.uUnits = 'Btu{}'.format('' if total else ('/lb' if mass else '/lbmol'))
            self.vUnits = 'ft^3{}'.format('' if total else ('/lb' if mass else '/lbmol'))
            self.VUnits = 'ft^3'
            self.hUnits = self.uUnits
            self.mUnits = 'lb'
            self.TUnits = 'R'
            self.PUnits = 'atm'
            self.EUnits = 'Btu'

        self.setPlotUnits(SI=SI, mass=mass, total=total)

    def setPlotUnits(self, SI=True, mass=True, total=False):
        if SI:
            self.PPlotUnits = r'P $\left(Pa\right)$'
            self.TPlotUnits = r'T $\left(K\right)$'

            if total:
                self.sPlotUnits = r'S $\left(\frac{J}{K}\right)$'
                self.uPlotUnits = r'U $\left(J\right)$'
                self.hPlotUnits = r'H $\left(J\right)$'
                self.vPlotUnits = r'V $\left(m^3\right)$'
            elif mass:
                self.sPlotUnits = r's $\left(\frac{J}{kg*K}\right)$'
                self.uPlotUnits = r'u $\left(\frac{J}{kg}\right)$'
                self.hPlotUnits = r'h $\left(\frac{J}{kg}\right)$'
                self.vPlotUnits = r'v $\left(\frac{m^3}{kg}\right)$'
            else:
                self.sPlotUnits = r'$\bar{s} \left(\frac{J}{mol*K}\right)$'
                self.uPlotUnits = r'$\bar{u} \left(\frac{J}{mol}\right)$'
                self.hPlotUnits = r'$\bar{h} \left(\frac{J}{mol}\right)$'
                self.vPlotUnits = r'$\bar{v} \left(\frac{m^3}{mol}\right)$'
        else:
            self.PPlotUnits = r'P $\left(atm\right)$'
            self.TPlotUnits = r'T $\left(^{o}R\right)$'

            if total:
                self.sPlotUnits = r'S $\left(\frac{Btu}{^{o}R}\right)$'
                self.uPlotUnits = r'U $\left(Btu\right)$'
                self.hPlotUnits = r'H $\left(Btu\right)$'
                self.vPlotUnits = r'V $\left(ft^3\right)$'
            elif mass:
                self.sPlotUnits = r's $\left(\frac{Btu}{lb\cdot^{o}R}\right)$'
                self.uPlotUnits = r'u $\left(\frac{Btu}{lb}\right)$'
                self.hPlotUnits = r'h $\left(\frac{Btu}{lb}\right)$'
                self.vPlotUnits = r'v $\left(\frac{ft^3}{lb}\right)$'
            else:
                self.sPlotUnits = r'$\bar{s} \left(\frac{Btu}{lb_{mol}\cdot^{o}R}\right)$'
                self.uPlotUnits = r'$\bar{u} \left(\frac{Btu}{lb_{mol}}\right)$'
                self.hPlotUnits = r'$\bar{h} \left(\frac{Btu}{lb_{mol}}\right)$'
                self.vPlotUnits = r'$\bar{v} \left(\frac{ft^3}{lb_{mol}}\right)$'

    def T_RtoK(self, T):
        return T * 5.0 / 9.0

    def T_FtoC(self, T):
        return (T - 32.0) * 5.0 / 9.0

    def T_RtoF(self, T):
        return T - 459.67

    def T_FtoR(self, T):
        return T + 459.67

    def T_FtoK(self, T):
        return self.T_RtoK(self.T_FtoR(T))

    def T_CtoK(self, T):
        return T + 273.15

    def T_CtoF(self, T):
        return T * 9.0 / 5.0 + 32.0

    def T_KtoC(self, T):
        return T - 273.15

    def T_KtoR(self, T):
        return T * 9.0 / 5.0


class air:
    """
    Ideal gas air model using molar SI units internally.
    """

    def __init__(self):
        self.RBar = 8.3145
        self.MW = 28.97
        self.R = self.RBar / self.MW

        self.StandardState = stateProps()
        self.StandardState.P = 101325.0
        self.StandardState.T = 273.15
        self.StandardState.v = self.RBar * self.StandardState.T / self.StandardState.P
        self.StandardState.u = 0.0
        self.StandardState.h = 0.0
        self.StandardState.s = 0.0

        self.State = stateProps()
        self.n = 1.0
        self.m = self.n * self.MW / 1000.0

    def cv(self, T):
        return self.cp(T) - self.RBar

    def cp(self, T):
        TLowRange = 1630.0

        a = 3.653 if T < TLowRange else 2.753
        b = -1.337E-3 if T < TLowRange else 0.002
        c = 3.294E-6 if T < TLowRange else -1.0E-6
        d = -1.913E-9 if T < TLowRange else 3.0E-10
        e = 0.2763E-12 if T < TLowRange else -3.0E-14

        return self.RBar * (a + b * T + c * T ** 2 + d * T ** 3 + e * T ** 4)

    def _safe_temperature(self, T):
        """
        Returns a physically safe absolute temperature for numerical integration.
        The entropy integrals contain cp(T)/T or cv(T)/T, so T <= 0 causes
        divide-by-zero or divergent integration warnings.
        ChatGPT helped patch this numerical safety check.
        """
        try:
            T = float(T)
        except (TypeError, ValueError):
            T = self.StandardState.T
        return max(T, 1.0)

    def _safe_positive(self, value, default=1.0e-12):
        """
        Returns a positive value for logarithms and ideal-gas calculations.
        This prevents math-domain errors if a solver briefly guesses a
        nonphysical pressure or volume.
        ChatGPT helped patch this numerical safety check.
        """
        try:
            value = float(value)
        except (TypeError, ValueError):
            value = default
        return max(value, default)

    def _safe_quad(self, fn, T1, T2):
        """
        Integrates a temperature-based thermodynamic property with protected
        bounds and a higher subdivision limit to reduce IntegrationWarning
        messages during valid cycle calculations.
        ChatGPT helped patch this numerical integration helper.
        """
        T1 = self._safe_temperature(T1)
        T2 = self._safe_temperature(T2)
        if abs(T2 - T1) < 1.0e-12:
            return 0.0
        return quad(fn, T1, T2, limit=200, epsabs=1.0e-7, epsrel=1.0e-7)[0]

    def deltau(self, T1=None, T2=None):
        if T1 is None:
            T1 = self.StandardState.T
        if T2 is None:
            T2 = self.StandardState.T

        return self._safe_quad(self.cv, T1, T2)

    def deltah(self, T1=None, T2=None):
        if T1 is None:
            T1 = self.StandardState.T
        if T2 is None:
            T2 = self.StandardState.T

        return self._safe_quad(self.cp, T1, T2)

    def deltas_tv(self, T1=None, T2=None, V1=None, V2=None):
        if T1 is None:
            T1 = self.StandardState.T
        if T2 is None:
            T2 = self.StandardState.T
        if V1 is None:
            V1 = self.StandardState.v
        if V2 is None:
            V2 = self.StandardState.v

        V1 = self._safe_positive(V1)
        V2 = self._safe_positive(V2)
        fn = lambda T: self.cv(self._safe_temperature(T)) / self._safe_temperature(T)
        deltaS = self._safe_quad(fn, T1, T2)
        deltaS += self.RBar * math.log(V2 / V1)

        return deltaS

    def deltas_tp(self, T1=None, T2=None, P1=None, P2=None):
        if T1 is None:
            T1 = self.StandardState.T
        if T2 is None:
            T2 = self.StandardState.T
        if P1 is None:
            P1 = self.StandardState.P
        if P2 is None:
            P2 = self.StandardState.P

        P1 = self._safe_positive(P1)
        P2 = self._safe_positive(P2)
        fn = lambda T: self.cp(self._safe_temperature(T)) / self._safe_temperature(T)
        deltaS = self._safe_quad(fn, T1, T2)
        deltaS += self.RBar * math.log(P1 / P2)

        return deltaS

    def set(self, P=None, T=None, v=None, h=None, u=None, s=None, name=None):
        self.State.P = P
        self.State.T = T
        self.State.v = v
        self.State.h = h
        self.State.u = u
        self.State.s = s
        self.State.name = name

        if T is None and P is None and u is None and v is None and h is None and s is None:
            return None

        self.calc()
        return dc(self.State)

    def calc(self):
        if self.State.P is not None and self.State.T is not None:
            self.State.v = self.RBar * self.State.T / self.State.P
            self.State.u = self.deltau(T2=self.State.T)
            self.State.h = self.deltah(T2=self.State.T)
            self.State.s = self.deltas_tp(T2=self.State.T, P2=self.State.P)

        elif self.State.P is not None and self.State.u is not None:
            fn = lambda T: self.deltau(T2=T[0]) - self.State.u
            self.State.T = fsolve(fn, np.array([300.0]))[0]
            self.State.v = self.RBar * self.State.T / self.State.P
            self.State.h = self.deltah(T2=self.State.T)
            self.State.s = self.deltas_tp(T2=self.State.T, P2=self.State.P)

        elif self.State.P is not None and self.State.v is not None:
            self.State.T = self.State.v * self.State.P / self.RBar
            self.State.u = self.deltau(T2=self.State.T)
            self.State.h = self.deltah(T2=self.State.T)
            self.State.s = self.deltas_tp(T2=self.State.T, P2=self.State.P)

        elif self.State.P is not None and self.State.h is not None:
            fn = lambda T: self.deltah(T2=T[0]) - self.State.h
            self.State.T = fsolve(fn, np.array([300.0]))[0]
            self.State.v = self.RBar * self.State.T / self.State.P
            self.State.u = self.deltau(T2=self.State.T)
            self.State.s = self.deltas_tp(T2=self.State.T, P2=self.State.P)

        elif self.State.P is not None and self.State.s is not None:
            fn = lambda T: self.deltas_tp(T2=T[0], P2=self.State.P) - self.State.s
            self.State.T = fsolve(fn, np.array([300.0]))[0]
            self.State.v = self.RBar * self.State.T / self.State.P
            self.State.u = self.deltau(T2=self.State.T)
            self.State.h = self.deltah(T2=self.State.T)

        elif self.State.T is not None and self.State.v is not None:
            self.State.P = self.State.T * self.RBar / self.State.v
            self.State.u = self.deltau(T2=self.State.T)
            self.State.h = self.deltah(T2=self.State.T)
            self.State.s = self.deltas_tp(T2=self.State.T, P2=self.State.P)

        elif self.State.T is not None and self.State.s is not None:
            fn = lambda P: self.deltas_tp(T2=self.State.T, P2=P[0]) - self.State.s
            self.State.P = fsolve(fn, np.array([101325.0]))[0]
            self.State.v = self.RBar * self.State.T / self.State.P
            self.State.u = self.deltau(T2=self.State.T)
            self.State.h = self.deltah(T2=self.State.T)

        elif self.State.u is not None and self.State.v is not None:
            fn = lambda T: self.deltau(T2=T[0]) - self.State.u
            self.State.T = fsolve(fn, np.array([300.0]))[0]
            self.State.P = self.State.T * self.RBar / self.State.v
            self.State.h = self.deltah(T2=self.State.T)
            self.State.s = self.deltas_tp(T2=self.State.T, P2=self.State.P)

        elif self.State.u is not None and self.State.s is not None:
            fn = lambda T: self.deltau(T2=T[0]) - self.State.u
            self.State.T = fsolve(fn, np.array([300.0]))[0]
            fn = lambda P: self.deltas_tp(T2=self.State.T, P2=P[0]) - self.State.s
            self.State.P = fsolve(fn, np.array([101325.0]))[0]
            self.State.v = self.RBar * self.State.T / self.State.P
            self.State.h = self.deltah(T2=self.State.T)

        elif self.State.v is not None and self.State.h is not None:
            fn = lambda T: self.deltah(T2=T[0]) - self.State.h
            self.State.T = fsolve(fn, np.array([300.0]))[0]
            self.State.P = self.State.T * self.RBar / self.State.v
            self.State.u = self.deltau(T2=self.State.T)
            self.State.s = self.deltas_tp(T2=self.State.T, P2=self.State.P)

        elif self.State.v is not None and self.State.s is not None:
            fn = lambda T: self.deltas_tv(T2=T[0], V2=self.State.v) - self.State.s
            self.State.T = fsolve(fn, np.array([300.0]))[0]
            self.State.P = self.RBar * self.State.T / self.State.v
            self.State.h = self.deltah(T2=self.State.T)
            self.State.u = self.deltau(T2=self.State.T)

        elif self.State.h is not None and self.State.s is not None:
            fn = lambda T: self.deltah(T2=T[0]) - self.State.h
            self.State.T = fsolve(fn, np.array([300.0]))[0]
            fn = lambda P: self.deltas_tp(T2=self.State.T, P2=P[0]) - self.State.s
            self.State.P = fsolve(fn, np.array([101325.0]))[0]
            self.State.v = self.RBar * self.State.T / self.State.P
            self.State.u = self.deltau(T2=self.State.T)

    def getSummary_MassBasis(self, Units=None):
        UC = Units if Units is not None else units()

        TCF = 1.0 if UC.SI else UC.CF_T
        PCF = 1.0 if UC.SI else UC.CF_P
        vCF = 1.0 if UC.SI else UC.CF_V
        uCF = 1.0 if UC.SI else UC.CF_E
        hCF = 1.0 if UC.SI else UC.CF_E
        sCF = 1.0 if UC.SI else UC.CF_s

        stTmp = ''
        stTmp += 'T={:0.2f} {}\n'.format(self.State.T * TCF, UC.TUnits)
        stTmp += 'P={:0.3f} {}\n'.format(self.State.P * PCF, UC.PUnits)
        stTmp += 'v={:0.4f} {}\n'.format(self.State.v * vCF * 1000.0 / self.MW, UC.vUnits)
        stTmp += 'u={:0.4f} {}\n'.format(self.State.u * uCF * 1000.0 / self.MW, UC.uUnits)
        stTmp += 'h={:0.4f} {}\n'.format(self.State.h * hCF * 1000.0 / self.MW, UC.hUnits)
        stTmp += 's={:0.4f} {}'.format(self.State.s * sCF * 1000.0 / self.MW, UC.sUnits)

        return stTmp

    def print_MassBasis(self):
        print(self.getSummary_MassBasis())

    def getSummary_Extensive(self, Units=None):
        UC = Units if Units is not None else units()

        TCF = 1.0 if UC.SI else UC.CF_T
        PCF = 1.0 if UC.SI else UC.CF_P
        vCF = 1.0 if UC.SI else UC.CF_V
        uCF = 1.0 if UC.SI else UC.CF_E
        hCF = 1.0 if UC.SI else UC.CF_E
        sCF = 1.0 if UC.SI else UC.CF_s

        stTmp = ''
        stTmp += 'T={:0.2f} {}\n'.format(self.State.T * TCF, UC.TUnits)
        stTmp += 'P={:0.3f} {}\n'.format(self.State.P * PCF, UC.PUnits)
        stTmp += 'V={:0.4f} {}\n'.format(self.n * self.State.v * vCF, UC.VUnits)
        stTmp += 'U={:0.4f} {}\n'.format(self.n * self.State.u * uCF, UC.EUnits)
        stTmp += 'H={:0.4f} {}\n'.format(self.n * self.State.h * hCF, UC.EUnits)
        stTmp += 'S={:0.4f} {}'.format(self.n * self.State.s * sCF, UC.EUnits + '/K')

        return stTmp

    def print_Extensive(self):
        ext = self.State * self.n

        print('T={:0.2f} {}'.format(ext.T, 'K'))
        print('P={:0.3f} {}'.format(ext.P / 1000.0, 'kPa'))
        print('V={:0.6f} {}'.format(ext.v, 'm^3'))
        print('U={:0.4f} {}'.format(ext.u / 1000.0, 'kJ'))
        print('H={:0.4f} {}'.format(ext.h / 1000.0, 'kJ'))
        print('S={:0.4f} {}'.format(ext.s / 1000.0, 'kJ/K'))
# endregion


def main():
    a = air()
    a.set(P=a.StandardState.P, T=200.0)
    a.print_Extensive()


if __name__ == "__main__":
    main()