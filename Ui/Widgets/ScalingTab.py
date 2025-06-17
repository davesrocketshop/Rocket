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
"""Class for drawing scaling tab"""

__title__ = "FreeCAD Scaling Tab"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"


import FreeCAD
import FreeCADGui

from DraftTools import translate

from PySide import QtGui, QtCore
from PySide.QtWidgets import QGridLayout, QVBoxLayout, QSizePolicy

class ScalingTab(QtGui.QWidget):

    def __init__(self, obj, parent=None) -> None:
        super().__init__(parent)
        self._obj = obj

        self.setTabScaling()
        self._setConnections()
        self._setScaleState()

    def setTabScaling(self) -> None:
        ui = FreeCADGui.UiLoader()

        # Scaling
        self.scalingGroup = QtGui.QGroupBox(translate('Rocket', "Scaling"), self)
        self.scalingGroup.setCheckable(True)
        self.scalingGroup.setChecked(False)

        self.scaleRadio = QtGui.QRadioButton (translate('Rocket', "By value"), self.scalingGroup)
        self.scaleRadio.setChecked(True)

        self.scaleInput = ui.createWidget("Gui::InputField")
        self.scaleInput.setMinimumWidth(20)

        self.scaleDiameterRadio = QtGui.QRadioButton (translate('Rocket', "By body diameter"), self.scalingGroup)
        self.scaleDiameterRadio.setChecked(False)

        self.scaleDiameterInput = ui.createWidget("Gui::InputField")
        self.scaleDiameterInput.unit = FreeCAD.Units.Length
        self.scaleDiameterInput.setMinimumWidth(20)

        self.autoScaleDiameterCheckbox = QtGui.QCheckBox(translate('Rocket', "auto"), self)
        self.autoScaleDiameterCheckbox.setCheckState(QtCore.Qt.Unchecked)

        grid = QGridLayout()
        row = 0

        grid.addWidget(self.scaleRadio, row, 0)
        grid.addWidget(self.scaleInput, row, 1)
        row += 1

        grid.addWidget(self.scaleDiameterRadio, row, 0)
        grid.addWidget(self.scaleDiameterInput, row, 1)
        grid.addWidget(self.autoScaleDiameterCheckbox, row, 2)
        row += 1

        self.scalingGroup.setLayout(grid)

        layout = QVBoxLayout()
        layout.addWidget(self.scalingGroup)
        layout.addItem(QtGui.QSpacerItem(0,0, QSizePolicy.Expanding, QSizePolicy.Expanding))

        self.setLayout(layout)

    def _setConnections(self) -> None:
        self.scalingGroup.toggled.connect(self.onScalingGroup)
        self.scaleRadio.toggled.connect(self.onScale)
        self.scaleDiameterRadio.toggled.connect(self.onScaleDiameter)
        self.autoScaleDiameterCheckbox.stateChanged.connect(self.onScaleAutoDiameter)
        self.scaleInput.textEdited.connect(self.onScaleValue)
        self.scaleDiameterInput.textEdited.connect(self.onScaleDiameterValue)

    def _setScaleState(self) -> None:
        if self.scalingGroup.isChecked():
            self.scaleInput.setEnabled(self.scaleRadio.isChecked())
            self.scaleDiameterInput.setEnabled(self.scaleDiameterRadio.isChecked())
            self.autoScaleDiameterCheckbox.setEnabled(self.scaleDiameterRadio.isChecked())

    def transferTo(self, obj) -> None:
        "Transfer from the dialog to the object"
        obj.Scale = self.scalingGroup.isChecked()
        obj.ScaleByValue = self.scaleRadio.isChecked()
        obj.ScaleByDiameter = self.scaleDiameterRadio.isChecked()
        obj.AutoScaleDiameter = self.autoScaleDiameterCheckbox.isChecked()
        if obj.ScaleByValue:
            obj.ScaleValue = FreeCAD.Units.Quantity(self.scaleInput.text()).Value
        else:
            obj.ScaleValue = FreeCAD.Units.Quantity(self.scaleDiameterInput.text())

    def transferFrom(self, obj) -> None:
        "Transfer from the object to the dialog"
        self.scalingGroup.setChecked(obj.Scale)
        self.scaleRadio.setChecked(obj.ScaleByValue)
        self.scaleDiameterRadio.setChecked(obj.ScaleByDiameter)
        self.autoScaleDiameterCheckbox.setChecked(obj.AutoScaleDiameter)
        if obj.ScaleByValue:
            self.scaleInput.setText(f"{obj.ScaleValue.Value}")
        else:
            self.scaleInput.setText("0")
        if obj.ScaleByDiameter:
            self.scaleDiameterInput.setText(obj.ScaleValue.UserString)
        else:
            self.scaleDiameterInput.setText(FreeCAD.Units.Quantity(0, FreeCAD.Units.Length).UserString)

        self._setScaleState()

    def setEdited(self):
        try:
            self._obj.Proxy.setEdited()
        except ReferenceError:
            # Object may be deleted
            pass

    def onScalingGroup(self, on : bool) -> None:
        try:
            self._obj.Scale = on
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self._setScaleState()
        self.setEdited()

    def onScale(self, checked : bool) -> None:
        try:
            self._obj.ScaleByValue = checked
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self._setScaleState()
        self.setEdited()

    def onScaleDiameter(self, checked: bool) -> None:
        try:
            self._obj.ScaleByDiameter = checked
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self._setScaleState()
        self.setEdited()

    def onScaleAutoDiameter(self, checked : bool) -> None:
        try:
            self._obj.AutoScaleDiameter = checked
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self._setScaleState()
        self.setEdited()

    def onScaleValue(self, value):
        try:
            self._obj.ScaleValue = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def onScaleDiameterValue(self, value):
        try:
            self._obj.ScaleValue = FreeCAD.Units.Quantity(value)
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()
