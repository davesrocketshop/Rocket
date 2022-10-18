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
"""Class for drawing centering rings"""

__title__ = "FreeCAD Centering Rings"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import FreeCADGui

from App.ShapeCenteringRing import ShapeCenteringRing
from Ui.ViewCenteringRing import ViewProviderCenteringRing
from Ui.Commands.CmdStage import addToStage

from DraftTools import translate

def makeCenteringRing(name='CenteringRing'):
    '''makeCenteringRing(name): makes a centering ring'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    ShapeCenteringRing(obj)
    if FreeCAD.GuiUp:
        ViewProviderCenteringRing(obj.ViewObject)

        addToStage(obj)
    return obj

class CmdCenteringRing:
    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction("Create centering ring")
        FreeCADGui.addModule("Ui.Commands.CmdCenteringRing")
        FreeCADGui.doCommand("Ui.Commands.CmdCenteringRing.makeCenteringRing('CenteringRing')")
        FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        return False
        
    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Centering Ring'),
                'ToolTip': translate("Rocket", 'Centering Ring design'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_CenteringRing.svg"}