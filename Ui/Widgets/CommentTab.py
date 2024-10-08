# ***************************************************************************
# *   Copyright (c) 2023-2024 David Carter <dcarter@davidcarter.ca>         *
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
"""Class for drawing comment tab"""

__title__ = "FreeCAD Comment Tab"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"


from DraftTools import translate

from PySide import QtGui
from PySide6.QtWidgets import QVBoxLayout, QTextEdit

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
