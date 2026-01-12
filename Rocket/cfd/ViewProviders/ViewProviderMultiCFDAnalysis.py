# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

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
"""Class for drawing CFD Rockets"""

__title__ = "FreeCAD CFD Rockets View Provider"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui
from CfdOF import CfdAnalysis, CfdTools

from Rocket.cfd.Ui.TaskPanelMultiCFD import TaskPanelMultiCFD

translate = FreeCAD.Qt.translate

class ViewProviderMutliCFDAnalysis(CfdAnalysis.ViewProviderCfdAnalysis):

    def __init__(self, vobj):
        super().__init__(vobj)
        vobj.Proxy = self

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object

    # def getIcon(self):
    #     return FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_CFDRocket.svg"

    def setEdit(self, vobj, mode):
        if mode == 0:
            taskd = TaskPanelMultiCFD(self.Object, mode)
            taskd.obj = vobj.Object
            taskd.update()
            FreeCADGui.Control.showDialog(taskd)
        return True

    def unsetEdit(self, vobj, mode):
        if mode == 0:
            FreeCADGui.Control.closeDialog()
            if FreeCADGui.activeWorkbench().name() != 'RocketWorkbench':
                FreeCADGui.activateWorkbench("RocketWorkbench")
            return

    def setupContextMenu(self, viewObject, menu):
        action = menu.addAction(translate('Rocket', 'Edit %1').replace('%1', viewObject.Object.Label))
        action.triggered.connect(lambda: self.startDefaultEditMode(viewObject))
        return False

    def startDefaultEditMode(self, viewObject):
        viewObject.Document.setEdit(viewObject.Object, 0)

    def doubleClicked(self, viewObject):
        if not CfdTools.getActiveAnalysis() == self.Object:
            CfdTools.setActiveAnalysis(self.Object)
        viewObject.Document.setEdit(viewObject.Object, 0)
        return True

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None
