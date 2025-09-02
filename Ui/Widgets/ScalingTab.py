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
import os

import FreeCAD
import FreeCADGui

from Rocket.Utilities import translate

from PySide import QtGui, QtCore
from PySide.QtCore import QObject, Signal
from PySide.QtWidgets import QGridLayout, QVBoxLayout, QSizePolicy

from Rocket.Constants import FIN_TYPE_TRAPEZOID

from Ui.UIPaths import getUIPath

class ScalingTab(QObject):
    scaled = Signal()   # emitted when scale parameters have changed

    def __init__(self, obj : Any) -> None:
        super().__init__()
        self._obj = obj
        self._loading = False # Prevent updates when loading
        self._isAssembly = self._obj.Proxy.isRocketAssembly()
        self._form = FreeCADGui.PySideUic.loadUi(os.path.join(getUIPath(), 'Ui', "Widgets", "ScalingTab.ui"))

        self.setTabScaling()
        self._setConnections()
        self._setScaleState()

    def widget(self) -> QtGui.QWidget:
        return self._form

    def setTabScaling(self) -> None:
        # Scaling
        self._scalingGroup()

        # Show the results
        self._reportingGroup()

    def _scalingGroup(self) -> None:

        self._form.scaleDiameterCheckbox.setVisible(False)

        self._form.scaleForeRadio.setVisible(False)
        self._form.scaleAftRadio.setVisible(False)

        self._form.scaleRootRadio.setVisible(False)
        self._form.scaleRootInput.setVisible(False)

        self._form.scaleHeightRadio.setVisible(False)
        self._form.scaleHeightInput.setVisible(False)

    def _reportingGroup(self) -> None:
        ...
        # Show the results
        # group = QtGui.QGroupBox(translate('Rocket', "Scaled Values"), self)

        # self.scaledLabel = QtGui.QLabel(translate('Rocket', "Scale"), self)

        # self.scaledInput = ui.createWidget("Gui::InputField")
        # self.scaledInput.setMinimumWidth(20)
        # self.scaledInput.setEnabled(False)

        # self.scaledLengthLabel = QtGui.QLabel(translate('Rocket', "Length"), self)

        # self.scaledLengthInput = ui.createWidget("Gui::InputField")
        # self.scaledLengthInput.unit = FreeCAD.Units.Length
        # self.scaledLengthInput.setMinimumWidth(20)
        # self.scaledLengthInput.setEnabled(False)

        # self.scaledDiameterLabel = QtGui.QLabel(translate('Rocket', "Diameter"), self)

        # self.scaledDiameterInput = ui.createWidget("Gui::InputField")
        # self.scaledDiameterInput.unit = FreeCAD.Units.Length
        # self.scaledDiameterInput.setMinimumWidth(20)
        # self.scaledDiameterInput.setEnabled(False)

        # self.scaledSetValuesButton = QtGui.QPushButton(translate('Rocket', 'Set as values'), self)
        # self.scaledSetValuesButton.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)

        # grid = QGridLayout()
        # row = 0

        # grid.addWidget(self.scaledLabel, row, 0)
        # grid.addWidget(self.scaledInput, row, 1, 1, 2)
        # row += 1

        # grid.addWidget(self.scaledLengthLabel, row, 0)
        # grid.addWidget(self.scaledLengthInput, row, 1, 1, 2)
        # row += 1

        # grid.addWidget(self.scaledDiameterLabel, row, 0)
        # grid.addWidget(self.scaledDiameterInput, row, 1, 1, 2)
        # row += 1

        # grid.addWidget(self.scaledSetValuesButton, row, 2)
        # row += 1

        # group.setLayout(grid)
        # return group

    def _setConnections(self) -> None:
        self._form.scalingGroup.toggled.connect(self.onScalingGroup)
        self._form.scaleRadio.toggled.connect(self.onScale)
        self._form.scaleDiameterRadio.toggled.connect(self.onScaleDiameter)
        self._form.scaleDiameterCheckbox.stateChanged.connect(self.onScaleAutoDiameter)
        self._form.upscaleCheckbox.stateChanged.connect(self.onUpscale)
        self._form.scaleInput.textEdited.connect(self.onScaleValue)
        self._form.scaleDiameterInput.textEdited.connect(self.onScaleDiameterValue)

    def _setScaleState(self) -> None:
        if self._form.scalingGroup.isChecked():
            byValue = self._form.scaleRadio.isChecked()
            self._form.scaleInput.setEnabled(byValue)
            self._form.upscaleCheckbox.setEnabled(byValue)

            byDiameter = self._form.scaleDiameterRadio.isChecked()
            self._form.scaleDiameterInput.setEnabled(byDiameter)
            # self._form.scaleDiameterCheckbox.setEnabled(byDiameter)
        self._form.scaleDiameterCheckbox.setVisible(False)

    def transferTo(self, obj : Any) -> None:
        "Transfer from the dialog to the object"
        obj.Scale = self._form.scalingGroup.isChecked()
        obj.ScaleByValue = self._form.scaleRadio.isChecked()
        obj.ScaleByDiameter = self._form.scaleDiameterRadio.isChecked()
        obj.AutoScaleDiameter = self._form.scaleDiameterCheckbox.isChecked()
        if obj.ScaleByValue:
            obj.ScaleValue = self.getScaleValue()
        else:
            obj.ScaleValue = FreeCAD.Units.Quantity(self._form.scaleDiameterInput.text())

    def transferFrom(self, obj : Any) -> None:
        "Transfer from the object to the dialog"
        self._loading = True

        self._form.scalingGroup.setChecked(obj.Scale)
        self._form.scaleRadio.setChecked(obj.ScaleByValue)
        self._form.scaleDiameterRadio.setChecked(obj.ScaleByDiameter)
        self._form.scaleDiameterCheckbox.setChecked(obj.AutoScaleDiameter)
        if obj.ScaleByValue:
            if obj.ScaleValue.Value > 0.0 and obj.ScaleValue.Value < 1.0:
                self._form.scaleInput.setText(f"{1.0 / obj.ScaleValue.Value}")
                self._form.upscaleCheckbox.setChecked(True)
            else:
                self._form.scaleInput.setText(f"{obj.ScaleValue.Value}")
                self._form.upscaleCheckbox.setChecked(False)
        else:
            self._form.scaleInput.setText("0")
        if obj.ScaleByDiameter:
            self._form.scaleDiameterInput.setText(obj.ScaleValue.UserString)
        else:
            self._form.scaleDiameterInput.setText(obj.Diameter.UserString)

        self._loading = False

        self._setScaleState()

    def getScaleValue(self) -> float:
        value = FreeCAD.Units.Quantity(self._form.scaleInput.text()).Value
        if self._form.upscaleCheckbox.isChecked():
            if value > 0:
                value = 1.0 / value
            else:
                value = 1.0
        return value

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
            self._obj.ScaleValue = self.getScaleValue()
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
            self._obj.ScaleValue = FreeCAD.Units.Quantity(self._form.scaleDiameterInput.text())
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
            scale = FreeCAD.Units.Quantity(self._form.scaleInput.text()).Value
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
            if self._form.upscaleCheckbox.isChecked():
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

    def __init__(self, obj : Any) -> None:
        super().__init__(obj)

    def _reportingGroup(self) -> None:
        ...
        # Show the results
        # group = QtGui.QGroupBox(translate('Rocket', "Scaled Values"), self)

        # self.scaledLabel = QtGui.QLabel(translate('Rocket', "Scale"), self)

        # self.scaledInput = ui.createWidget("Gui::InputField")
        # self.scaledInput.setMinimumWidth(20)
        # self.scaledInput.setEnabled(False)

        # self.scaledLengthLabel = QtGui.QLabel(translate('Rocket', "Length"), self)

        # self.scaledLengthInput = ui.createWidget("Gui::InputField")
        # self.scaledLengthInput.unit = FreeCAD.Units.Length
        # self.scaledLengthInput.setMinimumWidth(20)
        # self.scaledLengthInput.setEnabled(False)

        # self.scaledDiameterLabel = QtGui.QLabel(translate('Rocket', "Diameter"), self)

        # self.scaledDiameterInput = ui.createWidget("Gui::InputField")
        # self.scaledDiameterInput.unit = FreeCAD.Units.Length
        # self.scaledDiameterInput.setMinimumWidth(20)
        # self.scaledDiameterInput.setEnabled(False)

        # self.scaledOgiveDiameterLabel = QtGui.QLabel(translate('Rocket', "Ogive Diameter"), self)

        # self.scaledOgiveDiameterInput = ui.createWidget("Gui::InputField")
        # self.scaledOgiveDiameterInput.unit = FreeCAD.Units.Length
        # self.scaledOgiveDiameterInput.setMinimumWidth(20)
        # self.scaledOgiveDiameterInput.setEnabled(False)

        # self.scaledBluntedDiameterLabel = QtGui.QLabel(translate('Rocket', "Blunted Diameter"), self)

        # self.scaledBluntedDiameterInput = ui.createWidget("Gui::InputField")
        # self.scaledBluntedDiameterInput.unit = FreeCAD.Units.Length
        # self.scaledBluntedDiameterInput.setMinimumWidth(20)
        # self.scaledBluntedDiameterInput.setEnabled(False)

        # self.scaledSetValuesButton = QtGui.QPushButton(translate('Rocket', 'Set as values'), self)
        # self.scaledSetValuesButton.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)

        # grid = QGridLayout()
        # row = 0

        # grid.addWidget(self.scaledLabel, row, 0)
        # grid.addWidget(self.scaledInput, row, 1, 1, 2)
        # row += 1

        # grid.addWidget(self.scaledLengthLabel, row, 0)
        # grid.addWidget(self.scaledLengthInput, row, 1, 1, 2)
        # row += 1

        # grid.addWidget(self.scaledDiameterLabel, row, 0)
        # grid.addWidget(self.scaledDiameterInput, row, 1, 1, 2)
        # row += 1

        # grid.addWidget(self.scaledOgiveDiameterLabel, row, 0)
        # grid.addWidget(self.scaledOgiveDiameterInput, row, 1, 1, 2)
        # row += 1

        # grid.addWidget(self.scaledBluntedDiameterLabel, row, 0)
        # grid.addWidget(self.scaledBluntedDiameterInput, row, 1, 1, 2)
        # row += 1

        # grid.addWidget(self.scaledSetValuesButton, row, 2)
        # row += 1

        # group.setLayout(grid)
        # return group

class ScalingTabTransition(ScalingTab):

    def __init__(self, obj : Any) -> None:
        super().__init__(obj)

    def _setConnections(self) -> None:
        super()._setConnections()

        self._form.scaleForeRadio.toggled.connect(self.onScaleFore)
        self._form.scaleAftRadio.toggled.connect(self.onScaleAft)

    def _scalingGroup(self) -> None:
        ...

        # group = super()._scalingGroup(ui)

        # self.foreAftGroup = QtGui.QButtonGroup()
        # self._form.scaleForeRadio = QtGui.QRadioButton(translate('Rocket', "Fore"))
        # self.foreAftGroup.addButton(self._form.scaleForeRadio)
        # self._form.scaleForeRadio.setChecked(False)

        # self._form.scaleAftRadio = QtGui.QRadioButton(translate('Rocket', "Aft"))
        # self.foreAftGroup.addButton(self._form.scaleAftRadio)
        # self._form.scaleAftRadio.setChecked(True)

        # grid = group.layout()
        # row = grid.rowCount()

        # grid.addWidget(self._form.scaleForeRadio, row, 1)
        # grid.addWidget(self._form.scaleAftRadio, row, 2)
        # row += 1

        # return group

    def _reportingGroup(self) -> None:
        ...
        # Show the results
        # group = super()._reportingGroup(ui)

        # self.scaledDiameterLabel.setText(translate('Rocket', "Fore Diameter"))

        # self.scaledAftDiameterLabel = QtGui.QLabel(translate('Rocket', "Aft Diameter"), self)

        # self.scaledAftDiameterInput = ui.createWidget("Gui::InputField")
        # self.scaledAftDiameterInput.unit = FreeCAD.Units.Length
        # self.scaledAftDiameterInput.setMinimumWidth(20)
        # self.scaledAftDiameterInput.setEnabled(False)

        # grid = group.layout()
        # row = grid.rowCount()

        # # Insert before the set values button
        # grid.addWidget(self.scaledAftDiameterLabel, row - 1, 0)
        # grid.addWidget(self.scaledAftDiameterInput, row - 1, 1, 1, 2)
        # row += 1

        # return group

    def _setScaleState(self) -> None:
        super()._setScaleState()
        if self._form.scalingGroup.isChecked():
            byDiameter = self._form.scaleDiameterRadio.isChecked()
            self._form.scaleForeRadio.setEnabled(byDiameter)
            self._form.scaleAftRadio.setEnabled(byDiameter)

    def transferTo(self, obj : Any) -> None:
        "Transfer from the dialog to the object"
        obj.Scale = self._form.scalingGroup.isChecked()
        obj.ScaleByValue = self._form.scaleRadio.isChecked()
        obj.ScaleByDiameter = self._form.scaleDiameterRadio.isChecked()
        obj.AutoScaleDiameter = self._form.scaleDiameterCheckbox.isChecked()
        obj.ScaleForeDiameter = self._form.scaleForeRadio.isChecked()
        if obj.ScaleByValue:
            value = FreeCAD.Units.Quantity(self._form.scaleInput.text()).Value
            if self._form.upscaleCheckbox.isChecked():
                if value > 0:
                    obj.ScaleValue = 1.0 / value
                else:
                    obj.ScaleValue = 1.0
            else:
                obj.ScaleValue = value
        else:
            obj.ScaleValue = FreeCAD.Units.Quantity(self._form.scaleDiameterInput.text())

    def transferFrom(self, obj : Any) -> None:
        "Transfer from the object to the dialog"
        self._loading = True

        self._form.scalingGroup.setChecked(obj.Scale)
        self._form.scaleRadio.setChecked(obj.ScaleByValue)
        self._form.scaleDiameterRadio.setChecked(obj.ScaleByDiameter)
        self._form.scaleDiameterCheckbox.setChecked(obj.AutoScaleDiameter)
        if obj.ScaleByValue:
            if obj.ScaleValue.Value > 0.0 and obj.ScaleValue.Value < 1.0:
                self._form.scaleInput.setText(f"{1.0 / obj.ScaleValue.Value}")
                self._form.upscaleCheckbox.setChecked(True)
            else:
                self._form.scaleInput.setText(f"{obj.ScaleValue.Value}")
                self._form.upscaleCheckbox.setChecked(False)
        else:
            self._form.scaleInput.setText("0")
        if obj.ScaleByDiameter:
            self._form.scaleDiameterInput.setText(obj.ScaleValue.UserString)
        else:
            if obj.ScaleForeDiameter:
                self._form.scaleDiameterInput.setText(obj.ForeDiameter.UserString)
            else:
                self._form.scaleDiameterInput.setText(obj.AftDiameter.UserString)
        self._form.scaleForeRadio.setChecked(obj.ScaleForeDiameter)
        self._form.scaleAftRadio.setChecked(not obj.ScaleForeDiameter)

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

    def __init__(self, obj : Any) -> None:
        super().__init__(obj)

class ScalingTabFins(ScalingTab):

    def __init__(self, obj : Any) -> None:
        super().__init__(obj)

    def _scalingGroup(self) -> None:
        ...

        # Scaling
        # group = QtGui.QGroupBox(translate('Rocket', "Scaling"), self)
        # group.setCheckable(True)
        # group.setChecked(False)

        # self._form.scaleRadio = QtGui.QRadioButton (translate('Rocket', "By value"), group)
        # self._form.scaleRadio.setChecked(True)

        # self._form.scaleInput = ui.createWidget("Gui::InputField")
        # self._form.scaleInput.setMinimumWidth(20)

        # self._form.upscaleCheckbox = QtGui.QCheckBox(translate('Rocket', "Upscale"), self)
        # self._form.upscaleCheckbox.setCheckState(QtCore.Qt.Unchecked)

        # self._form.scaleRootRadio = QtGui.QRadioButton(translate('Rocket', "By root chord"), group)
        # self._form.scaleRootRadio.setChecked(False)

        # self._form.scaleRootInput = ui.createWidget("Gui::InputField")
        # self._form.scaleRootInput.unit = FreeCAD.Units.Length
        # self._form.scaleRootInput.setMinimumWidth(20)

        # self._form.scaleHeightRadio = QtGui.QRadioButton(translate('Rocket', "By height"), group)
        # self._form.scaleHeightRadio.setChecked(False)

        # self._form.scaleHeightInput = ui.createWidget("Gui::InputField")
        # self._form.scaleHeightInput.unit = FreeCAD.Units.Length
        # self._form.scaleHeightInput.setMinimumWidth(20)

        # grid = QGridLayout()
        # row = 0

        # grid.addWidget(self._form.scaleRadio, row, 0)
        # grid.addWidget(self._form.scaleInput, row, 1, 1, 2)
        # grid.addWidget(self._form.upscaleCheckbox, row, 3)
        # row += 1

        # grid.addWidget(self._form.scaleRootRadio, row, 0)
        # grid.addWidget(self._form.scaleRootInput, row, 1, 1, 2)
        # row += 1

        # grid.addWidget(self._form.scaleHeightRadio, row, 0)
        # grid.addWidget(self._form.scaleHeightInput, row, 1, 1, 2)
        # row += 1

        # group.setLayout(grid)
        # return group

    def _reportingGroup(self) -> None:
        ...

        # Show the results
        # group = QtGui.QGroupBox(translate('Rocket', "Scaled Values"), self)

        # self.scaledLabel = QtGui.QLabel(translate('Rocket', "Scale"), self)

        # self.scaledInput = ui.createWidget("Gui::InputField")
        # self.scaledInput.setMinimumWidth(20)
        # self.scaledInput.setEnabled(False)

        # self.scaledRootLabel = QtGui.QLabel(translate('Rocket', "Root chord"), self)

        # self.scaledRootInput = ui.createWidget("Gui::InputField")
        # self.scaledRootInput.unit = FreeCAD.Units.Length
        # self.scaledRootInput.setMinimumWidth(20)
        # self.scaledRootInput.setEnabled(False)

        # self.scaledRootThicknessLabel = QtGui.QLabel(translate('Rocket', "Root thickness"), self)

        # self.scaledRootThicknessInput = ui.createWidget("Gui::InputField")
        # self.scaledRootThicknessInput.unit = FreeCAD.Units.Length
        # self.scaledRootThicknessInput.setMinimumWidth(20)
        # self.scaledRootThicknessInput.setEnabled(False)

        # self._form.scaledTipLabel = QtGui.QLabel(translate('Rocket', "Tip chord"), self)

        # self._form.scaledTipInput = ui.createWidget("Gui::InputField")
        # self._form.scaledTipInput.unit = FreeCAD.Units.Length
        # self._form.scaledTipInput.setMinimumWidth(20)
        # self._form.scaledTipInput.setEnabled(False)

        # self._form.scaledTipThicknessLabel = QtGui.QLabel(translate('Rocket', "Tip thickness"), self)

        # self._form.scaledTipThicknessInput = ui.createWidget("Gui::InputField")
        # self._form.scaledTipThicknessInput.unit = FreeCAD.Units.Length
        # self._form.scaledTipThicknessInput.setMinimumWidth(20)
        # self._form.scaledTipThicknessInput.setEnabled(False)

        # self.scaledHeightLabel = QtGui.QLabel(translate('Rocket', "Height"), self)

        # self.scaledHeightInput = ui.createWidget("Gui::InputField")
        # self.scaledHeightInput.unit = FreeCAD.Units.Length
        # self.scaledHeightInput.setMinimumWidth(20)
        # self.scaledHeightInput.setEnabled(False)

        # self.scaledSetValuesButton = QtGui.QPushButton(translate('Rocket', 'Set as values'), self)
        # self.scaledSetValuesButton.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)

        # grid = QGridLayout()
        # row = 0

        # grid.addWidget(self.scaledLabel, row, 0)
        # grid.addWidget(self.scaledInput, row, 1, 1, 2)
        # row += 1

        # grid.addWidget(self.scaledRootLabel, row, 0)
        # grid.addWidget(self.scaledRootInput, row, 1, 1, 2)
        # row += 1

        # grid.addWidget(self.scaledRootThicknessLabel, row, 0)
        # grid.addWidget(self.scaledRootThicknessInput, row, 1, 1, 2)
        # row += 1

        # grid.addWidget(self._form.scaledTipLabel, row, 0)
        # grid.addWidget(self._form.scaledTipInput, row, 1, 1, 2)
        # row += 1

        # grid.addWidget(self._form.scaledTipThicknessLabel, row, 0)
        # grid.addWidget(self._form.scaledTipThicknessInput, row, 1, 1, 2)
        # row += 1

        # grid.addWidget(self.scaledHeightLabel, row, 0)
        # grid.addWidget(self.scaledHeightInput, row, 1, 1, 2)
        # row += 1

        # grid.addWidget(self.scaledSetValuesButton, row, 2)
        # row += 1

        # group.setLayout(grid)
        # return group

    def _setConnections(self) -> None:
        self._form.scalingGroup.toggled.connect(self.onScalingGroup)
        self._form.scaleRadio.toggled.connect(self.onScale)
        self._form.scaleRootRadio.toggled.connect(self.onScaleRoot)
        self._form.scaleHeightRadio.toggled.connect(self.onScaleHeight)
        self._form.upscaleCheckbox.stateChanged.connect(self.onUpscale)
        self._form.scaleInput.textEdited.connect(self.onScaleValue)
        self._form.scaleRootInput.textEdited.connect(self.onScaleRootValue)
        self._form.scaleHeightInput.textEdited.connect(self.onScaleHeightValue)

    def _setScaleState(self) -> None:
        if self._form.scalingGroup.isChecked():
            byValue = self._form.scaleRadio.isChecked()
            self._form.scaleInput.setEnabled(byValue)
            self._form.upscaleCheckbox.setEnabled(byValue)

            byRoot = self._form.scaleRootRadio.isChecked()
            self._form.scaleRootInput.setEnabled(byRoot)

            byHeight = self._form.scaleHeightRadio.isChecked()
            self._form.scaleHeightInput.setEnabled(byHeight)

        isTrapezoid = (self._obj.FinType == FIN_TYPE_TRAPEZOID)
        self._form.scaledTipLabel.setVisible(isTrapezoid)
        self._form.scaledTipInput.setVisible(isTrapezoid)
        self._form.scaledTipThicknessLabel.setVisible(isTrapezoid)
        self._form.scaledTipThicknessInput.setVisible(isTrapezoid)

    def transferTo(self, obj : Any) -> None:
        "Transfer from the dialog to the object"
        obj.Scale = self._form.scalingGroup.isChecked()
        obj.ScaleByValue = self._form.scaleRadio.isChecked()
        obj.ScaleByRootChord = self._form.scaleRootRadio.isChecked()
        obj.ScaleByHeight = self._form.scaleHeightRadio.isChecked()
        obj.ScaleByDiameter = False
        obj.AutoScaleDiameter = False
        if obj.ScaleByValue:
            value = FreeCAD.Units.Quantity(self._form.scaleInput.text()).Value
            if self._form.upscaleCheckbox.isChecked():
                if value > 0:
                    obj.ScaleValue = 1.0 / value
                else:
                    obj.ScaleValue = 1.0
            else:
                obj.ScaleValue = value
        elif obj.ScaleByRootChord:
            obj.ScaleValue = FreeCAD.Units.Quantity(self._form.scaleRootInput.text())
        elif obj.ScaleByHeight:
            obj.ScaleValue = FreeCAD.Units.Quantity(self._form.scaleHeightInput.text())

    def transferFrom(self, obj : Any) -> None:
        "Transfer from the object to the dialog"
        self._loading = True

        self._form.scalingGroup.setChecked(obj.Scale)
        self._form.scaleRadio.setChecked(obj.ScaleByValue)
        self._form.scaleRootRadio.setChecked(obj.ScaleByRootChord)
        self._form.scaleHeightRadio.setChecked(obj.ScaleByHeight)
        if obj.ScaleByValue:
            if obj.ScaleValue.Value > 0.0 and obj.ScaleValue.Value < 1.0:
                self._form.scaleInput.setText(f"{1.0 / obj.ScaleValue.Value}")
                self._form.upscaleCheckbox.setChecked(True)
            else:
                self._form.scaleInput.setText(f"{obj.ScaleValue.Value}")
                self._form.upscaleCheckbox.setChecked(False)
        else:
            self._form.scaleInput.setText("0")
        if obj.ScaleByRootChord:
            self._form.scaleRootInput.setText(obj.ScaleValue.UserString)
        else:
            # self._form.scaleRootInput.setText(FreeCAD.Units.Quantity(0, FreeCAD.Units.Length).UserString)
            self._form.scaleRootInput.setText(obj.RootChord.UserString)
        if obj.ScaleByHeight:
            self._form.scaleHeightInput.setText(obj.ScaleValue.UserString)
        else:
            # self._form.scaleHeightInput.setText(FreeCAD.Units.Quantity(0, FreeCAD.Units.Length).UserString)
            self._form.scaleHeightInput.setText(obj.Height.UserString)

        self._loading = False

        self._setScaleState()

    def onScaleRoot(self, checked: bool) -> None:
        if self._loading:
            return
        try:
            self._obj.ScaleByRootChord = checked
            self._obj.ScaleValue = FreeCAD.Units.Quantity(self._form.scaleRootInput.text())
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
            self._obj.ScaleValue = FreeCAD.Units.Quantity(self._form.scaleHeightInput.text())
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

    def __init__(self, obj : Any) -> None:
        super().__init__(obj)

    def _scalingGroup(self) -> None:
        ...
        # Scaling
        # group = QtGui.QGroupBox(translate('Rocket', "Scaling"), self)
        # group.setCheckable(True)
        # group.setChecked(False)

        # self.scaleLabel = QtGui.QLabel(translate('Rocket', "By value"), group)

        # self._form.scaleInput = ui.createWidget("Gui::InputField")
        # self._form.scaleInput.setMinimumWidth(20)

        # self._form.upscaleCheckbox = QtGui.QCheckBox(translate('Rocket', "Upscale"), self)
        # self._form.upscaleCheckbox.setCheckState(QtCore.Qt.Unchecked)

        # grid = QGridLayout()
        # row = 0

        # grid.addWidget(self.scaleLabel, row, 0)
        # grid.addWidget(self._form.scaleInput, row, 1, 1, 2)
        # grid.addWidget(self._form.upscaleCheckbox, row, 3)
        # row += 1

        # group.setLayout(grid)
        # return group

    def _reportingGroup(self) -> None:
        ...
        # # Show the results
        # group = QtGui.QGroupBox(translate('Rocket', "Scaled Values"), self)

        # self.scaledLabel = QtGui.QLabel(translate('Rocket', "Scale"), self)

        # self.scaledInput = ui.createWidget("Gui::InputField")
        # self.scaledInput.setMinimumWidth(20)
        # self.scaledInput.setEnabled(False)

        # # self.scaledLengthLabel = QtGui.QLabel(translate('Rocket', "Length"), self)

        # # self.scaledLengthInput = ui.createWidget("Gui::InputField")
        # # self.scaledLengthInput.unit = FreeCAD.Units.Length
        # # self.scaledLengthInput.setMinimumWidth(20)
        # # self.scaledLengthInput.setEnabled(False)

        # self.scaledSetValuesButton = QtGui.QPushButton(translate('Rocket', 'Set as values'), self)
        # self.scaledSetValuesButton.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)

        # grid = QGridLayout()
        # row = 0

        # grid.addWidget(self.scaledLabel, row, 0)
        # grid.addWidget(self.scaledInput, row, 1, 1, 2)
        # row += 1

        # # grid.addWidget(self.scaledLengthLabel, row, 0)
        # # grid.addWidget(self.scaledLengthInput, row, 1, 1, 2)
        # # row += 1

        # grid.addWidget(self.scaledSetValuesButton, row, 2)
        # row += 1

        # group.setLayout(grid)
        # return group

    def _setConnections(self) -> None:
        self._form.scalingGroup.toggled.connect(self.onScalingGroup)
        self._form.upscaleCheckbox.stateChanged.connect(self.onUpscale)
        self._form.scaleInput.textEdited.connect(self.onScaleValue)

    def _setScaleState(self) -> None:
        if self._form.scalingGroup.isChecked():
            self._form.scaleInput.setEnabled(True)
            self._form.upscaleCheckbox.setEnabled(True)

    def transferTo(self, obj : Any) -> None:
        "Transfer from the dialog to the object"
        obj.Scale = self._form.scalingGroup.isChecked()
        obj.ScaleByValue = True
        value = FreeCAD.Units.Quantity(self._form.scaleInput.text()).Value
        if self._form.upscaleCheckbox.isChecked():
            if value > 0:
                obj.ScaleValue = 1.0 / value
            else:
                obj.ScaleValue = 1.0
        else:
            obj.ScaleValue = value

    def transferFrom(self, obj : Any) -> None:
        "Transfer from the object to the dialog"
        self._loading = True

        self._form.scalingGroup.setChecked(obj.Scale)
        if obj.ScaleValue.Value < 1.0:
            self._form.scaleInput.setText(f"{1.0 / obj.ScaleValue.Value}")
            self._form.upscaleCheckbox.setChecked(True)
        else:
            self._form.scaleInput.setText(f"{obj.ScaleValue.Value}")
            self._form.upscaleCheckbox.setChecked(False)

        self._loading = False

        self._setScaleState()
