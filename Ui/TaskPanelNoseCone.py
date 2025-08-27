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
"""Class for drawing nose cones"""

__title__ = "FreeCAD Nose Cones"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from typing import Any
import os

import FreeCAD
import FreeCADGui
import Materials

from PySide import QtGui
from PySide.QtWidgets import QDialog, QVBoxLayout

from Rocket.Utilities import translate

from Ui.TaskPanelDatabase import TaskPanelDatabase
from Ui.Widgets.MaterialTab import MaterialTab
from Ui.Widgets.CommentTab import CommentTab
from Ui.Widgets.ScalingTab import ScalingTabNose
from Ui.UIPaths import getUIPath

from Rocket.Constants import TYPE_CONE, TYPE_BLUNTED_CONE, TYPE_SPHERICAL, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, \
    TYPE_BLUNTED_OGIVE, TYPE_SECANT_OGIVE, TYPE_VON_KARMAN, TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_POWER, TYPE_NIKE_SMOKE, \
    TYPE_PROXY
from Rocket.Constants import STYLE_CAPPED, STYLE_HOLLOW, STYLE_SOLID
from Rocket.Constants import STYLE_CAP_SOLID, STYLE_CAP_BAR, STYLE_CAP_CROSS
from Rocket.Constants import COMPONENT_TYPE_NOSECONE

from Rocket.Utilities import _toFloat, _valueWithUnits, _valueOnly, _err

class _NoseConeDialog(QDialog):

    def __init__(self, obj : Any, parent : QtGui.QWidget = None) -> None:
        super().__init__(parent)

        self.form = FreeCADGui.PySideUic.loadUi(os.path.join(getUIPath(), 'Ui', "TaskPanelNoseCone.ui"))

        self.tabScaling = ScalingTabNose(obj)
        self.tabMaterial = MaterialTab()
        self.tabComment = CommentTab()
        self.form.tabWidget.addTab(self.tabScaling, translate('Rocket', "Scaling"))
        self.form.tabWidget.addTab(self.tabMaterial, translate('Rocket', "Material"))
        self.form.tabWidget.addTab(self.tabComment, translate('Rocket', "Comment"))

        self.setTabGeneral()
        self.setTabShoulder()

    def setTabGeneral(self):
        # Select the type of nose cone
        self.form.noseConeTypesCombo.addItem(translate('Rocket', TYPE_CONE), TYPE_CONE)
        self.form.noseConeTypesCombo.addItem(translate('Rocket', TYPE_BLUNTED_CONE), TYPE_BLUNTED_CONE)
        self.form.noseConeTypesCombo.addItem(translate('Rocket', TYPE_SPHERICAL), TYPE_SPHERICAL)
        self.form.noseConeTypesCombo.addItem(translate('Rocket', TYPE_ELLIPTICAL), TYPE_ELLIPTICAL)
        self.form.noseConeTypesCombo.addItem(translate('Rocket', TYPE_OGIVE), TYPE_OGIVE)
        self.form.noseConeTypesCombo.addItem(translate('Rocket', TYPE_BLUNTED_OGIVE), TYPE_BLUNTED_OGIVE)
        self.form.noseConeTypesCombo.addItem(translate('Rocket', TYPE_SECANT_OGIVE), TYPE_SECANT_OGIVE)
        self.form.noseConeTypesCombo.addItem(translate('Rocket', TYPE_PARABOLA), TYPE_PARABOLA)
        self.form.noseConeTypesCombo.addItem(translate('Rocket', TYPE_PARABOLIC), TYPE_PARABOLIC)
        self.form.noseConeTypesCombo.addItem(translate('Rocket', TYPE_POWER), TYPE_POWER)
        self.form.noseConeTypesCombo.addItem(translate('Rocket', TYPE_VON_KARMAN), TYPE_VON_KARMAN)
        self.form.noseConeTypesCombo.addItem(translate('Rocket', TYPE_HAACK), TYPE_HAACK)
        # self.form.noseConeTypesCombo.addItem(translate('Rocket', TYPE_NIKE_SMOKE), TYPE_NIKE_SMOKE)
        self.form.noseConeTypesCombo.addItem(translate('Rocket', TYPE_PROXY), TYPE_PROXY)

        self.form.noseStylesCombo.addItem(translate('Rocket', STYLE_SOLID), STYLE_SOLID)
        self.form.noseStylesCombo.addItem(translate('Rocket', STYLE_HOLLOW), STYLE_HOLLOW)
        self.form.noseStylesCombo.addItem(translate('Rocket', STYLE_CAPPED), STYLE_CAPPED)

        self.form.noseCapStylesCombo.addItem(translate('Rocket', STYLE_CAP_SOLID), STYLE_CAP_SOLID)
        self.form.noseCapStylesCombo.addItem(translate('Rocket', STYLE_CAP_BAR), STYLE_CAP_BAR)
        self.form.noseCapStylesCombo.addItem(translate('Rocket', STYLE_CAP_CROSS), STYLE_CAP_CROSS)

        self.form.lengthInput.unit = FreeCAD.Units.Length
        self.form.diameterInput.unit = FreeCAD.Units.Length
        self.form.thicknessInput.unit = FreeCAD.Units.Length
        self.form.ogiveDiameterInput.unit = FreeCAD.Units.Length
        self.form.bluntedInput.unit = FreeCAD.Units.Length
        self.form.noseCapBarWidthInput.unit = FreeCAD.Units.Length

        self.coefficientValidator = QtGui.QDoubleValidator(self)
        self.coefficientValidator.setBottom(0.0)
        self.form.coefficientInput.setValidator(self.coefficientValidator)

        # Proxy
        self.form.noseConeProxyTypesCombo.addItem(translate('Rocket', TYPE_CONE), TYPE_CONE)
        self.form.noseConeProxyTypesCombo.addItem(translate('Rocket', TYPE_BLUNTED_CONE), TYPE_BLUNTED_CONE)
        self.form.noseConeProxyTypesCombo.addItem(translate('Rocket', TYPE_SPHERICAL), TYPE_SPHERICAL)
        self.form.noseConeProxyTypesCombo.addItem(translate('Rocket', TYPE_ELLIPTICAL), TYPE_ELLIPTICAL)
        self.form.noseConeProxyTypesCombo.addItem(translate('Rocket', TYPE_OGIVE), TYPE_OGIVE)
        self.form.noseConeProxyTypesCombo.addItem(translate('Rocket', TYPE_BLUNTED_OGIVE), TYPE_BLUNTED_OGIVE)
        self.form.noseConeProxyTypesCombo.addItem(translate('Rocket', TYPE_SECANT_OGIVE), TYPE_SECANT_OGIVE)
        self.form.noseConeProxyTypesCombo.addItem(translate('Rocket', TYPE_PARABOLA), TYPE_PARABOLA)
        self.form.noseConeProxyTypesCombo.addItem(translate('Rocket', TYPE_PARABOLIC), TYPE_PARABOLIC)
        self.form.noseConeProxyTypesCombo.addItem(translate('Rocket', TYPE_POWER), TYPE_POWER)
        self.form.noseConeProxyTypesCombo.addItem(translate('Rocket', TYPE_VON_KARMAN), TYPE_VON_KARMAN)
        self.form.noseConeProxyTypesCombo.addItem(translate('Rocket', TYPE_HAACK), TYPE_HAACK)
        self.form.noseConeProxyTypesCombo.addItem(translate('Rocket', TYPE_PROXY), TYPE_PROXY)

        self.form.proxyEffectiveDiameterInput.unit = FreeCAD.Units.Length
        self.form.xRotationInput.unit = FreeCAD.Units.Angle
        self.form.yRotationInput.unit = FreeCAD.Units.Angle
        self.form.zRotationInput.unit = FreeCAD.Units.Angle
        self.form.offsetInput.unit = FreeCAD.Units.Length

    def setTabShoulder(self):
        self.form.shoulderDiameterInput.unit = FreeCAD.Units.Length
        self.form.shoulderLengthInput.unit = FreeCAD.Units.Length
        self.form.shoulderThicknessInput.unit = FreeCAD.Units.Length

class TaskPanelNoseCone:

    def __init__(self,obj,mode):
        self._obj = obj
        self._isAssembly = self._obj.Proxy.isRocketAssembly()

        # Used to prevent recursion
        self._updateNoseType = True

        self._noseForm = _NoseConeDialog(obj)
        self._db = TaskPanelDatabase(obj, COMPONENT_TYPE_NOSECONE)
        self._dbForm = self._db.getForm()

        self.form = [self._noseForm.form, self._dbForm]
        self._noseForm.form.setWindowIcon(QtGui.QIcon(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_NoseCone.svg"))

        self._noseForm.form.noseConeTypesCombo.currentTextChanged.connect(self.onNoseType)
        self._noseForm.form.noseConeProxyTypesCombo.currentTextChanged.connect(self.onNoseType)
        self._noseForm.form.noseStylesCombo.currentTextChanged.connect(self.onNoseStyle)
        self._noseForm.form.noseCapStylesCombo.currentTextChanged.connect(self.onNoseCapStyle)
        self._noseForm.form.noseCapBarWidthInput.textEdited.connect(self.onBarWidthChanged)

        self._noseForm.form.lengthInput.textEdited.connect(self.onLength)
        self._noseForm.form.diameterInput.textEdited.connect(self.onDiameter)
        self._noseForm.form.autoDiameterCheckbox.stateChanged.connect(self.onAutoDiameter)
        self._noseForm.form.thicknessInput.textEdited.connect(self.onThickness)
        self._noseForm.form.coefficientInput.textEdited.connect(self.onCoefficient)
        self._noseForm.form.bluntedInput.textEdited.connect(self.onBlunted)
        self._noseForm.form.ogiveDiameterInput.textEdited.connect(self.onOgiveDiameter)

        self._noseForm.form.shoulderGroup.clicked.connect(self.onShoulder)
        self._noseForm.form.shoulderDiameterInput.textEdited.connect(self.onShoulderDiameter)
        self._noseForm.form.shoulderAutoDiameterCheckbox.stateChanged.connect(self.onShoulderAutoDiameter)
        self._noseForm.form.shoulderLengthInput.textEdited.connect(self.onShoulderLength)
        self._noseForm.form.shoulderThicknessInput.textEdited.connect(self.onShoulderThickness)

        self._noseForm.form.proxyBaseObjectButton.clicked.connect(self.onSelect)
        self._noseForm.form.proxyEffectiveDiameterInput.textEdited.connect(self.onEffectiveDiameter)
        self._noseForm.form.xRotationInput.textEdited.connect(self.onRotation)
        self._noseForm.form.yRotationInput.textEdited.connect(self.onRotation)
        self._noseForm.form.zRotationInput.textEdited.connect(self.onRotation)
        self._noseForm.form.offsetInput.textEdited.connect(self.onOffset)

        self._db.dbLoad.connect(self.onLookup)
        self._noseForm.tabScaling.scaled.connect(self.onScale)
        self._noseForm.tabScaling.scaledSetValuesButton.clicked.connect(self.onSetToScale)

        self.update()

        if mode == 0: # fresh created
            self._obj.Proxy.execute(self._obj)  # calculate once
            FreeCAD.Gui.SendMsgToActiveView("ViewFit")

    def transferTo(self):
        "Transfer from the dialog to the object"
        if self._obj.NoseType == TYPE_PROXY:
            self._obj.NoseType = str(self._noseForm.form.noseConeProxyTypesCombo.currentData())
            self._obj.Proxy.setAftDiameter(FreeCAD.Units.Quantity(self._noseForm.form.proxyEffectiveDiameterInput.text()).Value)
        else:
            self._obj.NoseType = str(self._noseForm.form.noseConeTypesCombo.currentData())
            self._obj.Proxy.setAftDiameter(FreeCAD.Units.Quantity(self._noseForm.form.diameterInput.text()).Value)
        self._obj.NoseStyle = str(self._noseForm.form.noseStylesCombo.currentData())
        self._obj.CapStyle = str(self._noseForm.form.noseCapStylesCombo.currentData())
        self._obj.CapBarWidth = self._noseForm.form.noseCapBarWidthInput.text()
        # self._noseForm.form.proxyBaseObjectInput.setText(object)
        self._obj.Proxy.setLength(FreeCAD.Units.Quantity(self._noseForm.form.lengthInput.text()).Value)
        self._obj.Proxy.setAftDiameterAutomatic(self._noseForm.form.autoDiameterCheckbox.isChecked())
        self._obj.Proxy.setThickness(FreeCAD.Units.Quantity(self._noseForm.form.thicknessInput.text()).Value)
        self._obj.Coefficient = _toFloat(self._noseForm.form.coefficientInput.text())
        self._obj.BluntedDiameter = self._noseForm.form.bluntedInput.text()
        self._obj.OgiveDiameter = self._noseForm.form.ogiveDiameterInput.text()
        self._obj.Shoulder = self._noseForm.form.shoulderGroup.isChecked()
        self._obj.ShoulderDiameter = self._noseForm.form.shoulderDiameterInput.text()
        self._obj.ShoulderAutoDiameter = self._noseForm.form.shoulderAutoDiameterCheckbox.isChecked()
        self._obj.ShoulderLength = self._noseForm.form.shoulderLengthInput.text()
        self._obj.ShoulderThickness = self._noseForm.form.shoulderThicknessInput.text()

        # if self._obj.Base is not None:
        #     self._noseForm.form.proxyBaseObjectInput.setText(self._obj.Base.Label)
        # else:
        #     self._noseForm.form.proxyBaseObjectInput.setText("")
        # self._obj.Diameter = self._noseForm.form.proxyEffectiveDiameterInput.text()

        placement = FreeCAD.Placement()
        yaw = FreeCAD.Units.Quantity(self._noseForm.form.zRotationInput.text()).Value
        pitch = FreeCAD.Units.Quantity(self._noseForm.form.yRotationInput.text()).Value
        roll = FreeCAD.Units.Quantity(self._noseForm.form.xRotationInput.text()).Value
        placement.Rotation.setYawPitchRoll(yaw, pitch, roll)
        placement.Base.x = FreeCAD.Units.Quantity(self._noseForm.form.offsetInput.text()).Value
        self._obj.ProxyPlacement = placement

        self._noseForm.tabScaling.transferTo(self._obj)
        self._noseForm.tabMaterial.transferTo(self._obj)
        self._noseForm.tabComment.transferTo(self._obj)

    def transferFrom(self):
        "Transfer from the object to the dialog"
        self._noseForm.form.noseConeTypesCombo.setCurrentIndex(self._noseForm.form.noseConeTypesCombo.findData(self._obj.NoseType))
        self._noseForm.form.noseConeProxyTypesCombo.setCurrentIndex(self._noseForm.form.noseConeProxyTypesCombo.findData(self._obj.NoseType))
        self._noseForm.form.noseStylesCombo.setCurrentIndex(self._noseForm.form.noseStylesCombo.findData(self._obj.NoseStyle))
        self._noseForm.form.noseCapStylesCombo.setCurrentIndex(self._noseForm.form.noseCapStylesCombo.findData(self._obj.CapStyle))
        self._noseForm.form.noseCapBarWidthInput.setText(self._obj.CapBarWidth.UserString)
        self._noseForm.form.lengthInput.setText(self._obj.Length.UserString)
        self._noseForm.form.diameterInput.setText(self._obj.Diameter.UserString)
        self._noseForm.form.autoDiameterCheckbox.setChecked(self._obj.AutoDiameter)
        self._noseForm.form.thicknessInput.setText(self._obj.Thickness.UserString)
        self._noseForm.form.coefficientInput.setText("%f" % self._obj.Coefficient)
        self._noseForm.form.bluntedInput.setText(self._obj.BluntedDiameter.UserString)
        self._noseForm.form.ogiveDiameterInput.setText(self._obj.OgiveDiameter.UserString)
        self._noseForm.form.shoulderGroup.setChecked(self._obj.Shoulder)
        self._noseForm.form.shoulderDiameterInput.setText(self._obj.ShoulderDiameter.UserString)
        self._noseForm.form.shoulderAutoDiameterCheckbox.setChecked(self._obj.ShoulderAutoDiameter)
        self._noseForm.form.shoulderLengthInput.setText(self._obj.ShoulderLength.UserString)
        self._noseForm.form.shoulderThicknessInput.setText(self._obj.ShoulderThickness.UserString)

        if self._obj.Base is not None:
            self._noseForm.form.proxyBaseObjectInput.setText(self._obj.Base.Label)
        else:
            self._noseForm.form.proxyBaseObjectInput.setText("")
        self._noseForm.form.proxyEffectiveDiameterInput.setText(self._obj.Diameter.UserString)

        placement = self._obj.ProxyPlacement
        yaw, pitch, roll = placement.Rotation.getYawPitchRoll()
        self._noseForm.form.xRotationInput.setText(f"{roll} deg")
        self._noseForm.form.yRotationInput.setText(f"{pitch} deg")
        self._noseForm.form.zRotationInput.setText(f"{yaw} deg")
        self._noseForm.form.offsetInput.setText(FreeCAD.Units.Quantity(placement.Base.x, FreeCAD.Units.Length).UserString)

        self._noseForm.tabScaling.transferFrom(self._obj)
        self._noseForm.tabMaterial.transferFrom(self._obj)
        self._noseForm.tabComment.transferFrom(self._obj)

        self._setTypeState()
        self._setStyleState()
        self._setAutoDiameterState()
        self._setShoulderState()
        self._setProxyState()

    def setEdited(self):
        try:
            self._obj.Proxy.setEdited()
        except ReferenceError:
            # Object may be deleted
            pass

    def _NikeScale(self):
        # Set the scale based on the body diameter being 16.5 inches on the original
        return (16.5 * 25.4) / float(self._obj.Diameter)

    def _setProxyStateVisible(self, visible):
        if visible:
            index = 0
        else:
            index = 1
        self._noseForm.form.stackedWidget.setCurrentIndex(index)

    def _setProxyState(self):
        self._setProxyStateVisible(self._obj.NoseType != TYPE_PROXY)
        # Hide the shoulder tab
        self._noseForm.form.tabWidget.setTabVisible(1, self._obj.NoseType != TYPE_PROXY)

        self._updateNoseType = False
        self._noseForm.form.noseConeTypesCombo.setCurrentIndex(self._noseForm.form.noseConeTypesCombo.findData(self._obj.NoseType))
        self._noseForm.form.noseConeProxyTypesCombo.setCurrentIndex(self._noseForm.form.noseConeProxyTypesCombo.findData(self._obj.NoseType))
        self._updateNoseType = True

    def _setCoeffientState(self):
        value = self._obj.NoseType
        if value == TYPE_HAACK or value == TYPE_PARABOLIC:
            self._noseForm.form.coefficientInput.setEnabled(True)
        elif value == TYPE_POWER:
            self._noseForm.form.coefficientInput.setEnabled(True)
        elif value == TYPE_VON_KARMAN:
            self._obj.Coefficient = 0.0
            self._noseForm.form.coefficientInput.setText("%f" % self._obj.Coefficient)
            self._noseForm.form.coefficientInput.setEnabled(False)
        elif value == TYPE_PARABOLA:
            self._obj.Coefficient = 0.5
            self._noseForm.form.coefficientInput.setText("%f" % self._obj.Coefficient)
            self._noseForm.form.coefficientInput.setEnabled(False)
        else:
            self._noseForm.form.coefficientInput.setEnabled(False)

    def _setBluntState(self):
        value = self._obj.NoseType
        if value in [TYPE_BLUNTED_CONE, TYPE_BLUNTED_OGIVE]:
            self._noseForm.form.bluntedInput.setEnabled(True)
        else:
            self._noseForm.form.bluntedInput.setEnabled(False)

    def _setOgiveDiameterState(self):
        value = self._obj.NoseType
        if value == TYPE_SECANT_OGIVE:
            self._noseForm.form.ogiveDiameterInput.setEnabled(True)
        else:
            self._noseForm.form.ogiveDiameterInput.setEnabled(False)

    def _setLengthState(self):
        value = self._obj.NoseType
        if value == TYPE_SPHERICAL:
            self._obj.Proxy.setLength(float(self._obj.Diameter) / 2.0)
            self._noseForm.form.lengthInput.setText(self._obj.Length.UserString)
            self._noseForm.form.lengthInput.setEnabled(False)
        elif value == TYPE_NIKE_SMOKE:
            length = (101.83 + 0.75 + 4.05) / self._NikeScale() * 25.4
            self._obj.Proxy.setLength(length)
            self._noseForm.form.lengthInput.setText(self._obj.Length.UserString)
            self._noseForm.form.lengthInput.setEnabled(False)
        else:
            self._noseForm.form.lengthInput.setEnabled(True)

    def _setTypeState(self):
        self._setProxyState()
        self._setCoeffientState()
        self._setBluntState()
        self._setOgiveDiameterState()
        self._setLengthState()

        # Scaling information is nose cone type dependent
        self.onScale()

    def onNoseType(self, value):
        if self._updateNoseType:
            self._obj.NoseType = value
            # print("Nose type set to {}".format(value))
            self._setTypeState()

            self._obj.Proxy.execute(self._obj)
            self.setEdited()

    def _setStyleState(self):
        value = self._obj.NoseStyle
        if value == STYLE_HOLLOW or value == STYLE_CAPPED:
            self._noseForm.form.thicknessInput.setEnabled(True)

            if self._noseForm.form.shoulderGroup.isChecked():
                self._noseForm.form.shoulderThicknessInput.setEnabled(True)
            else:
                self._noseForm.form.shoulderThicknessInput.setEnabled(False)
        else:
            self._noseForm.form.thicknessInput.setEnabled(False)
            self._noseForm.form.shoulderThicknessInput.setEnabled(False)

        if value == STYLE_CAPPED:
            self._noseForm.form.noseCapGroup.setEnabled(True)
            self._setCapStyleState()
        else:
            self._noseForm.form.noseCapGroup.setEnabled(False)

    def onScale(self) -> None:
        # Update the scale values
        scale = self._noseForm.tabScaling.getScale()
        length = self._obj.Length / scale
        diameter = self._obj.Diameter / scale
        noseDiameter = self._obj.BluntedDiameter / scale
        ogiveDiameter = self._obj.OgiveDiameter / scale
        if scale < 1.0:
            self._noseForm.tabScaling.scaledLabel.setText(translate('Rocket', "Upscale"))
            self._noseForm.tabScaling.scaledInput.setText(f"{1.0/scale}")
        else:
            self._noseForm.tabScaling.scaledLabel.setText(translate('Rocket', "Scale"))
            self._noseForm.tabScaling.scaledInput.setText(f"{scale}")
        self._noseForm.tabScaling.scaledLengthInput.setText(length.UserString)
        self._noseForm.tabScaling.scaledDiameterInput.setText(diameter.UserString)
        if self._obj.NoseType in [TYPE_OGIVE, TYPE_BLUNTED_OGIVE, TYPE_SECANT_OGIVE]:
            self._noseForm.tabScaling.scaledOgiveDiameterInput.setText(ogiveDiameter.UserString)
            self._noseForm.tabScaling.scaledOgiveDiameterInput.setVisible(True)
            self._noseForm.tabScaling.scaledOgiveDiameterLabel.setVisible(True)
        else:
            self._noseForm.tabScaling.scaledOgiveDiameterInput.setVisible(False)
            self._noseForm.tabScaling.scaledOgiveDiameterLabel.setVisible(False)
        if self._obj.NoseType in [TYPE_BLUNTED_CONE, TYPE_BLUNTED_OGIVE]:
            self._noseForm.tabScaling.scaledBluntedDiameterInput.setText(noseDiameter.UserString)
            self._noseForm.tabScaling.scaledBluntedDiameterInput.setVisible(True)
            self._noseForm.tabScaling.scaledBluntedDiameterLabel.setVisible(True)
        else:
            self._noseForm.tabScaling.scaledBluntedDiameterInput.setVisible(False)
            self._noseForm.tabScaling.scaledBluntedDiameterLabel.setVisible(False)

    def onNoseStyle(self, value):
        self._obj.NoseStyle = value
        self._setStyleState()

        self._obj.Proxy.execute(self._obj)

    def _setCapStyleState(self):
        value = self._obj.CapStyle
        if value == STYLE_CAP_SOLID:
            self._noseForm.form.noseCapBarWidthInput.setEnabled(False)
        else:
            self._noseForm.form.noseCapBarWidthInput.setEnabled(True)

    def onNoseCapStyle(self, value):
        self._obj.CapStyle = value
        self._setCapStyleState()

        self._obj.Proxy.execute(self._obj)
        self.setEdited()

    def onBarWidthChanged(self, value):
        try:
            self._obj.CapBarWidth = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def onLength(self, value):
        try:
            self._obj.Proxy.setLength(FreeCAD.Units.Quantity(value).Value)
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def onDiameter(self, value):
        try:
            self._obj.Proxy.setAftDiameter(FreeCAD.Units.Quantity(value).Value)
            self._obj.Proxy.setAftDiameterAutomatic(False)
            self._obj.Proxy.execute(self._obj)

            self._setLengthState() # Update for spherical noses
        except ValueError:
            pass
        self.setEdited()

    def _setAutoDiameterState(self):
        if self._isAssembly:
            self._noseForm.form.diameterInput.setEnabled(not self._obj.AutoDiameter)
            self._noseForm.form.autoDiameterCheckbox.setEnabled(True)
        else:
            self._noseForm.form.diameterInput.setEnabled(True)
            self._obj.AutoDiameter = False
            self._noseForm.form.autoDiameterCheckbox.setEnabled(False)
        self._noseForm.form.autoDiameterCheckbox.setChecked(self._obj.AutoDiameter)

        if self._obj.AutoDiameter:
            self._obj.Diameter = self._obj.Proxy.getAftDiameter()
            self._noseForm.form.diameterInput.setText(self._obj.Diameter.UserString)

    def onAutoDiameter(self, value):
        self._obj.Proxy.setAftDiameterAutomatic(value)
        self._setAutoDiameterState()

        self._obj.Proxy.execute(self._obj)
        self.setEdited()

    def onThickness(self, value):
        try:
            self._obj.Proxy.setThickness(FreeCAD.Units.Quantity(value).Value)
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def onCoefficient(self, value):
        self._obj.Coefficient = _toFloat(value)
        self._obj.Proxy.execute(self._obj)
        self.setEdited()

    def onBlunted(self, value):
        try:
            self._obj.BluntedDiameter = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def onOgiveDiameter(self, value):
        try:
            self._obj.OgiveDiameter = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def _setShoulderState(self):
        if self._obj.Shoulder:
            self._noseForm.form.shoulderDiameterInput.setEnabled(True)
            self._noseForm.form.shoulderLengthInput.setEnabled(True)

            selectedText = self._noseForm.form.noseStylesCombo.currentData()
            if selectedText == STYLE_HOLLOW or selectedText == STYLE_CAPPED:
                self._noseForm.form.shoulderThicknessInput.setEnabled(True)
            else:
                self._noseForm.form.shoulderThicknessInput.setEnabled(False)
        else:
            self._noseForm.form.shoulderDiameterInput.setEnabled(False)
            self._noseForm.form.shoulderLengthInput.setEnabled(False)
            self._noseForm.form.shoulderThicknessInput.setEnabled(False)

        self._setAutoShoulderDiameterState()

    def onShoulder(self, value):
        self._obj.Shoulder = self._noseForm.form.shoulderGroup.isChecked()
        self._setShoulderState()

        self._obj.Proxy.execute(self._obj)
        self.setEdited()

    def onShoulderDiameter(self, value):
        try:
            self._obj.ShoulderDiameter = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.setAftShoulderDiameterAutomatic(False)
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def _setAutoShoulderDiameterState(self):
        if self._isAssembly:
            self._noseForm.form.shoulderDiameterInput.setEnabled((not self._obj.ShoulderAutoDiameter) and self._obj.Shoulder)
            self._noseForm.form.shoulderAutoDiameterCheckbox.setChecked(self._obj.ShoulderAutoDiameter)
            self._noseForm.form.shoulderAutoDiameterCheckbox.setEnabled(self._obj.Shoulder)
        else:
            self._obj.ShoulderAutoDiameter = False
            self._noseForm.form.shoulderDiameterInput.setEnabled(self._obj.Shoulder)
            self._noseForm.form.shoulderAutoDiameterCheckbox.setChecked(self._obj.ShoulderAutoDiameter)
            self._noseForm.form.shoulderAutoDiameterCheckbox.setEnabled(self._obj.ShoulderAutoDiameter)

    def onShoulderAutoDiameter(self, value):
        self._obj.Proxy.setAftShoulderDiameterAutomatic(value)
        self._setAutoShoulderDiameterState()

        self._obj.Proxy.execute(self._obj)
        self.setEdited()

    def onShoulderLength(self, value):
        try:
            self._obj.ShoulderLength = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def onShoulderThickness(self, value):
        try:
            self._obj.ShoulderThickness = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def onLookup(self):
        result = self._db.getLookupResult()

        self._obj.NoseType = str(result["shape"])
        self._obj.NoseStyle = str(result["style"])
        self._obj.Proxy.setLength(_valueOnly(result["length"], result["length_units"]))
        self._obj.Proxy.setAftDiameter(_valueOnly(result["diameter"], result["diameter_units"]))
        self._obj.Proxy.setThickness(_valueOnly(result["thickness"], result["thickness_units"]))
        # self._obj.Coefficient = _toFloat(self._noseForm.form.coefficientInput.text())
        # self._obj.BluntedDiameter = _valueWithUnits("0", "mm")
        self._obj.ShoulderDiameter = _valueWithUnits(result["shoulder_diameter"], result["shoulder_diameter_units"])
        self._obj.ShoulderLength = _valueWithUnits(result["shoulder_length"], result["shoulder_length_units"])
        self._obj.Shoulder = (self._obj.ShoulderDiameter > 0.0) and (self._obj.ShoulderLength >= 0)
        self._obj.ShoulderThickness = self._obj.Thickness
        try:
            self._obj.ShapeMaterial = Materials.MaterialManager().getMaterial(result["uuid"])
        except LookupError:
            # Use the default
            _err(translate('Rocket', "Unable to find material '{}'").format(result["uuid"]))

        self.update()
        self._obj.Proxy.execute(self._obj)
        self.setEdited()

    def onSelect(self):
        # FreeCADGui.Control.closeDialog()
        # FreeCADGui.Control.showDialog(TaskPanelSelection())
        FreeCAD.RocketObserver = self
        FreeCADGui.Selection.addObserver(FreeCAD.RocketObserver)

        self._noseForm.form.proxyBaseObjectLabelSelect.setText(translate('Rocket', 'Select an object'))

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
            self._noseForm.form.proxyBaseObjectInput.setText(obj.Label)
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass

        self._noseForm.form.proxyBaseObjectLabelSelect.setText("")
        del FreeCAD.RocketObserver

    def onEffectiveDiameter(self, value):
        try:
            self._obj.Diameter = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def onRotation(self, value):
        try:
            yaw = FreeCAD.Units.Quantity(self._noseForm.form.zRotationInput.text()).Value
            pitch = FreeCAD.Units.Quantity(self._noseForm.form.yRotationInput.text()).Value
            roll = FreeCAD.Units.Quantity(self._noseForm.form.xRotationInput.text()).Value
            self._obj.ProxyPlacement.Rotation.setYawPitchRoll(yaw, pitch, roll)
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def onOffset(self, value):
        try:
            self._obj.ProxyPlacement.Base.x = FreeCAD.Units.Quantity(self._noseForm.form.offsetInput.text()).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def onSetToScale(self) -> None:
        # Update the scale values
        scale = self._noseForm.tabScaling.getScale()
        self._obj.Scale = False

        self._obj.Length /= scale
        self._obj.Diameter /= scale
        self._obj.OgiveDiameter /= scale
        self._obj.BluntedDiameter /= scale

        scale = self._noseForm.tabScaling.resetScale()
        self.update()

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
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.resetEdit()


    def reject(self):
        FreeCAD.ActiveDocument.abortTransaction()
        self.setEdited()
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.resetEdit()
