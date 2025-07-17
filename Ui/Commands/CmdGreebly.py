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
"""Class for drawing greeblies"""

__title__ = "FreeCAD Greeblies"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

from Rocket.FeatureGreebly import FeatureGreebly
from Ui.ViewGreebly import ViewProviderGreebly
from Ui.Commands.Command import Command

from Rocket.Constants import FEATURE_GREEBLY

from DraftTools import translate

def makeGreebly(name='Greebly'):
    '''makeGreebly(name): makes a Greebly'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureGreebly(obj)
    obj.Proxy.setDefaults()
    if FreeCAD.GuiUp:
        ViewProviderGreebly(obj.ViewObject)

    return obj.Proxy

class CmdGreebly(Command):
    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction("Create greebly")
        FreeCADGui.addModule("Ui.Commands.CmdGreebly")
        FreeCADGui.doCommand("obj=Ui.Commands.CmdGreebly.makeGreebly('Greebly')")
        FreeCADGui.doCommand("Ui.Commands.CmdStage.addToStage(obj)")
        FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return self.partEligibleFeature(FEATURE_GREEBLY)
        return False

    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Greebly'),
                'ToolTip': translate("Rocket", 'Greebly design'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Greebly.svg"}
