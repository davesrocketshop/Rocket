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
"""Class for drawing fins"""

__title__ = "FreeCAD Fins"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

from Rocket.Constants import FEATURE_FIN, FIN_TYPE_SKETCH
from Rocket.FeatureFin import FeatureFin
from Ui.ViewFin import ViewProviderFin
from Ui.Commands.Command import Command

from DraftTools import translate

def makeFin(name='Fin'):
    '''makeFin(name): makes a Fin'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureFin(obj)
    obj.Proxy.setDefaults()

    # See if we have a sketch selected. If so, this is a custom fin
    for sketch in FreeCADGui.Selection.getSelection():
        if sketch.isDerivedFrom('Sketcher::SketchObject'):
            obj.FinType = FIN_TYPE_SKETCH
            obj.Profile = sketch
            sketch.Visibility = False

    if FreeCAD.GuiUp:
        ViewProviderFin(obj.ViewObject)

    return obj.Proxy

class CmdFin(Command):
    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction("Create fin")
        FreeCADGui.addModule("Ui.Commands.CmdFin")
        FreeCADGui.doCommand("obj=Ui.Commands.CmdFin.makeFin('Fin')")
        FreeCADGui.doCommand("Ui.Commands.CmdStage.addToStage(obj)")
        FreeCADGui.doCommand("FreeCADGui.Selection.clearSelection()")
        FreeCADGui.doCommand("FreeCADGui.Selection.addSelection(obj._obj)")
        FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return self.partEligibleFeature(FEATURE_FIN)
        return False

    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Fin'),
                'ToolTip': translate("Rocket", 'Fin design'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Fin.svg"}
