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

from Analyzers.pyatmos import coesa76
from Analyzers.pyatmos.utils.Const import p0, gamma, R_air

from App.Constants import FIN_TYPE_TRAPEZOID

class FinFlutter:

    def __init__(self, fin):
        self._fin = fin
        
        if fin.FinType != FIN_TYPE_TRAPEZOID:
            raise TypeError("Only trapezoidal fins are supported at this time")

        # Convert from mm to m
        self._tipChord = float(fin.TipChord) / 1000.0
        self._rootChord = float(fin.RootChord) / 1000.0
        self._thickness = float(fin.RootThickness) / 1000.0
        self._semiSpan = float(fin.Height) / 1000.0

        self._area = (self._rootChord + self._tipChord) * self._semiSpan / 2.0
        print("area %f" % self._area)
        self._aspectRatio = self._semiSpan**2 / self._area
        print("aspectRatio %f" % self._aspectRatio)
        self._lambda = self._tipChord / self._rootChord
        print("lambda %f" % self._lambda)

    def flutter(self, altitude, G):

        # Get the atmospheric conditions at the specified altitude (convert mm to km)
        atmo = coesa76([altitude / (1000.0 * 1000.0)])

        temp = atmo.T
        print("temp %f" % temp)
        pressure = atmo.P
        print("pressure %f" % pressure)

        # speed of sound
        a = math.sqrt(gamma * R_air * temp)
        print("a %f" % a)

        # Flutter velocity in Mach
        coeff = 39.3
        # coeff = 24 * .25 / math.pi * 1.4 * p0
        print("coeff %f" % coeff)

        # temp -= 273.15


        print("G %f" % G)
        t0 = (coeff * (self._aspectRatio**3))
        print("t0 %g" % t0)
        t1 = (pow(self._thickness / self._rootChord, 3) * (self._aspectRatio + 2))
        print("t1 %g" % t1)
        t2 = (self._lambda + 1) / 2
        print("t2 %f" % t2)
        t3 = pressure / p0
        print("t3 %f" % t3)
        Vf = math.sqrt(G / ((39.3 * (self._aspectRatio**3)) / (pow(self._thickness / self._rootChord, 3) * (self._aspectRatio + 2)) * ((self._lambda + 1) / 2) * (pressure / p0)))
        print("Vf %f" % Vf)

        # Flutter velocity in m/s
        Vfa = a * Vf
        print("Vfa %f" % Vfa)

        # Divergent velocity in Mach
        Vd = math.sqrt(G / (((3.3 * pressure) / (1 + (2 / self._aspectRatio))) * ((self._rootChord + self._tipChord) / self._thickness**3) * (self._semiSpan**2)))
        print("Vd %f" % Vd)

        # Divergent velocity in m/s
        Vda = a * Vd
        print("Vda %f" % Vda)

        return Vf, Vfa, Vd, Vda
        
