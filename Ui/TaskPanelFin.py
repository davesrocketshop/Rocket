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
import os

import FreeCAD
import FreeCADGui
import Part
import Sketcher

from PySide import QtGui, QtCore
from PySide.QtCore import QObject, Signal
from PySide.QtWidgets import QDialog, QGridLayout, QVBoxLayout, QSizePolicy, QTextEdit
import math

from DraftTools import translate

from Ui.TaskPanelLocation import TaskPanelLocation
from Ui.Commands.CmdSketcher import newSketchNoEdit
from Ui.UIPaths import getUIPath

from Ui.Widgets.MaterialTab import MaterialTab
from Ui.Widgets.CommentTab import CommentTab
from Ui.Widgets.ScalingTab import ScalingTabFins

from Rocket.Constants import FIN_TYPE_TRAPEZOID, FIN_TYPE_TRIANGLE, FIN_TYPE_ELLIPSE, FIN_TYPE_TUBE, FIN_TYPE_SKETCH
from Rocket.Constants import FIN_CROSS_SAME, FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, \
    FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE, FIN_CROSS_BICONVEX, FIN_CROSS_ELLIPSE
from Rocket.Constants import FIN_EDGE_SQUARE, FIN_EDGE_ROUNDED

from Rocket.Utilities import _err, _toFloat

# Main tab indices
TAB_GENERAL = 0
TAB_FINTABS = 1
TAB_FINCAN = 2
TAB_COUPLER = 3
TAB_LAUNCHLUG = 4
TAB_SCALING = 5
TAB_MATERIAL = 6
TAB_COMMENT = 7

# Tab Cross Section indices
TAB_FIN_ROOT = 0
TAB_FIN_TIP = 1
TAB_FIN_TUBE = 2
TAB_FIN_FILLETS = 3

# This dialog is shared with TaskPanelFinCan
class _FinDialog(QDialog):

    def __init__(self, obj : Any, parent : QtGui.QWidget = None) -> None:
        super().__init__(parent)

        self.form = FreeCADGui.PySideUic.loadUi(os.path.join(getUIPath(), 'Ui', "TaskPanelFin.ui"))
        self.initUI(obj)

    def initUI(self, obj : Any) -> None:
        # define our window
        self.setGeometry(250, 250, 400, 350)
        self.setWindowTitle(translate('Rocket', "Fin Parameter"))

        self.tabScaling = ScalingTabFins(obj)
        self.tabMaterial = MaterialTab()
        self.tabComment = CommentTab()
        self.form.tabWidget.addTab(self.tabScaling, translate('Rocket', "Scaling"))
        self.form.tabWidget.addTab(self.tabMaterial, translate('Rocket', "Material"))
        self.form.tabWidget.addTab(self.tabComment, translate('Rocket', "Comment"))

        # Hide unused tabs
        self.form.tabWidget.setTabVisible(TAB_FINCAN, False)
        self.form.tabWidget.setTabVisible(TAB_COUPLER, False)
        self.form.tabWidget.setTabVisible(TAB_LAUNCHLUG, False)

        self.setTabGeneral()
        self.setTabTtw()

    def setTabGeneral(self) -> None:
        # Select the type of fin
        self.form.finTypesCombo.addItem(translate('Rocket', FIN_TYPE_TRAPEZOID), FIN_TYPE_TRAPEZOID)
        self.form.finTypesCombo.addItem(translate('Rocket', FIN_TYPE_TRIANGLE), FIN_TYPE_TRIANGLE)
        self.form.finTypesCombo.addItem(translate('Rocket', FIN_TYPE_ELLIPSE), FIN_TYPE_ELLIPSE)
        self.form.finTypesCombo.addItem(translate('Rocket', FIN_TYPE_TUBE), FIN_TYPE_TUBE)
        self.form.finTypesCombo.addItem(translate('Rocket', FIN_TYPE_SKETCH), FIN_TYPE_SKETCH)

        # Set the units
        self.form.finSpacingInput.unit = FreeCAD.Units.Angle
        self.form.finCantInput.unit = FreeCAD.Units.Angle
        self.form.heightInput.unit = FreeCAD.Units.Length
        self.form.spanInput.unit = FreeCAD.Units.Length
        self.form.sweepLengthInput.unit = FreeCAD.Units.Length
        self.form.sweepAngleInput.unit = FreeCAD.Units.Angle
        self.form.minimumEdgeSizeInput.unit = FreeCAD.Units.Length

        self.setTabFinRoot()
        self.setTabFinTip()
        self.setTabFinTube()

    def setTabFinRoot(self) -> None:

        # # Select the type of cross section
        self.form.rootCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_SQUARE), FIN_CROSS_SQUARE)
        self.form.rootCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_ROUND), FIN_CROSS_ROUND)
        self.form.rootCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_ELLIPSE), FIN_CROSS_ELLIPSE)
        self.form.rootCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_BICONVEX), FIN_CROSS_BICONVEX)
        self.form.rootCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_AIRFOIL), FIN_CROSS_AIRFOIL)
        self.form.rootCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_WEDGE), FIN_CROSS_WEDGE)
        self.form.rootCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_DIAMOND), FIN_CROSS_DIAMOND)
        self.form.rootCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_TAPER_LE), FIN_CROSS_TAPER_LE)
        self.form.rootCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_TAPER_TE), FIN_CROSS_TAPER_TE)
        self.form.rootCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_TAPER_LETE), FIN_CROSS_TAPER_LETE)

        # Set the units
        self.form.rootChordInput.unit = FreeCAD.Units.Length
        self.form.rootThicknessInput.unit = FreeCAD.Units.Length
        self.form.rootLength1Input.unit = FreeCAD.Units.Length
        self.form.rootLength2Input.unit = FreeCAD.Units.Length

    def setTabFinTip(self) -> None:

        # Select the type of cross section
        self.form.tipCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_SAME), FIN_CROSS_SAME)
        self.form.tipCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_SQUARE), FIN_CROSS_SQUARE)
        self.form.tipCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_ROUND), FIN_CROSS_ROUND)
        self.form.tipCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_ELLIPSE), FIN_CROSS_ELLIPSE)
        self.form.tipCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_BICONVEX), FIN_CROSS_BICONVEX)
        self.form.tipCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_AIRFOIL), FIN_CROSS_AIRFOIL)
        self.form.tipCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_WEDGE), FIN_CROSS_WEDGE)
        self.form.tipCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_DIAMOND), FIN_CROSS_DIAMOND)
        self.form.tipCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_TAPER_LE), FIN_CROSS_TAPER_LE)
        self.form.tipCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_TAPER_TE), FIN_CROSS_TAPER_TE)
        self.form.tipCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_TAPER_LETE), FIN_CROSS_TAPER_LETE)

        # Set the units
        self.form.tipChordInput.unit = FreeCAD.Units.Length
        self.form.tipThicknessInput.unit = FreeCAD.Units.Length
        self.form.tipLength1Input.unit = FreeCAD.Units.Length
        self.form.tipLength2Input.unit = FreeCAD.Units.Length

    def setTabFinTube(self) -> None:

        # Set the units
        self.form.tubeLengthInput.unit = FreeCAD.Units.Length
        self.form.tubeOuterDiameterInput.unit = FreeCAD.Units.Length
        self.form.tubeThicknessInput.unit = FreeCAD.Units.Length

    def setTabTtw(self) -> None:

        # Set the units
        self.form.ttwOffsetInput.unit = FreeCAD.Units.Length
        self.form.ttwLengthInput.unit = FreeCAD.Units.Length
        self.form.ttwHeightInput.unit = FreeCAD.Units.Length
        self.form.ttwThicknessInput.unit = FreeCAD.Units.Length

    def getGridLayout(self):
        grid = QGridLayout()
        grid.setHorizontalSpacing(7)
        grid.setVerticalSpacing(7)
        return grid

class TaskPanelFin(QObject):

    redrawRequired = Signal()   # Allows for async redraws to allow for longer processing times

    def __init__(self, obj : Any, mode : int) -> None:
        super().__init__()

        self._obj = obj
        self._isAssembly = self._obj.Proxy.isRocketAssembly()

        self._finForm = _FinDialog(obj)

        self._location = TaskPanelLocation(obj)
        self._locationForm = self._location.getForm()

        self.form = [self._finForm.form, self._locationForm]
        self._finForm.setWindowIcon(QtGui.QIcon(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Fin.svg"))

        self._finForm.form.finTypesCombo.currentTextChanged.connect(self.onFinTypes)

        self._finForm.form.finSetGroup.toggled.connect(self.onFinSet)
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

        self._finForm.form.tubeLengthInput.textEdited.connect(self.onTubeLength)
        self._finForm.form.tubeOuterDiameterInput.textEdited.connect(self.onTubeOuterDiameter)
        self._finForm.form.tubeAutoOuterDiameterCheckbox.stateChanged.connect(self.onTubeAutoOuterDiameter)
        self._finForm.form.tubeThicknessInput.textEdited.connect(self.onTubeThickness)

        self._finForm.form.heightInput.textEdited.connect(self.onHeight)
        self._finForm.form.autoHeightCheckBox.stateChanged.connect(self.onAutoHeight)
        self._finForm.form.spanInput.textEdited.connect(self.onSpan)
        self._finForm.form.sweepLengthInput.textEdited.connect(self.onSweepLength)
        self._finForm.form.sweepAngleInput.textEdited.connect(self.onSweepAngle)

        self._finForm.form.ttwGroup.toggled.connect(self.onTtw)
        self._finForm.form.ttwOffsetInput.textEdited.connect(self.onTTWOffset)
        self._finForm.form.ttwLengthInput.textEdited.connect(self.onTTWLength)
        self._finForm.form.ttwHeightInput.textEdited.connect(self.onTTWHeight)
        self._finForm.form.ttwAutoHeightCheckbox.stateChanged.connect(self.onTTWAutoHeight)
        self._finForm.form.ttwThicknessInput.textEdited.connect(self.onTTWThickness)

        self._finForm.form.minimumEdgeGroup.toggled.connect(self.onMinimumEdge)
        self._finForm.form.minimumEdgeSizeInput.textEdited.connect(self.onMinimumEdgeSize)

        self._finForm.tabScaling.scaled.connect(self.onScale)
        self._finForm.tabScaling.scaledSetValuesButton.clicked.connect(self.onSetToScale)

        self._location.locationChange.connect(self.onLocation)

        self._redrawPending = False
        self.redrawRequired.connect(self.onRedraw, QtCore.Qt.QueuedConnection)

        self.update()

        if mode == 0: # fresh created
            self.redraw()  # calculate once
            FreeCAD.Gui.SendMsgToActiveView("ViewFit")

    def transferTo(self) -> None:
        "Transfer from the dialog to the object"
        self._obj.FinType = str(self._finForm.form.finTypesCombo.currentData())

        self._obj.FinSet = self._finForm.form.finSetGroup.isChecked()
        self._obj.FinCount = self._finForm.form.finCountSpinBox.value()
        self._obj.FinSpacing = self._finForm.form.finSpacingInput.text()
        self._obj.Cant = self._finForm.form.finCantInput.text()

        self._obj.RootCrossSection = str(self._finForm.form.rootCrossSectionsCombo.currentData())
        if self._obj.FinType != FIN_TYPE_TUBE:
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

        if self._obj.FinType == FIN_TYPE_TUBE:
            self._obj.RootChord = self._finForm.form.tubeLengthInput.text()
        self._obj.TubeOuterDiameter = self._finForm.form.tubeOuterDiameterInput.text()
        self._obj.TubeAutoOuterDiameter = self._finForm.form.tubeAutoOuterDiameterCheckbox.isChecked()
        self._obj.TubeThickness = self._finForm.form.tubeThicknessInput.text()

        self._obj.Height = self._finForm.form.heightInput.text()
        self._obj.AutoHeight = self._finForm.form.autoHeightCheckBox.isChecked()
        self._obj.Span = self._finForm.form.spanInput.text()
        self._obj.SweepLength = self._finForm.form.sweepLengthInput.text()
        self._obj.SweepAngle = self._finForm.form.sweepAngleInput.text()

        self._obj.Ttw = self._finForm.form.ttwGroup.isChecked()
        self._obj.TtwOffset = self._finForm.form.ttwOffsetInput.text()
        self._obj.TtwLength = self._finForm.form.ttwLengthInput.text()
        self._obj.TtwHeight = self._finForm.form.ttwHeightInput.text()
        self._obj.TtwAutoHeight = self._finForm.form.ttwAutoHeightCheckbox.isChecked()
        self._obj.TtwThickness = self._finForm.form.ttwThicknessInput.text()

        self._obj.MinimumEdge = self._finForm.form.minimumEdgeGroup.isChecked()
        self._obj.MinimumEdgeSize = self._finForm.form.minimumEdgeSizeInput.text()

        self._finForm.tabScaling.transferTo(self._obj)
        self._finForm.tabMaterial.transferTo(self._obj)
        self._finForm.tabComment.transferTo(self._obj)

    def transferFrom(self) -> None:
        "Transfer from the object to the dialog"
        self._finForm.form.finTypesCombo.setCurrentIndex(self._finForm.form.finTypesCombo.findData(self._obj.FinType))

        self._finForm.form.finSetGroup.setChecked(self._obj.FinSet)
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

        self._finForm.form.tubeLengthInput.setText(self._obj.RootChord.UserString)
        self._finForm.form.tubeOuterDiameterInput.setText(self._obj.TubeOuterDiameter.UserString)
        self._finForm.form.tubeAutoOuterDiameterCheckbox.setChecked(self._obj.TubeAutoOuterDiameter)
        self._finForm.form.tubeThicknessInput.setText(self._obj.TubeThickness.UserString)

        self._finForm.form.heightInput.setText(self._obj.Height.UserString)
        self._finForm.form.autoHeightCheckBox.setChecked(self._obj.AutoHeight)
        self._finForm.form.spanInput.setText(self._obj.Span.UserString)
        self._finForm.form.sweepLengthInput.setText(self._obj.SweepLength.UserString)
        self._finForm.form.sweepAngleInput.setText(self._obj.SweepAngle.UserString)

        self._finForm.form.ttwGroup.setChecked(self._obj.Ttw)
        self._finForm.form.ttwOffsetInput.setText(self._obj.TtwOffset.UserString)
        self._finForm.form.ttwLengthInput.setText(self._obj.TtwLength.UserString)
        self._finForm.form.ttwHeightInput.setText(self._obj.TtwHeight.UserString)
        self._finForm.form.ttwAutoHeightCheckbox.setChecked(self._obj.TtwAutoHeight)
        self._finForm.form.ttwThicknessInput.setText(self._obj.TtwThickness.UserString)

        self._finForm.form.minimumEdgeGroup.setChecked(self._obj.MinimumEdge)
        self._finForm.form.minimumEdgeSizeInput.setText(self._obj.MinimumEdgeSize.UserString)

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
        self._setTtwState()

    def setEdited(self) -> None:
        try:
            self._obj.Proxy.setEdited()
        except ReferenceError:
            # Object may be deleted
            pass

    def redraw(self) -> None:
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

    def onFinTypes(self, value : str) -> None:
        self._obj.FinType = value
        self._enableFinTypes()
        self.redraw()
        self.setEdited()

        # Scaling information is fin type dependent
        self.onScale()

    def _setFinSetState(self) -> None:
        if self._isAssembly:
            checked = self._finForm.form.finSetGroup.isChecked()
            self._finForm.form.finSetGroup.setEnabled(True)
        else:
            if self._obj.FinSet:
                self._obj.FinSet = False
                self._finForm.form.finSetGroup.setChecked(self._obj.FinSet)
            checked = False
            self._finForm.form.finSetGroup.setEnabled(False)

        self._finForm.form.finCountSpinBox.setEnabled(checked)
        self._finForm.form.finSpacingInput.setEnabled(checked)
        self._finForm.form.finCantInput.setEnabled(self._isAssembly)
        self._finForm.form.tipThicknessInput.setEnabled(not self._obj.TipSameThickness)

    def onFinSet(self, value : bool) -> None:
        self._obj.FinSet = self._finForm.form.finSetGroup.isChecked()
        self._setFinSetState()
        self.redraw()
        self.setEdited()

    def onCount(self, value : int) -> None:
        self._obj.FinCount = value
        self._obj.FinSpacing = 360.0 / float(value)
        self._finForm.form.finSpacingInput.setText(self._obj.FinSpacing.UserString)
        self._obj.Proxy.getTubeOuterDiameter() # Set automatic sizing
        self._finForm.form.tubeOuterDiameterInput.setText(self._obj.TubeOuterDiameter.UserString)
        self.redraw()
        self.setEdited()

    def onSpacing(self, value : str) -> None:
        self._obj.FinSpacing = value
        self.redraw()
        self.setEdited()

    def onCant(self, value : str) -> None:
        self._obj.Cant = value
        self.redraw()
        self.setEdited()

    def _enableFinTypes(self) -> None:
        if self._obj.FinType == FIN_TYPE_TRAPEZOID:
            self._enableFinTypeTrapezoid()
        elif self._obj.FinType == FIN_TYPE_TRIANGLE:
            self._enableFinTypeTriangle()
        elif self._obj.FinType == FIN_TYPE_ELLIPSE:
            self._enableFinTypeEllipse()
        elif self._obj.FinType == FIN_TYPE_TUBE:
            self._enableFinTypeTube()
        else:
            self._enableFinTypeSketch()
        self.onScale()

    def setRootCrossSections(self) -> None:
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

    def setEllipseRootCrossSections(self) -> None:
        self._finForm.form.rootCrossSectionsCombo.clear()
        self._finForm.form.rootCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_SQUARE), FIN_CROSS_SQUARE)
        self._finForm.form.rootCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_ROUND), FIN_CROSS_ROUND)
        self._finForm.form.rootCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_ELLIPSE), FIN_CROSS_ELLIPSE)
        self._finForm.form.rootCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_BICONVEX), FIN_CROSS_BICONVEX)
        self._finForm.form.rootCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_AIRFOIL), FIN_CROSS_AIRFOIL)
        self._finForm.form.rootCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_WEDGE), FIN_CROSS_WEDGE)
        self._finForm.form.rootCrossSectionsCombo.addItem(translate('Rocket', FIN_CROSS_TAPER_LETE), FIN_CROSS_TAPER_LETE)


    def _enableFinTypeTrapezoid(self) -> None:
        self._finForm.form.tabWidget.setTabEnabled(1, True) # Fin tabs is index 1

        self._finForm.form.rootChordInput.setText(self._obj.RootChord.UserString)

        old = self._obj.RootCrossSection # This must be saved and restored
        self.setRootCrossSections()
        self._obj.RootCrossSection = old

        self._finForm.form.rootCrossSectionsCombo.setCurrentIndex(self._finForm.form.rootCrossSectionsCombo.findData(self._obj.RootCrossSection))

        self._finForm.form.heightLabel.setHidden(False)
        self._finForm.form.heightInput.setHidden(False)
        self._finForm.form.autoHeightCheckBox.setHidden(False)

        self._finForm.form.spanLabel.setHidden(False)
        self._finForm.form.spanInput.setHidden(False)

        self._finForm.form.sweepLengthLabel.setHidden(False)
        self._finForm.form.sweepLengthInput.setHidden(False)
        self._finForm.form.sweepAngleLabel.setHidden(False)
        self._finForm.form.sweepAngleInput.setHidden(False)

        self._finForm.form.rootChordLabel.setHidden(False)
        self._finForm.form.rootChordInput.setHidden(False)
        self._finForm.form.rootLength2Label.setHidden(False)
        self._finForm.form.rootLength2Input.setHidden(False)

        self._finForm.form.tabCrossSections.setTabVisible(TAB_FIN_ROOT, True)
        self._finForm.form.tabCrossSections.setTabVisible(TAB_FIN_TIP, True)
        self._finForm.form.tabCrossSections.setTabVisible(TAB_FIN_TUBE, False)
        self._finForm.form.tabCrossSections.setTabVisible(TAB_FIN_FILLETS, False)
        self._finForm.form.minimumEdgeGroup.setHidden(False)

        self._enableTipLengths()

    def _enableFinTypeTriangle(self) -> None:
        self._finForm.form.tabWidget.setTabEnabled(1, True) # Fin tabs is index 1

        self._finForm.form.rootChordInput.setText(self._obj.RootChord.UserString)

        old = self._obj.RootCrossSection # This must be saved and restored
        self.setRootCrossSections()
        self._obj.RootCrossSection = old

        self._finForm.form.rootCrossSectionsCombo.setCurrentIndex(self._finForm.form.rootCrossSectionsCombo.findData(self._obj.RootCrossSection))

        self._finForm.form.heightLabel.setHidden(False)
        self._finForm.form.heightInput.setHidden(False)
        self._finForm.form.autoHeightCheckBox.setHidden(False)

        self._finForm.form.spanLabel.setHidden(False)
        self._finForm.form.spanInput.setHidden(False)

        self._finForm.form.sweepLengthLabel.setHidden(False)
        self._finForm.form.sweepLengthInput.setHidden(False)
        self._finForm.form.sweepAngleLabel.setHidden(False)
        self._finForm.form.sweepAngleInput.setHidden(False)

        self._finForm.form.rootChordLabel.setHidden(False)
        self._finForm.form.rootChordInput.setHidden(False)
        self._finForm.form.rootLength2Label.setHidden(False)
        self._finForm.form.rootLength2Input.setHidden(False)

        self._finForm.form.tabCrossSections.setTabVisible(TAB_FIN_ROOT, True)
        self._finForm.form.tabCrossSections.setTabVisible(TAB_FIN_TIP, False)
        self._finForm.form.tabCrossSections.setTabVisible(TAB_FIN_TUBE, False)
        self._finForm.form.tabCrossSections.setTabVisible(TAB_FIN_FILLETS, False)
        self._finForm.form.minimumEdgeGroup.setHidden(False)

    def _enableFinTypeEllipse(self) -> None:
        self._finForm.form.tabWidget.setTabEnabled(1, True) # Fin tabs is index 1

        self._finForm.form.rootChordInput.setText(self._obj.RootChord.UserString)

        old = self._obj.RootCrossSection # This must be saved and restored
        self.setEllipseRootCrossSections()
        self._obj.RootCrossSection = old

        if self._obj.RootCrossSection in [FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE]:
            self._obj.RootCrossSection = FIN_CROSS_TAPER_LETE
        self._finForm.form.rootCrossSectionsCombo.setCurrentIndex(self._finForm.form.rootCrossSectionsCombo.findData(self._obj.RootCrossSection))

        self._finForm.form.heightLabel.setHidden(False)
        self._finForm.form.heightInput.setHidden(False)
        self._finForm.form.autoHeightCheckBox.setHidden(False)

        self._finForm.form.spanLabel.setHidden(False)
        self._finForm.form.spanInput.setHidden(False)

        self._finForm.form.sweepLengthLabel.setHidden(True)
        self._finForm.form.sweepLengthInput.setHidden(True)
        self._finForm.form.sweepAngleLabel.setHidden(True)
        self._finForm.form.sweepAngleInput.setHidden(True)

        self._finForm.form.rootChordLabel.setHidden(False)
        self._finForm.form.rootChordInput.setHidden(False)
        self._finForm.form.rootLength2Label.setHidden(True)
        self._finForm.form.rootLength2Input.setHidden(True)

        self._finForm.form.tabCrossSections.setTabVisible(TAB_FIN_ROOT, True)
        self._finForm.form.tabCrossSections.setTabVisible(TAB_FIN_TIP, False)
        self._finForm.form.tabCrossSections.setTabVisible(TAB_FIN_TUBE, False)
        self._finForm.form.tabCrossSections.setTabVisible(TAB_FIN_FILLETS, False)
        self._finForm.form.minimumEdgeGroup.setHidden(False)

    def _enableFinTypeTube(self) -> None:
        self._finForm.form.tabWidget.setTabEnabled(1, False) # Fin tabs is index 1
        self._obj.Ttw = False
        self._finForm.form.ttwGroup.setChecked(self._obj.Ttw)

        self._finForm.form.tubeLengthInput.setText(self._obj.RootChord.UserString)

        self._finForm.form.heightLabel.setHidden(True)
        self._finForm.form.heightInput.setHidden(True)
        self._finForm.form.autoHeightCheckBox.setHidden(True)

        self._finForm.form.spanLabel.setHidden(True)
        self._finForm.form.spanInput.setHidden(True)

        self._finForm.form.sweepLengthLabel.setHidden(True)
        self._finForm.form.sweepLengthInput.setHidden(True)
        self._finForm.form.sweepAngleLabel.setHidden(True)
        self._finForm.form.sweepAngleInput.setHidden(True)

        self._finForm.form.tabCrossSections.setTabVisible(TAB_FIN_ROOT, False)
        self._finForm.form.tabCrossSections.setTabVisible(TAB_FIN_TIP, False)
        self._finForm.form.tabCrossSections.setTabVisible(TAB_FIN_TUBE, True)
        self._finForm.form.tabCrossSections.setTabVisible(TAB_FIN_FILLETS, False)
        self._finForm.form.minimumEdgeGroup.setHidden(True)

        if self._isAssembly:
            self._finForm.form.tubeAutoOuterDiameterCheckbox.setHidden(False)
        else:
            self._finForm.form.tubeAutoOuterDiameterCheckbox.setHidden(True)
            self._obj.TubeAutoOuterDiameter = False
        self._finForm.form.tubeAutoOuterDiameterCheckbox.setChecked(self._obj.TubeAutoOuterDiameter)
        self._finForm.form.tubeOuterDiameterInput.setEnabled(not self._obj.TubeAutoOuterDiameter)

    def _enableFinTypeSketch(self) -> None:
        self._finForm.form.tabWidget.setTabEnabled(1, True) # Fin tabs is index 1

        old = self._obj.RootCrossSection # This must be saved and restored
        self.setRootCrossSections()
        self._obj.RootCrossSection = old

        self._finForm.form.rootCrossSectionsCombo.setCurrentIndex(self._finForm.form.rootCrossSectionsCombo.findData(self._obj.RootCrossSection))

        self._finForm.form.heightLabel.setHidden(True)
        self._finForm.form.heightInput.setHidden(True)
        self._finForm.form.autoHeightCheckBox.setHidden(True)

        self._finForm.form.spanLabel.setHidden(True)
        self._finForm.form.spanInput.setHidden(True)

        self._finForm.form.sweepLengthLabel.setHidden(True)
        self._finForm.form.sweepLengthInput.setHidden(True)
        self._finForm.form.sweepAngleLabel.setHidden(True)
        self._finForm.form.sweepAngleInput.setHidden(True)

        self._finForm.form.rootChordLabel.setHidden(True)
        self._finForm.form.rootChordInput.setHidden(True)

        self._finForm.form.tabCrossSections.setTabVisible(TAB_FIN_ROOT, True)
        self._finForm.form.tabCrossSections.setTabVisible(TAB_FIN_TIP, False)
        self._finForm.form.tabCrossSections.setTabVisible(TAB_FIN_TUBE, False)
        self._finForm.form.tabCrossSections.setTabVisible(TAB_FIN_FILLETS, False)
        self._finForm.form.minimumEdgeGroup.setHidden(False)

        # Create a default sketch if none exists
        self._defaultFinSketch()

    def _drawLines(self, sketch : Any, points : list) -> None:
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

    def _defaultFinSketch(self) -> None:
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

    def _enableRootLengths(self) -> None:
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

    def _enableTipLengths(self) -> None:
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

    def onRootCrossSection(self, value : str) -> None:
        if len(value) <= 0:
            return

        self._obj.RootCrossSection = value
        self._enableRootLengths()

        if self._obj.TipCrossSection == FIN_CROSS_SAME:
            self._enableTipLengths()

        self.redraw()
        self.setEdited()

    def onRootChord(self, value : str) -> None:
        try:
            self._obj.RootChord = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def onRootThickness(self, value : str) -> None:
        try:
            self._obj.RootThickness = FreeCAD.Units.Quantity(value).Value
            if self._obj.TipSameThickness:
                self._obj.TipThickness = FreeCAD.Units.Quantity(value).Value
                self._finForm.form.tipThicknessInput.setText(self._obj.TipThickness.UserString)
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def _toPercent(self, length : float, chord : float) -> float:
        percent = 100.0 * length / chord
        if percent > 100.0:
            percent = 100.0
        if percent < 0.0:
            percent = 0.0
        return percent

    def _toLength(self, percent : float, chord : float) -> float:
        length = percent * chord / 100.0
        if length > chord:
            length = chord
        if length < 0.0:
            length = 0.0
        return length

    def _enableRootPercent(self) -> None:
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

    def _convertRootPercent(self) -> None:
        if self._obj.RootPerCent:
            # Convert to percentages
            self._obj.RootLength1 = self._toPercent(self._obj.RootLength1.Value, self._obj.RootChord.Value)
            self._obj.RootLength2 = self._toPercent(self._obj.RootLength2.Value, self._obj.RootChord.Value)
        else:
            # Convert to lengths
            self._obj.RootLength1 = self._toLength(self._obj.RootLength1.Value, self._obj.RootChord.Value)
            self._obj.RootLength2 = self._toLength(self._obj.RootLength2.Value, self._obj.RootChord.Value)
        self._enableRootPercent()

    def onRootPerCent(self, value : str) -> None:
        self._obj.RootPerCent = self._finForm.form.rootPerCentCheckbox.isChecked()
        self._convertRootPercent()

        self.redraw()
        self.setEdited()

    def onRootLength1(self, value : str) -> None:
        try:
            self._obj.RootLength1 = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def onRootLength2(self, value : str) -> None:
        try:
            self._obj.RootLength2 = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def onTipCrossSection(self, value : str) -> None:
        self._obj.TipCrossSection = value
        self._enableTipLengths()

        self.redraw()
        self.setEdited()

    def onTipChord(self, value : str) -> None:
        try:
            self._obj.Proxy.setTipChord(FreeCAD.Units.Quantity(value).Value)
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def onTipThickness(self, value : str) -> None:
        try:
            self._obj.Proxy.setTipThickness(FreeCAD.Units.Quantity(value).Value)
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def onTipSameThickness(self, value : bool) -> None:
        try:
            self._obj.TipSameThickness = value
            self.redraw()
            self._setFinSetState()
        except ValueError:
            pass
        self.setEdited()

    def _enableTipPercent(self) -> None:
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

    def _convertTipPercent(self) -> None:
        if self._obj.TipPerCent:
            # Convert to percentages
            self._obj.TipLength1 = self._toPercent(self._obj.TipLength1.Value, self._obj.TipChord.Value)
            self._obj.TipLength2 = self._toPercent(self._obj.TipLength2.Value, self._obj.TipChord.Value)
        else:
            # Convert to lengths
            self._obj.TipLength1 = self._toLength(self._obj.TipLength1.Value, self._obj.TipChord.Value)
            self._obj.TipLength2 = self._toLength(self._obj.TipLength2.Value, self._obj.TipChord.Value)
        self._enableTipPercent()

    def onTipPerCent(self, value : bool) -> None:
        self._obj.TipPerCent = self._finForm.form.tipPerCentCheckbox.isChecked()
        self._convertTipPercent()

        self.redraw()
        self.setEdited()

    def onTipLength1(self, value : str) -> None:
        try:
            self._obj.TipLength1 = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def onTipLength2(self, value : str) -> None:
        try:
            self._obj.TipLength2 = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def onTubeLength(self, value):
        self.onRootChord(value)

    def onTubeOuterDiameter(self, value : str) -> None:
        try:
            self._obj.TubeOuterDiameter = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def onTubeAutoOuterDiameter(self, value : bool) -> None:
        self._obj.TubeAutoOuterDiameter = value
        self._finForm.form.tubeOuterDiameterInput.setEnabled(not self._obj.TubeAutoOuterDiameter)

        # Set automatic sizing
        if self._obj.TubeAutoOuterDiameter:
            self._obj.Proxy.getTubeOuterDiameter()
            self._finForm.form.tubeOuterDiameterInput.setText(self._obj.TubeOuterDiameter.UserString)

        self.redraw()
        self.setEdited()

    def onTubeThickness(self, value : str) -> None:
        try:
            self._obj.TubeThickness = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def onHeight(self, value : str) -> None:
        try:
            self._obj.Proxy.setHeight(FreeCAD.Units.Quantity(value).Value)
            self._sweepAngleFromLength()
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def onAutoHeight(self, value : bool) -> None:
        try:
            self._obj.Proxy.setAutoHeight(value)
            self._finForm.form.heightInput.setText(self._obj.Height.UserString)
            self._sweepAngleFromLength()
            self._setHeightState()
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def _setHeightState(self) -> None:
        if not self._isAssembly:
            self._obj.AutoHeight = False
        self._finForm.form.autoHeightCheckBox.setChecked(self._obj.AutoHeight)
        self._finForm.form.autoHeightCheckBox.setEnabled(self._isAssembly)
        self._finForm.form.heightInput.setEnabled(not self._obj.AutoHeight)
        self._finForm.form.spanInput.setEnabled(self._obj.AutoHeight)

    def onSpan(self, value : str) -> None:
        try:
            self._obj.Proxy.setSpan(FreeCAD.Units.Quantity(value).Value)
            self._finForm.form.heightInput.setText(self._obj.Height.UserString)
            self._sweepAngleFromLength()
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def _sweepLengthFromAngle(self) -> None:
        self._finForm.form.sweepLengthInput.setText(self._obj.SweepLength.UserString)

    def _sweepAngleFromLength(self) -> None:
        self._finForm.form.sweepAngleInput.setText(self._obj.SweepAngle.UserString)

    def onSweepLength(self, value : str) -> None:
        try:
            self._obj.Proxy.setSweepLength(FreeCAD.Units.Quantity(value).Value)
            self._sweepAngleFromLength()
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def onSweepAngle(self, value : str) -> None:
        try:
            self._obj.Proxy.setSweepAngle(FreeCAD.Units.Quantity(value).Value)
            self._sweepLengthFromAngle()
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def _setTtwState(self) -> None:
        self._finForm.form.ttwOffsetInput.setEnabled(self._obj.Ttw)
        self._finForm.form.ttwLengthInput.setEnabled(self._obj.Ttw)
        if not self._isAssembly:
            self._obj.TtwAutoHeight = False
        self._finForm.form.ttwAutoHeightCheckbox.setChecked(self._obj.TtwAutoHeight)
        self._finForm.form.ttwAutoHeightCheckbox.setEnabled(self._isAssembly)
        self._finForm.form.ttwHeightInput.setEnabled(self._obj.Ttw and not self._obj.TtwAutoHeight)
        self._finForm.form.ttwThicknessInput.setEnabled(self._obj.Ttw)

    def onTtw(self, value : bool) -> None:
        self._obj.Ttw = self._finForm.form.ttwGroup.isChecked()
        self._setTtwState()

        self.redraw()
        self.setEdited()

    def onTTWOffset(self, value : str) -> None:
        try:
            self._obj.TtwOffset = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def onTTWLength(self, value : str) -> None:
        try:
            self._obj.TtwLength = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def onTTWHeight(self, value : str) -> None:
        try:
            self._obj.TtwHeight = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def onTTWAutoHeight(self, value : bool) -> None:
        try:
            self._obj.TtwAutoHeight = value
            self.redraw()
            self._setTtwState()
        except ValueError:
            pass
        self.setEdited()

    def onTTWThickness(self, value : str) -> None:
        try:
            self._obj.TtwThickness = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def onMinimumEdge(self, value : bool) -> None:
        self._obj.MinimumEdge = self._finForm.form.minimumEdgeGroup.isChecked()

        self.redraw()
        self.setEdited()

    def onMinimumEdgeSize(self, value : str) -> None:
        try:
            self._obj.MinimumEdgeSize = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def onLocation(self) -> None:
        self._obj.Proxy.updateChildren()
        self.redraw()
        self.setEdited()

    def onRedraw(self) -> None:
        self._obj.Proxy.execute(self._obj)
        self._redrawPending = False

    def onSetToScale(self) -> None:
        # Update the scale values
        scale = self._finForm.tabScaling.getScale()
        # self._obj.Length = self._obj.Length / scale

        scale = self._finForm.tabScaling.resetScale()

        self.update()

    def getStandardButtons(self) -> Any:
        return QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Apply

    def clicked(self, button : Any) -> None:
        if button == QtGui.QDialogButtonBox.Apply:
            self.transferTo()
            self.redraw()

    def update(self) -> None:
        'fills the widgets'
        self.transferFrom()

    def accept(self) -> None:
        self.transferTo()
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.resetEdit()


    def reject(self) -> None:
        FreeCAD.ActiveDocument.abortTransaction()
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.resetEdit()
        self.setEdited()
