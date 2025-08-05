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
"""Class for drawing fins"""

__title__ = "FreeCAD Fins"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from typing import Any

import FreeCAD
import FreeCADGui
import Part
import Sketcher

from PySide import QtGui, QtCore
from PySide.QtCore import QObject, Signal
from PySide.QtWidgets import QDialog, QGridLayout, QVBoxLayout, QSizePolicy
import math

from DraftTools import translate

from Rocket.Constants import FIN_TYPE_TRAPEZOID, FIN_TYPE_TRIANGLE, FIN_TYPE_ELLIPSE, FIN_TYPE_SKETCH
from Rocket.Constants import FIN_CROSS_SAME, FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, \
    FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE, FIN_CROSS_BICONVEX, FIN_CROSS_ELLIPSE
from Rocket.Constants import FINCAN_STYLE_SLEEVE, FINCAN_STYLE_BODYTUBE
from Rocket.Constants import FINCAN_EDGE_SQUARE, FINCAN_EDGE_ROUND, FINCAN_EDGE_TAPER
from Rocket.Constants import FINCAN_PRESET_CUSTOM, FINCAN_PRESET_1_8, FINCAN_PRESET_3_16, FINCAN_PRESET_1_4
from Rocket.Constants import FINCAN_COUPLER_MATCH_ID, FINCAN_COUPLER_STEPPED

from Ui.TaskPanelFin import _FinDialog, TAB_FIN_ROOT, TAB_FIN_TIP, TAB_FIN_TUBE, TAB_FIN_FILLETS
from Ui.TaskPanelFin import TAB_GENERAL, TAB_FINTABS, TAB_FINCAN, TAB_COUPLER, TAB_LAUNCHLUG

from Ui.TaskPanelLocation import TaskPanelLocation
from Ui.Commands.CmdSketcher import newSketchNoEdit

from Ui.Widgets.MaterialTab import MaterialTab
from Ui.Widgets.CommentTab import CommentTab
from Ui.Widgets.ScalingTab import ScalingTabFins

class _FinCanDialog(_FinDialog):

    def __init__(self, obj : Any, parent : QtGui.QWidget = None) -> None:
        super().__init__(obj, parent)

    def initUI(self, obj : Any) -> None:
        # define our window
        self.setGeometry(250, 250, 400, 350)
        self.setWindowTitle(translate('Rocket', "Fin Can Parameter"))

        self.tabScaling = ScalingTabFins(obj)
        self.tabMaterial = MaterialTab()
        self.tabComment = CommentTab()
        self.form.tabWidget.addTab(self.tabScaling, translate('Rocket', "Scaling"))
        self.form.tabWidget.addTab(self.tabMaterial, translate('Rocket', "Material"))
        self.form.tabWidget.addTab(self.tabComment, translate('Rocket', "Comment"))

        # Hide unused tabs
        self.form.tabWidget.setTabVisible(TAB_FINTABS, False)
        # self.form.tabCrossSections.setTabVisible(TAB_FIN_FILLETS, False)

        self.setTabGeneral()
        self.setTabCan()
        self.setTabCoupler()
        self.setTabLaunchLug()

    def setTabGeneral(self):
        # Select the type of fin
        self.form.finTypesCombo.addItem(translate('Rocket', FIN_TYPE_TRAPEZOID), FIN_TYPE_TRAPEZOID)
        self.form.finTypesCombo.addItem(translate('Rocket', FIN_TYPE_TRIANGLE), FIN_TYPE_TRIANGLE)
        self.form.finTypesCombo.addItem(translate('Rocket', FIN_TYPE_ELLIPSE), FIN_TYPE_ELLIPSE)
        self.form.finTypesCombo.addItem(translate('Rocket', FIN_TYPE_SKETCH), FIN_TYPE_SKETCH)

        # Set the units
        self.form.finSpacingInput.unit = FreeCAD.Units.Angle
        self.form.finCantInput.unit = FreeCAD.Units.Angle
        self.form.heightInput.unit = FreeCAD.Units.Length
        self.form.spanInput.unit = FreeCAD.Units.Length
        self.form.sweepLengthInput.unit = FreeCAD.Units.Length
        self.form.sweepAngleInput.unit = FreeCAD.Units.Angle

        self.setTabFinRoot()
        self.setTabFinTip()
        # self.setTabFinTube() - not supported
        self.setTabFinFillets()

    def setTabCan(self):
        # Fin can leading and trailing edges
        self.form.canLeadingCombo.addItem(translate('Rocket', FINCAN_EDGE_SQUARE), FINCAN_EDGE_SQUARE)
        self.form.canLeadingCombo.addItem(translate('Rocket', FINCAN_EDGE_ROUND), FINCAN_EDGE_ROUND)
        self.form.canLeadingCombo.addItem(translate('Rocket', FINCAN_EDGE_TAPER), FINCAN_EDGE_TAPER)

        self.form.canTrailingCombo.addItem(translate('Rocket', FINCAN_EDGE_SQUARE), FINCAN_EDGE_SQUARE)
        self.form.canTrailingCombo.addItem(translate('Rocket', FINCAN_EDGE_ROUND), FINCAN_EDGE_ROUND)
        self.form.canTrailingCombo.addItem(translate('Rocket', FINCAN_EDGE_TAPER), FINCAN_EDGE_TAPER)

        # Set the units
        self.form.canDiameterInput.unit = FreeCAD.Units.Length
        self.form.canThicknessInput.unit = FreeCAD.Units.Length
        self.form.canLengthInput.unit = FreeCAD.Units.Length
        self.form.canLeadingOffsetInput.unit = FreeCAD.Units.Length
        self.form.canLeadingLengthInput.unit = FreeCAD.Units.Length
        self.form.canTrailingLengthInput.unit = FreeCAD.Units.Length


    def setTabCoupler(self):
        self.form.couplerStylesCombo.addItem(translate('Rocket', "Flush with fin can"), FINCAN_COUPLER_MATCH_ID)
        self.form.couplerStylesCombo.addItem(translate('Rocket', "Stepped"), FINCAN_COUPLER_STEPPED)

        self.form.couplerDiameterInput.unit = FreeCAD.Units.Length
        self.form.couplerThicknessInput.unit = FreeCAD.Units.Length
        self.form.couplerLengthInput.unit = FreeCAD.Units.Length

    def setTabLaunchLug(self):
        self.form.lugPresetsCombo.addItem(translate('Rocket', FINCAN_PRESET_CUSTOM), FINCAN_PRESET_CUSTOM)
        self.form.lugPresetsCombo.addItem(translate('Rocket', FINCAN_PRESET_1_8), FINCAN_PRESET_1_8)
        self.form.lugPresetsCombo.addItem(translate('Rocket', FINCAN_PRESET_3_16), FINCAN_PRESET_3_16)
        self.form.lugPresetsCombo.addItem(translate('Rocket', FINCAN_PRESET_1_4), FINCAN_PRESET_1_4)

        self.form.lugInnerDiameterInput.unit = FreeCAD.Units.Length
        self.form.lugThicknessInput.unit = FreeCAD.Units.Length
        self.form.lugLengthInput.unit = FreeCAD.Units.Length
        self.form.lugLeadingOffsetInput.unit = FreeCAD.Units.Length
        self.form.lugFilletRadiusInput.unit = FreeCAD.Units.Length
        self.form.forwardSweepInput.unit = FreeCAD.Units.Angle
        self.form.aftSweepInput.unit = FreeCAD.Units.Angle

class TaskPanelFinCan(QObject):

    redrawRequired = Signal()   # Allows for async redraws to allow for longer processing times

    def __init__(self,obj,mode):
        super().__init__()

        self._obj = obj
        self._isAssembly = self._obj.Proxy.isRocketAssembly()

        self._finForm = _FinCanDialog(obj)

        self._location = TaskPanelLocation(obj)
        self._locationForm = self._location.getForm()

        self.form = [self._finForm.form, self._locationForm]
        self._finForm.setWindowIcon(QtGui.QIcon(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Fin.svg"))

        self.update()

        self._finForm.form.finTypesCombo.currentTextChanged.connect(self.onFinTypes)

        self._finForm.form.finCountSpinBox.valueChanged.connect(self.onCount)
        self._finForm.form.finSpacingInput.textEdited.connect(self.onSpacing)
        self._finForm.form.finCantInput.textEdited.connect(self.onCant)

        self._finForm.form.rootCrossSectionsCombo.currentTextChanged.connect(self.onRootCrossSection)
        self._finForm.form.rootChordInput.textEdited.connect(self.onRootChord)
        self._finForm.form.rootThicknessInput.textEdited.connect(self.onRootThickness)
        self._finForm.form.rootPerCentCheckbox.clicked.connect(self.onRootPerCent)
        self._finForm.form.rootLength1Input.textEdited.connect(self.onRootLength1)
        self._finForm.form.rootLength2Input.textEdited.connect(self.onRootLength2)

        self._finForm.form.tipCrossSectionsCombo.currentTextChanged.connect(self.onTipCrossSection)
        self._finForm.form.tipChordInput.textEdited.connect(self.onTipChord)
        self._finForm.form.tipThicknessInput.textEdited.connect(self.onTipThickness)
        self._finForm.form.tipSameThicknessCheckbox.stateChanged.connect(self.onTipSameThickness)
        self._finForm.form.tipPerCentCheckbox.clicked.connect(self.onTipPerCent)
        self._finForm.form.tipLength1Input.textEdited.connect(self.onTipLength1)
        self._finForm.form.tipLength2Input.textEdited.connect(self.onTipLength2)

        self._finForm.form.filletCrossSectionsCombo.currentTextChanged.connect(self.onFilletCrossSection)
        self._finForm.form.filletsCheckbox.stateChanged.connect(self.onFillet)
        self._finForm.form.filletRadiusInput.textEdited.connect(self.onFilletRadius)

        self._finForm.form.heightInput.textEdited.connect(self.onHeight)
        self._finForm.form.autoHeightCheckBox.stateChanged.connect(self.onAutoHeight)
        self._finForm.form.spanInput.textEdited.connect(self.onSpan)
        self._finForm.form.sweepLengthInput.textEdited.connect(self.onSweepLength)
        self._finForm.form.sweepAngleInput.textEdited.connect(self.onSweepAngle)

        self._finForm.tabScaling.scaled.connect(self.onScale)
        self._finForm.tabScaling.scaledSetValuesButton.clicked.connect(self.onSetToScale)

        self._finForm.form.canDiameterInput.textEdited.connect(self.onCanDiameter)
        self._finForm.form.canAutoDiameterCheckbox.stateChanged.connect(self.onCanAutoDiameter)
        self._finForm.form.canThicknessInput.textEdited.connect(self.onCanThickness)
        self._finForm.form.canLengthInput.textEdited.connect(self.onCanLength)
        self._finForm.form.canLeadingOffsetInput.textEdited.connect(self.onCanLeadingEdgeOffset)

        self._finForm.form.canLeadingCombo.currentTextChanged.connect(self.onCanLeadingEdge)
        self._finForm.form.canLeadingLengthInput.textEdited.connect(self.onCanLeadingLength)
        self._finForm.form.canTrailingCombo.currentTextChanged.connect(self.onCanTrailingEdge)
        self._finForm.form.canTrailingLengthInput.textEdited.connect(self.onCanTrailingLength)

        self._finForm.form.couplerGroup.toggled.connect(self.onCoupler)
        self._finForm.form.couplerStylesCombo.currentIndexChanged.connect(self.onCouplerStyle)
        self._finForm.form.couplerThicknessInput.textEdited.connect(self.onCouplerThickness)
        self._finForm.form.couplerDiameterInput.textEdited.connect(self.onCouplerDiameter)
        self._finForm.form.couplerAutoDiameterCheckbox.stateChanged.connect(self.onCouplerAutoDiameter)
        self._finForm.form.couplerLengthInput.textEdited.connect(self.onCouplerLength)

        self._finForm.form.lugGroup.toggled.connect(self.onLug)
        self._finForm.form.lugInnerDiameterInput.textEdited.connect(self.onLugInnerDiameter)
        self._finForm.form.lugPresetsCombo.currentTextChanged.connect(self.onLugPreset)
        self._finForm.form.lugThicknessInput.textEdited.connect(self.onLugThickness)
        self._finForm.form.lugAutoThicknessCheckbox.stateChanged.connect(self.onLugAutoThickness)
        self._finForm.form.lugLengthInput.textEdited.connect(self.onLugLength)
        self._finForm.form.lugLeadingOffsetInput.textEdited.connect(self.onLugLeadingEdgeOffset)
        self._finForm.form.lugAutoLengthCheckbox.stateChanged.connect(self.onLugAutoLength)
        self._finForm.form.lugFilletRadiusInput.textEdited.connect(self.onLugFilletRadius)

        self._finForm.form.forwardSweepGroup.toggled.connect(self.onForwardSweep)
        self._finForm.form.forwardSweepInput.textEdited.connect(self.onForwardSweepAngle)
        self._finForm.form.aftSweepGroup.toggled.connect(self.onAftSweep)
        self._finForm.form.aftSweepInput.textEdited.connect(self.onAftSweepAngle)

        self._location.locationChange.connect(self.onLocation)

        self._redrawPending = False
        self.redrawRequired.connect(self.onRedraw, QtCore.Qt.QueuedConnection)

        if mode == 0: # fresh created
            self.redraw()  # calculate once
            FreeCAD.Gui.SendMsgToActiveView("ViewFit")

    def transferTo(self):
        "Transfer from the dialog to the object"
        self._obj.FinType = str(self._finForm.form.finTypesCombo.currentData())

        self._obj.FinCount = self._finForm.form.finCountSpinBox.value()
        self._obj.FinSpacing = self._finForm.form.finSpacingInput.text()
        self._obj.Cant = self._finForm.form.finCantInput.text()

        self._obj.RootCrossSection = str(self._finForm.form.rootCrossSectionsCombo.currentData())
        self._obj.RootChord = self._finForm.form.rootChordInput.text()
        self._obj.RootThickness = self._finForm.form.rootThicknessInput.text()
        self._obj.RootPerCent = self._finForm.form.rootPerCentCheckbox.isChecked()
        self._obj.RootLength1 = self._finForm.form.rootLength1Input.text()
        self._obj.RootLength2 = self._finForm.form.rootLength2Input.text()

        self._obj.TipCrossSection = str(self._finForm.form.tipCrossSectionsCombo.currentData())
        self._obj.TipChord = self._finForm.form.tipChordInput.text()
        self._obj.TipThickness = self._finForm.form.tipThicknessInput.text()
        self._obj.TipSameThickness = self._finForm.form.tipSameThicknessCheckbox.isChecked()
        self._obj.TipPerCent = self._finForm.form.tipPerCentCheckbox.isChecked()
        self._obj.TipLength1 = self._finForm.form.tipLength1Input.text()
        self._obj.TipLength2 =self._finForm.form.tipLength2Input.text()

        self._obj.FilletCrossSection = str(self._finForm.form.filletCrossSectionsCombo.currentData())
        self._obj.Fillets = self._finForm.form.filletsCheckbox.isChecked()
        self._obj.FilletRadius = self._finForm.form.filletRadiusInput.text()

        self._obj.Height = self._finForm.form.heightInput.text()
        self._obj.AutoHeight = self._finForm.form.autoHeightCheckBox.isChecked()
        self._obj.Span = self._finForm.form.spanInput.text()
        self._obj.SweepLength = self._finForm.form.sweepLengthInput.text()
        self._obj.SweepAngle = self._finForm.form.sweepAngleInput.text()

        self._obj.Diameter = self._finForm.form.canDiameterInput.text()
        self._obj.AutoDiameter = self._finForm.form.canAutoDiameterCheckbox.isChecked()
        self._obj.Thickness = self._finForm.form.canThicknessInput.text()
        self._obj.Length = self._finForm.form.canLengthInput.text()
        self._obj.LeadingEdgeOffset = self._finForm.form.canLeadingOffsetInput.text()

        self._obj.LeadingEdge = str(self._finForm.form.canLeadingCombo.currentData())
        self._obj.LeadingLength = self._finForm.form.canLeadingLengthInput.text()
        self._obj.TrailingEdge = str(self._finForm.form.canTrailingCombo.currentData())
        self._obj.TrailingLength = self._finForm.form.canTrailingLengthInput.text()

        self._obj.Coupler = self._finForm.form.couplerGroup.isChecked()
        self._obj.CouplerStyle = str(self._finForm.form.couplerStylesCombo.currentData())
        self._obj.CouplerThickness = self._finForm.form.couplerThicknessInput.text()
        self._obj.CouplerDiameter = self._finForm.form.couplerDiameterInput.text()
        self._obj.CouplerAutoDiameter = self._finForm.form.couplerAutoDiameterCheckbox.isChecked()
        self._obj.CouplerLength = self._finForm.form.couplerLengthInput.text()

        self._obj.LaunchLug = self._finForm.form.lugGroup.isChecked()
        self._obj.LugInnerDiameter = self._finForm.form.lugInnerDiameterInput.text()
        self._obj.LaunchLugPreset = str(self._finForm.form.lugPresetsCombo.currentData())
        self._obj.LugThickness = self._finForm.form.lugThicknessInput.text()
        self._obj.LugAutoThickness = self._finForm.form.lugAutoThicknessCheckbox.isChecked()
        self._obj.LugLength = self._finForm.form.lugLengthInput.text()
        self._obj.LugAutoLength = self._finForm.form.lugAutoLengthCheckbox.isChecked()
        self._obj.LugLeadingEdgeOffset = self._finForm.form.lugLeadingOffsetInput.text()
        self._obj.LugFilletRadius = self._finForm.form.lugFilletRadiusInput.text()

        self._obj.LaunchLugForwardSweep = self._finForm.form.forwardSweepGroup.isChecked()
        self._obj.LaunchLugForwardSweepAngle = self._finForm.form.forwardSweepInput.text()
        self._obj.LaunchLugAftSweep = self._finForm.form.aftSweepGroup.isChecked()
        self._obj.LaunchLugAftSweepAngle = self._finForm.form.aftSweepInput.text()

        self._finForm.tabScaling.transferTo(self._obj)
        self._finForm.tabMaterial.transferTo(self._obj)
        self._finForm.tabComment.transferTo(self._obj)

    def transferFrom(self):
        "Transfer from the object to the dialog"
        self._finForm.form.finTypesCombo.setCurrentIndex(self._finForm.form.finTypesCombo.findData(self._obj.FinType))

        self._finForm.form.finCountSpinBox.setValue(self._obj.FinCount)
        self._finForm.form.finSpacingInput.setText(self._obj.FinSpacing.UserString)
        self._finForm.form.finCantInput.setText(self._obj.Cant.UserString)

        self._finForm.form.rootCrossSectionsCombo.setCurrentIndex(self._finForm.form.rootCrossSectionsCombo.findData(self._obj.RootCrossSection))
        self._finForm.form.rootChordInput.setText(self._obj.RootChord.UserString)
        self._finForm.form.rootThicknessInput.setText(self._obj.RootThickness.UserString)
        self._finForm.form.rootPerCentCheckbox.setChecked(self._obj.RootPerCent)
        self._finForm.form.rootLength1Input.setText(self._obj.RootLength1.UserString)
        self._finForm.form.rootLength2Input.setText(self._obj.RootLength2.UserString)

        self._finForm.form.tipCrossSectionsCombo.setCurrentIndex(self._finForm.form.tipCrossSectionsCombo.findData(self._obj.TipCrossSection))
        self._finForm.form.tipChordInput.setText(self._obj.TipChord.UserString)
        self._finForm.form.tipThicknessInput.setText(self._obj.TipThickness.UserString)
        self._finForm.form.tipSameThicknessCheckbox.setChecked(self._obj.TipSameThickness)
        self._finForm.form.tipPerCentCheckbox.setChecked(self._obj.TipPerCent)
        self._finForm.form.tipLength1Input.setText(self._obj.TipLength1.UserString)
        self._finForm.form.tipLength2Input.setText(self._obj.TipLength2.UserString)

        self._finForm.form.filletCrossSectionsCombo.setCurrentIndex(self._finForm.form.filletCrossSectionsCombo.findData(self._obj.FilletCrossSection))
        self._finForm.form.filletsCheckbox.setChecked(self._obj.Fillets)
        self._finForm.form.filletRadiusInput.setText(self._obj.FilletRadius.UserString)

        self._finForm.form.heightInput.setText(self._obj.Height.UserString)
        self._finForm.form.autoHeightCheckBox.setChecked(self._obj.AutoHeight)
        self._finForm.form.spanInput.setText(self._obj.Span.UserString)
        self._finForm.form.sweepLengthInput.setText(self._obj.SweepLength.UserString)
        self._finForm.form.sweepAngleInput.setText(self._obj.SweepAngle.UserString)

        self._finForm.form.canDiameterInput.setText(self._obj.Diameter.UserString)
        self._finForm.form.canAutoDiameterCheckbox.setChecked(self._obj.AutoDiameter)
        self._finForm.form.canThicknessInput.setText(self._obj.Thickness.UserString)
        self._finForm.form.canLengthInput.setText(self._obj.Length.UserString)
        self._finForm.form.canLeadingOffsetInput.setText(self._obj.LeadingEdgeOffset.UserString)

        self._finForm.form.canLeadingCombo.setCurrentIndex(self._finForm.form.canLeadingCombo.findData(self._obj.LeadingEdge))
        self._finForm.form.canLeadingLengthInput.setText(self._obj.LeadingLength.UserString)
        self._finForm.form.canTrailingCombo.setCurrentIndex(self._finForm.form.canTrailingCombo.findData(self._obj.TrailingEdge))
        self._finForm.form.canTrailingLengthInput.setText(self._obj.TrailingLength.UserString)

        self._finForm.form.couplerGroup.setChecked(self._obj.Coupler)
        self._finForm.form.couplerStylesCombo.setCurrentIndex(self._finForm.form.couplerStylesCombo.findData(self._obj.CouplerStyle))
        self._finForm.form.couplerThicknessInput.setText(self._obj.CouplerThickness.UserString)
        self._finForm.form.couplerDiameterInput.setText(self._obj.CouplerDiameter.UserString)
        self._finForm.form.couplerAutoDiameterCheckbox.setChecked(self._obj.CouplerAutoDiameter)
        self._finForm.form.couplerLengthInput.setText(self._obj.CouplerLength.UserString)

        self._finForm.form.lugGroup.setChecked(self._obj.LaunchLug)
        self._finForm.form.lugInnerDiameterInput.setText(self._obj.LugInnerDiameter.UserString)
        self._finForm.form.lugPresetsCombo.setCurrentIndex(self._finForm.form.lugPresetsCombo.findData(self._obj.LaunchLugPreset))
        self._finForm.form.lugThicknessInput.setText(self._obj.LugThickness.UserString)
        self._finForm.form.lugAutoThicknessCheckbox.setChecked(self._obj.LugAutoThickness)
        self._finForm.form.lugLengthInput.setText(self._obj.LugLength.UserString)
        self._finForm.form.lugAutoLengthCheckbox.setChecked(self._obj.LugAutoLength)
        self._finForm.form.lugLeadingOffsetInput.setText(self._obj.LugLeadingEdgeOffset.UserString)
        self._finForm.form.lugFilletRadiusInput.setText(self._obj.LugFilletRadius.UserString)

        self._finForm.form.forwardSweepGroup.setChecked(self._obj.LaunchLugForwardSweep)
        self._finForm.form.forwardSweepInput.setText(self._obj.LaunchLugForwardSweepAngle.UserString)
        self._finForm.form.aftSweepGroup.setChecked(self._obj.LaunchLugAftSweep)
        self._finForm.form.aftSweepInput.setText(self._obj.LaunchLugAftSweepAngle.UserString)

        self._finForm.tabScaling.transferFrom(self._obj)
        self._finForm.tabMaterial.transferFrom(self._obj)
        self._finForm.tabComment.transferFrom(self._obj)

        self._setFinSetState()
        self._setHeightState()
        self._enableRootLengths()
        self._enableFinTypes() # This calls _enableTipLengths()
        self._enableRootPercent()
        self._enableTipPercent()
        self._sweepAngleFromLength()
        self._enableLeadingEdge()
        self._enableTrailingEdge()
        self._setCanStyle()
        self._setCanAutoDiameterState()
        self._setCouplerAutoDiameterState()
        self._setLugAutoThicknessState()
        self._setLugAutoLengthState()

    def setEdited(self):
        try:
            self._obj.Proxy.setEdited()
        except ReferenceError:
            # Object may be deleted
            pass

    def redraw(self):
        if not self._redrawPending:
            self._redrawPending = True
            self.redrawRequired.emit()

    def onScale(self) -> None:
        # Update the scale values
        scale = self._finForm.tabScaling.getScale()

        if scale < 1.0:
            self._finForm.tabScaling.scaledLabel.setText(translate('Rocket', "Upscale"))
            self._finForm.tabScaling.scaledInput.setText(f"{1.0/scale}")
        else:
            self._finForm.tabScaling.scaledLabel.setText(translate('Rocket', "Scale"))
            self._finForm.tabScaling.scaledInput.setText(f"{scale}")

        rootChord = self._obj.RootChord / scale
        rootThickness = self._obj.RootThickness / scale
        height = self._obj.Height / scale
        self._finForm.tabScaling.scaledRootInput.setText(rootChord.UserString)
        self._finForm.tabScaling.scaledRootThicknessInput.setText(rootThickness.UserString)
        self._finForm.tabScaling.scaledHeightInput.setText(height.UserString)

        if self._obj.FinType == FIN_TYPE_TRAPEZOID:
            tipChord = self._obj.TipChord / scale
            tipThickness = self._obj.TipThickness / scale
            self._finForm.tabScaling.scaledTipInput.setText(tipChord.UserString)
            self._finForm.tabScaling.scaledTipThicknessInput.setText(tipThickness.UserString)
            self._finForm.tabScaling.scaledTipLabel.setVisible(True)
            self._finForm.tabScaling.scaledTipInput.setVisible(True)
            self._finForm.tabScaling.scaledTipThicknessLabel.setVisible(True)
            self._finForm.tabScaling.scaledTipThicknessInput.setVisible(True)
        else:
            self._finForm.tabScaling.scaledTipLabel.setVisible(False)
            self._finForm.tabScaling.scaledTipInput.setVisible(False)
            self._finForm.tabScaling.scaledTipThicknessLabel.setVisible(False)
            self._finForm.tabScaling.scaledTipThicknessInput.setVisible(False)

    def onCount(self, value):
        self._obj.FinCount = value
        if self._obj.FinCount > 0:
            self._obj.FinSpacing = 360.0 / float(value)
        else:
            self._obj.FinSpacing = 360.0
        self._finForm.form.finSpacingInput.setText(self._obj.FinSpacing.UserString)
        self.redraw()
        self.setEdited()

    def onSpacing(self, value):
        self._obj.FinSpacing = value
        self.redraw()
        self.setEdited()

    def onCant(self, value):
        self._obj.Cant = value
        self.redraw()
        self.setEdited()

    def _enableFinTypes(self):
        if self._obj.FinType == FIN_TYPE_TRAPEZOID:
            self._enableFinTypeTrapezoid()
        elif self._obj.FinType == FIN_TYPE_TRIANGLE:
            self._enableFinTypeTriangle()
        elif self._obj.FinType == FIN_TYPE_ELLIPSE:
            self._enableFinTypeEllipse()
        else:
            self._enableFinTypeSketch()

    def setRootCrossSections(self):
        self._finForm.form.rootCrossSectionsCombo.clear()
        self._finForm.form.rootCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_SQUARE), FIN_CROSS_SQUARE)
        self._finForm.form.rootCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_ROUND), FIN_CROSS_ROUND)
        self._finForm.form.rootCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_ELLIPSE), FIN_CROSS_ELLIPSE)
        self._finForm.form.rootCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_BICONVEX), FIN_CROSS_BICONVEX)
        self._finForm.form.rootCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_AIRFOIL), FIN_CROSS_AIRFOIL)
        self._finForm.form.rootCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_WEDGE), FIN_CROSS_WEDGE)
        self._finForm.form.rootCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_DIAMOND), FIN_CROSS_DIAMOND)
        self._finForm.form.rootCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_TAPER_LE), FIN_CROSS_TAPER_LE)
        self._finForm.form.rootCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_TAPER_TE), FIN_CROSS_TAPER_TE)
        self._finForm.form.rootCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_TAPER_LETE), FIN_CROSS_TAPER_LETE)

    def setEllipseRootCrossSections(self):
        self._finForm.form.rootCrossSectionsCombo.clear()
        self._finForm.form.rootCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_SQUARE), FIN_CROSS_SQUARE)
        self._finForm.form.rootCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_ROUND), FIN_CROSS_ROUND)
        self._finForm.form.rootCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_ELLIPSE), FIN_CROSS_ELLIPSE)
        self._finForm.form.rootCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_BICONVEX), FIN_CROSS_BICONVEX)
        self._finForm.form.rootCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_AIRFOIL), FIN_CROSS_AIRFOIL)
        self._finForm.form.rootCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_WEDGE), FIN_CROSS_WEDGE)
        self._finForm.form.rootCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_TAPER_LETE), FIN_CROSS_TAPER_LETE)

    def _enableFinTypeTrapezoid(self):
        old = self._obj.RootCrossSection # This must be saved and restored
        self.setRootCrossSections()
        self._obj.RootCrossSection = old

        self._finForm.form.rootCrossSectionsCombo.setCurrentIndex(self._finForm.form.rootCrossSectionsCombo.findData(self._obj.RootCrossSection))

        self._finForm.form.heightLabel.setHidden(False)
        self._finForm.form.heightInput.setHidden(False)

        self._finForm.form.sweepLengthLabel.setHidden(False)
        self._finForm.form.sweepLengthInput.setHidden(False)
        self._finForm.form.sweepAngleLabel.setHidden(False)
        self._finForm.form.sweepAngleInput.setHidden(False)

        self._finForm.form.rootChordLabel.setHidden(False)
        self._finForm.form.rootChordInput.setHidden(False)
        self._finForm.form.rootLength2Label.setHidden(False)
        self._finForm.form.rootLength2Input.setHidden(False)

        # self._finForm.form.tipGroup.setHidden(False)
        self._finForm.form.tabCrossSections.setTabVisible(TAB_FIN_ROOT, True)
        self._finForm.form.tabCrossSections.setTabVisible(TAB_FIN_TIP, True)
        self._finForm.form.tabCrossSections.setTabVisible(TAB_FIN_TUBE, False)

        self._enableTipLengths()

    def _enableFinTypeTriangle(self):
        old = self._obj.RootCrossSection # This must be saved and restored
        self.setRootCrossSections()
        self._obj.RootCrossSection = old

        self._finForm.form.rootCrossSectionsCombo.setCurrentIndex(self._finForm.form.rootCrossSectionsCombo.findData(self._obj.RootCrossSection))

        self._finForm.form.heightLabel.setHidden(False)
        self._finForm.form.heightInput.setHidden(False)

        self._finForm.form.sweepLengthLabel.setHidden(False)
        self._finForm.form.sweepLengthInput.setHidden(False)
        self._finForm.form.sweepAngleLabel.setHidden(False)
        self._finForm.form.sweepAngleInput.setHidden(False)

        self._finForm.form.rootChordLabel.setHidden(False)
        self._finForm.form.rootChordInput.setHidden(False)
        self._finForm.form.rootLength2Label.setHidden(False)
        self._finForm.form.rootLength2Input.setHidden(False)

        # self._finForm.form.tipGroup.setHidden(True)
        self._finForm.form.tabCrossSections.setTabVisible(TAB_FIN_ROOT, True)
        self._finForm.form.tabCrossSections.setTabVisible(TAB_FIN_TIP, False)
        self._finForm.form.tabCrossSections.setTabVisible(TAB_FIN_TUBE, False)

    def _enableFinTypeEllipse(self):
        old = self._obj.RootCrossSection # This must be saved and restored
        self.setEllipseRootCrossSections()
        self._obj.RootCrossSection = old

        if self._obj.RootCrossSection in [FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE]:
            self._obj.RootCrossSection = FIN_CROSS_TAPER_LETE
        self._finForm.form.rootCrossSectionsCombo.setCurrentIndex(self._finForm.form.rootCrossSectionsCombo.findData(self._obj.RootCrossSection))

        self._finForm.form.heightLabel.setHidden(False)
        self._finForm.form.heightInput.setHidden(False)

        self._finForm.form.sweepLengthLabel.setHidden(True)
        self._finForm.form.sweepLengthInput.setHidden(True)
        self._finForm.form.sweepAngleLabel.setHidden(True)
        self._finForm.form.sweepAngleInput.setHidden(True)

        self._finForm.form.rootChordLabel.setHidden(False)
        self._finForm.form.rootChordInput.setHidden(False)
        self._finForm.form.rootLength2Label.setHidden(True)
        self._finForm.form.rootLength2Input.setHidden(True)

        # self._finForm.form.tipGroup.setHidden(True)
        self._finForm.form.tabCrossSections.setTabVisible(TAB_FIN_ROOT, True)
        self._finForm.form.tabCrossSections.setTabVisible(TAB_FIN_TIP, False)
        self._finForm.form.tabCrossSections.setTabVisible(TAB_FIN_TUBE, False)

    def _enableFinTypeSketch(self):
        old = self._obj.RootCrossSection # This must be saved and restored
        self.setRootCrossSections()
        self._obj.RootCrossSection = old

        self._finForm.form.rootCrossSectionsCombo.setCurrentIndex(self._finForm.form.rootCrossSectionsCombo.findData(self._obj.RootCrossSection))

        self._finForm.form.heightLabel.setHidden(True)
        self._finForm.form.heightInput.setHidden(True)

        self._finForm.form.sweepLengthLabel.setHidden(True)
        self._finForm.form.sweepLengthInput.setHidden(True)
        self._finForm.form.sweepAngleLabel.setHidden(True)
        self._finForm.form.sweepAngleInput.setHidden(True)

        self._finForm.form.rootChordLabel.setHidden(True)
        self._finForm.form.rootChordInput.setHidden(True)

        # self._finForm.form.tipGroup.setHidden(True)
        self._finForm.form.tabCrossSections.setTabVisible(TAB_FIN_ROOT, True)
        self._finForm.form.tabCrossSections.setTabVisible(TAB_FIN_TIP, True)
        self._finForm.form.tabCrossSections.setTabVisible(TAB_FIN_TUBE, False)

        # Create a default sketch if none exists
        self._defaultFinSketch()

    def _drawLines(self, sketch, points):
        last = points[-1]
        for index, point in enumerate(points):
            sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(float(last[0]), float(last[1]), 0),
                                                        FreeCAD.Vector(float(point[0]), float(point[1]), 0)))
            sketch.addConstraint(Sketcher.Constraint("DistanceX", index, 2, point[0]))
            sketch.addConstraint(Sketcher.Constraint("DistanceY", index, 2, point[1]))
            last = point

        count = len(points)
        for index in range(count):
            if index == 0:
                sketch.addConstraint(Sketcher.Constraint("Coincident", count-1, 2, index, 1))
            else:
                sketch.addConstraint(Sketcher.Constraint("Coincident", index-1, 2, index, 1))

        return sketch

    def _defaultFinSketch(self):
        if self._obj.Profile is None:
            sketch = newSketchNoEdit()
            points = []
            points.append((0.0, 0.0))
            points.append((float(self._obj.RootChord), 0.0))
            points.append((float(self._obj.SweepLength) + float(self._obj.TipChord), float(self._obj.Height)))
            points.append((float(self._obj.SweepLength), float(self._obj.Height)))

            sketch = self._drawLines(sketch, points)
            FreeCAD.ActiveDocument.recompute([sketch]) # Compute the sketch
            self._obj.Profile = sketch
            sketch.Visibility = False

    def onFinTypes(self, value):
        self._obj.FinType = value
        self._enableFinTypes()
        self.redraw()
        self.setEdited()

    def _setFinSetState(self):
        # if self._isAssembly:
        #     checked = self._finForm.form.finSetGroup.isChecked()
        #     self._finForm.form.finSetGroup.setEnabled(True)
        # else:
        #     if self._obj.FinSet:
        #         self._obj.FinSet = False
        #         self._finForm.form.finSetGroup.setChecked(self._obj.FinSet)
        #     checked = False
        #     self._finForm.form.finSetGroup.setEnabled(False)
        self._finForm.form.finSetGroup.setEnabled(True)
        self._finForm.form.finSetGroup.setChecked(self._obj.FinSet)
        # checked = self._finForm.form.finSetGroup.isChecked()

        # self._finForm.form.finCountSpinBox.setEnabled(checked)
        # self._finForm.form.finSpacingInput.setEnabled(checked)
        self._finForm.form.tipThicknessInput.setEnabled(not self._obj.TipSameThickness)

    def _enableRootLengths(self):
        value = self._obj.RootCrossSection
        if value in [FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE]:
            self._finForm.form.rootPerCentCheckbox.setEnabled(True)
            self._finForm.form.rootLength1Input.setEnabled(True)
            if value == FIN_CROSS_TAPER_LETE:
                self._finForm.form.rootLength2Input.setEnabled(True)
            else:
                self._finForm.form.rootLength2Input.setEnabled(False)
        else:
            self._finForm.form.rootPerCentCheckbox.setEnabled(False)
            self._finForm.form.rootLength1Input.setEnabled(False)
            self._finForm.form.rootLength2Input.setEnabled(False)

    def _enableTipLengths(self):
        if self._obj.FinType == FIN_TYPE_TRAPEZOID:
            value = self._obj.TipCrossSection
            if value == FIN_CROSS_SAME:
                value = self._obj.RootCrossSection
            if value in [FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE]:
                self._finForm.form.tipPerCentCheckbox.setEnabled(True)
                self._finForm.form.tipLength1Input.setEnabled(True)
                if value == FIN_CROSS_TAPER_LETE:
                    self._finForm.form.tipLength2Input.setEnabled(True)
                else:
                    self._finForm.form.tipLength2Input.setEnabled(False)
            else:
                self._finForm.form.tipPerCentCheckbox.setEnabled(False)
                self._finForm.form.tipLength1Input.setEnabled(False)
                self._finForm.form.tipLength2Input.setEnabled(False)

    def onRootCrossSection(self, value):
        if len(value) <= 0:
            return

        self._obj.RootCrossSection = value
        self._enableRootLengths()

        if self._obj.TipCrossSection == FIN_CROSS_SAME:
            self._enableTipLengths()

        self.redraw()
        self.setEdited()

    def onRootChord(self, value):
        try:
            self._obj.RootChord = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def onRootThickness(self, value):
        try:
            self._obj.RootThickness = FreeCAD.Units.Quantity(value).Value
            if self._obj.TipSameThickness:
                self._obj.TipThickness = FreeCAD.Units.Quantity(value).Value
                self._finForm.form.tipThicknessInput.setText(self._obj.TipThickness.UserString)
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def _toPercent(self, length, chord):
        percent = 100.0 * length / chord
        if percent > 100.0:
            percent = 100.0
        if percent < 0.0:
            percent = 0.0
        return percent

    def _toLength(self, percent, chord):
        length = percent * chord / 100.0
        if length > chord:
            length = chord
        if length < 0.0:
            length = 0.0
        return length

    def _enableRootPercent(self):
        if self._obj.RootPerCent:
            self._finForm.form.rootLength1Input.unit = ''
            self._finForm.form.rootLength2Input.unit = ''
            self._finForm.form.rootLength1Input.setText(str(self._obj.RootLength1.Value))
            self._finForm.form.rootLength2Input.setText(str(self._obj.RootLength2.Value))
        else:
            self._finForm.form.rootLength1Input.unit = FreeCAD.Units.Length
            self._finForm.form.rootLength2Input.unit = FreeCAD.Units.Length
            self._finForm.form.rootLength1Input.setText(self._obj.RootLength1.UserString)
            self._finForm.form.rootLength2Input.setText(self._obj.RootLength2.UserString)

    def _convertRootPercent(self):
        if self._obj.RootPerCent:
            # Convert to percentages
            self._obj.RootLength1 = self._toPercent(self._obj.RootLength1.Value, self._obj.RootChord.Value)
            self._obj.RootLength2 = self._toPercent(self._obj.RootLength2.Value, self._obj.RootChord.Value)
        else:
            # Convert to lengths
            self._obj.RootLength1 = self._toLength(self._obj.RootLength1.Value, self._obj.RootChord.Value)
            self._obj.RootLength2 = self._toLength(self._obj.RootLength2.Value, self._obj.RootChord.Value)
        self._enableRootPercent()

    def onRootPerCent(self, value):
        self._obj.RootPerCent = self._finForm.form.rootPerCentCheckbox.isChecked()
        self._convertRootPercent()

        self.redraw()
        self.setEdited()

    def onRootLength1(self, value):
        try:
            self._obj.RootLength1 = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def onRootLength2(self, value):
        try:
            self._obj.RootLength2 = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def onTipCrossSection(self, value):
        self._obj.TipCrossSection = value
        self._enableTipLengths()

        self.redraw()
        self.setEdited()

    def onTipChord(self, value):
        try:
            self._obj.Proxy.setTipChord(FreeCAD.Units.Quantity(value).Value)
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def onTipThickness(self, value):
        try:
            self._obj.Proxy.setTipThickness(FreeCAD.Units.Quantity(value).Value)
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def onTipSameThickness(self, value):
        try:
            self._obj.TipSameThickness = value
            self.redraw()
            self._setFinSetState()
        except ValueError:
            pass
        self.setEdited()

    def _enableTipPercent(self):
        if self._obj.TipPerCent:
            self._finForm.form.tipLength1Input.unit = ''
            self._finForm.form.tipLength2Input.unit = ''
            self._finForm.form.tipLength1Input.setText(str(self._obj.TipLength1.Value))
            self._finForm.form.tipLength2Input.setText(str(self._obj.TipLength2.Value))
        else:
            self._finForm.form.tipLength1Input.unit = FreeCAD.Units.Length
            self._finForm.form.tipLength2Input.unit = FreeCAD.Units.Length
            self._finForm.form.tipLength1Input.setText(self._obj.TipLength1.UserString)
            self._finForm.form.tipLength2Input.setText(self._obj.TipLength2.UserString)

    def _convertTipPercent(self):
        if self._obj.TipPerCent:
            # Convert to percentages
            self._obj.TipLength1 = self._toPercent(self._obj.TipLength1.Value, self._obj.TipChord.Value)
            self._obj.TipLength2 = self._toPercent(self._obj.TipLength2.Value, self._obj.TipChord.Value)
        else:
            # Convert to lengths
            self._obj.TipLength1 = self._toLength(self._obj.TipLength1.Value, self._obj.TipChord.Value)
            self._obj.TipLength2 = self._toLength(self._obj.TipLength2.Value, self._obj.TipChord.Value)
        self._enableTipPercent()

    def onTipPerCent(self, value):
        self._obj.TipPerCent = self._finForm.form.tipPerCentCheckbox.isChecked()
        self._convertTipPercent()

        self.redraw()
        self.setEdited()

    def onTipLength1(self, value):
        try:
            self._obj.TipLength1 = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def onTipLength2(self, value):
        try:
            self._obj.TipLength2 = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def onFilletCrossSection(self, value : str) -> None:
        self._obj.FilletCrossSection = value

        self.redraw()
        self.setEdited()

    def onFillet(self, value : bool) -> None:
        self._obj.Fillets = value

        self.redraw()
        self.setEdited()

    def onFilletRadius(self, value : str) -> None:
        try:
            self._obj.FilletRadius = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def onHeight(self, value):
        try:
            self._obj.Proxy.setHeight(FreeCAD.Units.Quantity(value).Value)
            self._sweepAngleFromLength()
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def onAutoHeight(self, value):
        try:
            self._obj.Proxy.setAutoHeight(value)
            self._finForm.form.heightInput.setText(self._obj.Height.UserString)
            self._sweepAngleFromLength()
            self._setHeightState()
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def _setHeightState(self):
        if not self._isAssembly:
            self._obj.AutoHeight = False
        self._finForm.form.autoHeightCheckBox.setChecked(self._obj.AutoHeight)
        self._finForm.form.autoHeightCheckBox.setEnabled(self._isAssembly)
        self._finForm.form.heightInput.setEnabled(not self._obj.AutoHeight)
        self._finForm.form.spanInput.setEnabled(self._obj.AutoHeight)

    def onSpan(self, value):
        try:
            self._obj.Proxy.setSpan(FreeCAD.Units.Quantity(value).Value)
            self._finForm.form.heightInput.setText(self._obj.Height.UserString)
            self._sweepAngleFromLength()
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def _sweepLengthFromAngle(self):
        self._finForm.form.sweepLengthInput.setText(self._obj.SweepLength.UserString)

    def _sweepAngleFromLength(self):
        self._finForm.form.sweepAngleInput.setText(self._obj.SweepAngle.UserString)

    def onSweepLength(self, value):
        try:
            self._obj.Proxy.setSweepLength(FreeCAD.Units.Quantity(value).Value)
            self._sweepAngleFromLength()
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def onSweepAngle(self, value):
        try:
            self._obj.Proxy.setSweepAngle(FreeCAD.Units.Quantity(value).Value)
            self._sweepLengthFromAngle()
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def _setCanStyle(self):
        if self._obj.FinCanStyle == FINCAN_STYLE_SLEEVE:
            self._finForm.form.canDiameterLabel.setText(translate('Rocket', "Inner Diameter"))
            self._finForm.form.canLeadingGroup.setHidden(False)
            if self._isAssembly:
                self._finForm.form.couplerGroup.setEnabled(False)
            else:
                self._finForm.form.couplerGroup.setEnabled(True)
            self._obj.Coupler = False
        else:
            self._finForm.form.canDiameterLabel.setText(translate('Rocket', "Outer Diameter"))
            if self._isAssembly:
                self._finForm.form.canLeadingGroup.setHidden(True)
            else:
                self._finForm.form.canLeadingGroup.setHidden(False)
            self._finForm.form.couplerGroup.setEnabled(True)
        self._finForm.form.couplerGroup.setChecked(self._obj.Coupler)

    def onCanDiameter(self, value):
        try:
            self._obj.Diameter = FreeCAD.Units.Quantity(value).Value
            self._obj.ParentRadius = (self._obj.Diameter / 2.0) # + self._obj.Thickness
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def _setCanAutoDiameterState(self):
        if self._isAssembly:
            self._finForm.form.canDiameterInput.setEnabled(not self._obj.AutoDiameter)
            self._finForm.form.canAutoDiameterCheckbox.setChecked(self._obj.AutoDiameter)
        else:
            self._obj.AutoDiameter = False
            self._finForm.form.canAutoDiameterCheckbox.setEnabled(False)
            self._finForm.form.canDiameterInput.setEnabled(not self._obj.AutoDiameter)
            self._finForm.form.canAutoDiameterCheckbox.setChecked(self._obj.AutoDiameter)

        if self._obj.AutoDiameter:
            self._obj.Diameter = (self._obj.ParentRadius * 2.0)
            self._finForm.form.canDiameterInput.setText(self._obj.Diameter.UserString)

    def onCanAutoDiameter(self, value):
        self._obj.AutoDiameter = value
        self._setCanAutoDiameterState()

        self.redraw()
        self.setEdited()

    def onCanThickness(self, value):
        try:
            self._obj.Thickness = FreeCAD.Units.Quantity(value).Value
            self._obj.ParentRadius = (self._obj.Diameter / 2.0) # + self._obj.Thickness
            self._setLugAutoThicknessState()
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def onCanLength(self, value):
        try:
            self._obj.Length = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def onCanLeadingEdgeOffset(self, value):
        try:
            self._obj.LeadingEdgeOffset = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass
        self.setEdited()


    def _enableLeadingEdge(self):
        if self._obj.LeadingEdge == FINCAN_EDGE_SQUARE:
            self._finForm.form.canLeadingLengthInput.setEnabled(False)
        else:
            self._finForm.form.canLeadingLengthInput.setEnabled(True)

    def onCanLeadingEdge(self, value):
        if len(value) <= 0:
            return

        self._obj.LeadingEdge = value
        self._enableLeadingEdge()
        self._setLugAutoLengthState()

        self.redraw()
        self.setEdited()

    def onCanLeadingLength(self, value):
        try:
            self._obj.LeadingLength = FreeCAD.Units.Quantity(value).Value
            self._setLugAutoLengthState()
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def _enableTrailingEdge(self):
        if self._obj.TrailingEdge == FINCAN_EDGE_SQUARE:
            self._finForm.form.canTrailingLengthInput.setEnabled(False)
        else:
            self._finForm.form.canTrailingLengthInput.setEnabled(True)

    def onCanTrailingEdge(self, value):
        if len(value) <= 0:
            return

        self._obj.TrailingEdge = value
        self._enableTrailingEdge()
        self._setLugAutoLengthState()

        self.redraw()
        self.setEdited()

    def onCanTrailingLength(self, value):
        try:
            self._obj.TrailingLength = FreeCAD.Units.Quantity(value).Value
            self._setLugAutoLengthState()
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def onCoupler(self, value):
        self._obj.Coupler = self._finForm.form.couplerGroup.isChecked()

        self.redraw()

    def onCouplerStyle(self, value):
        self._obj.CouplerStyle = self._finForm.form.couplerStylesCombo.currentData()

        self.redraw()

    def onCouplerThickness(self, value):
        try:
            self._obj.CouplerThickness = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass

    def _setCouplerAutoDiameterState(self):
        if self._isAssembly:
            self._finForm.form.couplerDiameterInput.setEnabled(not self._obj.CouplerAutoDiameter)
            self._finForm.form.couplerAutoDiameterCheckbox.setChecked(self._obj.CouplerAutoDiameter)
        else:
            self._obj.CouplerAutoDiameter = False
            self._finForm.form.couplerAutoDiameterCheckbox.setEnabled(False)
            self._finForm.form.couplerDiameterInput.setEnabled(not self._obj.CouplerAutoDiameter)
            self._finForm.form.couplerAutoDiameterCheckbox.setChecked(self._obj.CouplerAutoDiameter)

        if self._obj.CouplerAutoDiameter:
            pass
            # self._obj.Diameter = (self._obj.ParentRadius * 2.0)
            # self._finForm.form.canDiameterInput.setText(self._obj.Diameter.UserString)

    def onCouplerAutoDiameter(self, value):
        self._obj.CouplerAutoDiameter = value
        self._setCouplerAutoDiameterState()

        self.redraw()
        self.setEdited()

    def onCouplerDiameter(self, value):
        try:
            self._obj.CouplerDiameter = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass

    def onCouplerLength(self, value):
        try:
            self._obj.CouplerLength = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass

    def onLug(self, value):
        self._obj.LaunchLug = self._finForm.form.lugGroup.isChecked()

        self.redraw()
        self.setEdited()

    def onLugInnerDiameter(self, value):
        try:
            self._obj.LugInnerDiameter = FreeCAD.Units.Quantity(value).Value
            self._finForm.form.lugPresetsCombo.setCurrentIndex(self._finForm.form.lugPresetsCombo.findData(FINCAN_PRESET_CUSTOM))
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def _setLugDiameter(self, value):
        try:
            self._obj.LugInnerDiameter = value
            self._finForm.form.lugInnerDiameterInput.setText(self._obj.LugInnerDiameter.UserString)
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def onLugPreset(self, value):
        if value == FINCAN_PRESET_1_8:
            self._setLugDiameter(3.56)
        elif value == FINCAN_PRESET_3_16:
            self._setLugDiameter(5.56)
        elif value == FINCAN_PRESET_1_4:
            self._setLugDiameter(6.35)

    def onLugThickness(self, value):
        try:
            self._obj.LugThickness = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def _setLugAutoThicknessState(self):
        self._finForm.form.lugThicknessInput.setEnabled(not self._obj.LugAutoThickness)
        self._finForm.form.lugAutoThicknessCheckbox.setChecked(self._obj.LugAutoThickness)

        if self._obj.LugAutoThickness:
            self._obj.LugThickness = self._obj.Thickness
            self._finForm.form.lugThicknessInput.setText(self._obj.Thickness.UserString)

    def onLugAutoThickness(self, value):
        self._obj.LugAutoThickness = value
        self._setLugAutoThicknessState()

        self.redraw()
        self.setEdited()

    def onLugLength(self, value):
        try:
            self._obj.LugLength = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def _setLugAutoLengthState(self):
        self._finForm.form.lugLengthInput.setEnabled(not self._obj.LugAutoLength)
        self._finForm.form.lugAutoLengthCheckbox.setChecked(self._obj.LugAutoLength)

        if self._obj.LugAutoLength:
            length = float(self._obj.Length)

            if self._obj.LugLeadingEdgeOffset > 0:
                length -= float(self._obj.LugLeadingEdgeOffset)
            elif self._obj.LeadingEdge != FINCAN_EDGE_SQUARE:
                length -= float(self._obj.LeadingLength)

            if self._obj.TrailingEdge != FINCAN_EDGE_SQUARE:
                length -= float(self._obj.TrailingLength)

            self._obj.LugLength = length
            self._finForm.form.lugLengthInput.setText(self._obj.LugLength.UserString)

    def onLugAutoLength(self, value):
        self._obj.LugAutoLength = value
        self._setLugAutoLengthState()

        self.redraw()
        self.setEdited()

    def onLugLeadingEdgeOffset(self, value):
        try:
            self._obj.LugLeadingEdgeOffset = FreeCAD.Units.Quantity(value).Value
            self._setLugAutoLengthState()
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def onLugFilletRadius(self, value):
        try:
            self._obj.LugFilletRadius = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def _setForwardSweepState(self):
        # self._finForm.form.forwardSweepInput.setEnabled(self._obj.LaunchLugForwardSweep)
        self._finForm.form.forwardSweepGroup.setChecked(self._obj.LaunchLugForwardSweep)

    def onForwardSweep(self, value):
        self._obj.LaunchLugForwardSweep = value
        self._setForwardSweepState()

        self.redraw()

    def onForwardSweepAngle(self, value):
        try:
            self._obj.LaunchLugForwardSweepAngle = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass

    def _setAftSweepState(self):
        # self._finForm.form.aftSweepInput.setEnabled(self._obj.LaunchLugAftSweep)
        self._finForm.form.aftSweepGroup.setChecked(self._obj.LaunchLugAftSweep)

    def onAftSweep(self, value):
        self._obj.LaunchLugAftSweep = value
        self._setAftSweepState()

        self.redraw()

    def onAftSweepAngle(self, value):
        try:
            self._obj.LaunchLugAftSweepAngle = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass

    def onLocation(self):
        self._obj.Proxy.updateChildren()
        self.redraw()
        self.setEdited()

    def onRedraw(self):
        self._obj.Proxy.execute(self._obj)
        self._redrawPending = False

    def onSetToScale(self) -> None:
        # Update the scale values
        scale = self._finForm.tabScaling.getScale()
        # self._obj.Length = self._obj.Length / scale

        scale = self._finForm.tabScaling.resetScale()

        self.update()

    def getStandardButtons(self):
        return QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Apply

    def clicked(self,button):
        if button == QtGui.QDialogButtonBox.Apply:
            self.transferTo()
            self.redraw()

    def update(self):
        'fills the widgets'
        self.transferFrom()

    def accept(self):
        self.transferTo()
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.resetEdit()


    def reject(self):
        FreeCAD.ActiveDocument.abortTransaction()
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.resetEdit()
