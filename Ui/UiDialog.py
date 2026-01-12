# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

################################################################################
#                                                                              #
#   © 2025 David Carter <dcarter@davidcarter.ca>                               #
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


"""Class for UI Based Dialogs"""

__title__ = "FreeCAD UI Dialog base class"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCADGui
import os

from PySide.QtWidgets import QDialog

from Ui.DialogUtilities import saveDialog, restoreDialog, getParams
from Ui.UIPaths import getUIPath

class UiDialog(QDialog):
    def __init__(self, dialogName : str, filePath : str) -> None:
        super().__init__()

        self._dialogName = dialogName
        self._filePath = filePath

        # self.initUI()

    def initUI(self) -> None:
        self._ui = FreeCADGui.PySideUic.loadUi(os.path.join(getUIPath(), 'Ui', self._filePath), self)

        self._param = getParams(self._dialogName)

        # create our window
        restoreDialog(self._ui, self._dialogName, 640, 480)

        self._ui.accepted.connect(self.onAccepted)
        self._ui.finished.connect(self.onFinished)
        self._ui.rejected.connect(self.onRejected)

    def exec(self) -> int:
        return self._ui.exec()

    def open(self) -> None:
        self._ui.open()

    def onAccepted(self) -> None:
        self.accept()

    def onFinished(self, result) -> None:
        saveDialog(self._ui, self._dialogName)
        self.done(result)

    def onRejected(self) -> None:
        self.reject()

    def result(self) -> int:
        return self._ui.result()
