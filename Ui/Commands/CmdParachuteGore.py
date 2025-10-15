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
"""Class for drawing parachute gores"""

__title__ = "FreeCAD Parachute Gores"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

from Rocket.FeatureFin import FeatureFin
if FreeCAD.GuiUp:
    from Ui.ViewParachuteGore import ViewProviderParachuteGore
    from Ui.Widgets.WaitCursor import WaitCursor

translate = FreeCAD.Qt.translate

def makeParachuteGore(name : str) -> FeatureFin:
    '''makeParachuteGore(name): makes a Fin'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureFin(obj)

    if FreeCAD.GuiUp:
        ViewProviderParachuteGore(obj.ViewObject)

        body=FreeCADGui.ActiveDocument.ActiveView.getActiveObject("pdbody")
        part=FreeCADGui.ActiveDocument.ActiveView.getActiveObject("part")
        if body:
            body.Group=body.Group+[obj]
        elif part:
            part.Group=part.Group+[obj]
    return obj

class CmdParachuteGore:
    def Activated(self) -> None:
        with WaitCursor():
            FreeCAD.ActiveDocument.openTransaction("Create parachute  gore")
            FreeCADGui.addModule("Ui.Commands.CmdParachuteGore")
            FreeCADGui.doCommand("Ui.Commands.CmdParachuteGore.makeParachuteGore('Gore')")
            FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self) -> bool:
        if FreeCAD.ActiveDocument:
            return True
        return False

    def GetResources(self) -> dict:
        return {'MenuText': translate("Rocket", 'Parachute Gore'),
                'ToolTip': translate("Rocket", 'Parachute gore design'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_ParachuteGore.svg"}
