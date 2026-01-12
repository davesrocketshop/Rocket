# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

################################################################################
#                                                                              #
#   © 2023 David Carter <dcarter@davidcarter.ca>                               #
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


"""Class for drawing comment tab"""

__title__ = "FreeCAD Comment Tab"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"


import FreeCAD
translate = FreeCAD.Qt.translate

from PySide import QtGui
from PySide.QtWidgets import QVBoxLayout, QTextEdit

class CommentTab(QtGui.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTabComment()

    def setTabComment(self):

        self.commentLabel = QtGui.QLabel(translate('Rocket', "Comment"), self)

        self.commentInput = QTextEdit()

        layout = QVBoxLayout()
        layout.addWidget(self.commentLabel)
        layout.addWidget(self.commentInput)

        self.setLayout(layout)

    def transferTo(self, obj):
        "Transfer from the dialog to the object"
        obj.Comment = self.commentInput.toPlainText()

    def transferFrom(self, obj):
        "Transfer from the object to the dialog"
        self.commentInput.setPlainText(obj.Comment)
