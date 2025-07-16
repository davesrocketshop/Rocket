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

from typing import Any

import FreeCAD
import FreeCADGui

from DraftTools import translate

from PySide import QtGui, QtCore
from PySide.QtCore import QObject, Signal
from PySide.QtWidgets import QGridLayout, QVBoxLayout, QSizePolicy

from Rocket.Constants import FIN_TYPE_TRAPEZOID
class ScalingTab(QtGui.QWidget):
    scaled = Signal()   # emitted when scale parameters have changed

    def __init__(self, obj : Any, parent : QtGui.QWidget = None) -> None:
        super().__init__(parent)
        self._obj = obj
        self._loading = False # Prevent updates when loading
        self._isAssembly = self._obj.Proxy.isRocketAssembly()

        self.setTabScaling()
        self._setConnections()
        self._setScaleState()

    def setTabScaling(self) -> None:
        ui = FreeCADGui.UiLoader()

        # Scaling
        self.scalingGroup = self._scalingGroup(ui)

        # Show the results
        self.reportingGroup = self._reportingGroup(ui)

        layout = QVBoxLayout()
        layout.addWidget(self.scalingGroup)
        layout.addWidget(self.reportingGroup)
        layout.addItem(QtGui.QSpacerItem(0,0, QSizePolicy.Expanding, QSizePolicy.Expanding))

        self.setLayout(layout)

    def _scalingGroup(self, ui : FreeCADGui.UiLoader) -> QtGui.QGroupBox:

        # Scaling
        group = QtGui.QGroupBox(translate('Rocket', "Scaling"), self)
        group.setCheckable(True)
        group.setChecked(False)

        self.scaleRadio = QtGui.QRadioButton (translate('Rocket', "By value"), group)
        self.scaleRadio.setChecked(True)

        self.scaleInput = ui.createWidget("Gui::InputField")
        self.scaleInput.setMinimumWidth(20)

        self.upscaleCheckbox = QtGui.QCheckBox(translate('Rocket', "Upscale"), self)
        self.upscaleCheckbox.setCheckState(QtCore.Qt.Unchecked)

        self.scaleDiameterRadio = QtGui.QRadioButton(translate('Rocket', "By body diameter"), group)
        self.scaleDiameterRadio.setChecked(False)

        self.scaleDiameterInput = ui.createWidget("Gui::InputField")
        self.scaleDiameterInput.unit = FreeCAD.Units.Length
        self.scaleDiameterInput.setMinimumWidth(20)

        self.autoScaleDiameterCheckbox = QtGui.QCheckBox(translate('Rocket', "auto"), self)
        self.autoScaleDiameterCheckbox.setCheckState(QtCore.Qt.Unchecked)

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

        group.setLayout(grid)
        return group

    def _reportingGroup(self, ui : FreeCADGui.UiLoader) -> QtGui.QGroupBox:

        # Show the results
        group = QtGui.QGroupBox(translate('Rocket', "Scaled Values"), self)

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

        grid.addWidget(self.scaledSetValuesButton, row, 2)
        row += 1

        group.setLayout(grid)
        return group

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
            byValue = self.scaleRadio.isChecked()
            self.scaleInput.setEnabled(byValue)
            self.upscaleCheckbox.setEnabled(byValue)

            byDiameter = self.scaleDiameterRadio.isChecked()
            self.scaleDiameterInput.setEnabled(byDiameter)
            self.autoScaleDiameterCheckbox.setEnabled(byDiameter)

    def transferTo(self, obj : Any) -> None:
        "Transfer from the dialog to the object"
        obj.Scale = self.scalingGroup.isChecked()
        obj.ScaleByValue = self.scaleRadio.isChecked()
        obj.ScaleByDiameter = self.scaleDiameterRadio.isChecked()
        obj.AutoScaleDiameter = self.autoScaleDiameterCheckbox.isChecked()
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

    def transferFrom(self, obj : Any) -> None:
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

        self._loading = False

        self._setScaleState()

    def isScaled(self):
        return self._obj.Proxy.isScaled()

    def getScale(self) -> float:
        return self._obj.Proxy.getScale()

    def resetScale(self) -> None:
        self._loading = True

        self._obj.Proxy.resetScale()

        self._loading = False
        self._setScaleState()

    def setEdited(self) -> None:
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

    def onScaleValue(self, value : str) -> None:
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

    def onScaleDiameterValue(self, value : str) -> None:
        if self._loading:
            return
        try:
            self._obj.ScaleValue = FreeCAD.Units.Quantity(value)
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

class ScalingTabNose(ScalingTab):

    def __init__(self, obj : Any, parent : QtGui.QWidget = None) -> None:
        super().__init__(obj, parent)

    def _reportingGroup(self, ui : FreeCADGui.UiLoader) -> QtGui.QGroupBox:

        # Show the results
        group = QtGui.QGroupBox(translate('Rocket', "Scaled Values"), self)

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

        grid.addWidget(self.scaledOgiveDiameterLabel, row, 0)
        grid.addWidget(self.scaledOgiveDiameterInput, row, 1, 1, 2)
        row += 1

        grid.addWidget(self.scaledBluntedDiameterLabel, row, 0)
        grid.addWidget(self.scaledBluntedDiameterInput, row, 1, 1, 2)
        row += 1

        grid.addWidget(self.scaledSetValuesButton, row, 2)
        row += 1

        group.setLayout(grid)
        return group

class ScalingTabTransition(ScalingTab):

    def __init__(self, obj : Any, parent : QtGui.QWidget = None) -> None:
        super().__init__(obj, parent)

    def _setConnections(self) -> None:
        super()._setConnections()

        self.scaleForeRadio.toggled.connect(self.onScaleFore)
        self.scaleAftRadio.toggled.connect(self.onScaleAft)

    def _scalingGroup(self, ui : FreeCADGui.UiLoader) -> QtGui.QGroupBox:

        group = super()._scalingGroup(ui)

        self.foreAftGroup = QtGui.QButtonGroup()
        self.scaleForeRadio = QtGui.QRadioButton(translate('Rocket', "Fore"))
        self.foreAftGroup.addButton(self.scaleForeRadio)
        self.scaleForeRadio.setChecked(False)

        self.scaleAftRadio = QtGui.QRadioButton(translate('Rocket', "Aft"))
        self.foreAftGroup.addButton(self.scaleAftRadio)
        self.scaleAftRadio.setChecked(True)

        grid = group.layout()
        row = grid.rowCount()

        grid.addWidget(self.scaleForeRadio, row, 1)
        grid.addWidget(self.scaleAftRadio, row, 2)
        row += 1

        return group

    def _reportingGroup(self, ui : FreeCADGui.UiLoader) -> QtGui.QGroupBox:

        # Show the results
        group = super()._reportingGroup(ui)

        self.scaledDiameterLabel.setText(translate('Rocket', "Fore Diameter"))

        self.scaledAftDiameterLabel = QtGui.QLabel(translate('Rocket', "Aft Diameter"), self)

        self.scaledAftDiameterInput = ui.createWidget("Gui::InputField")
        self.scaledAftDiameterInput.unit = FreeCAD.Units.Length
        self.scaledAftDiameterInput.setMinimumWidth(20)
        self.scaledAftDiameterInput.setEnabled(False)

        grid = group.layout()
        row = grid.rowCount()

        # Insert before the set values button
        grid.addWidget(self.scaledAftDiameterLabel, row - 1, 0)
        grid.addWidget(self.scaledAftDiameterInput, row - 1, 1, 1, 2)
        row += 1

        return group

    def _setScaleState(self) -> None:
        super()._setScaleState()
        if self.scalingGroup.isChecked():
            byDiameter = self.scaleDiameterRadio.isChecked()
            self.scaleForeRadio.setEnabled(byDiameter)
            self.scaleAftRadio.setEnabled(byDiameter)

    def transferTo(self, obj : Any) -> None:
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

    def transferFrom(self, obj : Any) -> None:
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

    def onScaleFore(self, checked : bool) -> None:
        if self._loading:
            return
        try:
            self._obj.ScaleForeDiameter = checked
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self._setScaleState()
        self.setEdited()

    def onScaleAft(self, checked : bool) -> None:
        if self._loading:
            return
        try:
            self._obj.ScaleForeDiameter = not checked
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self._setScaleState()
        self.setEdited()

class ScalingTabBodyTube(ScalingTab):

    def __init__(self, obj : Any, parent : QtGui.QWidget = None) -> None:
        super().__init__(obj, parent)

class ScalingTabFins(ScalingTab):

    def __init__(self, obj : Any, parent : QtGui.QWidget = None) -> None:
        super().__init__(obj, parent)

    def _scalingGroup(self, ui : FreeCADGui.UiLoader) -> QtGui.QGroupBox:

        # Scaling
        group = QtGui.QGroupBox(translate('Rocket', "Scaling"), self)
        group.setCheckable(True)
        group.setChecked(False)

        self.scaleRadio = QtGui.QRadioButton (translate('Rocket', "By value"), group)
        self.scaleRadio.setChecked(True)

        self.scaleInput = ui.createWidget("Gui::InputField")
        self.scaleInput.setMinimumWidth(20)

        self.upscaleCheckbox = QtGui.QCheckBox(translate('Rocket', "Upscale"), self)
        self.upscaleCheckbox.setCheckState(QtCore.Qt.Unchecked)

        self.scaleRootRadio = QtGui.QRadioButton(translate('Rocket', "By root chord"), group)
        self.scaleRootRadio.setChecked(False)

        self.scaleRootInput = ui.createWidget("Gui::InputField")
        self.scaleRootInput.unit = FreeCAD.Units.Length
        self.scaleRootInput.setMinimumWidth(20)

        self.scaleHeightRadio = QtGui.QRadioButton(translate('Rocket', "By height"), group)
        self.scaleHeightRadio.setChecked(False)

        self.scaleHeightInput = ui.createWidget("Gui::InputField")
        self.scaleHeightInput.unit = FreeCAD.Units.Length
        self.scaleHeightInput.setMinimumWidth(20)

        grid = QGridLayout()
        row = 0

        grid.addWidget(self.scaleRadio, row, 0)
        grid.addWidget(self.scaleInput, row, 1, 1, 2)
        grid.addWidget(self.upscaleCheckbox, row, 3)
        row += 1

        grid.addWidget(self.scaleRootRadio, row, 0)
        grid.addWidget(self.scaleRootInput, row, 1, 1, 2)
        row += 1

        grid.addWidget(self.scaleHeightRadio, row, 0)
        grid.addWidget(self.scaleHeightInput, row, 1, 1, 2)
        row += 1

        group.setLayout(grid)
        return group

    def _reportingGroup(self, ui : FreeCADGui.UiLoader) -> QtGui.QGroupBox:

        # Show the results
        group = QtGui.QGroupBox(translate('Rocket', "Scaled Values"), self)

        self.scaledLabel = QtGui.QLabel(translate('Rocket', "Scale"), self)

        self.scaledInput = ui.createWidget("Gui::InputField")
        self.scaledInput.setMinimumWidth(20)
        self.scaledInput.setEnabled(False)

        self.scaledRootLabel = QtGui.QLabel(translate('Rocket', "Root chord"), self)

        self.scaledRootInput = ui.createWidget("Gui::InputField")
        self.scaledRootInput.unit = FreeCAD.Units.Length
        self.scaledRootInput.setMinimumWidth(20)
        self.scaledRootInput.setEnabled(False)

        self.scaledRootThicknessLabel = QtGui.QLabel(translate('Rocket', "Root thickness"), self)

        self.scaledRootThicknessInput = ui.createWidget("Gui::InputField")
        self.scaledRootThicknessInput.unit = FreeCAD.Units.Length
        self.scaledRootThicknessInput.setMinimumWidth(20)
        self.scaledRootThicknessInput.setEnabled(False)

        self.scaledTipLabel = QtGui.QLabel(translate('Rocket', "Tip chord"), self)

        self.scaledTipInput = ui.createWidget("Gui::InputField")
        self.scaledTipInput.unit = FreeCAD.Units.Length
        self.scaledTipInput.setMinimumWidth(20)
        self.scaledTipInput.setEnabled(False)

        self.scaledTipThicknessLabel = QtGui.QLabel(translate('Rocket', "Tip thickness"), self)

        self.scaledTipThicknessInput = ui.createWidget("Gui::InputField")
        self.scaledTipThicknessInput.unit = FreeCAD.Units.Length
        self.scaledTipThicknessInput.setMinimumWidth(20)
        self.scaledTipThicknessInput.setEnabled(False)

        self.scaledHeightLabel = QtGui.QLabel(translate('Rocket', "Height"), self)

        self.scaledHeightInput = ui.createWidget("Gui::InputField")
        self.scaledHeightInput.unit = FreeCAD.Units.Length
        self.scaledHeightInput.setMinimumWidth(20)
        self.scaledHeightInput.setEnabled(False)

        self.scaledSetValuesButton = QtGui.QPushButton(translate('Rocket', 'Set as values'), self)
        self.scaledSetValuesButton.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)

        grid = QGridLayout()
        row = 0

        grid.addWidget(self.scaledLabel, row, 0)
        grid.addWidget(self.scaledInput, row, 1, 1, 2)
        row += 1

        grid.addWidget(self.scaledRootLabel, row, 0)
        grid.addWidget(self.scaledRootInput, row, 1, 1, 2)
        row += 1

        grid.addWidget(self.scaledRootThicknessLabel, row, 0)
        grid.addWidget(self.scaledRootThicknessInput, row, 1, 1, 2)
        row += 1

        grid.addWidget(self.scaledTipLabel, row, 0)
        grid.addWidget(self.scaledTipInput, row, 1, 1, 2)
        row += 1

        grid.addWidget(self.scaledTipThicknessLabel, row, 0)
        grid.addWidget(self.scaledTipThicknessInput, row, 1, 1, 2)
        row += 1

        grid.addWidget(self.scaledHeightLabel, row, 0)
        grid.addWidget(self.scaledHeightInput, row, 1, 1, 2)
        row += 1

        grid.addWidget(self.scaledSetValuesButton, row, 2)
        row += 1

        group.setLayout(grid)
        return group

    def _setConnections(self) -> None:
        self.scalingGroup.toggled.connect(self.onScalingGroup)
        self.scaleRadio.toggled.connect(self.onScale)
        self.scaleRootRadio.toggled.connect(self.onScaleRoot)
        self.scaleHeightRadio.toggled.connect(self.onScaleHeight)
        self.upscaleCheckbox.stateChanged.connect(self.onUpscale)
        self.scaleInput.textEdited.connect(self.onScaleValue)
        self.scaleRootInput.textEdited.connect(self.onScaleRootValue)
        self.scaleHeightInput.textEdited.connect(self.onScaleHeightValue)

    def _setScaleState(self) -> None:
        if self.scalingGroup.isChecked():
            byValue = self.scaleRadio.isChecked()
            self.scaleInput.setEnabled(byValue)
            self.upscaleCheckbox.setEnabled(byValue)

            byRoot = self.scaleRootRadio.isChecked()
            self.scaleRootInput.setEnabled(byRoot)

            byHeight = self.scaleHeightRadio.isChecked()
            self.scaleHeightInput.setEnabled(byHeight)

        isTrapezoid = (self._obj.FinType == FIN_TYPE_TRAPEZOID)
        self.scaledTipLabel.setVisible(isTrapezoid)
        self.scaledTipInput.setVisible(isTrapezoid)
        self.scaledTipThicknessLabel.setVisible(isTrapezoid)
        self.scaledTipThicknessInput.setVisible(isTrapezoid)

    def transferTo(self, obj : Any) -> None:
        "Transfer from the dialog to the object"
        obj.Scale = self.scalingGroup.isChecked()
        obj.ScaleByValue = self.scaleRadio.isChecked()
        obj.ScaleByRootChord = self.scaleRootRadio.isChecked()
        obj.ScaleByHeight = self.scaleHeightRadio.isChecked()
        obj.ScaleByDiameter = False
        obj.AutoScaleDiameter = False
        if obj.ScaleByValue:
            value = FreeCAD.Units.Quantity(self.scaleInput.text()).Value
            if self.upscaleCheckbox.isChecked():
                if value > 0:
                    obj.ScaleValue = 1.0 / value
                else:
                    obj.ScaleValue = 1.0
            else:
                obj.ScaleValue = value
        elif obj.ScaleByRootChord:
            obj.ScaleValue = FreeCAD.Units.Quantity(self.scaleRootInput.text())
        elif obj.ScaleByHeight:
            obj.ScaleValue = FreeCAD.Units.Quantity(self.scaleHeightInput.text())

    def transferFrom(self, obj : Any) -> None:
        "Transfer from the object to the dialog"
        self._loading = True

        self.scalingGroup.setChecked(obj.Scale)
        self.scaleRadio.setChecked(obj.ScaleByValue)
        self.scaleRootRadio.setChecked(obj.ScaleByRootChord)
        self.scaleHeightRadio.setChecked(obj.ScaleByHeight)
        if obj.ScaleByValue:
            if obj.ScaleValue.Value > 0.0 and obj.ScaleValue.Value < 1.0:
                self.scaleInput.setText(f"{1.0 / obj.ScaleValue.Value}")
                self.upscaleCheckbox.setChecked(True)
            else:
                self.scaleInput.setText(f"{obj.ScaleValue.Value}")
                self.upscaleCheckbox.setChecked(False)
        else:
            self.scaleInput.setText("0")
        if obj.ScaleByRootChord:
            self.scaleRootInput.setText(obj.ScaleValue.UserString)
        else:
            self.scaleRootInput.setText(FreeCAD.Units.Quantity(0, FreeCAD.Units.Length).UserString)
        if obj.ScaleByHeight:
            self.scaleHeightInput.setText(obj.ScaleValue.UserString)
        else:
            self.scaleHeightInput.setText(FreeCAD.Units.Quantity(0, FreeCAD.Units.Length).UserString)

        self._loading = False

        self._setScaleState()

    def onScaleRoot(self, checked: bool) -> None:
        if self._loading:
            return
        try:
            self._obj.ScaleByRootChord = checked
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self._setScaleState()
        self.setEdited()

    def onScaleHeight(self, checked: bool) -> None:
        if self._loading:
            return
        try:
            self._obj.ScaleByHeight = checked
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self._setScaleState()
        self.setEdited()

    def onScaleRootValue(self, value : str) -> None:
        if self._loading:
            return
        try:
            self._obj.ScaleValue = FreeCAD.Units.Quantity(value)
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def onScaleHeightValue(self, value : str) -> None:
        if self._loading:
            return
        try:
            self._obj.ScaleValue = FreeCAD.Units.Quantity(value)
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

class ScalingTabRocketStage(ScalingTab):

    def __init__(self, obj : Any, parent : QtGui.QWidget = None) -> None:
        super().__init__(obj, parent)

    def _scalingGroup(self, ui : FreeCADGui.UiLoader) -> QtGui.QGroupBox:

        # Scaling
        group = QtGui.QGroupBox(translate('Rocket', "Scaling"), self)
        group.setCheckable(True)
        group.setChecked(False)

        self.scaleLabel = QtGui.QLabel(translate('Rocket', "By value"), group)

        self.scaleInput = ui.createWidget("Gui::InputField")
        self.scaleInput.setMinimumWidth(20)

        self.upscaleCheckbox = QtGui.QCheckBox(translate('Rocket', "Upscale"), self)
        self.upscaleCheckbox.setCheckState(QtCore.Qt.Unchecked)

        grid = QGridLayout()
        row = 0

        grid.addWidget(self.scaleLabel, row, 0)
        grid.addWidget(self.scaleInput, row, 1, 1, 2)
        grid.addWidget(self.upscaleCheckbox, row, 3)
        row += 1

        group.setLayout(grid)
        return group

    def _reportingGroup(self, ui : FreeCADGui.UiLoader) -> QtGui.QGroupBox:

        # Show the results
        group = QtGui.QGroupBox(translate('Rocket', "Scaled Values"), self)

        self.scaledLabel = QtGui.QLabel(translate('Rocket', "Scale"), self)

        self.scaledInput = ui.createWidget("Gui::InputField")
        self.scaledInput.setMinimumWidth(20)
        self.scaledInput.setEnabled(False)

        # self.scaledLengthLabel = QtGui.QLabel(translate('Rocket', "Length"), self)

        # self.scaledLengthInput = ui.createWidget("Gui::InputField")
        # self.scaledLengthInput.unit = FreeCAD.Units.Length
        # self.scaledLengthInput.setMinimumWidth(20)
        # self.scaledLengthInput.setEnabled(False)

        self.scaledSetValuesButton = QtGui.QPushButton(translate('Rocket', 'Set as values'), self)
        self.scaledSetValuesButton.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)

        grid = QGridLayout()
        row = 0

        grid.addWidget(self.scaledLabel, row, 0)
        grid.addWidget(self.scaledInput, row, 1, 1, 2)
        row += 1

        # grid.addWidget(self.scaledLengthLabel, row, 0)
        # grid.addWidget(self.scaledLengthInput, row, 1, 1, 2)
        # row += 1

        grid.addWidget(self.scaledSetValuesButton, row, 2)
        row += 1

        group.setLayout(grid)
        return group

    def _setConnections(self) -> None:
        self.scalingGroup.toggled.connect(self.onScalingGroup)
        self.upscaleCheckbox.stateChanged.connect(self.onUpscale)
        self.scaleInput.textEdited.connect(self.onScaleValue)

    def _setScaleState(self) -> None:
        if self.scalingGroup.isChecked():
            self.scaleInput.setEnabled(True)
            self.upscaleCheckbox.setEnabled(True)

    def transferTo(self, obj : Any) -> None:
        "Transfer from the dialog to the object"
        obj.Scale = self.scalingGroup.isChecked()
        obj.ScaleByValue = True
        value = FreeCAD.Units.Quantity(self.scaleInput.text()).Value
        if self.upscaleCheckbox.isChecked():
            if value > 0:
                obj.ScaleValue = 1.0 / value
            else:
                obj.ScaleValue = 1.0
        else:
            obj.ScaleValue = value

    def transferFrom(self, obj : Any) -> None:
        "Transfer from the object to the dialog"
        self._loading = True

        self.scalingGroup.setChecked(obj.Scale)
        if obj.ScaleValue.Value < 1.0:
            self.scaleInput.setText(f"{1.0 / obj.ScaleValue.Value}")
            self.upscaleCheckbox.setChecked(True)
        else:
            self.scaleInput.setText(f"{obj.ScaleValue.Value}")
            self.upscaleCheckbox.setChecked(False)

        self._loading = False

        self._setScaleState()
