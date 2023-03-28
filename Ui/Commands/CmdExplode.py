# ***************************************************************************
# *   Copyright (c) 2023 David Carter <dcarter@davidcarter.ca>              *
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
"""Class for displaying exploded assembly diagram"""

__title__ = "FreeCAD Exploded Assembly"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import FreeCADGui

from DraftTools import translate

from PySide import QtGui

from Ui.DialogFinFlutter import DialogFinFlutter
from Ui.Commands.Command import Command, getRocket

import FemGui
import ObjectsFem
from Rocket.fem.Gmsh import RocketGmsh

def createAnalysis():
    doc = FreeCAD.ActiveDocument

    analyzer = ObjectsFem.makeAnalysis(doc, 'Analysis')
    FemGui.setActiveAnalysis(analyzer)

    # create a CalculiX ccx tools solver for any new analysis
    ObjectsFem.makeSolverCalculixCcxTools(doc)
    analyzer.addObject(doc.ActiveObject)

def doExplode():
    doc = FreeCAD.ActiveDocument
    if doc is None:
        return

    rocket = getRocket()
    if rocket is None:
        return
    
    # First, debug the sizes
    rocket.explode()

class CmdExplode(Command):
    def Activated(self):
        FreeCADGui.addModule("Ui.Commands.CmdExplode")
        FreeCADGui.doCommand("Ui.Commands.CmdExplode.doExplode()")

    def IsActive(self):
        return self.isRocketBuilder()
        
    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Show Exploded Assembly'),
                'ToolTip': translate("Rocket", 'Show Exploded Assembly'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_FinFem.svg"}
