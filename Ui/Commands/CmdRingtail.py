# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

# ***************************************************************************
# *   Copyright (c) 2025 David Carter <dcarter@davidcarter.ca>              *
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
"""Class for drawing ring tails"""

__title__ = "FreeCAD Ring Tails"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

from Rocket.FeatureRingtail import FeatureRingtail
if FreeCAD.GuiUp:
    from Ui.ViewRingtail import ViewProviderRingtail
    from Ui.Widgets.WaitCursor import WaitCursor
from Ui.Commands.Command import Command

from Rocket.Constants import FEATURE_RINGTAIL

translate = FreeCAD.Qt.translate

def makeRingtail(name='Ringtail'):
    '''makeRingtail(name): makes a ring tail'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureRingtail(obj)
    obj.Proxy.setDefaults()
    if FreeCAD.GuiUp:
        ViewProviderRingtail(obj.ViewObject)

    return obj.Proxy

class CmdRingtail(Command):
    def Activated(self):
        with WaitCursor():
            FreeCAD.ActiveDocument.openTransaction("Create ring tail")
            FreeCADGui.addModule("Ui.Commands.CmdRingtail")
            FreeCADGui.doCommand("obj=Ui.Commands.CmdRingtail.makeRingtail('Ringtail')")
            FreeCADGui.doCommand("Ui.Commands.CmdStage.addToStage(obj)")
            FreeCADGui.doCommand("FreeCADGui.Selection.clearSelection()")
            FreeCADGui.doCommand("FreeCADGui.Selection.addSelection(obj._obj)")
            FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return self.partEligibleFeature(FEATURE_RINGTAIL)
        return False

    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Ring tail'),
                'ToolTip': translate("Rocket", 'Adds a ring tail to the selected component'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Ringtail.svg"}
