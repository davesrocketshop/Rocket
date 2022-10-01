# ***************************************************************************
# *   Copyright (c) 2022 David Carter <dcarter@davidcarter.ca>              *
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

from DraftTools import translate

from Analyzers.pyatmos import coesa76
from Analyzers.pyatmos.utils.Const import p0, gamma, R_air

from App.Constants import FIN_TYPE_TRAPEZOID, FIN_TYPE_ELLIPSE, FIN_TYPE_SKETCH

from App.FinTrapezoidShapeHandler import FinTrapezoidShapeHandler
from App.FinEllipseShapeHandler import FinEllipseShapeHandler
from App.FinSketchShapeHandler import FinSketchShapeHandler

class FinFlutter:

    def __init__(self, fin):
        self._fin = fin

        # Create the fin shape without any extras such as TTW tabs, fin cans, etc
        # From this we can get properties such as CG, Volume, etc...
        handler = None
        if fin.FinType == FIN_TYPE_TRAPEZOID:
            handler = FinTrapezoidShapeHandler(fin)
        elif fin.FinType == FIN_TYPE_ELLIPSE:
            handler = FinEllipseShapeHandler(fin)
        elif fin.FinType == FIN_TYPE_SKETCH:
            handler = FinSketchShapeHandler(fin)
        self._Shape = handler.finOnlyShape()
        
        if fin.FinType == FIN_TYPE_TRAPEZOID:

            # Convert from mm to m
            self._tipChord = self._fromMM(fin.TipChord)
            self._rootChord = self._fromMM(fin.RootChord)
            if float(fin.RootThickness) != float(fin.TipThickness):
                raise TypeError(translate('Rocket', "Tapered thickness fins are not supported at this time"))

            self._span = self._fromMM(fin.Height)
            self._area = (self._rootChord + self._tipChord) * self._span / 2.0
            self._volume = float(self._Shape.Volume) * 1e-9 # mm^3 to m^3
            self._thickness = self._volume / self._area

            # This is experimental. It's veracity still needs to be confirmed
            # cg = self._Shape.CenterOfGravity
            # print("CG(%f, %fm %f)" % (cg.x, cg.y, cg.z))
            # self._epsilon = math.fabs((0.75 * self._rootChord) - self._fromMM(cg.x)) / self._rootChord # Does this work for forward sweeps?
            # print("epsilon %f" % (self._epsilon))

            # self._epsilon = self._epsilon / 0.25 # NACA Eqn 18 already has an epsilon value of 0.25, so need to compensate

        elif fin.FinType == FIN_TYPE_ELLIPSE:
            raise TypeError(translate('Rocket', "Elliptical fins are not supported at this time"))

            # # Convert from mm to m
            # self._tipChord = 0.0
            # self._rootChord = float(fin.RootChord) / 1000.0
            # self._thickness = float(fin.RootThickness) / 1000.0
            # self._span = float(fin.Height) / 1000.0

            # self._area = math.pi * (self._rootChord / 2.0) * self._span 
        else:
            raise TypeError(translate('Rocket', "Custom fins are not supported at this time"))

        self._aspectRatio = self._span**2 / self._area
        self._lambda = self._tipChord / self._rootChord

    def _fromMM(self, value):
        return float(value) / 1000.0

    def shearModulus(self, young, poisson):
        return young / (2.0 * (1.0 + poisson))

    def atmosphericConditions(self, altitude):

        # Get the atmospheric conditions at the specified altitude (convert mm to km)
        # Uses the coesa76 model which is an extension of US Standard Atmosphere 1976 model to work above 84K
        atmo = coesa76([altitude / (1000.0 * 1000.0)])

        temp = atmo.T
        pressure = atmo.P

        # speed of sound
        a = math.sqrt(gamma * R_air * temp)

        return a,pressure

    def flutter(self, altitude, shear):
        # Calculate fin flutter using the method outlined in NACA Technical Note 4197

        a,pressure = self.atmosphericConditions(altitude)

        shear *= 1000.0 # Convert from kPa to Pa

        # The coefficient is adjusted for SI units
        Vf = math.sqrt(shear / ((270964.068 * (self._aspectRatio**3)) / (pow(self._thickness / self._rootChord, 3) * (self._aspectRatio + 2)) * ((self._lambda + 1) / 2) * (pressure / p0)))

        # This is experimental. Its validity is not yet confirmed
        # Vfe = math.sqrt(shear / ((270964.068 * self._epsilon * (self._aspectRatio**3)) / (pow(self._thickness / self._rootChord, 3) * (self._aspectRatio + 2)) * ((self._lambda + 1) / 2) * (pressure / p0)))
        # print("Vf %f" % (Vf))
        # print("Vfe %f" % (Vfe))
        
        # Flutter velocity in m/s
        Vfa = a * Vf

        return Vf, Vfa

    def flutterPOF(self, altitude, shear):
        #
        # Calculate flutter using the formula outlined in Peak of Flight issue 291
        # There is some discussion that this may over estimate the flutter by a factor of sqrt(2) vs the NACA method
        #

        a,pressure = self.atmosphericConditions(altitude)

        shear *= 1000.0 # Convert from kPa to Pa

        # Flutter velocity in Mach
        Vf = math.sqrt((shear * 2 * (self._aspectRatio + 2) * pow(self._thickness / self._rootChord, 3)) / (1.337 * pow(self._aspectRatio, 3) * pressure * (self._lambda + 1)))

        # Flutter velocity in m/s
        Vfa = a * Vf

        return Vf, Vfa

    def divergence(self, altitude, shear):
        # Calculate fin divergence using the method outlined in NACA Technical Note 4197

        a,pressure = self.atmosphericConditions(altitude)

        shear *= 1000.0 # Convert from kPa to Pa

        # Divergent velocity in Mach
        Vd = math.sqrt(shear / (((3.3 * pressure) / (1 + (2 / self._aspectRatio))) * ((self._rootChord + self._tipChord) / self._thickness**3) * (self._span**2)))

        # Divergent velocity in m/s
        Vda = a * Vd

        return Vd, Vda
        
