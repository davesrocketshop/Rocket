# ***************************************************************************
# *   Copyright (c) 2021-2024 David Carter <dcarter@davidcarter.ca>         *
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
"""Class for drawing wind tunnels"""

__title__ = "FreeCAD Wind Tunnel"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from Rocket.Constants import FEATURE_WIND_TUNNEL

from Rocket.cfd.ShapeHandlers.WindTunnelShapeHandler import WindTunnelShapeHandler

from DraftTools import translate

class FeatureWindTunnel:

    def __init__(self, obj):
        # super().__init__(obj)
        self.Type = FEATURE_WIND_TUNNEL
        self.version = '3.0'

        self._obj = obj
        self._parent = None
        obj.Proxy=self

        if not hasattr(obj,"Diameter"):
            obj.addProperty('App::PropertyLength', 'Diameter', 'RocketComponent', translate('App::Property', 'Diameter of the wind tunnel')).Diameter = 10.0
        if not hasattr(obj,"Length"):
            obj.addProperty('App::PropertyLength', 'Length', 'RocketComponent', translate('App::Property', 'Length of the wind tunnel')).Length = 20

        if not hasattr(obj,"Shape"):
            obj.addProperty('Part::PropertyPartShape', 'Shape', 'RocketComponent', translate('App::Property', 'Shape of the wind tunnel'))

    def onDocumentRestored(self, obj):
        FeatureWindTunnel(obj)
        self._obj = obj

    def execute(self, obj):
        shape = WindTunnelShapeHandler(obj)
        if shape is not None:
            shape.draw()
