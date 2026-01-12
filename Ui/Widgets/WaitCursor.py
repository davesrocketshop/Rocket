# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

# ***************************************************************************
# *   Copyright (c) 2025 David Carter <dcarter@davidcarter.ca>              *
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
