# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for running parametric CFD Analysis"""

__title__ = "FreeCAD CFD Analysis"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
from CfdOF import CfdAnalysis, CfdTools

from Rocket.Constants import FEATURE_CFD_ANALYSIS

translate = FreeCAD.Qt.translate

class FeatureMultiCFDAnalysis(CfdAnalysis.CfdAnalysis):

    def __init__(self, obj):
        super().__init__(obj)
        # self.Type = FEATURE_CFD_ANALYSIS
        # self.version = '3.0'

        # self._obj = obj
        # obj.Proxy=self

    def initProperties(self, obj):
        super().initProperties(obj)

        if not hasattr(obj,"Shape"):
            obj.addProperty('Part::PropertyPartShape', 'Shape', 'RocketComponent', translate('App::Property', 'Shape of the base rocket'))
        if not hasattr(obj,"AOAList"):
            obj.addProperty('App::PropertyFloatList', 'AOAList', 'RocketComponent', translate('App::Property', 'List of AOAs to calculate'))
            obj.AOAList = [2.0] # Default AOA of 2 degrees
        if not hasattr(obj,"CFDRocket"):
            obj.addProperty('App::PropertyLinkGlobal', 'CFDRocket', 'RocketComponent', translate('App::Property', 'The rocket under study'))
        if not hasattr(obj,"Rocket"):
            obj.addProperty('App::PropertyLinkGlobal', 'Rocket', 'RocketComponent', translate('App::Property', 'The rocket under study'))
        if not hasattr(obj,"AverageLastN"):
            obj.addProperty('App::PropertyInteger', 'AverageLastN', 'RocketComponent', translate('App::Property', 'Use average of last N values')).AverageLastN = 5

    # def __getstate__(self):
    #     return self.Type, self.version

    # def __setstate__(self, state):
    #     if state:
    #         self.Type = state[0]
    #         self.version = state[1]

    # def onDocumentRestored(self, obj):
    #     FeatureMultiCFDAnalysis(obj)
    #     self._obj = obj

    # def execute(self, obj):
    #     # shape = WindTunnelShapeHandler(obj)
    #     # if shape:
    #     #     shape.draw()
    #     pass
