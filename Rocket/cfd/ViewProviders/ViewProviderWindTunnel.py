# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for drawing body tubes"""

__title__ = "FreeCAD Body Tube View Provider"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

from Rocket.cfd.Ui.TaskPanelWindTunnel import TaskPanelWindTunnel

translate = FreeCAD.Qt.translate

class ViewProviderWindTunnel:

    def __init__(self, vobj):
        # super().__init__(vobj)
        vobj.Proxy = self

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object

    def getIcon(self):
        return FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_WindTunnel.svg"

    def setEdit(self, vobj, mode):
        if mode == 0:
            taskd = TaskPanelWindTunnel(self.Object, mode)
            taskd.obj = vobj.Object
            taskd.update()
            FreeCADGui.Control.showDialog(taskd)
            return True

    def unsetEdit(self, vobj, mode):
        if mode == 0:
            FreeCADGui.Control.closeDialog()
            return

    def setupContextMenu(self, viewObject, menu):
        action = menu.addAction(translate('Rocket', 'Edit %1').replace('%1', viewObject.Object.Label))
        action.triggered.connect(lambda: self.startDefaultEditMode(viewObject))
        return False

    def startDefaultEditMode(self, viewObject):
        document = viewObject.Document.Document
        if not document.HasPendingTransaction:
            text = translate('Rocket', 'Edit %1').replace('%1', viewObject.Object.Label)
            document.openTransaction(text)
        viewObject.Document.setEdit(viewObject.Object, 0)

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None
