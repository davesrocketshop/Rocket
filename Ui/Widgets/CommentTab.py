# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2023 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


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
