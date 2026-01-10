# SPDX-License-Identifier: LGPL-2.1-or-later

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
"""Class for drawing transitions"""

__title__ = "FreeCAD Transitions"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import os

import FreeCAD
import FreeCADGui
import Materials

from PySide import QtGui, QtCore
from PySide.QtWidgets import QDialog, QGridLayout, QVBoxLayout, QSizePolicy

translate = FreeCAD.Qt.translate

from Ui.TaskPanelDatabase import TaskPanelDatabase
from Ui.Widgets.MaterialTab import MaterialTab
from Ui.Widgets.CommentTab import CommentTab
from Ui.Widgets.ScalingTab import ScalingTabTransition
from Ui.UIPaths import getUIPath

from Rocket.Constants import TYPE_CONE, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_VON_KARMAN, \
    TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_POWER, TYPE_PROXY
from Rocket.Constants import STYLE_CAPPED, STYLE_HOLLOW, STYLE_SOLID, STYLE_SOLID_CORE
from Rocket.Constants import STYLE_CAP_SOLID, STYLE_CAP_BAR, STYLE_CAP_CROSS
from Rocket.Constants import COMPONENT_TYPE_TRANSITION

from Rocket.Utilities import _toFloat, _valueWithUnits, _err

class _TransitionDialog(QDialog):

    def __init__(self, obj, parent=None):
        super(_TransitionDialog, self).__init__(parent)

        self.form = FreeCADGui.PySideUic.loadUi(os.path.join(getUIPath(), 'Ui', "TaskPanelTransition.ui"))

        self.tabScaling = ScalingTabTransition(obj)
        self.tabMaterial = MaterialTab()
        self.tabComment = CommentTab()
        self.form.tabWidget.addTab(self.tabScaling.widget(), translate('Rocket', "Scaling"))
        self.form.tabWidget.addTab(self.tabMaterial, translate('Rocket', "Material"))
        self.form.tabWidget.addTab(self.tabComment, translate('Rocket', "Comment"))

        self.setTabGeneral()
        self.setTabShoulder()

    def setTabGeneral(self):

        # Select the type of transition
        self.form.transitionTypesCombo.addItem(translate('Rocket', TYPE_CONE), TYPE_CONE)
        self.form.transitionTypesCombo.addItem(translate('Rocket', TYPE_ELLIPTICAL), TYPE_ELLIPTICAL)
        self.form.transitionTypesCombo.addItem(translate('Rocket', TYPE_OGIVE), TYPE_OGIVE)
        self.form.transitionTypesCombo.addItem(translate('Rocket', TYPE_PARABOLA), TYPE_PARABOLA)
        self.form.transitionTypesCombo.addItem(translate('Rocket', TYPE_PARABOLIC), TYPE_PARABOLIC)
        self.form.transitionTypesCombo.addItem(translate('Rocket', TYPE_POWER), TYPE_POWER)
        self.form.transitionTypesCombo.addItem(translate('Rocket', TYPE_VON_KARMAN), TYPE_VON_KARMAN)
        self.form.transitionTypesCombo.addItem(translate('Rocket', TYPE_HAACK), TYPE_HAACK)
        self.form.transitionTypesCombo.addItem(translate('Rocket', TYPE_PROXY), TYPE_PROXY)

        self.coefficientValidator = QtGui.QDoubleValidator(self)
        self.coefficientValidator.setBottom(0.0)
        self.form.coefficientInput.setValidator(self.coefficientValidator)

        self.form.transitionStylesCombo.addItem(translate('Rocket', STYLE_SOLID), STYLE_SOLID)
        self.form.transitionStylesCombo.addItem(translate('Rocket', STYLE_SOLID_CORE), STYLE_SOLID_CORE)
        self.form.transitionStylesCombo.addItem(translate('Rocket', STYLE_HOLLOW), STYLE_HOLLOW)
        self.form.transitionStylesCombo.addItem(translate('Rocket', STYLE_CAPPED), STYLE_CAPPED)

        # Forward cap styles
        self.form.foreCapStylesCombo.addItem(translate('Rocket', STYLE_CAP_SOLID), STYLE_CAP_SOLID)
        self.form.foreCapStylesCombo.addItem(translate('Rocket', STYLE_CAP_BAR), STYLE_CAP_BAR)
        self.form.foreCapStylesCombo.addItem(translate('Rocket', STYLE_CAP_CROSS), STYLE_CAP_CROSS)

        # Aft cap styles
        self.form.aftCapStylesCombo.addItem(translate('Rocket', STYLE_CAP_SOLID), STYLE_CAP_SOLID)
        self.form.aftCapStylesCombo.addItem(translate('Rocket', STYLE_CAP_BAR), STYLE_CAP_BAR)
        self.form.aftCapStylesCombo.addItem(translate('Rocket', STYLE_CAP_CROSS), STYLE_CAP_CROSS)

        self.form.lengthInput.unit = FreeCAD.Units.Length
        self.form.foreDiameterInput.unit = FreeCAD.Units.Length
        self.form.aftDiameterInput.unit = FreeCAD.Units.Length
        self.form.coreDiameterInput.unit = FreeCAD.Units.Length
        self.form.thicknessInput.unit = FreeCAD.Units.Length
        self.form.foreCapBarWidthInput.unit = FreeCAD.Units.Length
        self.form.aftCapBarWidthInput.unit = FreeCAD.Units.Length

        # Proxy
        self.form.transitionProxyTypesCombo.addItem(translate('Rocket', TYPE_CONE), TYPE_CONE)
        self.form.transitionProxyTypesCombo.addItem(translate('Rocket', TYPE_ELLIPTICAL), TYPE_ELLIPTICAL)
        self.form.transitionProxyTypesCombo.addItem(translate('Rocket', TYPE_OGIVE), TYPE_OGIVE)
        self.form.transitionProxyTypesCombo.addItem(translate('Rocket', TYPE_PARABOLA), TYPE_PARABOLA)
        self.form.transitionProxyTypesCombo.addItem(translate('Rocket', TYPE_PARABOLIC), TYPE_PARABOLIC)
        self.form.transitionProxyTypesCombo.addItem(translate('Rocket', TYPE_POWER), TYPE_POWER)
        self.form.transitionProxyTypesCombo.addItem(translate('Rocket', TYPE_VON_KARMAN), TYPE_VON_KARMAN)
        self.form.transitionProxyTypesCombo.addItem(translate('Rocket', TYPE_HAACK), TYPE_HAACK)
        self.form.transitionProxyTypesCombo.addItem(translate('Rocket', TYPE_PROXY), TYPE_PROXY)

        self.form.proxyForeEffectiveDiameterInput.unit = FreeCAD.Units.Length
        self.form.proxyAftEffectiveDiameterInput.unit = FreeCAD.Units.Length
        self.form.xRotationInput.unit = FreeCAD.Units.Angle
        self.form.yRotationInput.unit = FreeCAD.Units.Angle
        self.form.zRotationInput.unit = FreeCAD.Units.Angle
        self.form.foreOffsetInput.unit = FreeCAD.Units.Length
        self.form.aftOffsetInput.unit = FreeCAD.Units.Length

        self.form.proxyShowForeBasePlaneCheckbox.setVisible(False) # Not yet supported
        self.form.proxyShowAftBasePlaneCheckbox.setVisible(False)

    def setTabShoulder(self):
        self.form.foreShoulderDiameterInput.unit = FreeCAD.Units.Length
        self.form.foreShoulderLengthInput.unit = FreeCAD.Units.Length
        self.form.foreShoulderThicknessInput.unit = FreeCAD.Units.Length
        self.form.aftShoulderDiameterInput.unit = FreeCAD.Units.Length
        self.form.aftShoulderLengthInput.unit = FreeCAD.Units.Length
        self.form.aftShoulderThicknessInput.unit = FreeCAD.Units.Length

class TaskPanelTransition:

    def __init__(self,obj,mode):
        self._obj = obj
        self._isAssembly = self._obj.Proxy.isRocketAssembly()

        # Used to prevent recursion
        self._updateTransitionType = True

        self._tranForm = _TransitionDialog(obj)
        self._db = TaskPanelDatabase(obj, COMPONENT_TYPE_TRANSITION)
        self._dbForm = self._db.getForm()

        self.form = [self._tranForm.form, self._dbForm]
        self._tranForm.form.setWindowIcon(QtGui.QIcon(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Transition.svg"))

        self._tranForm.form.transitionTypesCombo.currentTextChanged.connect(self.onTransitionType)
        self._tranForm.form.transitionProxyTypesCombo.currentTextChanged.connect(self.onTransitionType)
        self._tranForm.form.transitionStylesCombo.currentTextChanged.connect(self.onTransitionStyle)
        self._tranForm.form.foreCapStylesCombo.currentTextChanged.connect(self.onForeCapStyle)
        self._tranForm.form.foreCapBarWidthInput.textEdited.connect(self.onForeBarWidth)
        self._tranForm.form.aftCapStylesCombo.currentTextChanged.connect(self.onAftCapStyle)
        self._tranForm.form.aftCapBarWidthInput.textEdited.connect(self.onAftBarWidth)
        self._tranForm.form.lengthInput.textEdited.connect(self.onLength)
        self._tranForm.form.foreDiameterInput.textEdited.connect(self.onForeDiameter)
        self._tranForm.form.foreAutoDiameterCheckbox.stateChanged.connect(self.onForeAutoDiameter)
        self._tranForm.form.aftDiameterInput.textEdited.connect(self.onAftDiameter)
        self._tranForm.form.aftAutoDiameterCheckbox.stateChanged.connect(self.onAftAutoDiameter)
        self._tranForm.form.coreDiameterInput.textEdited.connect(self.onCoreDiameter)
        self._tranForm.form.thicknessInput.textEdited.connect(self.onThickness)
        self._tranForm.form.coefficientInput.textEdited.connect(self.onCoefficient)
        self._tranForm.form.clippedCheckbox.stateChanged.connect(self.onClipped)
        self._tranForm.form.foreGroup.toggled.connect(self.onForeShoulder)
        self._tranForm.form.foreShoulderDiameterInput.textEdited.connect(self.onForeShoulderDiameter)
        self._tranForm.form.foreShoulderAutoDiameterCheckbox.stateChanged.connect(self.onForeShoulderAutoDiameter)
        self._tranForm.form.foreShoulderLengthInput.textEdited.connect(self.onForeShoulderLength)
        self._tranForm.form.foreShoulderThicknessInput.textEdited.connect(self.onForeShoulderThickness)
        self._tranForm.form.aftGroup.toggled.connect(self.onAftShoulder)
        self._tranForm.form.aftShoulderDiameterInput.textEdited.connect(self.onAftShoulderDiameter)
        self._tranForm.form.aftShoulderAutoDiameterCheckbox.stateChanged.connect(self.onAftShoulderAutoDiameter)
        self._tranForm.form.aftShoulderLengthInput.textEdited.connect(self.onAftShoulderLength)
        self._tranForm.form.aftShoulderThicknessInput.textEdited.connect(self.onAftShoulderThickness)

        self._tranForm.form.proxyBaseObjectButton.clicked.connect(self.onSelect)
        self._tranForm.form.proxyForeEffectiveDiameterInput.textEdited.connect(self.onForeEffectiveDiameter)
        self._tranForm.form.proxyAftEffectiveDiameterInput.textEdited.connect(self.onAftEffectiveDiameter)
        self._tranForm.form.xRotationInput.textEdited.connect(self.onRotation)
        self._tranForm.form.yRotationInput.textEdited.connect(self.onRotation)
        self._tranForm.form.zRotationInput.textEdited.connect(self.onRotation)
        self._tranForm.form.foreOffsetInput.textEdited.connect(self.onForeOffset)
        self._tranForm.form.aftOffsetInput.textEdited.connect(self.onAftOffset)

        self._tranForm.tabScaling.scaled.connect(self.onScale)

        self._db.dbLoad.connect(self.onLookup)

        self.update()

        if mode == 0: # fresh created
            self._obj.Proxy.execute(self._obj)  # calculate once
            FreeCAD.Gui.SendMsgToActiveView("ViewFit")

    def transferTo(self):
        "Transfer from the dialog to the object"
        if self._obj.TransitionType == TYPE_PROXY:
            self._obj.TransitionType = str(self._tranForm.form.transitionProxyTypesCombo.currentData())
            self._obj.Proxy.setForeDiameter(FreeCAD.Units.Quantity(self._tranForm.form.proxyAftEffectiveDiameterInput.text()).Value)
            self._obj.Proxy.setForeDiameter(FreeCAD.Units.Quantity(self._tranForm.form.proxyForeEffectiveDiameterInput.text()).Value)
            self._obj.Proxy.setAftDiameter(FreeCAD.Units.Quantity(self._tranForm.form.proxyAftEffectiveDiameterInput.text()).Value)
        else:
            self._obj.TransitionType = str(self._tranForm.form.transitionTypesCombo.currentData())
            self._obj.Proxy.setForeDiameter(FreeCAD.Units.Quantity(self._tranForm.form.foreDiameterInput.text()).Value)
            self._obj.Proxy.setAftDiameter(FreeCAD.Units.Quantity(self._tranForm.form.aftDiameterInput.text()).Value)
        self._obj.TransitionStyle = str(self._tranForm.form.transitionStylesCombo.currentData())
        self._obj.ForeCapStyle = str(self._tranForm.form.foreCapStylesCombo.currentData())
        self._obj.ForeCapBarWidth = self._tranForm.form.foreCapBarWidthInput.text()
        self._obj.AftCapStyle = str(self._tranForm.form.aftCapStylesCombo.currentData())
        self._obj.AftCapBarWidth = self._tranForm.form.aftCapBarWidthInput.text()
        self._obj.Length = self._tranForm.form.lengthInput.text()
        self._obj.ForeDiameter = self._tranForm.form.foreDiameterInput.text()
        self._obj.ForeAutoDiameter = self._tranForm.form.foreAutoDiameterCheckbox.isChecked()
        self._obj.AftDiameter = self._tranForm.form.aftDiameterInput.text()
        self._obj.AftAutoDiameter = self._tranForm.form.aftAutoDiameterCheckbox.isChecked()
        self._obj.CoreDiameter = self._tranForm.form.coreDiameterInput.text()
        self._obj.Thickness = self._tranForm.form.thicknessInput.text()
        self._obj.Coefficient = _toFloat(self._tranForm.form.coefficientInput.text())
        self._obj.Clipped = self._tranForm.form.clippedCheckbox.isChecked()
        self._obj.ForeShoulder = self._tranForm.form.foreGroup.isChecked()
        self._obj.ForeShoulderDiameter = self._tranForm.form.foreShoulderDiameterInput.text()
        self._obj.ForeShoulderAutoDiameter = self._tranForm.form.foreShoulderAutoDiameterCheckbox.isChecked()
        self._obj.ForeShoulderLength =self._tranForm.form.foreShoulderLengthInput.text()
        self._obj.ForeShoulderThickness = self._tranForm.form.foreShoulderThicknessInput.text()
        self._obj.AftShoulder = self._tranForm.form.aftGroup.isChecked()
        self._obj.AftShoulderDiameter = self._tranForm.form.aftShoulderDiameterInput.text()
        self._obj.AftShoulderAutoDiameter = self._tranForm.form.aftShoulderAutoDiameterCheckbox.isChecked()
        self._obj.AftShoulderLength = self._tranForm.form.aftShoulderLengthInput.text()
        self._obj.AftShoulderThickness = self._tranForm.form.aftShoulderThicknessInput.text()

        placement = FreeCAD.Placement()
        yaw = FreeCAD.Units.Quantity(self._tranForm.form.zRotationInput.text()).Value
        pitch = FreeCAD.Units.Quantity(self._tranForm.form.yRotationInput.text()).Value
        roll = FreeCAD.Units.Quantity(self._tranForm.form.xRotationInput.text()).Value
        placement.Rotation.setYawPitchRoll(yaw, pitch, roll)
        placement.Base.x = FreeCAD.Units.Quantity(self._tranForm.form.foreOffsetInput.text()).Value
        self._obj.ProxyPlacement = placement
        self._obj.ProxyAftOffset = FreeCAD.Units.Quantity(self._tranForm.form.aftOffsetInput.text())

        self._tranForm.tabScaling.transferTo(self._obj)
        self._tranForm.tabMaterial.transferTo(self._obj)
        self._tranForm.tabComment.transferTo(self._obj)

    def transferFrom(self):
        "Transfer from the object to the dialog"
        self._tranForm.form.transitionTypesCombo.setCurrentIndex(self._tranForm.form.transitionTypesCombo.findData(self._obj.TransitionType))
        self._tranForm.form.transitionProxyTypesCombo.setCurrentIndex(self._tranForm.form.transitionProxyTypesCombo.findData(self._obj.TransitionType))
        self._tranForm.form.transitionStylesCombo.setCurrentIndex(self._tranForm.form.transitionStylesCombo.findData(self._obj.TransitionStyle))
        self._tranForm.form.foreCapStylesCombo.setCurrentIndex(self._tranForm.form.foreCapStylesCombo.findData(self._obj.ForeCapStyle))
        self._tranForm.form.foreCapBarWidthInput.setText(self._obj.ForeCapBarWidth.UserString)
        self._tranForm.form.aftCapStylesCombo.setCurrentIndex(self._tranForm.form.aftCapStylesCombo.findData(self._obj.AftCapStyle))
        self._tranForm.form.aftCapBarWidthInput.setText(self._obj.AftCapBarWidth.UserString)
        self._tranForm.form.lengthInput.setText(self._obj.Length.UserString)
        self._tranForm.form.foreDiameterInput.setText(self._obj.ForeDiameter.UserString)
        self._tranForm.form.foreAutoDiameterCheckbox.setChecked(self._obj.ForeAutoDiameter)
        self._tranForm.form.aftDiameterInput.setText(self._obj.AftDiameter.UserString)
        self._tranForm.form.aftAutoDiameterCheckbox.setChecked(self._obj.AftAutoDiameter)
        self._tranForm.form.coreDiameterInput.setText(self._obj.CoreDiameter.UserString)
        self._tranForm.form.thicknessInput.setText(self._obj.Thickness.UserString)
        self._tranForm.form.coefficientInput.setText("%f" % self._obj.Coefficient)
        self._tranForm.form.clippedCheckbox.setChecked(self._obj.Clipped)
        self._tranForm.form.foreGroup.setChecked(self._obj.ForeShoulder)
        self._tranForm.form.foreShoulderDiameterInput.setText(self._obj.ForeShoulderDiameter.UserString)
        self._tranForm.form.foreShoulderAutoDiameterCheckbox.setChecked(self._obj.ForeShoulderAutoDiameter)
        self._tranForm.form.foreShoulderLengthInput.setText(self._obj.ForeShoulderLength.UserString)
        self._tranForm.form.foreShoulderThicknessInput.setText(self._obj.ForeShoulderThickness.UserString)
        self._tranForm.form.aftGroup.setChecked(self._obj.AftShoulder)
        self._tranForm.form.aftShoulderDiameterInput.setText(self._obj.AftShoulderDiameter.UserString)
        self._tranForm.form.aftShoulderAutoDiameterCheckbox.setChecked(self._obj.AftShoulderAutoDiameter)
        self._tranForm.form.aftShoulderLengthInput.setText(self._obj.AftShoulderLength.UserString)
        self._tranForm.form.aftShoulderThicknessInput.setText(self._obj.AftShoulderThickness.UserString)

        if self._obj.Base:
            self._tranForm.form.proxyBaseObjectInput.setText(self._obj.Base.Label)
        else:
            self._tranForm.form.proxyBaseObjectInput.setText("")
        self._tranForm.form.proxyForeEffectiveDiameterInput.setText(self._obj.ForeDiameter.UserString)
        self._tranForm.form.proxyAftEffectiveDiameterInput.setText(self._obj.AftDiameter.UserString)

        placement = self._obj.ProxyPlacement
        yaw, pitch, roll = placement.Rotation.getYawPitchRoll()
        self._tranForm.form.xRotationInput.setText(f"{roll} deg")
        self._tranForm.form.yRotationInput.setText(f"{pitch} deg")
        self._tranForm.form.zRotationInput.setText(f"{yaw} deg")
        self._tranForm.form.foreOffsetInput.setText(FreeCAD.Units.Quantity(placement.Base.x, FreeCAD.Units.Length).UserString)
        self._tranForm.form.aftOffsetInput.setText(self._obj.ProxyAftOffset.UserString)

        self._tranForm.tabScaling.transferFrom(self._obj)
        self._tranForm.tabMaterial.transferFrom(self._obj)
        self._tranForm.tabComment.transferFrom(self._obj)

        self._setForeAutoDiameterState()
        self._setAftAutoDiameterState()
        self._setForeShoulderAutoDiameterState()
        self._setAftShoulderAutoDiameterState()
        self._showTransitionType()
        self._showClippable()
        self._showTransitionStyle()

    def setEdited(self):
        try:
            self._obj.Proxy.setEdited()
        except ReferenceError:
            # Object may be deleted
            pass

    def _showClippable(self):
        if str(self._obj.TransitionType) in [TYPE_CONE, TYPE_OGIVE]:
            # These types aren't clippable
            self._obj.Clipped = False
            self._tranForm.form.clippedCheckbox.setChecked(self._obj.Clipped)
            self._tranForm.form.clippedCheckbox.setEnabled(False)
        else:
            self._tranForm.form.clippedCheckbox.setEnabled(True)

    def _setProxyStateVisible(self, visible):
        if visible:
            index = 0
        else:
            index = 1
        self._tranForm.form.stackedWidget.setCurrentIndex(index)

    def _setProxyState(self):
        self._setProxyStateVisible(self._obj.TransitionType != TYPE_PROXY)
        # # Hide the shoulder tab
        # self._tranForm.form.tabWidget.setTabVisible(1, self._obj.TransitionType != TYPE_PROXY)

        self._updateTransitionType = False
        self._tranForm.form.transitionTypesCombo.setCurrentIndex(self._tranForm.form.transitionTypesCombo.findData(self._obj.TransitionType))
        self._tranForm.form.transitionProxyTypesCombo.setCurrentIndex(self._tranForm.form.transitionProxyTypesCombo.findData(self._obj.TransitionType))
        self._updateTransitionType = True

    def _showTransitionType(self):
        self._setProxyState()
        value = self._obj.TransitionType
        if value == TYPE_HAACK or value == TYPE_PARABOLIC:
            self._tranForm.form.coefficientInput.setEnabled(True)
        elif value == TYPE_POWER:
            self._tranForm.form.coefficientInput.setEnabled(True)
        elif value == TYPE_PARABOLA:
            # Set the coefficient, but don't enable it
            self._obj.Coefficient = 0.5
            self._tranForm.form.coefficientInput.setText("%f" % self._obj.Coefficient)
            self._tranForm.form.coefficientInput.setEnabled(False)
        elif value == TYPE_VON_KARMAN:
            # Set the coefficient, but don't enable it
            self._obj.Coefficient = 0.0
            self._tranForm.form.coefficientInput.setText("%f" % self._obj.Coefficient)
            self._tranForm.form.coefficientInput.setEnabled(False)
        elif value == TYPE_PROXY:
            self._tranForm.form.coefficientInput.setEnabled(False)
        else:
            self._tranForm.form.coefficientInput.setEnabled(False)

        # Scaling information is transition cone type dependent
        self.onScale()

    def onScale(self) -> None:
        # Update the scale values
        scale = self._tranForm.tabScaling.getScale()
        length = self._obj.Length / scale
        if scale < 1.0:
            self._tranForm.tabScaling._form.scaledLabel.setText(translate('Rocket', "Upscale"))
            self._tranForm.tabScaling._form.scaledInput.setText(f"{1.0/scale}")
        else:
            self._tranForm.tabScaling._form.scaledLabel.setText(translate('Rocket', "Scale"))
            self._tranForm.tabScaling._form.scaledInput.setText(f"{scale}")
        self._tranForm.tabScaling._form.scaledLengthInput.setText(length.UserString)

        diameter = self._obj.Proxy.getForeDiameter() / scale
        diameter = FreeCAD.Units.Quantity(f"{diameter} mm")
        self._tranForm.tabScaling._form.scaledDiameterInput.setText(diameter.UserString)

        diameter = self._obj.Proxy.getAftDiameter() / scale
        diameter = FreeCAD.Units.Quantity(f"{diameter} mm")
        self._tranForm.tabScaling._form.scaledAftDiameterInput.setText(diameter.UserString)
        self._tranForm.tabScaling._form.scaledAftDiameterLabel.setVisible(True)
        self._tranForm.tabScaling._form.scaledAftDiameterInput.setVisible(True)

        self._tranForm.tabScaling._form.scaleForeRadio.setVisible(True)
        self._tranForm.tabScaling._form.scaleAftRadio.setVisible(True)

    def onTransitionType(self, value):
        if self._updateTransitionType:
            self._obj.TransitionType = value

            self._showTransitionType()
            self._showClippable()

            self._obj.Proxy.execute(self._obj)
            self.setEdited()

    def _showTransitionStyle(self):
        value = self._obj.TransitionStyle
        if value == STYLE_HOLLOW or value == STYLE_CAPPED:
            self._tranForm.form.thicknessInput.setEnabled(True)
            self._tranForm.form.coreDiameterInput.setEnabled(False)

            if self._tranForm.form.foreGroup.isChecked():
                self._tranForm.form.foreShoulderThicknessInput.setEnabled(True)
            else:
                self._tranForm.form.foreShoulderThicknessInput.setEnabled(False)

            if self._tranForm.form.aftGroup.isChecked():
                self._tranForm.form.aftShoulderThicknessInput.setEnabled(True)
            else:
                self._tranForm.form.aftShoulderThicknessInput.setEnabled(False)

            if value == STYLE_CAPPED:
                self._tranForm.form.foreCapGroup.setEnabled(True)
                self._tranForm.form.aftCapGroup.setEnabled(True)
                self._setForeCapStyleState()
                self._setAftCapStyleState()
            else:
                self._tranForm.form.foreCapGroup.setEnabled(False)
                self._tranForm.form.aftCapGroup.setEnabled(False)
        elif value == STYLE_SOLID_CORE:
            self._tranForm.form.thicknessInput.setEnabled(False)
            self._tranForm.form.coreDiameterInput.setEnabled(True)

            self._tranForm.form.foreShoulderThicknessInput.setEnabled(False)
            self._tranForm.form.aftShoulderThicknessInput.setEnabled(False)
            self._tranForm.form.foreCapGroup.setEnabled(False)
            self._tranForm.form.aftCapGroup.setEnabled(False)
        else:
            self._tranForm.form.thicknessInput.setEnabled(False)
            self._tranForm.form.coreDiameterInput.setEnabled(False)

            self._tranForm.form.foreShoulderThicknessInput.setEnabled(False)
            self._tranForm.form.aftShoulderThicknessInput.setEnabled(False)
            self._tranForm.form.foreCapGroup.setEnabled(False)
            self._tranForm.form.aftCapGroup.setEnabled(False)

    def _setForeCapStyleState(self):
        value = self._obj.ForeCapStyle
        if value == STYLE_CAP_SOLID:
            self._tranForm.form.foreCapBarWidthInput.setEnabled(False)
        else:
            self._tranForm.form.foreCapBarWidthInput.setEnabled(True)

    def _setAftCapStyleState(self):
        value = self._obj.AftCapStyle
        if value == STYLE_CAP_SOLID:
            self._tranForm.form.aftCapBarWidthInput.setEnabled(False)
        else:
            self._tranForm.form.aftCapBarWidthInput.setEnabled(True)

    def onTransitionStyle(self, value):
        self._obj.TransitionStyle = value

        self._showTransitionStyle()
        self._obj.Proxy.execute(self._obj)
        self.setEdited()

    def onForeCapStyle(self, value):
        self._obj.ForeCapStyle = value
        self._setForeCapStyleState()

        self._obj.Proxy.execute(self._obj)

    def onForeBarWidth(self, value):
        try:
            self._obj.ForeCapBarWidth = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass

    def onAftCapStyle(self, value):
        self._obj.AftCapStyle = value
        self._setAftCapStyleState()

        self._obj.Proxy.execute(self._obj)

    def onAftBarWidth(self, value):
        try:
            self._obj.AftCapBarWidth = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass

    def onLength(self, value):
        try:
            self._obj.Length = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def onForeDiameter(self, value):
        try:
            self._obj.ForeDiameter = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def _setForeAutoDiameterState(self):
        if self._isAssembly:
            self._tranForm.form.foreDiameterInput.setEnabled(not self._obj.ForeAutoDiameter)
            self._tranForm.form.foreAutoDiameterCheckbox.setEnabled(True)
        else:
            self._tranForm.form.foreDiameterInput.setEnabled(True)
            self._obj.ForeAutoDiameter = False
            self._tranForm.form.foreAutoDiameterCheckbox.setEnabled(False)
        self._tranForm.form.foreAutoDiameterCheckbox.setChecked(self._obj.ForeAutoDiameter)

        if self._obj.ForeAutoDiameter:
            self._obj.ForeDiameter = self._obj.Proxy.getForeDiameter()
            self._tranForm.form.foreDiameterInput.setText(self._obj.ForeDiameter.UserString)

    def onForeAutoDiameter(self, value):
        self._obj.ForeAutoDiameter = self._tranForm.form.foreAutoDiameterCheckbox.isChecked()
        self._setForeAutoDiameterState()

        self._obj.Proxy.execute(self._obj)
        self.setEdited()

    def onAftDiameter(self, value):
        try:
            self._obj.AftDiameter = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def _setAftAutoDiameterState(self):
        if self._isAssembly:
            self._tranForm.form.aftDiameterInput.setEnabled(not self._obj.AftAutoDiameter)
            self._tranForm.form.aftAutoDiameterCheckbox.setEnabled(True)
        else:
            self._tranForm.form.aftDiameterInput.setEnabled(True)
            self._obj.AftAutoDiameter = False
            self._tranForm.form.aftAutoDiameterCheckbox.setEnabled(False)
        self._tranForm.form.aftAutoDiameterCheckbox.setChecked(self._obj.AftAutoDiameter)

        if self._obj.AftAutoDiameter:
            self._obj.AftDiameter = self._obj.Proxy.getAftDiameter()
            self._tranForm.form.aftDiameterInput.setText(self._obj.AftDiameter.UserString)

    def onAftAutoDiameter(self, value):
        self._obj.AftAutoDiameter = self._tranForm.form.aftAutoDiameterCheckbox.isChecked()
        self._setAftAutoDiameterState()

        self._obj.Proxy.execute(self._obj)
        self.setEdited()

    def onCoreDiameter(self, value):
        try:
            self._obj.CoreDiameter = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def onThickness(self, value):
        try:
            self._obj.Thickness = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def onCoefficient(self, value):
        self._obj.Coefficient = _toFloat(value)
        self._obj.Proxy.execute(self._obj)
        self.setEdited()

    def onClipped(self, value):
        self._obj.Clipped = self._tranForm.form.clippedCheckbox.isChecked()
        self._obj.Proxy.execute(self._obj)
        self.setEdited()

    def onForeShoulder(self, value):
        self._obj.ForeShoulder = self._tranForm.form.foreGroup.isChecked()
        if self._obj.ForeShoulder:
            self._tranForm.form.foreShoulderDiameterInput.setEnabled(True)
            self._tranForm.form.foreShoulderLengthInput.setEnabled(True)

            selectedText = self._tranForm.form.transitionStylesCombo.currentData()
            if selectedText == STYLE_HOLLOW or selectedText == STYLE_CAPPED:
                self._tranForm.form.foreShoulderThicknessInput.setEnabled(True)
            else:
                self._tranForm.form.foreShoulderThicknessInput.setEnabled(False)
        else:
            self._tranForm.form.foreShoulderDiameterInput.setEnabled(False)
            self._tranForm.form.foreShoulderLengthInput.setEnabled(False)
            self._tranForm.form.foreShoulderThicknessInput.setEnabled(False)

        self._obj.Proxy.execute(self._obj)
        self.setEdited()

    def onForeShoulderDiameter(self, value):
        try:
            self._obj.ForeShoulderDiameter = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def _setForeShoulderAutoDiameterState(self):
        if self._isAssembly:
            self._tranForm.form.foreShoulderDiameterInput.setEnabled(not self._obj.ForeShoulderAutoDiameter)
            self._tranForm.form.foreShoulderAutoDiameterCheckbox.setEnabled(True)
        else:
            self._tranForm.form.foreShoulderDiameterInput.setEnabled(True)
            self._obj.ForeShoulderAutoDiameter = False
            self._tranForm.form.foreShoulderAutoDiameterCheckbox.setEnabled(False)
        self._tranForm.form.foreShoulderAutoDiameterCheckbox.setChecked(self._obj.ForeShoulderAutoDiameter)

        if self._obj.ForeShoulderAutoDiameter:
            self._obj.ForeShoulderDiameter = self._obj.Proxy.getForeShoulderDiameter()
            self._tranForm.form.foreShoulderDiameterInput.setText(self._obj.ForeShoulderDiameter.UserString)

    def onForeShoulderAutoDiameter(self, value):
        self._obj.ForeShoulderAutoDiameter = self._tranForm.form.foreShoulderAutoDiameterCheckbox.isChecked()
        self._setForeShoulderAutoDiameterState()

        self._obj.Proxy.execute(self._obj)
        self.setEdited()

    def onForeShoulderLength(self, value):
        try:
            self._obj.ForeShoulderLength = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def onForeShoulderThickness(self, value):
        try:
            self._obj.ForeShoulderThickness = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def onAftShoulder(self, value):
        self._obj.AftShoulder = self._tranForm.form.aftGroup.isChecked()
        if self._obj.AftShoulder:
            self._tranForm.form.aftShoulderDiameterInput.setEnabled(True)
            self._tranForm.form.aftShoulderLengthInput.setEnabled(True)

            selectedText = self._tranForm.form.transitionStylesCombo.currentData()
            if selectedText == STYLE_HOLLOW or selectedText == STYLE_CAPPED:
                self._tranForm.form.aftShoulderThicknessInput.setEnabled(True)
            else:
                self._tranForm.form.aftShoulderThicknessInput.setEnabled(False)
        else:
            self._tranForm.form.aftShoulderDiameterInput.setEnabled(False)
            self._tranForm.form.aftShoulderLengthInput.setEnabled(False)
            self._tranForm.form.aftShoulderThicknessInput.setEnabled(False)

        self._obj.Proxy.execute(self._obj)
        self.setEdited()

    def onAftShoulderDiameter(self, value):
        try:
            self._obj.AftShoulderDiameter = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def _setAftShoulderAutoDiameterState(self):
        if self._isAssembly:
            self._tranForm.form.aftShoulderDiameterInput.setEnabled(not self._obj.AftShoulderAutoDiameter)
            self._tranForm.form.aftShoulderAutoDiameterCheckbox.setEnabled(True)
        else:
            self._tranForm.form.aftShoulderDiameterInput.setEnabled(True)
            self._obj.AftShoulderAutoDiameter = False
            self._tranForm.form.aftShoulderAutoDiameterCheckbox.setEnabled(False)
        self._tranForm.form.aftShoulderAutoDiameterCheckbox.setChecked(self._obj.AftShoulderAutoDiameter)

        if self._obj.AftShoulderAutoDiameter:
            self._obj.AftShoulderDiameter = self._obj.Proxy.getAftShoulderDiameter()
            self._tranForm.form.aftShoulderDiameterInput.setText(self._obj.AftShoulderDiameter.UserString)

    def onAftShoulderAutoDiameter(self, value):
        self._obj.AftShoulderAutoDiameter = self._tranForm.form.aftShoulderAutoDiameterCheckbox.isChecked()
        self._setAftShoulderAutoDiameterState()

        self._obj.Proxy.execute(self._obj)
        self.setEdited()

    def onAftShoulderLength(self, value):
        try:
            self._obj.AftShoulderLength = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def onAftShoulderThickness(self, value):
        try:
            self._obj.AftShoulderThickness = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def onLookup(self):
        result = self._db.getLookupResult()

        self._obj.TransitionType = str(result["shape"])
        self._obj.TransitionStyle = str(result["style"])
        self._obj.Length = _valueWithUnits(result["length"], result["length_units"])
        self._obj.ForeDiameter = _valueWithUnits(result["fore_outside_diameter"], result["fore_outside_diameter_units"])
        self._obj.AftDiameter = _valueWithUnits(result["aft_outside_diameter"], result["aft_outside_diameter_units"])
        self._obj.CoreDiameter = 0.0
        self._obj.Thickness = _valueWithUnits(result["thickness"], result["thickness_units"])
        self._obj.Coefficient = 0.0
        self._obj.Clipped = True
        self._obj.ForeShoulderDiameter = _valueWithUnits(result["fore_shoulder_diameter"], result["fore_shoulder_diameter_units"])
        self._obj.ForeShoulderLength = _valueWithUnits(result["fore_shoulder_length"], result["fore_shoulder_length_units"])
        self._obj.ForeShoulderThickness = self._obj.Thickness
        self._obj.AftShoulderDiameter = _valueWithUnits(result["aft_shoulder_diameter"], result["aft_shoulder_diameter_units"])
        self._obj.AftShoulderLength = _valueWithUnits(result["aft_shoulder_length"], result["aft_shoulder_length_units"])
        self._obj.AftShoulderThickness = self._obj.Thickness
        try:
            self._obj.ShapeMaterial = Materials.MaterialManager().getMaterial(result["uuid"])
        except LookupError:
            # Use the default
            _err(translate('Rocket', "Unable to find material '{}'").format(result["uuid"]))

        self._obj.ForeShoulder = (self._obj.ForeShoulderDiameter > 0.0) and (self._obj.ForeShoulderLength >= 0)
        self._obj.AftShoulder = (self._obj.AftShoulderDiameter > 0.0) and (self._obj.AftShoulderLength >= 0)

        self.update()
        self._obj.Proxy.execute(self._obj)
        self.setEdited()

    def onSelect(self):
        # FreeCADGui.Control.closeDialog()
        # FreeCADGui.Control.showDialog(TaskPanelSelection())
        FreeCAD.RocketObserver = self
        FreeCADGui.Selection.addObserver(FreeCAD.RocketObserver)

        self._tranForm.form.proxyBaseObjectLabelSelect.setText(translate('Rocket', 'Select an object'))

    def addSelection(self,document, object, element, position):
        """Method called when a selection is made on the Gui.

        Parameters
        ----------
        document: str
            The document's Name.
        object: str
            The selected object's Name.
        element: str
            The element on the object that was selected, such as an edge or
            face.
        position:
            The location in XYZ space the selection was made.
        """

        FreeCADGui.Selection.removeObserver(FreeCAD.RocketObserver)

        try:
            obj = FreeCAD.getDocument(document).getObject(object)
            self._obj.Base = obj
            self._tranForm.form.proxyBaseObjectInput.setText(obj.Label)
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass

        self._tranForm.form.proxyBaseObjectLabelSelect.setText("")
        del FreeCAD.RocketObserver

    def onForeEffectiveDiameter(self, value):
        try:
            self._obj.ForeDiameter = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def onAftEffectiveDiameter(self, value):
        try:
            self._obj.AftDiameter = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def onRotation(self, value):
        try:
            yaw = FreeCAD.Units.Quantity(self._tranForm.form.zRotationInput.text()).Value
            pitch = FreeCAD.Units.Quantity(self._tranForm.form.yRotationInput.text()).Value
            roll = FreeCAD.Units.Quantity(self._tranForm.form.xRotationInput.text()).Value
            self._obj.ProxyPlacement.Rotation.setYawPitchRoll(yaw, pitch, roll)
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def onForeOffset(self, value):
        try:
            self._obj.ProxyPlacement.Base.x = FreeCAD.Units.Quantity(self._tranForm.form.foreOffsetInput.text()).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def onAftOffset(self, value):
        try:
            self._obj.ProxyAftOffset = FreeCAD.Units.Quantity(self._tranForm.form.aftOffsetInput.text())
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

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
        FreeCAD.ActiveDocument.recompute()
