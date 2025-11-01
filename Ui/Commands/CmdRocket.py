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
"""Class for drawing rocket assemblies"""

__title__ = "FreeCAD Rocket Assembly"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"


import FreeCAD
import FreeCADGui

translate = FreeCAD.Qt.translate

from Rocket.FeatureRocket import FeatureRocket

if FreeCAD.GuiUp:
    from Ui.Widgets.WaitCursor import WaitCursor
from Ui.Commands.Command import Command
from Ui.Commands.CmdStage import makeStage

def updateRocket():
    rocket = FreeCADGui.ActiveDocument.ActiveView.getActiveObject("rocket")
    if rocket:
        rocket.Proxy.updateChildren()

def makeRocket(name='Rocket', makeSustainer=False):
    obj = FreeCAD.ActiveDocument.addObject("App::GeometryPython",name)
    FeatureRocket(obj)
    obj.Proxy.setDefaults()
    if FreeCAD.GuiUp:
        from Ui.ViewRocket import ViewProviderRocket
        ViewProviderRocket(obj.ViewObject)
        FreeCADGui.ActiveDocument.ActiveView.setActiveObject('rocket', obj)

    if makeSustainer:
        sustainer = makeStage('Stage')
        obj.Proxy.addChild(sustainer._obj)
        FreeCADGui.Selection.clearSelection()
        FreeCADGui.Selection.addSelection(sustainer._obj)
    else:
        FreeCADGui.Selection.clearSelection()
        FreeCADGui.Selection.addSelection(obj)

    # obj.Proxy.enableEvents()
    return obj.Proxy

class CmdRocket(Command):
    def Activated(self):
        with WaitCursor():
            FreeCAD.ActiveDocument.openTransaction("Create rocket assembly")
            FreeCADGui.addModule("Ui.Commands.CmdRocket")
            FreeCADGui.doCommand("rocket=Ui.Commands.CmdRocket.makeRocket('Rocket', True)")
            FreeCADGui.doCommand("rocket.enableEvents()")
            FreeCADGui.doCommand("App.ActiveDocument.commitTransaction()")
            FreeCADGui.doCommand("App.activeDocument().recompute(None,True,True)")

    def IsActive(self):
        return self.noRocketBuilder()

    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Rocket'),
                'ToolTip': translate("Rocket", 'Creates a rocket assembly'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Rocket.svg"}

class CmdToggleRocket:
    def GetResources(self):
        return {'MenuText': translate("Rocket","Toggle active rocket"),
                'ToolTip' : translate("Rocket","Toggles the active rocket assembly")}

    def IsActive(self):
        return bool(FreeCADGui.Selection.getSelection())

    def Activated(self):
        with WaitCursor():
            view = FreeCADGui.ActiveDocument.ActiveView

            for obj in FreeCADGui.Selection.getSelection():
                if view.getActiveObject('rocket') == obj:
                    view.setActiveObject("rocket", None)
                else:
                    view.setActiveObject("rocket", obj)
