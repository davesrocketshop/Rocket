# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

# ***************************************************************************
# *   Copyright (c) 2024-2025 David Carter <dcarter@davidcarter.ca>         *
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
"""Class for drawing stages"""

__title__ = "FreeCAD Stages"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from typing import Any

import FreeCAD
import FreeCADGui

translate = FreeCAD.Qt.translate

from PySide import QtGui
from PySide.QtWidgets import QDialog, QVBoxLayout

from Ui.Widgets.CommentTab import CommentTab
from Ui.Widgets.ScalingTab import ScalingTabRocketStage

class _StageDialog(QDialog):

    def __init__(self, obj : Any, parent=None):
        super().__init__(parent)

        self.tabWidget = QtGui.QTabWidget()
        self.tabScaling = ScalingTabRocketStage(obj)
        self.tabComment = CommentTab()
        self.tabWidget.addTab(self.tabScaling.widget(), translate('Rocket', "Scaling"))
        self.tabWidget.addTab(self.tabComment, translate('Rocket', "Comment"))

        layout = QVBoxLayout()
        layout.addWidget(self.tabWidget)
        self.setLayout(layout)

class TaskPanelStage:

    def __init__(self,obj,mode):
        self._obj = obj

        self._stageForm = _StageDialog(obj)

        self.form = [self._stageForm]
        self._stageForm.setWindowIcon(QtGui.QIcon(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Stage.svg"))

        self._stageForm.tabScaling.scaled.connect(self.onScale)

        self.update()

        if mode == 0: # fresh created
            self._obj.Proxy.execute(self._obj)  # calculate once
            FreeCAD.Gui.SendMsgToActiveView("ViewFit")

    def transferTo(self):
        "Transfer from the dialog to the object"
        self._stageForm.tabScaling.transferTo(self._obj)
        self._stageForm.tabComment.transferTo(self._obj)

    def transferFrom(self):
        "Transfer from the object to the dialog"
        self._stageForm.tabScaling.transferFrom(self._obj)
        self._stageForm.tabComment.transferFrom(self._obj)

    def setEdited(self):
        try:
            self._obj.Proxy.setEdited()
        except ReferenceError:
            # Object may be deleted
            pass

    def onScale(self) -> None:
        # Update the scale values
        scale = self._stageForm.tabScaling.getScale()

        if scale < 1.0:
            self._stageForm.tabScaling._form.scaledLabel.setText(translate('Rocket', "Upscale"))
            self._stageForm.tabScaling._form.scaledInput.setText(f"{1.0/scale}")
        else:
            self._stageForm.tabScaling._form.scaledLabel.setText(translate('Rocket', "Scale"))
            self._stageForm.tabScaling._form.scaledInput.setText(f"{scale}")
        self.setEdited()

    def getStandardButtons(self):
        return QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Apply

    def update(self):
        'fills the widgets'
        self.transferFrom()

    def accept(self):
        self.transferTo()
        FreeCAD.ActiveDocument.commitTransaction()
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.resetEdit()
        self.setEdited()
        FreeCAD.ActiveDocument.recompute()

    def reject(self):
        FreeCAD.ActiveDocument.abortTransaction()
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.resetEdit()
        self.setEdited()
        FreeCAD.ActiveDocument.recompute()
