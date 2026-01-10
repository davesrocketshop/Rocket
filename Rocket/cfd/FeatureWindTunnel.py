# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for drawing wind tunnels"""

__title__ = "FreeCAD Wind Tunnel"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD

translate = FreeCAD.Qt.translate

from Rocket.Constants import FEATURE_WIND_TUNNEL

from Rocket.cfd.ShapeHandlers.WindTunnelShapeHandler import WindTunnelShapeHandler

class FeatureWindTunnel:

    def __init__(self, obj):
        # super().__init__(obj)
        self.Type = FEATURE_WIND_TUNNEL
        self.version = '3.0'

        self._obj = obj
        obj.Proxy=self

        if not hasattr(obj,"Diameter"):
            obj.addProperty('App::PropertyLength', 'Diameter', 'RocketComponent', translate('App::Property', 'Diameter of the wind tunnel')).Diameter = 10.0
        if not hasattr(obj,"Length"):
            obj.addProperty('App::PropertyLength', 'Length', 'RocketComponent', translate('App::Property', 'Length of the wind tunnel')).Length = 20

        if not hasattr(obj,"Shape"):
            obj.addProperty('Part::PropertyPartShape', 'Shape', 'RocketComponent', translate('App::Property', 'Shape of the wind tunnel'))

    def __getstate__(self):
        return self.Type, self.version

    def __setstate__(self, state):
        if state:
            self.Type = state[0]
            self.version = state[1]

    def onDocumentRestored(self, obj):
        FeatureWindTunnel(obj)
        self._obj = obj

    def execute(self, obj):
        shape = WindTunnelShapeHandler(obj)
        if shape:
            shape.draw()
