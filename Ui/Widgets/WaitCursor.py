# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2025 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for a wait cursor"""

__title__ = "FreeCAD Wait Cursor"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from PySide.QtWidgets import QApplication
from PySide import QtGui, QtCore
from PySide.QtCore import QObject
from PySide.QtGui import QCursor


from Ui.UIPaths import getUIPath

class WaitCursor(QObject):
    def __init__(self) -> None:
        super().__init__()

    def __enter__(self) -> None:
        QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        QApplication.restoreOverrideCursor()
        return True

    def setWait(self) -> None:
        QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))

    def resetWait(self) -> None:
        QApplication.restoreOverrideCursor()
