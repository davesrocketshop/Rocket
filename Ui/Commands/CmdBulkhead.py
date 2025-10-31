# ***************************************************************************
# *   Copyright (c) 2021-2025 David Carter <dcarter@davidcarter.ca>         *
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
"""Class for drawing bulkheads"""

__title__ = "FreeCAD Bulkheads"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

from Rocket.FeatureBulkhead import FeatureBulkhead
if FreeCAD.GuiUp:
    from Ui.ViewBulkhead import ViewProviderBulkhead
    from Ui.Widgets.WaitCursor import WaitCursor
from Ui.Commands.Command import Command

from Rocket.Constants import FEATURE_BULKHEAD

translate = FreeCAD.Qt.translate

def makeBulkhead(name='Bulkhead'):
    '''makeBulkhead(name): makes a bulkhead'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureBulkhead(obj)
    obj.Proxy.setDefaults()
    if FreeCAD.GuiUp:
        ViewProviderBulkhead(obj.ViewObject)

    return obj.Proxy

class CmdBulkhead(Command):
    def Activated(self):
        with WaitCursor():
            FreeCAD.ActiveDocument.openTransaction("Create bulkhead")
            FreeCADGui.addModule("Ui.Commands.CmdBulkhead")
            FreeCADGui.doCommand("obj=Ui.Commands.CmdBulkhead.makeBulkhead('Bulkhead')")
            FreeCADGui.doCommand("Ui.Commands.CmdStage.addToStage(obj)")
            FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return self.partEligibleFeature(FEATURE_BULKHEAD)
        return False

    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Bulkhead'),
                'ToolTip': translate("Rocket", 'Add a bulkhead'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Bulkhead.svg"}
