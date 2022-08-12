# ***************************************************************************
# *   Copyright (c) 2021 David Carter <dcarter@davidcarter.ca>              *
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
    

import FreeCAD
import FreeCADGui

from PySide import QtGui, QtCore
from PySide.QtCore import QObject, Signal
from PySide2.QtWidgets import QDialog, QGridLayout, QVBoxLayout, QSizePolicy
import math

from DraftTools import translate

from Ui.TaskPanelLocation import TaskPanelLocation

from App.Constants import FIN_TYPE_TRAPEZOID, FIN_TYPE_ELLIPSE, FIN_TYPE_SKETCH
from App.Constants import FIN_CROSS_SAME, FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, \
    FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE

from App.Utilities import _err, _toFloat

class _FinDialog(QDialog):

    def __init__(self, sketch, parent=None):
        super(_FinDialog, self).__init__(parent)

        # define our window
        self.setGeometry(250, 250, 400, 350)
        self.setWindowTitle(translate('Rocket', "Fin Parameter"))

        self.tabWidget = QtGui.QTabWidget()
        self.tabGeneral = QtGui.QWidget()
        self.tabTtw = QtGui.QWidget()
        self.tabWidget.addTab(self.tabGeneral, translate('Rocket', "General"))
        self.tabWidget.addTab(self.tabTtw, translate('Rocket', "Fin Tabs"))

        layout = QVBoxLayout()
        layout.addWidget(self.tabWidget)
        self.setLayout(layout)

        self.setTabGeneral(sketch)
        self.setTabTtw()

    def setTabGeneral(self, sketch):

        ui = FreeCADGui.UiLoader()

        # Select the type of fin
        self.finTypeLabel = QtGui.QLabel(translate('Rocket', "Fin type"), self)

        if not sketch:
            self.finTypes = (FIN_TYPE_TRAPEZOID, 
                FIN_TYPE_ELLIPSE, 
                #FIN_TYPE_TUBE, 
                )
        else:
            self.finTypes = ( FIN_TYPE_SKETCH, )
        self.finTypesCombo = QtGui.QComboBox(self)
        self.finTypesCombo.addItems(self.finTypes)

        self.finSetGroup = QtGui.QGroupBox(translate('Rocket', "Fin Set"), self)
        self.finSetGroup.setCheckable(True)
        
        self.finCountLabel = QtGui.QLabel(translate('Rocket', "Fin Count"), self)

        self.finCountSpinBox = QtGui.QSpinBox(self)
        self.finCountSpinBox.setFixedWidth(80)
        self.finCountSpinBox.setMinimum(1)
        self.finCountSpinBox.setMaximum(10000)

        self.finSpacingLabel = QtGui.QLabel(translate('Rocket', "Fin Spacing"), self)

        self.finSpacingInput = ui.createWidget("Gui::InputField")
        self.finSpacingInput.unit = 'deg'
        self.finSpacingInput.setFixedWidth(80)

        # Get the fin parameters: length, width, etc...
        self.rootGroup = QtGui.QGroupBox(translate('Rocket', "Fin Root"), self)

        # Select the type of cross section
        self.rootCrossSectionLabel = QtGui.QLabel(translate('Rocket', "Cross Section"), self)

        self.rootCrossSections = (FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE,
            FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE)
        self.rootEllipseCrossSections = (FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE,
            FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LETE)
        self.rootCrossSectionsCombo = QtGui.QComboBox(self)
        self.rootCrossSectionsCombo.addItems(self.rootCrossSections)

        # Get the fin parameters: length, width, etc...
        self.rootChordLabel = QtGui.QLabel(translate('Rocket', "Chord"), self)

        self.rootChordInput = ui.createWidget("Gui::InputField")
        self.rootChordInput.unit = 'mm'
        self.rootChordInput.setMinimumWidth(100)

        self.rootThicknessLabel = QtGui.QLabel(translate('Rocket', "Thickness"), self)

        self.rootThicknessInput = ui.createWidget("Gui::InputField")
        self.rootThicknessInput.unit = 'mm'
        self.rootThicknessInput.setMinimumWidth(100)

        self.rootPerCentLabel = QtGui.QLabel(translate('Rocket', "Use percentage"), self)

        self.rootPerCentCheckbox = QtGui.QCheckBox(self)
        self.rootPerCentCheckbox.setCheckState(QtCore.Qt.Unchecked)

        self.rootLength1Label = QtGui.QLabel(translate('Rocket', "Length 1"), self)

        self.rootLength1Input = ui.createWidget("Gui::InputField")
        self.rootLength1Input.unit = 'mm'
        self.rootLength1Input.setMinimumWidth(100)

        self.rootLength2Label = QtGui.QLabel(translate('Rocket', "Length 2"), self)

        self.rootLength2Input = ui.createWidget("Gui::InputField")
        self.rootLength2Input.unit = 'mm'
        self.rootLength2Input.setMinimumWidth(100)

        self.tipGroup = QtGui.QGroupBox(translate('Rocket', "Fin Tip"), self)

        # Select the type of cross section
        self.tipCrossSectionLabel = QtGui.QLabel(translate('Rocket', "Cross Section"), self)

        self.tipCrossSections = (FIN_CROSS_SAME, FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE,
            FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE)
        self.tipCrossSectionsCombo = QtGui.QComboBox(self)
        self.tipCrossSectionsCombo.addItems(self.tipCrossSections)

        self.tipChordLabel = QtGui.QLabel(translate('Rocket', "Chord"), self)

        self.tipChordInput = ui.createWidget("Gui::InputField")
        self.tipChordInput.unit = 'mm'
        self.tipChordInput.setMinimumWidth(100)

        self.tipThicknessLabel = QtGui.QLabel(translate('Rocket', "Thickness"), self)

        self.tipThicknessInput = ui.createWidget("Gui::InputField")
        self.tipThicknessInput.unit = 'mm'
        self.tipThicknessInput.setMinimumWidth(100)

        self.tipPerCentLabel = QtGui.QLabel(translate('Rocket', "Use percentage"), self)

        self.tipPerCentCheckbox = QtGui.QCheckBox(self)
        self.tipPerCentCheckbox.setCheckState(QtCore.Qt.Unchecked)

        self.tipLength1Label = QtGui.QLabel(translate('Rocket', "Length 1"), self)

        self.tipLength1Input = ui.createWidget("Gui::InputField")
        self.tipLength1Input.unit = 'mm'
        self.tipLength1Input.setMinimumWidth(100)

        self.tipLength2Label = QtGui.QLabel(translate('Rocket', "Length 2"), self)

        self.tipLength2Input = ui.createWidget("Gui::InputField")
        self.tipLength2Input.unit = 'mm'
        self.tipLength2Input.setMinimumWidth(100)

        self.heightLabel = QtGui.QLabel(translate('Rocket', "Height"), self)

        self.heightInput = ui.createWidget("Gui::InputField")
        self.heightInput.unit = 'mm'
        self.heightInput.setMinimumWidth(100)

        # Sweep can be forward (-sweep) or backward (+sweep)
        self.sweepLengthLabel = QtGui.QLabel(translate('Rocket', "Sweep Length"), self)

        self.sweepLengthInput = ui.createWidget("Gui::InputField")
        self.sweepLengthInput.unit = 'mm'
        self.sweepLengthInput.setMinimumWidth(100)

        # Sweep angle is tied to sweep length. It can be forward (> -90) or backward (< 90)
        self.sweepAngleLabel = QtGui.QLabel(translate('Rocket', "Sweep Angle"), self)

        self.sweepAngleInput = ui.createWidget("Gui::InputField")
        self.sweepAngleInput.unit = 'deg'
        self.sweepAngleInput.setMinimumWidth(100)

        # Fin set group
        row = 0
        grid = QGridLayout()

        grid.addWidget(self.finCountLabel, row, 0)
        grid.addWidget(self.finCountSpinBox, row, 1)
        row += 1

        grid.addWidget(self.finSpacingLabel, row, 0)
        grid.addWidget(self.finSpacingInput, row, 1)

        self.finSetGroup.setLayout(grid)

        # Root group
        row = 0
        grid = QGridLayout()

        grid.addWidget(self.rootCrossSectionLabel, row, 0)
        grid.addWidget(self.rootCrossSectionsCombo, row, 1)
        row += 1

        grid.addWidget(self.rootChordLabel, row, 0)
        grid.addWidget(self.rootChordInput, row, 1)
        row += 1

        grid.addWidget(self.rootThicknessLabel, row, 0)
        grid.addWidget(self.rootThicknessInput, row, 1)
        row += 1

        grid.addWidget(self.rootPerCentLabel, row, 0)
        grid.addWidget(self.rootPerCentCheckbox, row, 1)
        row += 1

        grid.addWidget(self.rootLength1Label, row, 0)
        grid.addWidget(self.rootLength1Input, row, 1)
        row += 1

        grid.addWidget(self.rootLength2Label, row, 0)
        grid.addWidget(self.rootLength2Input, row, 1)

        self.rootGroup.setLayout(grid)

        # Tip group
        row = 0
        grid = QGridLayout()

        grid.addWidget(self.tipCrossSectionLabel, row, 0)
        grid.addWidget(self.tipCrossSectionsCombo, row, 1)
        row += 1

        grid.addWidget(self.tipChordLabel, row, 0)
        grid.addWidget(self.tipChordInput, row, 1)
        row += 1

        grid.addWidget(self.tipThicknessLabel, row, 0)
        grid.addWidget(self.tipThicknessInput, row, 1)
        row += 1

        grid.addWidget(self.tipPerCentLabel, row, 0)
        grid.addWidget(self.tipPerCentCheckbox, row, 1)
        row += 1

        grid.addWidget(self.tipLength1Label, row, 0)
        grid.addWidget(self.tipLength1Input, row, 1)
        row += 1

        grid.addWidget(self.tipLength2Label, row, 0)
        grid.addWidget(self.tipLength2Input, row, 1)

        self.tipGroup.setLayout(grid)

        # Main items
        row = 0
        grid = QGridLayout()

        grid.addWidget(self.finTypeLabel, row, 0)
        grid.addWidget(self.finTypesCombo, row, 1)
        row += 1

        grid.addWidget(self.heightLabel, row, 0)
        grid.addWidget(self.heightInput, row, 1)
        row += 1

        grid.addWidget(self.sweepLengthLabel, row, 0)
        grid.addWidget(self.sweepLengthInput, row, 1)
        row += 1

        grid.addWidget(self.sweepAngleLabel, row, 0)
        grid.addWidget(self.sweepAngleInput, row, 1)


        layout = QVBoxLayout()
        layout.addItem(grid)
        layout.addWidget(self.finSetGroup)
        layout.addWidget(self.rootGroup)
        layout.addWidget(self.tipGroup)
        layout.addItem(QtGui.QSpacerItem(0,0, QSizePolicy.Expanding, QSizePolicy.Expanding))

        self.tabGeneral.setLayout(layout)

    def setTabTtw(self):

        ui = FreeCADGui.UiLoader()

        self.ttwGroup = QtGui.QGroupBox(translate('Rocket', "TTW Tab"), self)
        self.ttwGroup.setCheckable(True)

        self.ttwOffsetLabel = QtGui.QLabel(translate('Rocket', "Offset"), self)

        self.ttwOffsetInput = ui.createWidget("Gui::InputField")
        self.ttwOffsetInput.unit = 'mm'
        self.ttwOffsetInput.setMinimumWidth(100)

        self.ttwLengthLabel = QtGui.QLabel(translate('Rocket', "Length"), self)

        self.ttwLengthInput = ui.createWidget("Gui::InputField")
        self.ttwLengthInput.unit = 'mm'
        self.ttwLengthInput.setMinimumWidth(100)

        self.ttwHeightLabel = QtGui.QLabel(translate('Rocket', "Height"), self)

        self.ttwHeightInput = ui.createWidget("Gui::InputField")
        self.ttwHeightInput.unit = 'mm'
        self.ttwHeightInput.setMinimumWidth(100)

        self.ttwThicknessLabel = QtGui.QLabel(translate('Rocket', "Thickness"), self)

        self.ttwThicknessInput = ui.createWidget("Gui::InputField")
        self.ttwThicknessInput.unit = 'mm'
        self.ttwThicknessInput.setMinimumWidth(100)

        row = 0
        grid = QGridLayout()

        grid.addWidget(self.ttwOffsetLabel, row, 0)
        grid.addWidget(self.ttwOffsetInput, row, 1)
        row += 1

        grid.addWidget(self.ttwLengthLabel, row, 0)
        grid.addWidget(self.ttwLengthInput, row, 1)
        row += 1

        grid.addWidget(self.ttwHeightLabel, row, 0)
        grid.addWidget(self.ttwHeightInput, row, 1)
        row += 1

        grid.addWidget(self.ttwThicknessLabel, row, 0)
        grid.addWidget(self.ttwThicknessInput, row, 1)

        self.ttwGroup.setLayout(grid)

        layout = QVBoxLayout()
        layout.addWidget(self.ttwGroup)
        layout.addItem(QtGui.QSpacerItem(0,0, QSizePolicy.Expanding, QSizePolicy.Expanding))

        self.tabTtw.setLayout(layout)

class TaskPanelFin(QObject):

    redrawRequired = Signal()   # Allows for async redraws to allow for longer processing times

    def __init__(self, obj, mode):
        super().__init__()

        self._obj = obj
        
        self._finForm = _FinDialog(self._obj.FinType == FIN_TYPE_SKETCH)

        self._location = TaskPanelLocation(obj)
        self._locationForm = self._location.getForm()

        self.form = [self._finForm, self._locationForm]
        self._finForm.setWindowIcon(QtGui.QIcon(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Fin.svg"))
        
        self._finForm.finTypesCombo.currentTextChanged.connect(self.onFinTypes)

        self._finForm.finSetGroup.toggled.connect(self.onFinSet)
        self._finForm.finCountSpinBox.valueChanged.connect(self.onCount)
        self._finForm.finSpacingInput.textEdited.connect(self.onSpacing)

        self._finForm.rootCrossSectionsCombo.currentTextChanged.connect(self.onRootCrossSection)
        self._finForm.rootChordInput.textEdited.connect(self.onRootChord)
        self._finForm.rootThicknessInput.textEdited.connect(self.onRootThickness)
        self._finForm.rootPerCentCheckbox.clicked.connect(self.onRootPerCent)
        self._finForm.rootLength1Input.textEdited.connect(self.onRootLength1)
        self._finForm.rootLength2Input.textEdited.connect(self.onRootLength2)

        self._finForm.tipCrossSectionsCombo.currentTextChanged.connect(self.onTipCrossSection)
        self._finForm.tipChordInput.textEdited.connect(self.onTipChord)
        self._finForm.tipThicknessInput.textEdited.connect(self.onTipThickness)
        self._finForm.tipPerCentCheckbox.clicked.connect(self.onTipPerCent)
        self._finForm.tipLength1Input.textEdited.connect(self.onTipLength1)
        self._finForm.tipLength2Input.textEdited.connect(self.onTipLength2)

        self._finForm.heightInput.textEdited.connect(self.onHeight)
        self._finForm.sweepLengthInput.textEdited.connect(self.onSweepLength)
        self._finForm.sweepAngleInput.textEdited.connect(self.onSweepAngle)

        self._finForm.ttwGroup.toggled.connect(self.onTtw)
        self._finForm.ttwOffsetInput.textEdited.connect(self.onTTWOffset)
        self._finForm.ttwLengthInput.textEdited.connect(self.onTTWLength)
        self._finForm.ttwHeightInput.textEdited.connect(self.onTTWHeight)
        self._finForm.ttwThicknessInput.textEdited.connect(self.onTTWThickness)

        self._location.locationChange.connect(self.onLocation)

        self._redrawPending = False
        self.redrawRequired.connect(self.onRedraw, QtCore.Qt.QueuedConnection)
        
        self.update()
        
        if mode == 0: # fresh created
            self.redraw()  # calculate once 
            FreeCAD.Gui.SendMsgToActiveView("ViewFit")
        
    def transferTo(self):
        "Transfer from the dialog to the object" 
        self._obj.FinType = str(self._finForm.finTypesCombo.currentText())

        self._obj.FinSet = self._finForm.finSetGroup.isChecked()
        self._obj.FinCount = self._finForm.finCountSpinBox.value()
        self._obj.FinSpacing = self._finForm.finSpacingInput.text()

        self._obj.RootCrossSection = str(self._finForm.rootCrossSectionsCombo.currentText())
        self._obj.RootChord = self._finForm.rootChordInput.text()
        self._obj.RootThickness = self._finForm.rootThicknessInput.text()
        self._obj.RootPerCent = self._finForm.rootPerCentCheckbox.isChecked()
        self._obj.RootLength1 = self._finForm.rootLength1Input.text()
        self._obj.RootLength2 = self._finForm.rootLength2Input.text()

        self._obj.TipCrossSection = str(self._finForm.tipCrossSectionsCombo.currentText())
        self._obj.TipChord = self._finForm.tipChordInput.text()
        self._obj.TipThickness = self._finForm.tipThicknessInput.text()
        self._obj.TipPerCent = self._finForm.tipPerCentCheckbox.isChecked()
        self._obj.TipLength1 = self._finForm.tipLength1Input.text()
        self._obj.TipLength2 =self._finForm.tipLength2Input.text()

        self._obj.Height = self._finForm.heightInput.text()
        self._obj.SweepLength = self._finForm.sweepLengthInput.text()
        self._obj.SweepAngle = self._finForm.sweepAngleInput.text()

        self._obj.Ttw = self._finForm.ttwGroup.isChecked()
        self._obj.TtwOffset = self._finForm.ttwOffsetInput.text()
        self._obj.TtwLength = self._finForm.ttwLengthInput.text()
        self._obj.TtwHeight = self._finForm.ttwHeightInput.text()
        self._obj.TtwThickness = self._finForm.ttwThicknessInput.text()

    def transferFrom(self):
        "Transfer from the object to the dialog"
        self._finForm.finTypesCombo.setCurrentText(self._obj.FinType)

        self._finForm.finSetGroup.setChecked(self._obj.FinSet)
        self._finForm.finCountSpinBox.setValue(self._obj.FinCount)
        self._finForm.finSpacingInput.setText(self._obj.FinSpacing.UserString)

        self._finForm.rootCrossSectionsCombo.setCurrentText(self._obj.RootCrossSection)
        self._finForm.rootChordInput.setText(self._obj.RootChord.UserString)
        self._finForm.rootThicknessInput.setText(self._obj.RootThickness.UserString)
        self._finForm.rootPerCentCheckbox.setChecked(self._obj.RootPerCent)
        self._finForm.rootLength1Input.setText(self._obj.RootLength1.UserString)
        self._finForm.rootLength2Input.setText(self._obj.RootLength2.UserString)

        self._finForm.tipCrossSectionsCombo.setCurrentText(self._obj.TipCrossSection)
        self._finForm.tipChordInput.setText(self._obj.TipChord.UserString)
        self._finForm.tipThicknessInput.setText(self._obj.TipThickness.UserString)
        self._finForm.tipPerCentCheckbox.setChecked(self._obj.TipPerCent)
        self._finForm.tipLength1Input.setText(self._obj.TipLength1.UserString)
        self._finForm.tipLength2Input.setText(self._obj.TipLength2.UserString)

        self._finForm.heightInput.setText(self._obj.Height.UserString)
        self._finForm.sweepLengthInput.setText(self._obj.SweepLength.UserString)
        self._finForm.sweepAngleInput.setText(self._obj.SweepAngle.UserString)

        self._finForm.ttwGroup.setChecked(self._obj.Ttw)
        self._finForm.ttwOffsetInput.setText(self._obj.TtwOffset.UserString)
        self._finForm.ttwLengthInput.setText(self._obj.TtwLength.UserString)
        self._finForm.ttwHeightInput.setText(self._obj.TtwHeight.UserString)
        self._finForm.ttwThicknessInput.setText(self._obj.TtwThickness.UserString)

        self._setFinSetState()
        self._enableRootLengths()
        self._enableFinTypes() # This calls _enableTipLengths()
        self._enableRootPercent()
        self._enableTipPercent()
        self._sweepAngleFromLength(self._obj.SweepLength)
        self._setTtwState()

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
        
    def onFinTypes(self, value):
        self._obj.FinType = value
        self._enableFinTypes()
        self.redraw()
       
    def _setFinSetState(self):
        checked = self._finForm.finSetGroup.isChecked()

        self._finForm.finCountSpinBox.setEnabled(checked)
        self._finForm.finSpacingInput.setEnabled(checked)

    def onFinSet(self, value):
        self._obj.FinSet = self._finForm.finSetGroup.isChecked()
        self._setFinSetState()
        self.redraw()
        self.setEdited()
        
    def onCount(self, value):
        self._obj.FinCount = value
        self._obj.FinSpacing = 360.0 / float(value)
        self._finForm.finSpacingInput.setText(self._obj.FinSpacing.UserString)
        self.redraw()
        self.setEdited()
        
    def onFinTypes(self, value):
        self._obj.FinType = value
        self._enableFinTypes()
        self.redraw()
        
    def onSpacing(self, value):
        self._obj.FinSpacing = value
        self.redraw()
        self.setEdited()

    def _enableFinTypes(self):
        if self._obj.FinType == FIN_TYPE_TRAPEZOID:
            self._enableFinTypeTrapezoid()
        elif self._obj.FinType == FIN_TYPE_ELLIPSE:
            self._enableFinTypeEllipse()
        else:
            self._enableFinTypeSketch()


    def _enableFinTypeTrapezoid(self):
        old = self._obj.RootCrossSection # This must be saved and restored
        self._finForm.rootCrossSectionsCombo.clear()
        self._finForm.rootCrossSectionsCombo.addItems(self._finForm.rootCrossSections)
        self._obj.RootCrossSection = old

        self._finForm.rootCrossSectionsCombo.setCurrentText(self._obj.RootCrossSection)

        self._finForm.heightLabel.setHidden(False)
        self._finForm.heightInput.setHidden(False)

        self._finForm.sweepLengthLabel.setHidden(False)
        self._finForm.sweepLengthInput.setHidden(False)
        self._finForm.sweepAngleLabel.setHidden(False)
        self._finForm.sweepAngleInput.setHidden(False)

        self._finForm.rootChordLabel.setHidden(False)
        self._finForm.rootChordInput.setHidden(False)
        self._finForm.rootLength2Label.setHidden(False)
        self._finForm.rootLength2Input.setHidden(False)

        self._finForm.tipGroup.setHidden(False)

        self._enableTipLengths()

    def _enableFinTypeEllipse(self):
        old = self._obj.RootCrossSection # This must be saved and restored
        self._finForm.rootCrossSectionsCombo.clear()
        self._finForm.rootCrossSectionsCombo.addItems(self._finForm.rootEllipseCrossSections)
        self._obj.RootCrossSection = old

        if self._obj.RootCrossSection in [FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE]:
            self._obj.RootCrossSection = FIN_CROSS_TAPER_LETE
        self._finForm.rootCrossSectionsCombo.setCurrentText(self._obj.RootCrossSection)

        self._finForm.heightLabel.setHidden(False)
        self._finForm.heightInput.setHidden(False)
        
        self._finForm.sweepLengthLabel.setHidden(True)
        self._finForm.sweepLengthInput.setHidden(True)
        self._finForm.sweepAngleLabel.setHidden(True)
        self._finForm.sweepAngleInput.setHidden(True)

        self._finForm.rootChordLabel.setHidden(False)
        self._finForm.rootChordInput.setHidden(False)
        self._finForm.rootLength2Label.setHidden(True)
        self._finForm.rootLength2Input.setHidden(True)

        self._finForm.tipGroup.setHidden(True)

    def _enableFinTypeSketch(self):
        old = self._obj.RootCrossSection # This must be saved and restored
        self._finForm.rootCrossSectionsCombo.clear()
        self._finForm.rootCrossSectionsCombo.addItems(self._finForm.rootCrossSections)
        self._obj.RootCrossSection = old

        self._finForm.rootCrossSectionsCombo.setCurrentText(self._obj.RootCrossSection)

        self._finForm.heightLabel.setHidden(True)
        self._finForm.heightInput.setHidden(True)
        
        self._finForm.sweepLengthLabel.setHidden(True)
        self._finForm.sweepLengthInput.setHidden(True)
        self._finForm.sweepAngleLabel.setHidden(True)
        self._finForm.sweepAngleInput.setHidden(True)

        self._finForm.rootChordLabel.setHidden(True)
        self._finForm.rootChordInput.setHidden(True)

        self._finForm.tipGroup.setHidden(True)

    def _enableRootLengths(self):
        value = self._obj.RootCrossSection
        if value in [FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE]:
            self._finForm.rootPerCentCheckbox.setEnabled(True)
            self._finForm.rootLength1Input.setEnabled(True)
            if value == FIN_CROSS_TAPER_LETE:
                self._finForm.rootLength2Input.setEnabled(True)
            else:
                self._finForm.rootLength2Input.setEnabled(False)
        else:
            self._finForm.rootPerCentCheckbox.setEnabled(False)
            self._finForm.rootLength1Input.setEnabled(False)
            self._finForm.rootLength2Input.setEnabled(False)

    def _enableTipLengths(self):
        if self._obj.FinType == FIN_TYPE_TRAPEZOID:
            value = self._obj.TipCrossSection
            if value == FIN_CROSS_SAME:
                value = self._obj.RootCrossSection
            if value in [FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE]:
                self._finForm.tipPerCentCheckbox.setEnabled(True)
                self._finForm.tipLength1Input.setEnabled(True)
                if value == FIN_CROSS_TAPER_LETE:
                    self._finForm.tipLength2Input.setEnabled(True)
                else:
                    self._finForm.tipLength2Input.setEnabled(False)
            else:
                self._finForm.tipPerCentCheckbox.setEnabled(False)
                self._finForm.tipLength1Input.setEnabled(False)
                self._finForm.tipLength2Input.setEnabled(False)
        
    def onRootCrossSection(self, value):
        if len(value) <= 0:
            return
            
        self._obj.RootCrossSection = value
        self._enableRootLengths()

        if self._obj.TipCrossSection == FIN_CROSS_SAME:
            self._enableTipLengths()

        self.redraw()
        
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
            self._finForm.rootLength1Input.unit = ''
            self._finForm.rootLength2Input.unit = ''
            self._finForm.rootLength1Input.setText(str(self._obj.RootLength1.Value))
            self._finForm.rootLength2Input.setText(str(self._obj.RootLength2.Value))
        else:
            self._finForm.rootLength1Input.unit = 'mm'
            self._finForm.rootLength2Input.unit = 'mm'
            self._finForm.rootLength1Input.setText(self._obj.RootLength1.UserString)
            self._finForm.rootLength2Input.setText(self._obj.RootLength2.UserString)

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
        self._obj.RootPerCent = self._finForm.rootPerCentCheckbox.isChecked()
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
            self._obj.TipChord = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass
        self.setEdited()
        
    def onTipThickness(self, value):
        try:
            self._obj.TipThickness = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def _enableTipPercent(self):
        if self._obj.TipPerCent:
            self._finForm.tipLength1Input.unit = ''
            self._finForm.tipLength2Input.unit = ''
            self._finForm.tipLength1Input.setText(str(self._obj.TipLength1.Value))
            self._finForm.tipLength2Input.setText(str(self._obj.TipLength2.Value))
        else:
            self._finForm.tipLength1Input.unit = 'mm'
            self._finForm.tipLength2Input.unit = 'mm'
            self._finForm.tipLength1Input.setText(self._obj.TipLength1.UserString)
            self._finForm.tipLength2Input.setText(self._obj.TipLength2.UserString)

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
        self._obj.TipPerCent = self._finForm.tipPerCentCheckbox.isChecked()
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

    def onHeight(self, value):
        try:
            self._obj.Height = FreeCAD.Units.Quantity(value).Value
            self._sweepAngleFromLength(self._obj.SweepLength)
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def _sweepLengthFromAngle(self, value):
        theta = _toFloat(value)
        if theta <= -90.0 or theta >= 90.0:
            _err("Sweep angle must be greater than -90 and less than +90")
            return
        theta = math.radians(-1.0 * (theta + 90.0))
        length = _toFloat(self._obj.Height) / math.tan(theta)
        self._obj.SweepLength = length
        self._finForm.sweepLengthInput.setText(self._obj.SweepLength.UserString)

    def _sweepAngleFromLength(self, value):
        length = _toFloat(value)
        theta = 90.0 - math.degrees(math.atan2(_toFloat(self._obj.Height), length))
        self._obj.SweepAngle = theta
        self._finForm.sweepAngleInput.setText(self._obj.SweepAngle.UserString)
        
    def onSweepLength(self, value):
        try:
            self._obj.SweepLength = FreeCAD.Units.Quantity(value).Value
            self._sweepAngleFromLength(self._obj.SweepLength)
            self.redraw()
        except ValueError:
            pass
        self.setEdited()
        
    def onSweepAngle(self, value):
        try:
            self._obj.SweepAngle = FreeCAD.Units.Quantity(value).Value
            self._sweepLengthFromAngle(self._obj.SweepAngle)
            self.redraw()
        except ValueError:
            pass
        self.setEdited()
        
    def _setTtwState(self):
        self._finForm.ttwOffsetInput.setEnabled(self._obj.Ttw)
        self._finForm.ttwLengthInput.setEnabled(self._obj.Ttw)
        self._finForm.ttwHeightInput.setEnabled(self._obj.Ttw)
        self._finForm.ttwThicknessInput.setEnabled(self._obj.Ttw)
        
    def onTtw(self, value):
        self._obj.Ttw = self._finForm.ttwGroup.isChecked()
        self._setTtwState()

        self.redraw()
        self.setEdited()
        
    def onTTWOffset(self, value):
        try:
            self._obj.TtwOffset = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass
        self.setEdited()
        
    def onTTWLength(self, value):
        try:
            self._obj.TtwLength = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass
        self.setEdited()
        
    def onTTWHeight(self, value):
        try:
            self._obj.TtwHeight = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass
        self.setEdited()
        
    def onTTWThickness(self, value):
        try:
            self._obj.TtwThickness = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def onLocation(self):
        self.redraw()
        self.setEdited()

    def onRedraw(self):
        self._obj.Proxy.execute(self._obj)
        self._redrawPending = False
        
    def getStandardButtons(self):
        return int(QtGui.QDialogButtonBox.Ok) | int(QtGui.QDialogButtonBox.Cancel)| int(QtGui.QDialogButtonBox.Apply)

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
        self.setEdited()
