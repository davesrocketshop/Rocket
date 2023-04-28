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

__title__ = "FreeCAD Pod View Provider"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import FreeCADGui

from pivy import coin

from Ui.TaskPanelPod import TaskPanelPod
from Ui.ViewProvider import ViewProvider

class ViewProviderPod(ViewProvider):

    def __init__(self, vobj):
        super().__init__(vobj)

    def getIcon(self):
        return FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Pod.svg"

    def attach(self, vobj):
        super().attach(vobj)

        self.sep = coin.SoSeparator()
        vobj.addDisplayMode(self.sep, "Default")

    def getDisplayModes(self,vobj):
        return ["Default"]

    def getDefaultDisplayMode(self):
        return "Default"

    def setDisplayMode(self,mode):
        return mode

    def setEdit(self, vobj, mode):
        if mode == 0:
            taskd = TaskPanelPod(self.Object, mode)
            taskd.obj = vobj.Object
            taskd.update()
            FreeCADGui.Control.showDialog(taskd)
            return True

    def unsetEdit(self, vobj, mode):
        if mode == 0:
            FreeCADGui.Control.closeDialog()
            return
