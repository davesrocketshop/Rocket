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
from PySide2.QtWidgets import QDialog, QGridLayout
import math

from DraftTools import translate

from App.Constants import FIN_TYPE_TRAPEZOID
from App.Constants import FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, \
    FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE

from App.Utilities import _err, _toFloat

class _FinDialog(QDialog):

    def __init__(self, parent=None):
        super(_FinDialog, self).__init__(parent)

        ui = FreeCADGui.UiLoader()

        # define our window
        self.setGeometry(250, 250, 400, 350)
        self.setWindowTitle(translate('Rocket', "Fin Parameter"))

        # Select the type of nose cone
        self.finTypeLabel = QtGui.QLabel(translate('Rocket', "Fin type"), self)

        self.finTypes = (FIN_TYPE_TRAPEZOID, 
            #FIN_TYPE_ELLIPSE, 
            #FIN_TYPE_TUBE, 
            #FIN_TYPE_SKETCH
            )
        self.finTypesCombo = QtGui.QComboBox(self)
        self.finTypesCombo.addItems(self.finTypes)

        # Get the fin parameters: length, width, etc...
        self.rootLabel = QtGui.QLabel(translate('Rocket', "Fin Root"), self)

        # Select the type of cross section
        self.rootCrossSectionLabel = QtGui.QLabel(translate('Rocket', "Cross Section"), self)

        self.rootCrossSections = (FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE,
            FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE)
        self.rootCrossSectionsCombo = QtGui.QComboBox(self)
        self.rootCrossSectionsCombo.addItems(self.rootCrossSections)

        # Get the fin parameters: length, width, etc...
        self.rootChordLabel = QtGui.QLabel(translate('Rocket', "Chord"), self)

        self.rootChordInput = ui.createWidget("Gui::InputField")
        self.rootChordInput.unit = 'mm'
        self.rootChordInput.setFixedWidth(100)

        self.rootThicknessLabel = QtGui.QLabel(translate('Rocket', "Thickness"), self)

        self.rootThicknessInput = ui.createWidget("Gui::InputField")
        self.rootThicknessInput.unit = 'mm'
        self.rootThicknessInput.setFixedWidth(100)

        self.rootPerCentLabel = QtGui.QLabel(translate('Rocket', "Use percentage"), self)

        self.rootPerCentCheckbox = QtGui.QCheckBox(self)
        self.rootPerCentCheckbox.setCheckState(QtCore.Qt.Unchecked)

        self.rootLength1Label = QtGui.QLabel(translate('Rocket', "Length 1"), self)

        self.rootLength1Input = ui.createWidget("Gui::InputField")
        self.rootLength1Input.unit = 'mm'
        self.rootLength1Input.setFixedWidth(100)

        self.rootLength2Label = QtGui.QLabel(translate('Rocket', "Length 2"), self)

        self.rootLength2Input = ui.createWidget("Gui::InputField")
        self.rootLength2Input.unit = 'mm'
        self.rootLength2Input.setFixedWidth(100)

        self.tipLabel = QtGui.QLabel(translate('Rocket', "Fin Tip"), self)

        # Select the type of cross section
        self.tipCrossSectionLabel = QtGui.QLabel(translate('Rocket', "Cross Section"), self)

        self.tipCrossSections = (FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE,
            FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE)
        self.tipCrossSectionsCombo = QtGui.QComboBox(self)
        self.tipCrossSectionsCombo.addItems(self.tipCrossSections)

        self.tipChordLabel = QtGui.QLabel(translate('Rocket', "Chord"), self)

        self.tipChordInput = ui.createWidget("Gui::InputField")
        self.tipChordInput.unit = 'mm'
        self.tipChordInput.setFixedWidth(100)

        self.tipThicknessLabel = QtGui.QLabel(translate('Rocket', "Thickness"), self)

        self.tipThicknessInput = ui.createWidget("Gui::InputField")
        self.tipThicknessInput.unit = 'mm'
        self.tipThicknessInput.setFixedWidth(100)

        self.tipPerCentLabel = QtGui.QLabel(translate('Rocket', "Use percentage"), self)

        self.tipPerCentCheckbox = QtGui.QCheckBox(self)
        self.tipPerCentCheckbox.setCheckState(QtCore.Qt.Unchecked)

        self.tipLength1Label = QtGui.QLabel(translate('Rocket', "Length 1"), self)

        self.tipLength1Input = ui.createWidget("Gui::InputField")
        self.tipLength1Input.unit = 'mm'
        self.tipLength1Input.setFixedWidth(100)

        self.tipLength2Label = QtGui.QLabel(translate('Rocket', "Length 2"), self)

        self.tipLength2Input = ui.createWidget("Gui::InputField")
        self.tipLength2Input.unit = 'mm'
        self.tipLength2Input.setFixedWidth(100)

        self.heightLabel = QtGui.QLabel(translate('Rocket', "Height"), self)

        self.heightInput = ui.createWidget("Gui::InputField")
        self.heightInput.unit = 'mm'
        self.heightInput.setFixedWidth(100)

        # Sweep can be forward (-sweep) or backward (+sweep)
        self.sweepLengthLabel = QtGui.QLabel(translate('Rocket', "Sweep Length"), self)

        self.sweepLengthInput = ui.createWidget("Gui::InputField")
        self.sweepLengthInput.unit = 'mm'
        self.sweepLengthInput.setFixedWidth(100)

        # Sweep angle is tied to sweep length. It can be forward (> -90) or backward (< 90)
        self.sweepAngleLabel = QtGui.QLabel(translate('Rocket', "Sweep Angle"), self)

        self.sweepAngleInput = ui.createWidget("Gui::InputField")
        self.sweepAngleInput.unit = 'deg'
        self.sweepAngleInput.setFixedWidth(100)

        self.ttwLabel = QtGui.QLabel(translate('Rocket', "TTW Tab"), self)

        self.ttwCheckbox = QtGui.QCheckBox(self)
        self.ttwCheckbox.setCheckState(QtCore.Qt.Unchecked)

        self.ttwOffsetLabel = QtGui.QLabel(translate('Rocket', "Offset"), self)

        self.ttwOffsetInput = ui.createWidget("Gui::InputField")
        self.ttwOffsetInput.unit = 'mm'
        self.ttwOffsetInput.setFixedWidth(100)

        self.ttwLengthLabel = QtGui.QLabel(translate('Rocket', "Length"), self)

        self.ttwLengthInput = ui.createWidget("Gui::InputField")
        self.ttwLengthInput.unit = 'mm'
        self.ttwLengthInput.setFixedWidth(100)

        self.ttwHeightLabel = QtGui.QLabel(translate('Rocket', "Height"), self)

        self.ttwHeightInput = ui.createWidget("Gui::InputField")
        self.ttwHeightInput.unit = 'mm'
        self.ttwHeightInput.setFixedWidth(100)

        self.ttwThicknessLabel = QtGui.QLabel(translate('Rocket', "Thickness"), self)

        self.ttwThicknessInput = ui.createWidget("Gui::InputField")
        self.ttwThicknessInput.unit = 'mm'
        self.ttwThicknessInput.setFixedWidth(100)

        row = 0
        layout = QGridLayout()

        layout.addWidget(self.finTypeLabel, row, 0, 1, 2)
        layout.addWidget(self.finTypesCombo, row, 1)
        row += 1

        layout.addWidget(self.heightLabel, row, 0)
        layout.addWidget(self.heightInput, row, 1)
        row += 1

        layout.addWidget(self.sweepLengthLabel, row, 0)
        layout.addWidget(self.sweepLengthInput, row, 1)
        row += 1

        layout.addWidget(self.sweepAngleLabel, row, 0)
        layout.addWidget(self.sweepAngleInput, row, 1)
        row += 1

        layout.addWidget(self.rootLabel, row, 0)
        layout.addWidget(self.rootCrossSectionLabel, row, 1)
        layout.addWidget(self.rootCrossSectionsCombo, row, 2)
        row += 1

        layout.addWidget(self.rootChordLabel, row, 1)
        layout.addWidget(self.rootChordInput, row, 2)
        row += 1

        layout.addWidget(self.rootThicknessLabel, row, 1)
        layout.addWidget(self.rootThicknessInput, row, 2)
        row += 1

        layout.addWidget(self.rootPerCentLabel, row, 1)
        layout.addWidget(self.rootPerCentCheckbox, row, 2)
        row += 1

        layout.addWidget(self.rootLength1Label, row, 1)
        layout.addWidget(self.rootLength1Input, row, 2)
        row += 1

        layout.addWidget(self.rootLength2Label, row, 1)
        layout.addWidget(self.rootLength2Input, row, 2)
        row += 1

        layout.addWidget(self.tipLabel, row, 0)
        layout.addWidget(self.tipCrossSectionLabel, row, 1)
        layout.addWidget(self.tipCrossSectionsCombo, row, 2)
        row += 1

        layout.addWidget(self.tipChordLabel, row, 1)
        layout.addWidget(self.tipChordInput, row, 2)
        row += 1

        layout.addWidget(self.tipThicknessLabel, row, 1)
        layout.addWidget(self.tipThicknessInput, row, 2)
        row += 1

        layout.addWidget(self.tipPerCentLabel, row, 1)
        layout.addWidget(self.tipPerCentCheckbox, row, 2)
        row += 1

        layout.addWidget(self.tipLength1Label, row, 1)
        layout.addWidget(self.tipLength1Input, row, 2)
        row += 1

        layout.addWidget(self.tipLength2Label, row, 1)
        layout.addWidget(self.tipLength2Input, row, 2)
        row += 1

        layout.addWidget(self.ttwLabel, row, 0)
        layout.addWidget(self.ttwCheckbox, row, 1)
        row += 1

        layout.addWidget(self.ttwOffsetLabel, row, 1)
        layout.addWidget(self.ttwOffsetInput, row, 2)
        row += 1

        layout.addWidget(self.ttwLengthLabel, row, 1)
        layout.addWidget(self.ttwLengthInput, row, 2)
        row += 1

        layout.addWidget(self.ttwHeightLabel, row, 1)
        layout.addWidget(self.ttwHeightInput, row, 2)
        row += 1

        layout.addWidget(self.ttwThicknessLabel, row, 1)
        layout.addWidget(self.ttwThicknessInput, row, 2)

        self.setLayout(layout)

class TaskPanelFin:

    def __init__(self,obj,mode):
        self.obj = obj
        
        self.form = _FinDialog()
        self.form.setWindowIcon(QtGui.QIcon(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Fin.svg"))
        
        self.form.finTypesCombo.currentTextChanged.connect(self.onFinTypes)

        self.form.rootCrossSectionsCombo.currentTextChanged.connect(self.onRootCrossSection)
        self.form.rootChordInput.textEdited.connect(self.onRootChord)
        self.form.rootThicknessInput.textEdited.connect(self.onRootThickness)
        self.form.rootPerCentCheckbox.clicked.connect(self.onRootPerCent)
        self.form.rootLength1Input.textEdited.connect(self.onRootLength1)
        self.form.rootLength2Input.textEdited.connect(self.onRootLength2)

        self.form.tipCrossSectionsCombo.currentTextChanged.connect(self.onTipCrossSection)
        self.form.tipChordInput.textEdited.connect(self.onTipChord)
        self.form.tipThicknessInput.textEdited.connect(self.onTipThickness)
        self.form.tipPerCentCheckbox.clicked.connect(self.onTipPerCent)
        self.form.tipLength1Input.textEdited.connect(self.onTipLength1)
        self.form.tipLength2Input.textEdited.connect(self.onTipLength2)

        self.form.heightInput.textEdited.connect(self.onHeight)
        self.form.sweepLengthInput.textEdited.connect(self.onSweepLength)
        self.form.sweepAngleInput.textEdited.connect(self.onSweepAngle)

        self.form.ttwCheckbox.stateChanged.connect(self.onTtw)
        self.form.ttwOffsetInput.textEdited.connect(self.onTTWOffset)
        self.form.ttwLengthInput.textEdited.connect(self.onTTWLength)
        self.form.ttwHeightInput.textEdited.connect(self.onTTWHeight)
        self.form.ttwThicknessInput.textEdited.connect(self.onTTWThickness)
        
        self.update()
        
        if mode == 0: # fresh created
            self.obj.Proxy.execute(self.obj)  # calculate once 
            FreeCAD.Gui.SendMsgToActiveView("ViewFit")
        
    def transferTo(self):
        "Transfer from the dialog to the object" 
        self.obj.FinType = str(self.form.finTypesCombo.currentText())

        self.obj.RootCrossSection = str(self.form.rootCrossSectionsCombo.currentText())
        self.obj.RootChord = self.form.rootChordInput.text()
        self.obj.RootThickness = self.form.rootThicknessInput.text()
        self.obj.RootPerCent = self.form.rootPerCentCheckbox.isChecked()
        self.obj.RootLength1 = self.form.rootLength1Input.text()
        self.obj.RootLength2 = self.form.rootLength2Input.text()

        self.obj.TipCrossSection = str(self.form.tipCrossSectionsCombo.currentText())
        self.obj.TipChord = self.form.tipChordInput.text()
        self.obj.TipThickness = self.form.tipThicknessInput.text()
        self.obj.TipPerCent = self.form.tipPerCentCheckbox.isChecked()
        self.obj.TipLength1 = self.form.tipLength1Input.text()
        self.obj.TipLength2 =self.form.tipLength2Input.text()

        self.obj.Height = self.form.heightInput.text()
        self.obj.SweepLength = self.form.sweepLengthInput.text()
        self.obj.SweepAngle = self.form.sweepAngleInput.text()

        self.obj.Ttw = self.form.ttwCheckbox.isChecked()
        self.obj.TtwOffset = self.form.ttwOffsetInput.text()
        self.obj.TtwLength = self.form.ttwLengthInput.text()
        self.obj.TtwHeight = self.form.ttwHeightInput.text()
        self.obj.TtwThickness = self.form.ttwThicknessInput.text()

    def transferFrom(self):
        "Transfer from the object to the dialog"
        self.form.finTypesCombo.setCurrentText(self.obj.FinType)

        self.form.rootCrossSectionsCombo.setCurrentText(self.obj.RootCrossSection)
        self.form.rootChordInput.setText(self.obj.RootChord.UserString)
        self.form.rootThicknessInput.setText(self.obj.RootThickness.UserString)
        self.form.rootPerCentCheckbox.setChecked(self.obj.RootPerCent)
        self.form.rootLength1Input.setText(self.obj.RootLength1.UserString)
        self.form.rootLength2Input.setText(self.obj.RootLength2.UserString)

        self.form.tipCrossSectionsCombo.setCurrentText(self.obj.TipCrossSection)
        self.form.tipChordInput.setText(self.obj.TipChord.UserString)
        self.form.tipThicknessInput.setText(self.obj.TipThickness.UserString)
        self.form.tipPerCentCheckbox.setChecked(self.obj.TipPerCent)
        self.form.tipLength1Input.setText(self.obj.TipLength1.UserString)
        self.form.tipLength2Input.setText(self.obj.TipLength2.UserString)

        self.form.heightInput.setText(self.obj.Height.UserString)
        self.form.sweepLengthInput.setText(self.obj.SweepLength.UserString)
        self.form.sweepAngleInput.setText(self.obj.SweepAngle.UserString)

        self.form.ttwCheckbox.setChecked(self.obj.Ttw)
        self.form.ttwOffsetInput.setText(self.obj.TtwOffset.UserString)
        self.form.ttwLengthInput.setText(self.obj.TtwLength.UserString)
        self.form.ttwHeightInput.setText(self.obj.TtwHeight.UserString)
        self.form.ttwThicknessInput.setText(self.obj.TtwThickness.UserString)

        self._enableRootLengths()
        self._enableTipLengths()
        self._enableRootPercent()
        self._enableTipPercent()
        self._sweepAngleFromLength(self.obj.SweepLength)
        self._setTtwState()
        
    def onFinTypes(self, value):
        self.obj.FinType = value
        self.obj.Proxy.execute(self.obj)

    def _enableRootLengths(self):
        value = self.obj.RootCrossSection
        if value in [FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE]:
            self.form.rootPerCentCheckbox.setEnabled(True)
            self.form.rootLength1Input.setEnabled(True)
            if value == FIN_CROSS_TAPER_LETE:
                self.form.rootLength2Input.setEnabled(True)
            else:
                self.form.rootLength2Input.setEnabled(False)
        else:
            self.form.rootPerCentCheckbox.setEnabled(False)
            self.form.rootLength1Input.setEnabled(False)
            self.form.rootLength2Input.setEnabled(False)

    def _enableTipLengths(self):
        value = self.obj.TipCrossSection
        if value in [FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE]:
            self.form.tipPerCentCheckbox.setEnabled(True)
            self.form.tipLength1Input.setEnabled(True)
            if value == FIN_CROSS_TAPER_LETE:
                self.form.tipLength2Input.setEnabled(True)
            else:
                self.form.tipLength2Input.setEnabled(False)
        else:
            self.form.tipPerCentCheckbox.setEnabled(False)
            self.form.tipLength1Input.setEnabled(False)
            self.form.tipLength2Input.setEnabled(False)
        
    def onRootCrossSection(self, value):
        self.obj.RootCrossSection = value
        self._enableRootLengths()

        self.obj.Proxy.execute(self.obj)
        
    def onRootChord(self, value):
        try:
            self.obj.RootChord = FreeCAD.Units.Quantity(value).Value
            self.obj.Proxy.execute(self.obj)
        except ValueError:
            pass
        
    def onRootThickness(self, value):
        try:
            self.obj.RootThickness = FreeCAD.Units.Quantity(value).Value
            self.obj.Proxy.execute(self.obj)
        except ValueError:
            pass

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
        if self.obj.RootPerCent:
            self.form.rootLength1Input.unit = ''
            self.form.rootLength2Input.unit = ''
            self.form.rootLength1Input.setText(str(self.obj.RootLength1.Value))
            self.form.rootLength2Input.setText(str(self.obj.RootLength2.Value))
        else:
            self.form.rootLength1Input.unit = 'mm'
            self.form.rootLength2Input.unit = 'mm'
            self.form.rootLength1Input.setText(self.obj.RootLength1.UserString)
            self.form.rootLength2Input.setText(self.obj.RootLength2.UserString)

    def _convertRootPercent(self):
        if self.obj.RootPerCent:
            # Convert to percentages
            self.obj.RootLength1 = self._toPercent(self.obj.RootLength1.Value, self.obj.RootChord.Value)
            self.obj.RootLength2 = self._toPercent(self.obj.RootLength2.Value, self.obj.RootChord.Value)
        else:
            # Convert to lengths
            self.obj.RootLength1 = self._toLength(self.obj.RootLength1.Value, self.obj.RootChord.Value)
            self.obj.RootLength2 = self._toLength(self.obj.RootLength2.Value, self.obj.RootChord.Value)
        self._enableRootPercent()
        
    def onRootPerCent(self, value):
        self.obj.RootPerCent = self.form.rootPerCentCheckbox.isChecked()
        self._convertRootPercent()

        self.obj.Proxy.execute(self.obj)
        
    def onRootLength1(self, value):
        try:
            self.obj.RootLength1 = FreeCAD.Units.Quantity(value).Value
            self.obj.Proxy.execute(self.obj)
        except ValueError:
            pass
        
    def onRootLength2(self, value):
        try:
            self.obj.RootLength2 = FreeCAD.Units.Quantity(value).Value
            self.obj.Proxy.execute(self.obj)
        except ValueError:
            pass
        
    def onTipCrossSection(self, value):
        self.obj.TipCrossSection = value
        self._enableTipLengths()

        self.obj.Proxy.execute(self.obj)
        
    def onTipChord(self, value):
        try:
            self.obj.TipChord = FreeCAD.Units.Quantity(value).Value
            self.obj.Proxy.execute(self.obj)
        except ValueError:
            pass
        
    def onTipThickness(self, value):
        try:
            self.obj.TipThickness = FreeCAD.Units.Quantity(value).Value
            self.obj.Proxy.execute(self.obj)
        except ValueError:
            pass

    def _enableTipPercent(self):
        if self.obj.TipPerCent:
            self.form.tipLength1Input.unit = ''
            self.form.tipLength2Input.unit = ''
            self.form.tipLength1Input.setText(str(self.obj.TipLength1.Value))
            self.form.tipLength2Input.setText(str(self.obj.TipLength2.Value))
        else:
            self.form.tipLength1Input.unit = 'mm'
            self.form.tipLength2Input.unit = 'mm'
            self.form.tipLength1Input.setText(self.obj.TipLength1.UserString)
            self.form.tipLength2Input.setText(self.obj.TipLength2.UserString)

    def _convertTipPercent(self):
        if self.obj.TipPerCent:
            # Convert to percentages
            self.obj.TipLength1 = self._toPercent(self.obj.TipLength1.Value, self.obj.TipChord.Value)
            self.obj.TipLength2 = self._toPercent(self.obj.TipLength2.Value, self.obj.TipChord.Value)
        else:
            # Convert to lengths
            self.obj.TipLength1 = self._toLength(self.obj.TipLength1.Value, self.obj.TipChord.Value)
            self.obj.TipLength2 = self._toLength(self.obj.TipLength2.Value, self.obj.TipChord.Value)
        self._enableTipPercent()
        
    def onTipPerCent(self, value):
        self.obj.TipPerCent = self.form.tipPerCentCheckbox.isChecked()
        self._convertTipPercent()

        self.obj.Proxy.execute(self.obj)
        
    def onTipLength1(self, value):
        try:
            self.obj.TipLength1 = FreeCAD.Units.Quantity(value).Value
            self.obj.Proxy.execute(self.obj)
        except ValueError:
            pass
        
    def onTipLength2(self, value):
        try:
            self.obj.TipLength2 = FreeCAD.Units.Quantity(value).Value
            self.obj.Proxy.execute(self.obj)
        except ValueError:
            pass

    def onHeight(self, value):
        try:
            self.obj.Height = FreeCAD.Units.Quantity(value).Value
            self._sweepAngleFromLength(self.form.sweepLengthInput.property("quantity").Value)
            self.obj.Proxy.execute(self.obj)
        except ValueError:
            pass

    def _sweepLengthFromAngle(self, value):
        theta = _toFloat(value)
        if theta <= -90.0 or theta >= 90.0:
            _err("Sweep angle must be greater than -90 and less than +90")
            return
        theta = math.radians(-1.0 * (theta + 90.0))
        length = self.form.heightInput.property("quantity").Value / math.tan(theta)
        self.form.sweepLengthInput.setText("%f" % length)
        self.obj.SweepLength = length

    def _sweepAngleFromLength(self, value):
        length = _toFloat(value)
        theta = 90.0 - math.degrees(math.atan2(self.form.heightInput.property("quantity").Value, length))
        self.form.sweepAngleInput.setText("%f" % theta)
        self.obj.SweepAngle = theta
        
    def onSweepLength(self, value):
        try:
            self.obj.SweepLength = FreeCAD.Units.Quantity(value).Value
            self._sweepAngleFromLength(value)
            self.obj.Proxy.execute(self.obj)
        except ValueError:
            pass
        
    def onSweepAngle(self, value):
        try:
            self.obj.SweepAngle = FreeCAD.Units.Quantity(value).Value
            self._sweepLengthFromAngle(value)
            self.obj.Proxy.execute(self.obj)
        except ValueError:
            pass
        
    def _setTtwState(self):
        self.form.ttwOffsetInput.setEnabled(self.obj.Ttw)
        self.form.ttwLengthInput.setEnabled(self.obj.Ttw)
        self.form.ttwHeightInput.setEnabled(self.obj.Ttw)
        self.form.ttwThicknessInput.setEnabled(self.obj.Ttw)
        
    def onTtw(self, value):
        self.obj.Ttw = self.form.ttwCheckbox.isChecked()
        self._setTtwState()

        self.obj.Proxy.execute(self.obj)
        
    def onTTWOffset(self, value):
        try:
            self.obj.TtwOffset = FreeCAD.Units.Quantity(value).Value
            self.obj.Proxy.execute(self.obj)
        except ValueError:
            pass
        
    def onTTWLength(self, value):
        try:
            self.obj.TtwLength = FreeCAD.Units.Quantity(value).Value
            self.obj.Proxy.execute(self.obj)
        except ValueError:
            pass
        
    def onTTWHeight(self, value):
        try:
            self.obj.TtwHeight = FreeCAD.Units.Quantity(value).Value
            self.obj.Proxy.execute(self.obj)
        except ValueError:
            pass
        
    def onTTWThickness(self, value):
        try:
            self.obj.TtwThickness = FreeCAD.Units.Quantity(value).Value
            self.obj.Proxy.execute(self.obj)
        except ValueError:
            pass
        
    def getStandardButtons(self):
        return int(QtGui.QDialogButtonBox.Ok) | int(QtGui.QDialogButtonBox.Cancel)| int(QtGui.QDialogButtonBox.Apply)

    def clicked(self,button):
        if button == QtGui.QDialogButtonBox.Apply:
            #print "Apply"
            self.transferTo()
            self.obj.Proxy.execute(self.obj) 
        
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
