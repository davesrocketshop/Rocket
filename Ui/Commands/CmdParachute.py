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
"""Class for drawing parachutes"""

__title__ = "FreeCAD Parachutes"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

from Rocket.FeatureFin import FeatureFin
if FreeCAD.GuiUp:
    from Ui.ViewParachute import ViewProviderParachute
    from Ui.Widgets.WaitCursor import WaitCursor

translate = FreeCAD.Qt.translate

def makeParachute(name):
    '''makeParachute(name): makes a Parachute'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureFin(obj)
    obj.Proxy.setDefaults()

    if FreeCAD.GuiUp:
        ViewProviderParachute(obj.ViewObject)

    return obj.Proxy

class CmdParachute:
    def Activated(self):
        with WaitCursor():
            FreeCAD.ActiveDocument.openTransaction("Create parachute")
            FreeCADGui.addModule("Ui.Commands.CmdParachute")
            FreeCADGui.doCommand("obj=Ui.Commands.CmdParachute.makeParachute('Parachute')")
            FreeCADGui.doCommand("Ui.Commands.CmdStage.addToStage(obj)")
            FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        return False

    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Parachute'),
                'ToolTip': translate("Rocket", 'Add a parachute'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Parachute.svg"}
