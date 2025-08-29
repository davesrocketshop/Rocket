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
"""Class for drawing CFD Rockets"""

__title__ = "FreeCAD CFD Rockets"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"


import FreeCAD
import FreeCADGui

from Rocket.Utilities import translate

from PySide import QtGui
from PySide.QtWidgets import QDialog, QGridLayout, QVBoxLayout, QSizePolicy

class _CFDRocketDialog(QDialog):

    def __init__(self, parent=None):
        super(_CFDRocketDialog, self).__init__(parent)

        ui = FreeCADGui.UiLoader()

        # define our window
        self.setGeometry(250, 250, 400, 350)
        self.setWindowTitle(translate('Rocket', "CFD Rocket Parameter"))

        # Get the rocket parameters
        self.aoaLabel = QtGui.QLabel(translate('Rocket', "Angle of Attack"), self)

        self.aoaInput = ui.createWidget("Gui::InputField")
        self.aoaInput.unit = 'deg'
        self.aoaInput.setMinimumWidth(100)

        self.rotationLabel = QtGui.QLabel(translate('Rocket', "Rotation"), self)

        self.rotationInput = ui.createWidget("Gui::InputField")
        self.rotationInput.unit = 'deg'
        self.rotationInput.setMinimumWidth(100)

        # General parameters
        row = 0
        grid = QGridLayout()

        grid.addWidget(self.aoaLabel, row, 0)
        grid.addWidget(self.aoaInput, row, 1)
        row += 1

        grid.addWidget(self.rotationLabel, row, 0)
        grid.addWidget(self.rotationInput, row, 1)

        layout = QVBoxLayout()
        layout.addItem(grid)
        layout.addItem(QtGui.QSpacerItem(0,0, QSizePolicy.Expanding, QSizePolicy.Expanding))

        self.setLayout(layout)

class TaskPanelCFDRocket:

    def __init__(self,obj,mode):
        self._obj = obj

        self.form = _CFDRocketDialog()
        self.form.setWindowIcon(QtGui.QIcon(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_CFDRocket.svg"))

        self.form.aoaInput.textEdited.connect(self.onAOA)
        self.form.rotationInput.textEdited.connect(self.onRotation)

        self.update()

    def transferTo(self):
        "Transfer from the dialog to the object"
        self._obj.AngleOfAttack = FreeCAD.Units.Quantity(self.form.aoaInput.text()).Value
        self._obj.AngleOfRotation = FreeCAD.Units.Quantity(self.form.rotationInput.text()).Value

    def transferFrom(self):
        "Transfer from the object to the dialog"
        self.form.aoaInput.setText(self._obj.AngleOfAttack.UserString)
        self.form.rotationInput.setText(self._obj.AngleOfRotation.UserString)

    def setEdited(self):
        # try:
        #     self._obj.Proxy.setEdited()
        # except ReferenceError:
        #     # Object may be deleted
        #     pass
        pass

    def onAOA(self, value):
        try:
            self._obj.AngleOfAttack = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()
        FreeCAD.ActiveDocument.recompute()

    def onRotation(self, value):
        try:
            self._obj.AngleOfRotation = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()
        FreeCAD.ActiveDocument.recompute()

    def getStandardButtons(self):
        return QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Apply

    def clicked(self,button):
        if button == QtGui.QDialogButtonBox.Apply:
            self.transferTo()
            self._obj.Proxy.execute(self._obj)

    def update(self):
        'fills the widgets'
        self.transferFrom()

    def accept(self):
        self.transferTo()
        FreeCAD.ActiveDocument.commitTransaction()
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.resetEdit()


    def reject(self):
        FreeCAD.ActiveDocument.abortTransaction()
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.resetEdit()
        self.setEdited()
