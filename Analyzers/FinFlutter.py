# ***************************************************************************
# *   Copyright (c) 2022-2025 David Carter <dcarter@davidcarter.ca>         *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************
"""Class for analyzing fin flutter"""

__title__ = "FreeCAD Fin Flutter Analyzer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import math

import FreeCAD
translate = FreeCAD.Qt.translate

from Analyzers.pyatmos import coesa76, ussa76
from Analyzers.pyatmos.utils.Const import p0, gamma, R_air

from Rocket.Constants import FIN_TYPE_TRAPEZOID, FIN_TYPE_ELLIPSE, FIN_TYPE_SKETCH, FIN_TYPE_TRIANGLE, FIN_TYPE_TUBE, FIN_TYPE_PROXY
from Rocket.Constants import ATMOS_POF_615, ATMOS_USSA, ATMOS_COESA_GEOMETRIC, ATMOS_COESA_GEOPOTENTIAL

from Rocket.ShapeHandlers.FinTrapezoidShapeHandler import FinTrapezoidShapeHandler
from Rocket.ShapeHandlers.FinTriangleShapeHandler import FinTriangleShapeHandler
from Rocket.ShapeHandlers.FinEllipseShapeHandler import FinEllipseShapeHandler
from Rocket.ShapeHandlers.FinTubeShapeHandler import FinTubeShapeHandler
from Rocket.ShapeHandlers.FinSketchShapeHandler import FinSketchShapeHandler
from Rocket.ShapeHandlers.FinProxyShapeHandler import FinProxyShapeHandler

from Rocket.Utilities import _err

class FinFlutter:

    def __init__(self, fin):
        self._fin = fin

        if fin.FinType == FIN_TYPE_TUBE:
            raise TypeError(translate('Rocket', "Tube fins are not supported at this time"))
        # elif fin.FinType == FIN_TYPE_SKETCH:
        #     raise TypeError(translate('Rocket', "Custom fins are not supported at this time"))
        # elif fin.FinType == FIN_TYPE_PROXY:
        #     raise TypeError(translate('Rocket', "Proxy fins are not supported at this time"))

        # Create the fin shape without any extras such as TTW tabs, fin cans, etc
        # From this we can get properties such as CG, Volume, etc...
        if fin.FinType == FIN_TYPE_TRAPEZOID:
            handler = FinTrapezoidShapeHandler(fin)
        elif fin.FinType == FIN_TYPE_TRIANGLE:
            handler = FinTriangleShapeHandler(fin)
        elif fin.FinType == FIN_TYPE_ELLIPSE:
            handler = FinEllipseShapeHandler(fin)
        elif fin.FinType == FIN_TYPE_SKETCH:
            handler = FinSketchShapeHandler(fin)
        else: # fin.FinType == FIN_TYPE_PROXY:
            handler = FinProxyShapeHandler(fin)
        self._Shape = handler.finOnlyShape()

        self._rootChord = self._fromMM(fin.RootChord)
        self._span = self._fromMM(fin.Height)
        if fin.FinType in [FIN_TYPE_TRAPEZOID, FIN_TYPE_TRIANGLE]:

            # Convert from mm to m
            if fin.FinType == FIN_TYPE_TRIANGLE:
                self._tipChord = 0.0
            else:
                self._tipChord = self._fromMM(fin.TipChord)
            self._area = (self._rootChord + self._tipChord) * self._span / 2.0
        elif fin.FinType == FIN_TYPE_ELLIPSE:
            self._area = (self._span * math.pi * (self._rootChord / 2.0)) / 2.0
            self._tipChord = ((self._area / self._span) * 2.0) - self._rootChord
        elif fin.FinType == FIN_TYPE_SKETCH and isinstance(handler, FinSketchShapeHandler):
            self._area = handler.area() * 1e-6 # mm^2 to m^2
            self._span = self._fromMM(handler.findHeight())
            # self._rootChord = self._fromMM(handler.rootChordLength())
            self._tipChord = ((self._area / self._span) * 2.0) - self._rootChord
        elif fin.FinType == FIN_TYPE_PROXY and isinstance(handler, FinProxyShapeHandler):
            self._area = handler.area() * 1e-6 # mm^2 to m^2
            self._span = self._fromMM(handler.findHeight())
            # self._rootChord = self._fromMM(handler.rootChordLength())
            self._tipChord = ((self._area / self._span) * 2.0) - self._rootChord

        if float(fin.RootThickness) != float(fin.TipThickness):
            raise TypeError(translate('Rocket', "Tapered thickness fins are not supported at this time"))

        self._volume = float(self._Shape.Volume) * 1e-9 # mm^3 to m^3
        self._thickness = self._volume / self._area

        self._Cx = (self._Shape.CenterOfGravity.x * 1e-3) # mm to m
        self._epsilon = (self._Cx / self._rootChord) - 0.25
        self._DN = (24 * self._epsilon * 1.4 * 101325) / math.pi
        self._aspectRatio = self._span**2 / self._area
        self._lambda = self._tipChord / self._rootChord

        # Parameters used for POF 615 calculations
        # print(f"Thickness {self._formatFloat(self._thickness, 'm', 'cm', 'in')}")
        # print(f"TC {self._formatFloat(self._tipChord, 'm', 'cm', 'in')}")
        # print(f"RC {self._formatFloat(self._rootChord, 'm', 'cm', 'in')}")
        # print(f"SSL {self._formatFloat(self._span, 'm', 'cm', 'in')}")

        # print(f"Cx {self._formatFloat(self._Cx, 'm', 'cm', 'in')}")
        # print(f"t/c {self._thickness / self._rootChord}")
        # print(f"Lambda {self._lambda}")
        # print(f"Area {self._formatFloat(self._area, 'm^2', 'cm^2', 'in^2')}")
        # print(f"Aspect ratio {self._aspectRatio}")
        # print(f"epsilon {self._epsilon}")
        # print(f"DN {self._formatFloat(self._DN, 'Pa', 'kPa', 'psi')}")

    def _formatFloat(self, value : float, units : str, metric : str, imperial : str) -> str:
        quantity = FreeCAD.Units.Quantity(f"{value:.8g} {units}")
        return f"{float(quantity.getValueAs(FreeCAD.Units.Quantity(metric))):.4f} {metric}, " \
            f"{float(quantity.getValueAs(FreeCAD.Units.Quantity(imperial))):.4f} {imperial}"

    def _fromMM(self, value):
        return float(value) / 1000.0

    def shearModulus(self, young, poisson):
        return young / (2.0 * (1.0 + poisson))

    def temperatureCompensation(self, agl : float, T_agl : float) -> float:
        '''
            Temperature compensation for the altitude of the launch site

            agl = altitude of the launch site in meters
            T_agl = temperature at the launch site in K
        '''
        Tc = (273.15 + 15.0) - T_agl #- (0.0065 * agl)
        return Tc

    def atmospherePOF615(self, altitude : float, agl : float = 0, T_agl : float = 288.15) -> tuple[float, float]:

        # Get the atmospheric conditions at the specified altitude in m
        altitude_asl = altitude + agl

        try:
            temp = T_agl - (0.0065 * altitude_asl)
            pressure = (101.325 * math.pow((temp / 288.16), 5.256)) * 1000.0
        except ValueError:
            _err(translate("Rocket", "This atmospheric model doesn't support the specified altitude. Using the COESA76 geometric model instead."))
            return self.atmosphereCOESAGeometric(altitude, agl, T_agl)

        return temp, pressure

    def atmosphereUSSA(self, altitude : float, agl : float = 0, T_agl : float = 288.15) -> tuple[float, float]:

        # Get the atmospheric conditions at the specified altitude (convert m to km)
        altitude_asl = ((altitude + agl) / 1000.0)
        rho,T,P,Cs,eta,Kc = ussa76(altitude_asl)

        temp = float(T) + self.temperatureCompensation(agl, T_agl)
        pressure = float(P)

        return temp, pressure

    def atmosphereCOESAGeometric(self, altitude : float, agl : float = 0, T_agl : float = 288.15) -> tuple[float, float]:

        # Get the atmospheric conditions at the specified altitude (convert m to km)
        # Uses the coesa76 model which is an extension of US Standard Atmosphere 1976 model to work above 84K
        altitude_asl = ((altitude + agl) / 1000.0)
        atmo = coesa76([altitude_asl], alt_type='geometric')

        temp = float(atmo.T[0]) + self.temperatureCompensation(agl, T_agl)
        pressure = float(atmo.P[0])

        return temp, pressure

    def atmosphereCOESAGeopotential(self, altitude : float, agl : float = 0, T_agl : float = 288.15) -> tuple[float, float]:

        # Get the atmospheric conditions at the specified altitude (convert m to km)
        # Uses the coesa76 model which is an extension of US Standard Atmosphere 1976 model to work above 84K
        altitude_asl = ((altitude + agl) / 1000.0)
        atmo = coesa76([altitude_asl], alt_type='geopotential')

        temp = float(atmo.T[0]) + self.temperatureCompensation(agl, T_agl)
        pressure = float(atmo.P[0])

        return temp, pressure

    def atmosphericConditions(self, model : int, altitude : float, agl : float = 0, T_agl : float = 288.15) -> tuple[float, float]:

        # Get the atmospheric conditions at the specified altitude (convert mm to km)
        if model == ATMOS_POF_615:
            temp, pressure = self.atmospherePOF615(altitude, agl, T_agl)
        elif model == ATMOS_COESA_GEOMETRIC:
            temp, pressure = self.atmosphereCOESAGeometric(altitude, agl, T_agl)
        elif model == ATMOS_COESA_GEOPOTENTIAL:
            temp, pressure = self.atmosphereCOESAGeopotential(altitude, agl, T_agl)
        else:
            temp, pressure = self.atmosphereUSSA(altitude, agl, T_agl)

        # speed of sound
        mach = math.sqrt(gamma * R_air * temp)

        return mach,pressure

    def flutter(self, model : int, altitude : float, shear : float) -> tuple[float, float]:
        # Calculate fin flutter using the method outlined in NACA Technical Note 4197

        a,pressure = self.atmosphericConditions(model, altitude)

        shear *= 1000.0 # Convert from kPa to Pa

        # The coefficient is adjusted for SI units
        Vf = math.sqrt(shear /
                       ((270964.068 * (self._aspectRatio**3)) /
                        (pow(self._thickness / self._rootChord, 3) * (self._aspectRatio + 2)) * ((self._lambda + 1) / 2) * (pressure / p0)))

        # Flutter velocity in m/s
        Vfa = a * Vf

        return Vf, Vfa

    def flutterPOF615(self, model : int, altitude : float, shear : float, agl : float, T_agl : float) -> tuple[float, float]:
        #
        # Calculate flutter using the formula outlined in Peak of Flight issue 615
        #
        a,pressure = self.atmosphericConditions(model, altitude, agl, T_agl)

        shear *= 1000.0 # Convert from kPa to Pa

        # Flutter velocity in Mach
        Vf = math.sqrt(
            shear /
            ((self._DN * (self._aspectRatio**3)) / (pow(self._thickness / self._rootChord, 3) * (self._aspectRatio + 2)) *
                ((self._lambda + 1) / 2) * (pressure / p0)))

        # Flutter velocity in m/s
        Vfa = a * Vf

        return Vf, Vfa

    def flutterPOF(self, model : int, altitude : float, shear : float) -> tuple[float, float]:
        #
        # Calculate flutter using the formula outlined in Peak of Flight issue 291
        # There is some discussion that this may over estimate the flutter by a factor of sqrt(2) vs the NACA method
        #

        a,pressure = self.atmosphericConditions(model, altitude)

        shear *= 1000.0 # Convert from kPa to Pa

        # Flutter velocity in Mach
        Vf = math.sqrt((shear * 2 * (self._aspectRatio + 2) * pow(self._thickness / self._rootChord, 3)) /
                       (1.337 * pow(self._aspectRatio, 3) * pressure * (self._lambda + 1)))

        # Flutter velocity in m/s
        Vfa = a * Vf

        return Vf, Vfa

    def divergence(self, model : int, altitude : float, shear : float, agl : float, T_agl : float) -> tuple[float, float]:
        # Calculate fin divergence using the method outlined in NACA Technical Note 4197

        a,pressure = self.atmosphericConditions(model, altitude, agl, T_agl)

        shear *= 1000.0 # Convert from kPa to Pa

        # Divergent velocity in Mach
        Vd = math.sqrt(shear /
                       (((3.3 * pressure) / (1 + (2 / self._aspectRatio))) *
                        ((self._rootChord + self._tipChord) / self._thickness**3) * (self._span**2)))

        # Divergent velocity in m/s
        Vda = a * Vd

        return Vd, Vda

