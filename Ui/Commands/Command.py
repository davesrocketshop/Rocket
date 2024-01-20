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
"""Base class for commands"""

__title__ = "FreeCAD Commands"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import FreeCADGui

import FemGui

from Rocket.Constants import FEATURE_ROCKET

def getRocket():
    for obj in FreeCAD.ActiveDocument.Objects:
        if hasattr(obj, "Proxy"):
            if hasattr(obj.Proxy, "getType"):
                if obj.Proxy.getType() == FEATURE_ROCKET:
                    return obj.Proxy

    return None

class Command:

    def partFeatureSelected(self):
        """
            True if the selected object is a workbench feature
        """
        if FreeCADGui.ActiveDocument is None:
            return False
        sel = FreeCADGui.Selection.getSelection()
        if len(sel) == 1 and (sel[0].isDerivedFrom("Part::FeaturePython") or sel[0].isDerivedFrom("App::GeometryPython")):
            return True
        else:
            return False

    def partMoveableFeatureSelected(self):
        """
            True if the selected object is a workbench feature, and can be moved in the tree
        """
        if FreeCADGui.ActiveDocument is None:
            return False
        sel = FreeCADGui.Selection.getSelection()
        if len(sel) == 1:
            if sel[0].isDerivedFrom("Part::FeaturePython"):
                if sel[0].Proxy.getParent() is not None:
                    return True
            if sel[0].isDerivedFrom("App::GeometryPython"):
                return sel[0].Proxy.Type != FEATURE_ROCKET

        return False

    def partFinSelected(self):
        """
            True if the selected object has fins (Fin, FinCan)
        """
        if FreeCADGui.ActiveDocument is not None:
            sel = FreeCADGui.Selection.getSelection()
            if len(sel) == 1 and sel[0].isDerivedFrom("Part::FeaturePython"):
                if hasattr(sel[0],"FinType"):
                    return True
        return False

    def partStageEligibleFeature(self, feature):
        """
            Checks to see if we're at a point where we can add a stage. Stages can't be a standalone feature
        """
        if FreeCADGui.ActiveDocument is not None:
            sel = FreeCADGui.Selection.getSelection()
            if len(sel) == 1 and (sel[0].isDerivedFrom("Part::FeaturePython") or sel[0].isDerivedFrom("App::GeometryPython")):
                if isinstance(feature, list):
                    for f in feature:
                        if sel[0].Proxy.eligibleChild(f):
                            return True
                elif sel[0].Proxy.eligibleChild(feature):
                    return True
        return False

    def partEligibleFeature(self, feature):
        """
            Checks to see if we can add a part. If a rocket or one of its parts is selected, then we check to see if the
            part can be added to the current feature. Outside of a rocket, parts can be added as standalone objects.
        """
        if FreeCADGui.ActiveDocument is not None:
            if getRocket() is None:
                return True
            sel = FreeCADGui.Selection.getSelection()
            if len(sel) == 1 and (sel[0].isDerivedFrom("Part::FeaturePython") or sel[0].isDerivedFrom("App::GeometryPython")):
                if isinstance(feature, list):
                    for f in feature:
                        if sel[0].Proxy.eligibleChild(f):
                            return True
                elif sel[0].Proxy.eligibleChild(feature):
                    return True
                return False
        return True

    def noRocketBuilder(self):
        if FreeCADGui.ActiveDocument is None:
            return False

        if getRocket() is None:
            return True
        return False
        
    def hasActiveAnalysis(self):
        return (FemGui.getActiveAnalysis() is not None)
        
    def hasActiveAnalysisAndFin(self):
        if FemGui.getActiveAnalysis():
            return self.partFinSelected()
        return False
