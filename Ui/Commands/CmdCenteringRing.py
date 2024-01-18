# ***************************************************************************
# *   Copyright (c) 2021-2024 David Carter <dcarter@davidcarter.ca>         *
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
"""Class for drawing centering rings"""

__title__ = "FreeCAD Centering Rings"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import FreeCADGui

from Rocket.FeatureCenteringRing import FeatureCenteringRing
from Ui.ViewCenteringRing import ViewProviderCenteringRing
from Ui.Commands.Command import Command

from Rocket.Constants import FEATURE_CENTERING_RING

from DraftTools import translate

def makeCenteringRing(name='CenteringRing'):
    '''makeCenteringRing(name): makes a centering ring'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureCenteringRing(obj)
    obj.Proxy.setDefaults()
    if FreeCAD.GuiUp:
        ViewProviderCenteringRing(obj.ViewObject)

    return obj.Proxy

class CmdCenteringRing(Command):
    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction("Create centering ring")
        FreeCADGui.addModule("Ui.Commands.CmdCenteringRing")
        FreeCADGui.doCommand("obj=Ui.Commands.CmdCenteringRing.makeCenteringRing('CenteringRing')")
        FreeCADGui.doCommand("Ui.Commands.CmdStage.addToStage(obj)")
        FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return self.partEligibleFeature(FEATURE_CENTERING_RING)
        return False
        
    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Centering Ring'),
                'ToolTip': translate("Rocket", 'Centering Ring design'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_CenteringRing.svg"}
