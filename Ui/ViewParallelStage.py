# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

################################################################################
#                                                                              #
#   © 2021 David Carter <dcarter@davidcarter.ca>                               #
#                                                                              #
#   This addon is free software: you can redistribute it and/or modify         #
#   it under the terms of the GNU Lesser General Public License as             #
#   published by the Free Software Foundation, either version 2.1              #
#   of the License, or (at your option) any later version.                     #
#                                                                              #
#   This addon is distributed in the hope that it will be useful,              #
#   but WITHOUT ANY WARRANTY; without even the implied warranty                #
#   of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                    #
#   See the GNU Lesser General Public License for more details.                #
#                                                                              #
#   You should have received a copy of the GNU Lesser General Public           #
#   License along with this addon. If not, see https://www.gnu.org/licenses    #
#                                                                              #
################################################################################


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
