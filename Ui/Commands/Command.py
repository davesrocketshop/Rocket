# ***************************************************************************
# *   Copyright (c) 2021 David Carter <dcarter@davidcarter.ca>              *
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
    
import FreeCADGui

class Command:

    def part_feature_selected(self):
        if FreeCADGui.ActiveDocument is None:
            return False
        sel = FreeCADGui.Selection.getSelection()
        if len(sel) == 1 and sel[0].isDerivedFrom("Part::Feature"):
            return True
        else:
            return False

    def part_fin_selected(self):
        if FreeCADGui.ActiveDocument is not None:
            sel = FreeCADGui.Selection.getSelection()
            if len(sel) == 1 and sel[0].isDerivedFrom("Part::FeaturePython"):
                if hasattr(sel[0],"FinType"):
                    return True
        return False

    def part_eligible_feature(self, feature):
        if FreeCADGui.ActiveDocument is not None:
            sel = FreeCADGui.Selection.getSelection()
            if len(sel) == 1 and sel[0].isDerivedFrom("Part::FeaturePython"):
                if isinstance(feature, list):
                    for f in feature:
                        if sel[0].Proxy.eligibleChild(f):
                            return True
                elif sel[0].Proxy.eligibleChild(feature):
                    return True
        return False
