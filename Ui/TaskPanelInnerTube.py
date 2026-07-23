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


"""Class for drawing body tubes"""

__title__ = "FreeCAD Body Tubes"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from typing import Any

import FreeCAD
from Ui.TaskPanelBodyTube import TaskPanelBodyTube, BodyTubeDialog

translate = FreeCAD.Qt.translate

from Ui.Widgets.ClusterTab import ClusterTab

from Rocket.Utilities import _valueOnly, _err

class InnerTubeDialog(BodyTubeDialog):

    def __init__(self, obj: Any, parent : Any = None) -> None:
        super().__init__(obj, parent)

        self.tabCluster = ClusterTab(obj, parent=self)
        self.tabWidget.insertTab(1, self.tabCluster.widget(), translate('Rocket', "Cluster"))

class TaskPanelInnerTube(TaskPanelBodyTube):

    def __init__(self, obj : Any, mode : int) -> None:
        super().__init__(obj, mode, form=InnerTubeDialog(obj))

        if self._btForm.tabCluster:
            self._btForm.tabCluster.cluster.connect(self.onClusterChanged)

    def onClusterChanged(self) -> None:
        ...

    def transferTo(self):
        "Transfer from the dialog to the object"
        super().transferTo()

        if self._btForm.tabCluster:
            self._btForm.tabCluster.transferTo(self._obj)

    def transferFrom(self):
        "Transfer from the object to the dialog"
        super().transferFrom()

        try:
            if self._btForm.tabCluster:
                self._btForm.tabCluster.transferFrom(self._obj)
        except Exception as e:
            FreeCAD.Console.PrintError("Error occurred while transferring from object: {}".format(e))
