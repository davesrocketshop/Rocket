# ***************************************************************************
# *   Copyright (c) 2021-2023 David Carter <dcarter@davidcarter.ca>         *
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
"""Class for drawing fins"""

__title__ = "FreeCAD Fins"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from Rocket.SymmetricComponent import SymmetricComponent
from Rocket.FeatureFin import FeatureFin
from Rocket.Constants import FEATURE_FINCAN, FEATURE_LAUNCH_LUG, FEATURE_RAIL_BUTTON, FEATURE_RAIL_GUIDE, FEATURE_POD, FEATURE_STAGE
from Rocket.Constants import FIN_TYPE_TRAPEZOID, FIN_TYPE_TRIANGLE, FIN_TYPE_ELLIPSE, FIN_TYPE_SKETCH
from Rocket.Constants import FINCAN_STYLE_SLEEVE, FINCAN_STYLE_BODYTUBE
from Rocket.Constants import FINCAN_EDGE_SQUARE, FINCAN_EDGE_ROUND, FINCAN_EDGE_TAPER
from Rocket.Constants import FINCAN_PRESET_CUSTOM, FINCAN_PRESET_1_8, FINCAN_PRESET_3_16, FINCAN_PRESET_1_4
from Rocket.Constants import FINCAN_COUPLER_MATCH_ID, FINCAN_COUPLER_STEPPED
from Rocket.Constants import PROP_NONE
from Rocket.Constants import EDITOR_NONE, EDITOR_HIDDEN

from Rocket.position.AxialMethod import BOTTOM, AFTER

from Rocket.ShapeHandlers.FinCanShapeHandler import FinCanTrapezoidShapeHandler
from Rocket.ShapeHandlers.FinCanShapeHandler import FinCanTriangleShapeHandler
from Rocket.ShapeHandlers.FinCanShapeHandler import FinCanEllipseShapeHandler
from Rocket.ShapeHandlers.FinCanShapeHandler import FinCanSketchShapeHandler

from DraftTools import translate

class FeatureFinCan(SymmetricComponent, FeatureFin):

    def __init__(self, obj):
        super().__init__(obj)
        self.Type = FEATURE_FINCAN

        # Fin cans aren't TTW and are a fin set
        obj.Ttw = False
        obj.FinSet = True

        # Default set to fit on a BT-50
        if not hasattr(obj,"FinCanStyle"):
            obj.addProperty('App::PropertyEnumeration', 'FinCanStyle', 'RocketComponent', translate('App::Property', 'Fin can style'))
            obj.FinCanStyle = [FINCAN_STYLE_SLEEVE, FINCAN_STYLE_BODYTUBE]
            obj.FinCanStyle = FINCAN_STYLE_SLEEVE
        else:
            obj.FinCanStyle = [FINCAN_STYLE_SLEEVE, FINCAN_STYLE_BODYTUBE]

        if not hasattr(obj,"Diameter"):
            obj.addProperty('App::PropertyLength', 'Diameter', 'RocketComponent', translate('App::Property', 'Diameter of the inside or outside of the fin candepending on the style')).Diameter = 24.8
        if not hasattr(obj,"Thickness"):
            obj.addProperty('App::PropertyLength', 'Thickness', 'RocketComponent', translate('App::Property', 'Thickness of the fin can')).Thickness = 1.5
        if not hasattr(obj,"LeadingEdgeOffset"):
            obj.addProperty('App::PropertyDistance', 'LeadingEdgeOffset', 'RocketComponent', translate('App::Property', 'Distance between the fin can leading edge and the fin leading edge')).LeadingEdgeOffset = 0.0

        if not hasattr(obj,"LeadingEdge"):
            obj.addProperty('App::PropertyEnumeration', 'LeadingEdge', 'RocketComponent', translate('App::Property', 'Leading Edge'))
            obj.LeadingEdge = [FINCAN_EDGE_SQUARE, FINCAN_EDGE_ROUND, FINCAN_EDGE_TAPER]
            obj.LeadingEdge = FINCAN_EDGE_SQUARE
        else:
            obj.LeadingEdge = [FINCAN_EDGE_SQUARE, FINCAN_EDGE_ROUND, FINCAN_EDGE_TAPER]

        if not hasattr(obj,"LeadingLength"):
            obj.addProperty('App::PropertyLength', 'LeadingLength', 'RocketComponent', translate('App::Property', 'Leading Edge Length')).LeadingLength = 5.0

        if not hasattr(obj,"TrailingEdge"):
            obj.addProperty('App::PropertyEnumeration', 'TrailingEdge', 'RocketComponent', translate('App::Property', 'Trailing Edge'))
            obj.TrailingEdge = [FINCAN_EDGE_SQUARE, FINCAN_EDGE_ROUND, FINCAN_EDGE_TAPER]
            obj.TrailingEdge = FINCAN_EDGE_SQUARE
        else:
            obj.TrailingEdge = [FINCAN_EDGE_SQUARE, FINCAN_EDGE_ROUND, FINCAN_EDGE_TAPER]
        if not hasattr(obj,"TrailingLength"):
            obj.addProperty('App::PropertyLength', 'TrailingLength', 'RocketComponent', translate('App::Property', 'Trailing Edge Length')).TrailingLength = 5.0

        if not hasattr(obj,"LaunchLug"):
            obj.addProperty('App::PropertyBool', 'LaunchLug', 'RocketComponent', translate('App::Property', 'Fin can includes a launch lug')).LaunchLug = True
        if not hasattr(obj,"LugInnerDiameter"):
            obj.addProperty('App::PropertyLength', 'LugInnerDiameter', 'RocketComponent', translate('App::Property', 'Diameter of the inside of the launch lug')).LugInnerDiameter = 3.56
        if not hasattr(obj,"LugThickness"):
            obj.addProperty('App::PropertyLength', 'LugThickness', 'RocketComponent', translate('App::Property', 'Thickness of the launch lug')).LugThickness = 1.5
        if not hasattr(obj,"LugAutoThickness"):
            obj.addProperty('App::PropertyBool', 'LugAutoThickness', 'RocketComponent', translate('App::Property', 'Launch lug thickness is the same as the fin can')).LugAutoThickness = True
        if not hasattr(obj,"LugLength"):
            obj.addProperty('App::PropertyLength', 'LugLength', 'RocketComponent', translate('App::Property', 'Length of the launch lug')).LugLength = 60.0
        if not hasattr(obj,"LugAutoLength"):
            obj.addProperty('App::PropertyBool', 'LugAutoLength', 'RocketComponent', translate('App::Property', 'Automatically adjust the length of the launch lug')).LugAutoLength = True
        if not hasattr(obj,"LugLeadingEdgeOffset"):
            obj.addProperty('App::PropertyDistance', 'LugLeadingEdgeOffset', 'RocketComponent', translate('App::Property', 'Distance between the fin can leading edge and the launch lug leading edge')).LugLeadingEdgeOffset = 0.0
        if not hasattr(obj,"LugFilletRadius"):
            obj.addProperty('App::PropertyLength', 'LugFilletRadius', 'RocketComponent', translate('App::Property', 'Launch lug fillet radius')).LugFilletRadius = 3.0

        if not hasattr(obj, 'LaunchLugPreset'):
            obj.addProperty('App::PropertyEnumeration', 'LaunchLugPreset', 'RocketComponent', translate('App::Property', 'Launch lug size preset'))
            obj.LaunchLugPreset = [FINCAN_PRESET_CUSTOM,
                                FINCAN_PRESET_1_8, 
                                FINCAN_PRESET_3_16,
                                FINCAN_PRESET_1_4]
            obj.LaunchLugPreset = FINCAN_PRESET_1_8
        else:
            obj.LaunchLugPreset = [FINCAN_PRESET_CUSTOM,
                                FINCAN_PRESET_1_8, 
                                FINCAN_PRESET_3_16,
                                FINCAN_PRESET_1_4]

        if not hasattr(obj,"LaunchLugForwardSweep"):
            obj.addProperty('App::PropertyBool', 'LaunchLugForwardSweep', 'RocketComponent', translate('App::Property', 'Forward side of the launch lug is swept')).LaunchLugForwardSweep = True
        if not hasattr(obj,"LaunchLugForwardSweepAngle"):
            obj.addProperty('App::PropertyLength', 'LaunchLugForwardSweepAngle', 'RocketComponent', translate('App::Property', 'Forward sweep angle')).LaunchLugForwardSweepAngle = 30.0
        if not hasattr(obj,"LaunchLugAftSweep"):
            obj.addProperty('App::PropertyBool', 'LaunchLugAftSweep', 'RocketComponent', translate('App::Property', 'Aft side of the launch lug is swept')).LaunchLugAftSweep = True
        if not hasattr(obj,"LaunchLugAftSweepAngle"):
            obj.addProperty('App::PropertyLength', 'LaunchLugAftSweepAngle', 'RocketComponent', translate('App::Property', 'Aft sweep angle')).LaunchLugAftSweepAngle = 30.0

        if not hasattr(obj,"Coupler"):
            obj.addProperty('App::PropertyBool', 'Coupler', 'RocketComponent', translate('App::Property', 'Fin can includes coupler')).Coupler = False
        if not hasattr(obj, 'CouplerStyle'):
            obj.addProperty('App::PropertyEnumeration', 'CouplerStyle', 'RocketComponent', translate('App::Property', 'Launch lug size preset'))
            obj.CouplerStyle = [FINCAN_COUPLER_MATCH_ID,
                                FINCAN_COUPLER_STEPPED]
            obj.CouplerStyle = FINCAN_COUPLER_MATCH_ID
        else:
            obj.CouplerStyle = [FINCAN_COUPLER_MATCH_ID,
                                FINCAN_COUPLER_STEPPED]
        if not hasattr(obj,"CouplerThickness"):
            obj.addProperty('App::PropertyLength', 'CouplerThickness', 'RocketComponent', translate('App::Property', 'Thickness of the coupler')).CouplerThickness = 0.35
        if not hasattr(obj,"CouplerDiameter"):
            obj.addProperty('App::PropertyLength', 'CouplerDiameter', 'RocketComponent', translate('App::Property', 'Diameter of the outside of the coupler')).CouplerDiameter = 23.8
        if not hasattr(obj,"CouplerAutoDiameter"):
            obj.addProperty('App::PropertyBool', 'CouplerAutoDiameter', 'RocketComponent', translate('App::Property', 'Set coupler diamter automatically')).CouplerAutoDiameter = True
        if not hasattr(obj,"CouplerLength"):
            obj.addProperty('App::PropertyLength', 'CouplerLength', 'RocketComponent', translate('App::Property', 'Length of the coupler')).CouplerLength = 19.05

        # This is hidden for fins, but needs to be visible for fin cans
        obj.setEditorMode('AutoDiameter', PROP_NONE)  # unhide
        self._setFinCanEditorVisibility()

    def setDefaults(self):
        super().setDefaults()

        self.setFinCanPositioningMethod()
        self._obj.ParentRadius = (self._obj.Diameter / 2.0)
        self._obj.Length = 60.0

    def update(self):
        parent = self.getParent()
        if parent is not None and parent.Type in [FEATURE_STAGE]:
            self.setFinCanStyle(FINCAN_STYLE_BODYTUBE)
        else:
            self.setFinCanStyle(FINCAN_STYLE_SLEEVE)

        # Do the positioning with and new positioning method
        super().update()

        # Ensure any automatic variables are set
        self.setParentDiameter()
        # self.getTubeOuterDiameter()

    def isAfter(self):
        return (self._obj.FinCanStyle == FINCAN_STYLE_BODYTUBE)

    def setFinCanStyle(self, style):
        if self._obj.FinCanStyle == style:
            return

        self._obj.FinCanStyle = style
        self.setFinCanPositioningMethod()

    def setFinCanPositioningMethod(self):
        if self._obj.FinCanStyle == FINCAN_STYLE_SLEEVE:
            method = BOTTOM
        elif self._obj.FinCanStyle == FINCAN_STYLE_BODYTUBE:
            method = AFTER
        else:
            raise Exception(translate('Rocket', "Unknown fin can style"))
        
        self.setAxialMethod(method)
        self._setAxialOffset(self._obj.AxialMethod, 0)

    def _setFinCanEditorVisibility(self):
        self._obj.setEditorMode('Ttw', EDITOR_HIDDEN)  # hide
        self._obj.setEditorMode('TtwOffset', EDITOR_HIDDEN)  # hide
        self._obj.setEditorMode('TtwLength', EDITOR_HIDDEN)  # hide
        self._obj.setEditorMode('TtwHeight', EDITOR_HIDDEN)  # hide
        self._obj.setEditorMode('TtwThickness', EDITOR_HIDDEN)  # hide

        self._obj.setEditorMode('FinSet', EDITOR_HIDDEN)  # hide
        self._obj.setEditorMode('FinCount', EDITOR_NONE)  # show
        self._obj.setEditorMode('FinSpacing', EDITOR_NONE)  # show

    def onDocumentRestored(self, obj):
        if obj is not None:
            FeatureFinCan(obj) # Update any properties

            self._obj = obj

        self._setFinCanEditorVisibility()
        
    def setParentRadius(self, parentRadius=None):
        if parentRadius is None:
            self.setParentDiameter(parentRadius)
        else:
            self.setParentDiameter(parentRadius * 2.0)
        
    def setParentDiameterAuto(self):
        if self._obj.FinCanStyle == FINCAN_STYLE_BODYTUBE:
            # Return auto radius from front or rear
            d = -1
            inner = -1
            c = self.getPreviousSymmetricComponent()
            # Don't use the radius of a component who already has its auto diameter enabled
            if c is not None and not c.usesNextCompAutomatic():
                d = c.getFrontAutoDiameter()
                inner = c.getFrontAutoInnerDiameter()
                self._refComp = c
            if d < 0:
                c = self.getNextSymmetricComponent()
                # Don't use the radius of a component who already has its auto diameter enabled
                if c is not None and not c.usesPreviousCompAutomatic():
                    d = c.getRearAutoDiameter()
                    inner = c.getRearAutoInnerDiameter()
                    self._refComp = c

            if d < 0:
                d = self.DEFAULT_RADIUS * 2.0
            if inner < 0:
                inner = d - (2.0 * float(self._obj.Thickness))
            self._obj.ParentRadius = (d / 2.0)
            self._obj.Diameter = d - (2.0 * float(self._obj.Thickness))
            if self._obj.Coupler and self._obj.CouplerAutoDiameter:
                self._obj.CouplerDiameter = inner
                self._obj.CouplerThickness = max(self._obj.CouplerThickness,
                                                 (self._obj.CouplerDiameter - self._obj.Diameter) / 2.0)
        else:
            super().setParentDiameter()
            self._obj.Diameter = self._obj.ParentRadius * 2.0

    def setParentDiameter(self, parentDiameter=None):
        if self._obj.AutoDiameter:
            self.setParentDiameterAuto()
            return
        
        if parentDiameter is None:
            super().setParentDiameter()
            self._obj.Diameter = self._obj.ParentRadius * 2.0
        else:
            if self._obj.ParentRadius != (parentDiameter / 2.0):
                self._obj.ParentRadius = (parentDiameter / 2.0)
                self._obj.Diameter = parentDiameter

        if self._obj.FinCanStyle == FINCAN_STYLE_BODYTUBE:
            self._obj.Diameter = float(self._obj.Diameter) - (2.0 * float(self._obj.Thickness))

    def execute(self, obj):
        if obj.FinType == FIN_TYPE_TRAPEZOID:
            if self.getTipChord() > 0:
                shape = FinCanTrapezoidShapeHandler(obj)
            else:
                shape = FinCanTriangleShapeHandler(obj)
        elif obj.FinType == FIN_TYPE_TRIANGLE:
                shape = FinCanTriangleShapeHandler(obj)
        elif obj.FinType == FIN_TYPE_ELLIPSE:
            shape = FinCanEllipseShapeHandler(obj)
        elif obj.FinType == FIN_TYPE_SKETCH:
            shape = FinCanSketchShapeHandler(obj)

        if shape is not None:
            shape.draw()

    def eligibleChild(self, childType):
        return childType in [
            FEATURE_POD, 
            FEATURE_LAUNCH_LUG, 
            FEATURE_RAIL_BUTTON, 
            FEATURE_RAIL_GUIDE]

    def  getAftRadius(self):
        return self.getForeRadius()
    
    def getForeRadius(self):
        # For placing objects on the outer part of the parent
        return self.getOuterRadius()
    
    def getFrontAutoDiameter(self):
        if self.isOuterDiameterAutomatic():
            # Search for previous SymmetricComponent
            c = self.getPreviousSymmetricComponent()
            if c is not None:
                return c.getFrontAutoDiameter()
            else:
                return -1

        return self.getOuterDiameter()
    
    def getFrontAutoInnerDiameter(self):
        return self.getInnerDiameter()
    
    def getFrontAutoRadius(self):
        return self.getFrontAutoDiameter() / 2.0
    
    def getRadius(self):
        return self.getForeRadius()
    
    def getRearAutoDiameter(self):
        if self.isOuterDiameterAutomatic():
            # Search for next SymmetricComponent
            c = self.getNextSymmetricComponent()
            if c is not None:
                return c.getRearAutoDiameter()
            else:
                return -1

        return self.getOuterDiameter()
    
    def getRearAutoInnerDiameter(self):
        return self.getInnerDiameter()
    
    def getRearAutoRadius(self):
        return self.getRearAutoDiameter() / 2.0

    def getInnerDiameter(self, r=0):
        return float(self._obj.Diameter) - (2.0 * float(self._obj.Thickness))

    def isOuterDiameterAutomatic(self):
        return self._obj.AutoDiameter
    
    def isAftRadiusAutomatic(self):
        return self.getRearAutoDiameter()
    
    def isForeRadiusAutomatic(self):
        return self.getFrontAutoRadius()
    
    def usesNextCompAutomatic(self):
        return self.isOuterDiameterAutomatic() and (self._refComp == self.getNextSymmetricComponent())
    
    def usesPreviousCompAutomatic(self):
        return self.isOuterDiameterAutomatic() and (self._refComp == self.getPreviousSymmetricComponent())
    
    def explodeRadially(self):
        return False

    def explodedSize(self):
        length = float(self._obj.Length)
        if self._obj.Coupler:
            length += float(self._obj.CouplerLength)

        height = float(self._obj.ParentRadius) + float(self._obj.Height) + float(self._obj.Thickness)
        height *= 2

        for index, child in enumerate(self.getChildren()):
            childLength, childHeight = child.Proxy.explodedSize()
            # if index > 0:
            #     length += childLength + float(self._obj.AnimationDistance)
            # else:
            #     length = childLength
            height += 2 * childHeight


        return length, height
