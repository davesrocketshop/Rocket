# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2025 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


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
