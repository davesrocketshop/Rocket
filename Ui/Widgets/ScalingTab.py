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
from PySide.QtCore import QObject, Signal
from PySide.QtWidgets import QGridLayout, QVBoxLayout, QSizePolicy

class ScalingTab(QtGui.QWidget):
    scaled = Signal()   # emitted when scale parameters have changed

    def __init__(self, obj, parent=None) -> None:
        super().__init__(parent)
        self._obj = obj
        self._loading = False # Prevent updates when loading

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

        self.upscaleCheckbox = QtGui.QCheckBox(translate('Rocket', "Upscale"), self)
        self.upscaleCheckbox.setCheckState(QtCore.Qt.Unchecked)

        self.scaleDiameterRadio = QtGui.QRadioButton(translate('Rocket', "By body diameter"), self.scalingGroup)
        self.scaleDiameterRadio.setChecked(False)

        self.scaleDiameterInput = ui.createWidget("Gui::InputField")
        self.scaleDiameterInput.unit = FreeCAD.Units.Length
        self.scaleDiameterInput.setMinimumWidth(20)

        self.autoScaleDiameterCheckbox = QtGui.QCheckBox(translate('Rocket', "auto"), self)
        self.autoScaleDiameterCheckbox.setCheckState(QtCore.Qt.Unchecked)

        self.foreAftGroup = QtGui.QButtonGroup()
        self.scaleForeRadio = QtGui.QRadioButton(translate('Rocket', "Fore"))
        self.foreAftGroup.addButton(self.scaleForeRadio)
        self.scaleForeRadio.setChecked(False)

        self.scaleAftRadio = QtGui.QRadioButton(translate('Rocket', "Aft"))
        self.foreAftGroup.addButton(self.scaleAftRadio)
        self.scaleAftRadio.setChecked(True)

        # Show the results
        self.scaledGroup = QtGui.QGroupBox(translate('Rocket', "Scaled Values"), self)

        self.scaledLabel = QtGui.QLabel(translate('Rocket', "Scale"), self)

        self.scaledInput = ui.createWidget("Gui::InputField")
        self.scaledInput.setMinimumWidth(20)
        self.scaledInput.setEnabled(False)

        self.scaledLengthLabel = QtGui.QLabel(translate('Rocket', "Length"), self)

        self.scaledLengthInput = ui.createWidget("Gui::InputField")
        self.scaledLengthInput.unit = FreeCAD.Units.Length
        self.scaledLengthInput.setMinimumWidth(20)
        self.scaledLengthInput.setEnabled(False)

        self.scaledDiameterLabel = QtGui.QLabel(translate('Rocket', "Diameter"), self)

        self.scaledDiameterInput = ui.createWidget("Gui::InputField")
        self.scaledDiameterInput.unit = FreeCAD.Units.Length
        self.scaledDiameterInput.setMinimumWidth(20)
        self.scaledDiameterInput.setEnabled(False)

        self.scaledAftDiameterLabel = QtGui.QLabel(translate('Rocket', "Aft Diameter"), self)

        self.scaledAftDiameterInput = ui.createWidget("Gui::InputField")
        self.scaledAftDiameterInput.unit = FreeCAD.Units.Length
        self.scaledAftDiameterInput.setMinimumWidth(20)
        self.scaledAftDiameterInput.setEnabled(False)

        self.scaledOgiveDiameterLabel = QtGui.QLabel(translate('Rocket', "Ogive Diameter"), self)

        self.scaledOgiveDiameterInput = ui.createWidget("Gui::InputField")
        self.scaledOgiveDiameterInput.unit = FreeCAD.Units.Length
        self.scaledOgiveDiameterInput.setMinimumWidth(20)
        self.scaledOgiveDiameterInput.setEnabled(False)

        self.scaledBluntedDiameterLabel = QtGui.QLabel(translate('Rocket', "Blunted Diameter"), self)

        self.scaledBluntedDiameterInput = ui.createWidget("Gui::InputField")
        self.scaledBluntedDiameterInput.unit = FreeCAD.Units.Length
        self.scaledBluntedDiameterInput.setMinimumWidth(20)
        self.scaledBluntedDiameterInput.setEnabled(False)

        self.scaledSetValuesButton = QtGui.QPushButton(translate('Rocket', 'Set as values'), self)
        self.scaledSetValuesButton.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)

        grid = QGridLayout()
        row = 0

        grid.addWidget(self.scaledLabel, row, 0)
        grid.addWidget(self.scaledInput, row, 1, 1, 2)
        row += 1

        grid.addWidget(self.scaledLengthLabel, row, 0)
        grid.addWidget(self.scaledLengthInput, row, 1, 1, 2)
        row += 1

        grid.addWidget(self.scaledDiameterLabel, row, 0)
        grid.addWidget(self.scaledDiameterInput, row, 1, 1, 2)
        row += 1

        grid.addWidget(self.scaledAftDiameterLabel, row, 0)
        grid.addWidget(self.scaledAftDiameterInput, row, 1, 1, 2)
        row += 1

        grid.addWidget(self.scaledOgiveDiameterLabel, row, 0)
        grid.addWidget(self.scaledOgiveDiameterInput, row, 1, 1, 2)
        row += 1

        grid.addWidget(self.scaledBluntedDiameterLabel, row, 0)
        grid.addWidget(self.scaledBluntedDiameterInput, row, 1, 1, 2)
        row += 1

        grid.addWidget(self.scaledSetValuesButton, row, 2)
        row += 1

        self.scaledGroup.setLayout(grid)

        grid = QGridLayout()
        row = 0

        grid.addWidget(self.scaleRadio, row, 0)
        grid.addWidget(self.scaleInput, row, 1, 1, 2)
        grid.addWidget(self.upscaleCheckbox, row, 3)
        row += 1

        grid.addWidget(self.scaleDiameterRadio, row, 0)
        grid.addWidget(self.scaleDiameterInput, row, 1, 1, 2)
        grid.addWidget(self.autoScaleDiameterCheckbox, row, 3)
        row += 1

        grid.addWidget(self.scaleForeRadio, row, 1)
        grid.addWidget(self.scaleAftRadio, row, 2)
        row += 1

        self.scalingGroup.setLayout(grid)

        layout = QVBoxLayout()
        layout.addWidget(self.scalingGroup)
        layout.addWidget(self.scaledGroup)
        layout.addItem(QtGui.QSpacerItem(0,0, QSizePolicy.Expanding, QSizePolicy.Expanding))

        self.setLayout(layout)

    def _setConnections(self) -> None:
        self.scalingGroup.toggled.connect(self.onScalingGroup)
        self.scaleRadio.toggled.connect(self.onScale)
        self.scaleDiameterRadio.toggled.connect(self.onScaleDiameter)
        self.autoScaleDiameterCheckbox.stateChanged.connect(self.onScaleAutoDiameter)
        self.upscaleCheckbox.stateChanged.connect(self.onUpscale)
        self.scaleInput.textEdited.connect(self.onScaleValue)
        self.scaleDiameterInput.textEdited.connect(self.onScaleDiameterValue)

    def _setScaleState(self) -> None:
        if self.scalingGroup.isChecked():
            self.scaleInput.setEnabled(self.scaleRadio.isChecked())
            self.upscaleCheckbox.setEnabled(self.scaleRadio.isChecked())
            self.scaleDiameterInput.setEnabled(self.scaleDiameterRadio.isChecked())
            self.autoScaleDiameterCheckbox.setEnabled(self.scaleDiameterRadio.isChecked())

    def transferTo(self, obj) -> None:
        "Transfer from the dialog to the object"
        obj.Scale = self.scalingGroup.isChecked()
        obj.ScaleByValue = self.scaleRadio.isChecked()
        obj.ScaleByDiameter = self.scaleDiameterRadio.isChecked()
        obj.AutoScaleDiameter = self.autoScaleDiameterCheckbox.isChecked()
        obj.ScaleForeDiameter = self.scaleForeRadio.isChecked()
        if obj.ScaleByValue:
            value = FreeCAD.Units.Quantity(self.scaleInput.text()).Value
            if self.upscaleCheckbox.isChecked():
                if value > 0:
                    obj.ScaleValue = 1.0 / value
                else:
                    obj.ScaleValue = 1.0
            else:
                obj.ScaleValue = value
        else:
            obj.ScaleValue = FreeCAD.Units.Quantity(self.scaleDiameterInput.text())

    def transferFrom(self, obj) -> None:
        "Transfer from the object to the dialog"
        self._loading = True

        self.scalingGroup.setChecked(obj.Scale)
        self.scaleRadio.setChecked(obj.ScaleByValue)
        self.scaleDiameterRadio.setChecked(obj.ScaleByDiameter)
        self.autoScaleDiameterCheckbox.setChecked(obj.AutoScaleDiameter)
        if obj.ScaleByValue:
            if obj.ScaleValue.Value > 0.0 and obj.ScaleValue.Value < 1.0:
                self.scaleInput.setText(f"{1.0 / obj.ScaleValue.Value}")
                self.upscaleCheckbox.setChecked(True)
            else:
                self.scaleInput.setText(f"{obj.ScaleValue.Value}")
                self.upscaleCheckbox.setChecked(False)
        else:
            self.scaleInput.setText("0")
        if obj.ScaleByDiameter:
            self.scaleDiameterInput.setText(obj.ScaleValue.UserString)
        else:
            self.scaleDiameterInput.setText(FreeCAD.Units.Quantity(0, FreeCAD.Units.Length).UserString)
        self.scaleForeRadio.setChecked(obj.ScaleForeDiameter)
        self.scaleAftRadio.setChecked(not obj.ScaleForeDiameter)

        self._loading = False

        self._setScaleState()

    def getScale(self) -> float:
        scale = 1.0
        if self._obj.Scale:
            if self._obj.ScaleByValue and self._obj.ScaleValue.Value > 0.0:
                scale = self._obj.ScaleValue.Value
            elif self._obj.ScaleByDiameter:
                if self._obj.ScaleForeDiameter:
                    diameter = self._obj.Proxy.getForeDiameter()
                else:
                    diameter = self._obj.Proxy.getAftDiameter()
                if diameter > 0 and self._obj.ScaleValue > 0:
                    scale =  float(diameter / self._obj.ScaleValue)
        return scale

    def resetScale(self) -> None:
        self._loading = True

        self._obj.Scale = False
        self._obj.ScaleByValue = True
        self._obj.ScaleByDiameter = False
        self._obj.AutoScaleDiameter = False
        self._obj.ScaleForeDiameter = False
        self._obj.ScaleValue = FreeCAD.Units.Quantity("1.0")

        self._loading = False
        self._setScaleState()

    def setEdited(self):
        try:
            self._obj.Proxy.setEdited()
            self.scaled.emit()
        except ReferenceError:
            # Object may be deleted
            pass

    def onScalingGroup(self, on : bool) -> None:
        if self._loading:
            return
        try:
            self._obj.Scale = on
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self._setScaleState()
        self.setEdited()

    def onScale(self, checked : bool) -> None:
        if self._loading:
            return
        try:
            self._obj.ScaleByValue = checked
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self._setScaleState()
        self.setEdited()

    def onScaleDiameter(self, checked: bool) -> None:
        if self._loading:
            return
        try:
            self._obj.ScaleByDiameter = checked
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self._setScaleState()
        self.setEdited()

    def onScaleAutoDiameter(self, checked : bool) -> None:
        if self._loading:
            return
        try:
            self._obj.AutoScaleDiameter = checked
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self._setScaleState()
        self.setEdited()

    def onUpscale(self, checked : bool) -> None:
        if self._loading:
            return
        try:
            scale = FreeCAD.Units.Quantity(self.scaleInput.text()).Value
            if checked:
                if scale > 0:
                    self._obj.ScaleValue = 1 / scale
                else:
                    self._obj.ScaleValue = 1.0
            else:
                self._obj.ScaleValue = scale
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self._setScaleState()
        self.setEdited()

    def onScaleValue(self, value):
        if self._loading:
            return
        try:
            scale = FreeCAD.Units.Quantity(value).Value
            if self.upscaleCheckbox.isChecked():
                if scale > 0:
                    self._obj.ScaleValue = 1 / scale
                else:
                    self._obj.ScaleValue = 1.0
            else:
                self._obj.ScaleValue = scale
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def onScaleDiameterValue(self, value):
        if self._loading:
            return
        try:
            self._obj.ScaleValue = FreeCAD.Units.Quantity(value)
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()
