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
"""Class for drawing transitions"""

__title__ = "FreeCAD Transitions"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"


import FreeCAD
import FreeCADGui

from Rocket.FeatureTransition import FeatureTransition
if FreeCAD.GuiUp:
    from Ui.ViewTransition import ViewProviderTransition
    from Ui.Widgets.WaitCursor import WaitCursor
from Ui.Commands.Command import Command

from Rocket.Constants import FEATURE_TRANSITION

def QT_TRANSLATE_NOOP(context, text):
    return text

def makeTransition(name='Transition'):
    '''makeTransition(name): makes a Transition'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureTransition(obj)
    obj.Proxy.setDefaults()
    if FreeCAD.GuiUp:
        ViewProviderTransition(obj.ViewObject)

    return obj.Proxy

class CmdTransition(Command):
    def Activated(self):
        with WaitCursor():
            FreeCAD.ActiveDocument.openTransaction("Create transition")
            FreeCADGui.addModule("Ui.Commands.CmdTransition")
            FreeCADGui.doCommand("obj=Ui.Commands.CmdTransition.makeTransition('Transition')")
            FreeCADGui.doCommand("Ui.Commands.CmdStage.addToStage(obj)")
            FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return self.partEligibleFeature(FEATURE_TRANSITION)
        return False

    def GetResources(self):
        return {'MenuText': QT_TRANSLATE_NOOP("Rocket", 'Transition'),
                'ToolTip': QT_TRANSLATE_NOOP("Rocket", 'Transition design'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Transition.svg"}
