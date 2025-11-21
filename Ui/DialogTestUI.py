# ***************************************************************************
# *   Copyright (c) 2021-2025 David Carter <dcarter@davidcarter.ca>         *
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
"""Class for Thrust To Weight calculator"""

__title__ = "FreeCAD Thrust To Weight Calculator"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCADGui
import os

from PySide.QtWidgets import QDialog

from Ui.UIPaths import getUIPath

class UiDialog(QDialog):
    def __init__(self, file : str) -> None:
        super().__init__()

        self.initUI(file)

    def initUI(self, file : str) -> None:
        self.ui = FreeCADGui.PySideUic.loadUi(os.path.join(getUIPath(), 'Ui', file), self)

        self.ui.accepted.connect(self.onAccepted)
        self.ui.finished.connect(self.onFinished)
        self.ui.rejected.connect(self.onRejected)

    def exec(self) -> int:
        return self.ui.exec()

    def open(self) -> None:
        self.ui.open()

    def onAccepted(self) -> None:
        self.accept()

    def onFinished(self, result) -> None:
        self.done(result)

    def onRejected(self) -> None:
        self.reject()

    def result(self) -> int:
        return self.ui.result()

class DialogTestUI(UiDialog):
    def __init__(self):
        super().__init__("DialogTestUI.ui")

    def initUI(self, file):
        super().initUI(file)

    def accept(self):
        print("accept")
        super().accept()

    def reject(self):
        print("reject")
        super().reject()

    def done(self, result):
        print("done")
        super().done(result)
