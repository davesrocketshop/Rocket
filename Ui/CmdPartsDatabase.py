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
"""Class for recreating the parts database"""

__title__ = "FreeCAD Parts Database Generation"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import FreeCADGui

from App.Parts.PartDatabase import PartDatabase

def QT_TRANSLATE_NOOP(scope, text):
    return text

def makePartsDatabase():
    '''makePartsDatabase(): makes a Body Tube'''
    db = PartDatabase()
    db.updateDatabase()

class CmdPartsDatabase:
    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction("Create body tube")
        FreeCADGui.addModule("Ui.CmdPartsDatabase")
        FreeCADGui.doCommand("Ui.CmdPartsDatabase.makePartsDatabase()")
        # FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        return False
            
    def GetResources(self):
        return {'MenuText': QT_TRANSLATE_NOOP("Rocket_PartsDatabase", 'Create Parts Database...'),
                'ToolTip': QT_TRANSLATE_NOOP("Rocket_PartsDatabase", 'Create Parts Database'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_PartsDatabase.svg"}
