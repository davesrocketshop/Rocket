# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for drawing rockets"""

__title__ = "FreeCAD Rocket View Provider"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

from PySide import QtCore,QtGui
from pivy import coin

from Ui.ViewProvider import ViewProvider
from Ui.TaskPanelRocket import TaskPanelRocket
from Ui.Widgets.WaitCursor import WaitCursor

translate = FreeCAD.Qt.translate

class ViewProviderRocket(ViewProvider):

    def __init__(self, vobj):
        super().__init__(vobj)

    def getIcon(self):
        return FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Rocket.svg"

    def attach(self, vobj):
        super().attach(vobj)

        self.sep = coin.SoSeparator()
        # self.sep.addChild(coin.SoSphere()) # Show a sphere at the Placement.
        vobj.addDisplayMode(self.sep, "Default")

    def getDisplayModes(self,vobj):
        return ["Default"]

    def getDefaultDisplayMode(self):
        return "Default"

    def setDisplayMode(self,mode):
        return mode

    def setupContextMenu(self, vobj, menu):
        """Add the component specific options to the context menu."""
        action1 = QtGui.QAction(translate("Rocket","Toggle active rocket"),menu)
        QtCore.QObject.connect(action1,QtCore.SIGNAL("triggered()"),self.toggleRocket)
        menu.addAction(action1)

    def toggleRocket(self):
        with WaitCursor():
            FreeCADGui.runCommand("Rocket_ToggleRocket")
            FreeCADGui.runCommand("Rocket_ToggleStage")

    def getDialog(self, obj, mode):
        return TaskPanelRocket(obj, mode)
