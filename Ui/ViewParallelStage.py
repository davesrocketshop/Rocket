# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for drawing stages"""

__title__ = "FreeCAD Parallel Stage View Provider"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

from PySide import QtCore,QtGui

translate = FreeCAD.Qt.translate

from Ui.ViewProvider import ViewProvider
from Ui.TaskPanelParallelStage import TaskPanelParallelStage

class ViewProviderParallelStage(ViewProvider):

    def __init__(self, vobj):
        super().__init__(vobj)

    def getIcon(self):
        return FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_ParallelStage.svg"

    def setupContextMenu(self, vobj, menu):
        """Add the component specific options to the context menu."""
        action1 = QtGui.QAction(translate("Rocket","Toggle active stage"),menu)
        QtCore.QObject.connect(action1,QtCore.SIGNAL("triggered()"),self.toggleParallelStage)
        menu.addAction(action1)

        action = menu.addAction(translate('Rocket', 'Edit %1').replace('%1', vobj.Object.Label))
        action.triggered.connect(lambda: self.startDefaultEditMode(vobj))
        return False

    def toggleParallelStage(self):
        FreeCADGui.runCommand("Rocket_ToggleParallelStage")

    def getDialog(self, obj, mode):
        return TaskPanelParallelStage(obj, mode)
