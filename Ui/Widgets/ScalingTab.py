# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2025 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for drawing scaling tab"""

__title__ = "FreeCAD Scaling Tab"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from typing import Any
import os

import FreeCAD
import FreeCADGui

translate = FreeCAD.Qt.translate

from PySide import QtGui, QtCore
from PySide.QtCore import QObject, Signal

from Rocket.Constants import FIN_TYPE_TRAPEZOID
from Rocket.Constants import FEATURE_ROCKET
from Rocket.Constants import COMPONENT_TYPE_BODYTUBE, COMPONENT_TYPE_NOSECONE, COMPONENT_TYPE_TRANSITION

from Ui.Widgets.WaitCursor import WaitCursor
from Ui.UIPaths import getUIPath
from Ui.DialogLookup import DialogLookup

from Rocket.Utilities import _valueWithUnits

class ScalingTab(QObject):
    scaled = Signal()   # emitted when scale parameters have changed
    updated = Signal()   # emitted when the owner parameters need to be reloaded

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

        self._form.scaleForeAftGroup.setVisible(False)

        self._form.scaleRootRadio.setVisible(False)
        self._form.scaleRootInput.setVisible(False)

        self._form.scaleHeightRadio.setVisible(False)
        self._form.scaleHeightInput.setVisible(False)

    def _reportingGroup(self) -> None:
        self._form.scaledAftDiameterLabel.setVisible(False)
        self._form.scaledAftDiameterInput.setVisible(False)

        self._form.scaledOgiveDiameterLabel.setVisible(False)
        self._form.scaledOgiveDiameterInput.setVisible(False)

        self._form.scaledBluntedDiameterLabel.setVisible(False)
        self._form.scaledBluntedDiameterInput.setVisible(False)

        self._form.scaledRootLabel.setVisible(False)
        self._form.scaledRootInput.setVisible(False)

        self._form.scaledRootThicknessLabel.setVisible(False)
        self._form.scaledRootThicknessInput.setVisible(False)

        self._form.scaledTipLabel.setVisible(False)
        self._form.scaledTipInput.setVisible(False)

        self._form.scaledTipThicknessLabel.setVisible(False)
        self._form.scaledTipThicknessInput.setVisible(False)

        self._form.scaledHeightLabel.setVisible(False)
        self._form.scaledHeightInput.setVisible(False)

    def _setConnections(self) -> None:
        self._form.scalingGroup.toggled.connect(self.onScalingGroup)
        self._form.scaleOverrideCheckbox.stateChanged.connect(self.onOverride)
        self._form.scaleRadio.toggled.connect(self.onScale)
        self._form.scaleDiameterRadio.toggled.connect(self.onScaleDiameter)
        self._form.scaleDiameterCheckbox.stateChanged.connect(self.onScaleAutoDiameter)
        self._form.upscaleCheckbox.stateChanged.connect(self.onUpscale)
        self._form.scaleInput.textEdited.connect(self.onScaleValue)
        self._form.scaleDiameterInput.textEdited.connect(self.onScaleDiameterValue)
        self._form.scaledSetPartButton.clicked.connect(self.onSetPartScale)
        self._form.scaledSetStageButton.clicked.connect(self.onSetStageScale)
        self._form.scaleSetRocketButton.clicked.connect(self.onSetRocketScale)
        self._form.lookupButton.clicked.connect(self.onLookup)

    def _setScaleState(self) -> None:
        if self._obj.Proxy.isParentScaled():
            self._form.scalingGroup.setChecked(True)
            self._form.scaleOverrideCheckbox.setEnabled(True)
        else:
            self._form.scaleOverrideCheckbox.setEnabled(False)

        if self._form.scalingGroup.isChecked():
            if (self._obj.Proxy.isParentScaled() and self._obj.ScaleOverride) or \
                not self._obj.Proxy.isParentScaled():
                self._form.scaleRadio.setEnabled(True)
                byValue = self._form.scaleRadio.isChecked()
                self._form.scaleInput.setEnabled(byValue)
                self._form.upscaleCheckbox.setEnabled(byValue)

                self._form.scaleDiameterRadio.setEnabled(True)
                byDiameter = self._form.scaleDiameterRadio.isChecked()
                self._form.scaleDiameterInput.setEnabled(byDiameter)
                # self._form.scaleDiameterCheckbox.setEnabled(byDiameter)
                self._form.lookupButton.setEnabled(byDiameter)
            else:
                self._form.scaleRadio.setEnabled(False)
                self._form.scaleInput.setEnabled(False)
                self._form.upscaleCheckbox.setEnabled(False)
                self._form.scaleDiameterRadio.setEnabled(False)
                self._form.scaleDiameterInput.setEnabled(False)
                self._form.scaleDiameterCheckbox.setEnabled(False)
                self._form.lookupButton.setEnabled(False)
        self._form.scaleDiameterCheckbox.setVisible(False)

    def transferTo(self, obj : Any) -> None:
        "Transfer from the dialog to the object"
        obj.Scale = self._form.scalingGroup.isChecked()
        obj.ScaleOverride = self._form.scaleOverrideCheckbox.isChecked()
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
        self._form.scaleOverrideCheckbox.setChecked(obj.ScaleOverride)
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
        with WaitCursor():
            try:
                self._obj.Scale = on
                self._obj.Proxy.execute(self._obj)
            except ValueError:
                pass
            self._setScaleState()
            self.setEdited()

    def onOverride(self, checked : bool) -> None:
        if self._loading:
            return
        with WaitCursor():
            try:
                self._obj.ScaleOverride = checked
                self._obj.Proxy.execute(self._obj)
            except ValueError:
                pass
            self._setScaleState()
            self.setEdited()

    def onScale(self, checked : bool) -> None:
        if self._loading:
            return
        with WaitCursor():
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
        with WaitCursor():
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
        with WaitCursor():
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
        with WaitCursor():
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
        with WaitCursor():
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
        with WaitCursor():
            try:
                self._obj.ScaleValue = FreeCAD.Units.Quantity(value)
                self._obj.Proxy.execute(self._obj)
            except ValueError:
                pass
            self.setEdited()

    def onSetPartScale(self) -> None:
        with WaitCursor():
            scale = self.getScale()
            self._obj.Proxy.setPartScale(scale)

            scale = self.resetScale()
            self.update()
            self.setEdited()

    def onSetStageScale(self) -> None:
        # Update the scale values
        with WaitCursor():
            scale = self.getScale()
            self._obj.Proxy.setStageScale(scale)

            scale = self.resetScale()
            self.update()
            self.setEdited()

    def onSetRocketScale(self) -> None:
        # Update the scale values
        with WaitCursor():
            scale = self.getScale()
            self._obj.Proxy.setRocketScale(scale)

            scale = self.resetScale()
            self.update()
            self.setEdited()

    def onLookup(self) -> None:
        form = DialogLookup(COMPONENT_TYPE_BODYTUBE)
        form.exec()

        if len(form.result) > 0:
            result = form.result
            diameter = _valueWithUnits(result["outer_diameter"], result["outer_diameter_units"])
            self._form.scaleDiameterInput.setText(f"{diameter}")
            self.onScaleDiameterValue(f"{diameter}")

    def update(self):
        'fills the widgets'
        self.updated.emit()

class ScalingTabNose(ScalingTab):

    def __init__(self, obj : Any) -> None:
        super().__init__(obj)

    def _reportingGroup(self) -> None:
        self._form.scaledAftDiameterLabel.setVisible(False)
        self._form.scaledAftDiameterInput.setVisible(False)

        self._form.scaledRootLabel.setVisible(False)
        self._form.scaledRootInput.setVisible(False)

        self._form.scaledRootThicknessLabel.setVisible(False)
        self._form.scaledRootThicknessInput.setVisible(False)

        self._form.scaledTipLabel.setVisible(False)
        self._form.scaledTipInput.setVisible(False)

        self._form.scaledTipThicknessLabel.setVisible(False)
        self._form.scaledTipThicknessInput.setVisible(False)

        self._form.scaledHeightLabel.setVisible(False)
        self._form.scaledHeightInput.setVisible(False)

    def onLookup(self) -> None:
        form = DialogLookup(COMPONENT_TYPE_NOSECONE)
        form.exec()

        if len(form.result) > 0:
            result = form.result
            print(result.keys())
            diameter = _valueWithUnits(result["diameter"], result["diameter_units"])
            self._form.scaleDiameterInput.setText(f"{diameter}")
            self.onScaleDiameterValue(f"{diameter}")

class ScalingTabTransition(ScalingTab):

    def __init__(self, obj : Any) -> None:
        super().__init__(obj)

    def _setConnections(self) -> None:
        super()._setConnections()

        self._form.scaleForeRadio.toggled.connect(self.onScaleFore)
        self._form.scaleAftRadio.toggled.connect(self.onScaleAft)

    def _scalingGroup(self) -> None:

        self._form.scaleDiameterCheckbox.setVisible(False)

        self._form.scaleRootRadio.setVisible(False)
        self._form.scaleRootInput.setVisible(False)

        self._form.scaleHeightRadio.setVisible(False)
        self._form.scaleHeightInput.setVisible(False)

    def _reportingGroup(self) -> None:
        self._form.scaledDiameterLabel.setText(translate('Rocket', "Fore Diameter"))

        self._form.scaledRootLabel.setVisible(False)
        self._form.scaledRootInput.setVisible(False)

        self._form.scaledRootThicknessLabel.setVisible(False)
        self._form.scaledRootThicknessInput.setVisible(False)

        self._form.scaledTipLabel.setVisible(False)
        self._form.scaledTipInput.setVisible(False)

        self._form.scaledTipThicknessLabel.setVisible(False)
        self._form.scaledTipThicknessInput.setVisible(False)

        self._form.scaledHeightLabel.setVisible(False)
        self._form.scaledHeightInput.setVisible(False)

    def _setScaleState(self) -> None:
        super()._setScaleState()
        if self._form.scalingGroup.isChecked():
            if (self._obj.Proxy.isParentScaled() and self._obj.ScaleOverride) or \
                self._form.scaleDiameterRadio.isChecked():
                self._form.scaleForeAftGroup.setEnabled(True)
                # byDiameter = self._form.scaleDiameterRadio.isChecked()
                # self._form.scaleForeRadio.setEnabled(byDiameter)
                # self._form.scaleAftRadio.setEnabled(byDiameter)
                self._form.scaleForeRadio.setEnabled(True)
                self._form.scaleAftRadio.setEnabled(True)
            else:
                self._form.scaleForeAftGroup.setEnabled(False)

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
        with WaitCursor():
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
        with WaitCursor():
            try:
                self._obj.ScaleForeDiameter = not checked
                self._obj.Proxy.execute(self._obj)
            except ValueError:
                pass
            self._setScaleState()
            self.setEdited()

    def onLookup(self) -> None:
        form = DialogLookup(COMPONENT_TYPE_TRANSITION)
        form.exec()

        if len(form.result) > 0:
            result = form.result
            if self._form.scaleForeRadio.isChecked():
                diameter = _valueWithUnits(result["fore_outside_diameter"], result["fore_outside_diameter_units"])
            else:
                diameter = _valueWithUnits(result["aft_outside_diameter"], result["aft_outside_diameter_units"])
            self._form.scaleDiameterInput.setText(f"{diameter}")
            self.onScaleDiameterValue(f"{diameter}")

class ScalingTabBodyTube(ScalingTab):

    def __init__(self, obj : Any) -> None:
        super().__init__(obj)

class ScalingTabFins(ScalingTab):

    def __init__(self, obj : Any) -> None:
        super().__init__(obj)

    def _scalingGroup(self) -> None:
        self._form.scaleDiameterRadio.setVisible(False)
        self._form.scaleDiameterInput.setVisible(False)
        self._form.scaleDiameterCheckbox.setVisible(False)

        self._form.scaleForeAftGroup.setVisible(False)
        self._form.lookupButton.setVisible(False)

    def _reportingGroup(self) -> None:
        self._form.scaledLengthLabel.setVisible(False)
        self._form.scaledLengthInput.setVisible(False)

        self._form.scaledDiameterLabel.setVisible(False)
        self._form.scaledDiameterInput.setVisible(False)

        self._form.scaledAftDiameterLabel.setVisible(False)
        self._form.scaledAftDiameterInput.setVisible(False)

        self._form.scaledOgiveDiameterLabel.setVisible(False)
        self._form.scaledOgiveDiameterInput.setVisible(False)

        self._form.scaledBluntedDiameterLabel.setVisible(False)
        self._form.scaledBluntedDiameterInput.setVisible(False)

    def _setConnections(self) -> None:
        self._form.scalingGroup.toggled.connect(self.onScalingGroup)
        self._form.scaleOverrideCheckbox.stateChanged.connect(self.onOverride)
        self._form.scaleRadio.toggled.connect(self.onScale)
        self._form.scaleRootRadio.toggled.connect(self.onScaleRoot)
        self._form.scaleHeightRadio.toggled.connect(self.onScaleHeight)
        self._form.upscaleCheckbox.stateChanged.connect(self.onUpscale)
        self._form.scaleInput.textEdited.connect(self.onScaleValue)
        self._form.scaleRootInput.textEdited.connect(self.onScaleRootValue)
        self._form.scaleHeightInput.textEdited.connect(self.onScaleHeightValue)

    def _setScaleState(self) -> None:
        if self._obj.Proxy.isParentScaled():
            self._form.scalingGroup.setChecked(True)
            self._form.scaleOverrideCheckbox.setEnabled(True)
        else:
            self._form.scaleOverrideCheckbox.setEnabled(False)

        if self._form.scalingGroup.isChecked():
            if (self._obj.Proxy.isParentScaled() and self._obj.ScaleOverride) or \
                not self._obj.Proxy.isParentScaled():
                self._form.scaleRadio.setEnabled(True)
                byValue = self._form.scaleRadio.isChecked()
                self._form.scaleInput.setEnabled(byValue)
                self._form.upscaleCheckbox.setEnabled(byValue)

                self._form.scaleRootRadio.setEnabled(True)
                byRoot = self._form.scaleRootRadio.isChecked()
                self._form.scaleRootInput.setEnabled(byRoot)

                self._form.scaleHeightRadio.setEnabled(True)
                byHeight = self._form.scaleHeightRadio.isChecked()
                self._form.scaleHeightInput.setEnabled(byHeight)
            else:
                self._form.scaleRadio.setEnabled(False)
                self._form.scaleInput.setEnabled(False)
                self._form.upscaleCheckbox.setEnabled(False)

                self._form.scaleRootRadio.setEnabled(False)
                self._form.scaleRootInput.setEnabled(False)

                self._form.scaleHeightRadio.setEnabled(False)
                self._form.scaleHeightInput.setEnabled(False)
        self._form.scaleDiameterCheckbox.setVisible(False)

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
        with WaitCursor():
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
        with WaitCursor():
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
        with WaitCursor():
            try:
                self._obj.ScaleValue = FreeCAD.Units.Quantity(value)
                self._obj.Proxy.execute(self._obj)
            except ValueError:
                pass
            self.setEdited()

    def onScaleHeightValue(self, value : str) -> None:
        if self._loading:
            return
        with WaitCursor():
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
        if self._obj.Proxy.Type == FEATURE_ROCKET:
            # A rocket has no parent to override
            self._form.scaleOverrideCheckbox.setVisible(False)

        # There is only one option at this level in the tree
        self._form.scaleRadio.setChecked(True)

        self._form.scaleDiameterRadio.setVisible(False)
        self._form.scaleDiameterInput.setVisible(False)
        self._form.scaleDiameterCheckbox.setVisible(False)

        self._form.scaleForeAftGroup.setVisible(False)
        self._form.lookupButton.setVisible(False)

        self._form.scaleRootRadio.setVisible(False)
        self._form.scaleRootInput.setVisible(False)

        self._form.scaleHeightRadio.setVisible(False)
        self._form.scaleHeightInput.setVisible(False)

    def _reportingGroup(self) -> None:
        self._form.scaledDiameterLabel.setVisible(False)
        self._form.scaledDiameterInput.setVisible(False)

        self._form.scaledAftDiameterLabel.setVisible(False)
        self._form.scaledAftDiameterInput.setVisible(False)

        self._form.scaledOgiveDiameterLabel.setVisible(False)
        self._form.scaledOgiveDiameterInput.setVisible(False)

        self._form.scaledBluntedDiameterLabel.setVisible(False)
        self._form.scaledBluntedDiameterInput.setVisible(False)

        self._form.scaledRootLabel.setVisible(False)
        self._form.scaledRootInput.setVisible(False)

        self._form.scaledRootThicknessLabel.setVisible(False)
        self._form.scaledRootThicknessInput.setVisible(False)

        self._form.scaledTipLabel.setVisible(False)
        self._form.scaledTipInput.setVisible(False)

        self._form.scaledTipThicknessLabel.setVisible(False)
        self._form.scaledTipThicknessInput.setVisible(False)

        self._form.scaledHeightLabel.setVisible(False)
        self._form.scaledHeightInput.setVisible(False)

    def _setConnections(self) -> None:
        self._form.scalingGroup.toggled.connect(self.onScalingGroup)
        self._form.scaleOverrideCheckbox.stateChanged.connect(self.onOverride)
        self._form.upscaleCheckbox.stateChanged.connect(self.onUpscale)
        self._form.scaleInput.textEdited.connect(self.onScaleValue)

    def _setScaleState(self) -> None:
        super()._setScaleState()

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
