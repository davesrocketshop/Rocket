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
"""Class for drawing fin cans"""

__title__ = "FreeCAD Fin Can"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import FreeCADGui

from App.Constants import FIN_TYPE_SKETCH
from App.ShapeFinCan import ShapeFinCan
from Ui.ViewFinCan import ViewProviderFinCan
from Ui.Commands.CmdStage import addToStage

from DraftTools import translate

def makeFinCan(name):
    '''makeFinCan(name): makes a Fin Can'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    ShapeFinCan(obj)

    # See if we have a sketch selected. If so, this is a custom fin
    for sketch in FreeCADGui.Selection.getSelection():
        if sketch.isDerivedFrom('Sketcher::SketchObject'):
            obj.FinType = FIN_TYPE_SKETCH
            obj.Profile = sketch
            sketch.Visibility = False

    if FreeCAD.GuiUp:
        ViewProviderFinCan(obj.ViewObject)
        addToStage(obj)

    return obj

class CmdFinCan:
    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction("Create fin can")
        FreeCADGui.addModule("Ui.Commands.CmdFinCan")
        FreeCADGui.doCommand("Ui.Commands.CmdFinCan.makeFinCan('FinCan')")
        FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        return False
        
    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Fin Can'),
                'ToolTip': translate("Rocket", 'Fin can design'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_FinCan.svg"}