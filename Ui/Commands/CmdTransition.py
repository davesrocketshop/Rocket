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
"""Class for drawing transitions"""

__title__ = "FreeCAD Transitions"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    

import FreeCAD
import FreeCADGui

from App.ShapeTransition import ShapeTransition
from Ui.ViewTransition import ViewProviderTransition
from Ui.Commands.Command import Command
from Ui.Commands.CmdStage import addToStage

from App.Constants import FEATURE_TRANSITION

from DraftTools import translate

def makeTransition(name):
    '''makeTransition(name): makes a Transition'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    ShapeTransition(obj)
    if FreeCAD.GuiUp:
        ViewProviderTransition(obj.ViewObject)

        addToStage(obj)
    return obj

class CmdTransition(Command):
    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction("Create transition")
        FreeCADGui.addModule("Ui.Commands.CmdTransition")
        FreeCADGui.doCommand("Ui.Commands.CmdTransition.makeTransition('Transition')")
        FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return self.part_eligible_feature(FEATURE_TRANSITION)
        return False
        
    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Transition'),
                'ToolTip': translate("Rocket", 'Transition design'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Transition.svg"}
