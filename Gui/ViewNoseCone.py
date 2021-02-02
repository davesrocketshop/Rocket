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
"""Class for drawing nose cones"""

__title__ = "FreeCAD Nose Cones View Provider"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
from PySide import QtGui, QtCore
import FreeCAD
import FreeCADGui
import Part

from Gui.TaskPanelNoseCone import TaskPanelNoseCone
from App.Utilities import _trace

class ViewProviderNoseCone:

    def __init__(self, vobj):
        _trace(self.__class__.__name__, "__init__")
        vobj.Proxy = self
        
    def getIcon(self):
        _trace(self.__class__.__name__, "getIcon")
        return FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_NoseCone.svg"

    def attach(self, vobj):
        _trace(self.__class__.__name__, "attach")
        self.ViewObject = vobj
        self.Object = vobj.Object
  
    def setEdit(self,vobj,mode):
        _trace(self.__class__.__name__, "setEdit")
        taskd = TaskPanelNoseCone(self.Object,mode)
        taskd.obj = vobj.Object
        taskd.update()
        FreeCADGui.Control.showDialog(taskd)
        return True
    
    def unsetEdit(self,vobj,mode):
        _trace(self.__class__.__name__, "unsetEdit")
        FreeCADGui.Control.closeDialog()
        return

    def __getstate__(self):
        return None

    def __setstate__(self,state):
        return None
