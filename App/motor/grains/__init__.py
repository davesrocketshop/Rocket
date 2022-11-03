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
"""Class for rocket motors"""

__title__ = "FreeCAD Rocket Motors"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from App.Constants import GRAIN_GEOMETRY_BATES, GRAIN_GEOMETRY_C, GRAIN_GEOMETRY_CONICAL, GRAIN_GEOMETRY_CUSTOM, \
    GRAIN_GEOMETRY_D, GRAIN_GEOMETRY_END, GRAIN_GEOMETRY_FINOCYL, GRAIN_GEOMETRY_MOONBURNER, GRAIN_GEOMETRY_RODTUBE, \
    GRAIN_GEOMETRY_STAR, GRAIN_GEOMETRY_XCORE

from .endBurner import *
from .bates import *
from .finocyl import *
from .moonBurner import *
from .star import *
from .xCore import *
from .cGrain import *
from .dGrain import *
from .rodTube import *
from .conical import *
from .custom import *

# Generate grain geometry name -> constructor lookup table
grainTypes = {
    GRAIN_GEOMETRY_BATES : BatesGrain,
    GRAIN_GEOMETRY_C : CGrain,
    GRAIN_GEOMETRY_CONICAL : ConicalGrain,
    GRAIN_GEOMETRY_CUSTOM : CustomGrain,
    GRAIN_GEOMETRY_D : DGrain,
    GRAIN_GEOMETRY_END : EndBurningGrain,
    GRAIN_GEOMETRY_FINOCYL : Finocyl,
    GRAIN_GEOMETRY_MOONBURNER : MoonBurner,
    GRAIN_GEOMETRY_RODTUBE : RodTubeGrain,
    GRAIN_GEOMETRY_STAR : StarGrain,
    GRAIN_GEOMETRY_XCORE : XCore
}

grainClasses = [BatesGrain, EndBurningGrain, Finocyl, MoonBurner, StarGrain, XCore, CGrain, DGrain, RodTubeGrain,
                ConicalGrain, CustomGrain]
