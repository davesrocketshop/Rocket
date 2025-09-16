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
"""Class for editing the rocket tree"""

__title__ = "FreeCAD Body Tubes"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

from Ui.Commands.Command import Command
from Ui.Widgets.WaitCursor import WaitCursor

def QT_TRANSLATE_NOOP(context, text):
    return text

def moveUp():
    for obj in FreeCADGui.Selection.getSelection():
        obj.Proxy.moveUp()

def moveDown():
    for obj in FreeCADGui.Selection.getSelection():
        obj.Proxy.moveDown()

def edit():
    for obj in FreeCADGui.Selection.getSelection():
        FreeCADGui.activeDocument().setEdit(obj.Label,0)
        return # Only process the first in the selection

def delete():
    for obj in FreeCADGui.Selection.getSelection():
        if obj.Proxy.hasParent():
            parent = obj.Proxy.getParent()
            parent.removeChild(obj)
        FreeCAD.ActiveDocument.removeObject(obj.Label)

class CmdMoveUp(Command):
    def Activated(self):
        with WaitCursor():
            FreeCAD.ActiveDocument.openTransaction("Move up")
            FreeCADGui.addModule("Ui.Commands.CmdEditTree")
            FreeCADGui.doCommand("Ui.Commands.CmdEditTree.moveUp()")
            FreeCADGui.doCommand("App.ActiveDocument.commitTransaction()")
            FreeCADGui.doCommand("App.activeDocument().recompute(None,True,True)")

    def IsActive(self):
        if self.partMoveableFeatureSelected():
            return True
        return False

    def GetResources(self):
        return {'MenuText': QT_TRANSLATE_NOOP("Rocket", 'Move Up'),
                'ToolTip': QT_TRANSLATE_NOOP("Rocket", 'Move the object up in the rocket tree'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/button_up.svg"}

class CmdMoveDown(Command):
    def Activated(self):
        with WaitCursor():
            FreeCAD.ActiveDocument.openTransaction("Move down")
            FreeCADGui.addModule("Ui.Commands.CmdEditTree")
            FreeCADGui.doCommand("Ui.Commands.CmdEditTree.moveDown()")
            FreeCADGui.doCommand("App.ActiveDocument.commitTransaction()")
            FreeCADGui.doCommand("App.activeDocument().recompute(None,True,True)")

    def IsActive(self):
        if self.partMoveableFeatureSelected():
            return True
        return False

    def GetResources(self):
        return {'MenuText': QT_TRANSLATE_NOOP("Rocket", 'Move Down'),
                'ToolTip': QT_TRANSLATE_NOOP("Rocket", 'Move the object down in the rocket tree'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/button_down.svg"}
