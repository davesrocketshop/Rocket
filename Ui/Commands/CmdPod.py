# ***************************************************************************
# *   Copyright (c) 2021-2023 David Carter <dcarter@davidcarter.ca>         *
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
"""Class for drawing pods"""

__title__ = "FreeCAD Pods"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import FreeCADGui

from App.FeaturePod import FeaturePod
from Ui.ViewPod import ViewProviderPod
from Ui.Commands.Command import Command

from App.Constants import FEATURE_POD

from DraftTools import translate

def makePod(name='Pod'):
    '''makePod(name): makes a Pod'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeaturePod(obj)
    if FreeCAD.GuiUp:
        ViewProviderPod(obj.ViewObject)

    return obj.Proxy

class CmdPod(Command):
    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction("Create pod")
        FreeCADGui.addModule("Ui.Commands.CmdPod")
        FreeCADGui.doCommand("obj=Ui.Commands.CmdPod.makePod('Pod')")
        FreeCADGui.doCommand("Ui.Commands.CmdStage.addToStage(obj)")
        FreeCADGui.doCommand("FreeCADGui.Selection.clearSelection()")
        FreeCADGui.doCommand("FreeCADGui.Selection.addSelection(obj._obj)")
        FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return self.part_eligible_feature(FEATURE_POD)
        return False
            
    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Pod'),
                'ToolTip': translate("Rocket", 'Pod design'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Pod.svg"}
