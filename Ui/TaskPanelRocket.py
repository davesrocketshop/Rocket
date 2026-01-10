# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2024 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for drawing rockets"""

__title__ = "FreeCAD Rocket"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"


import FreeCAD

from PySide import QtGui

from Ui.TaskPanelStage import TaskPanelStage

class TaskPanelRocket(TaskPanelStage):

    def __init__(self,obj,mode):
        super().__init__(obj, mode)

        self._stageForm.setWindowIcon(QtGui.QIcon(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Rocket.svg"))

        self.update()
