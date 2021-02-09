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

from App.Constants import FIN_TYPE_TRAPEZOID, FIN_TYPE_ELLIPSE, FIN_TYPE_TUBE, FIN_TYPE_SKETCH
from App.Constants import FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, \
    FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE

from App.Utilities import _toFloat, _err

class _FinDialog(QDialog):

    def __init__(self, parent=None):
        super(_FinDialog, self).__init__(parent)


        # define our window
        self.setGeometry(250, 250, 400, 350)
        self.setWindowTitle("Fin Parameter")

        # Select the type of nose cone
        self.finTypeLabel = QtGui.QLabel("Fin type", self)

        self.finTypes = (FIN_TYPE_TRAPEZOID, 
            #FIN_TYPE_ELLIPSE, 
            #FIN_TYPE_TUBE, 
            #FIN_TYPE_SKETCH
            )
        self.finTypesCombo = QtGui.QComboBox(self)
        self.finTypesCombo.addItems(self.finTypes)

        # Get the fin parameters: length, width, etc...
        self.rootLabel = QtGui.QLabel("Fin Root", self)

        # Select the type of cross section
        self.rootCrossSectionLabel = QtGui.QLabel("Cross Section", self)

        self.rootCrossSections = (FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE,
            FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE)
        self.rootCrossSectionsCombo = QtGui.QComboBox(self)
        self.rootCrossSectionsCombo.addItems(self.rootCrossSections)

        # Get the fin parameters: length, width, etc...
        self.rootChordLabel = QtGui.QLabel("Chord", self)

        self.rootChordValidator = QtGui.QDoubleValidator(self)
        self.rootChordValidator.setBottom(0.0)

        self.rootChordInput = QtGui.QLineEdit(self)
        self.rootChordInput.setFixedWidth(100)
        self.rootChordInput.setValidator(self.rootChordValidator)

        self.rootThicknessLabel = QtGui.QLabel("Thickness", self)

        self.rootThicknessValidator = QtGui.QDoubleValidator(self)
        self.rootThicknessValidator.setBottom(0.0)

        self.rootThicknessInput = QtGui.QLineEdit(self)
        self.rootThicknessInput.setFixedWidth(100)
        self.rootThicknessInput.setValidator(self.rootThicknessValidator)

        self.rootPerCentLabel = QtGui.QLabel("Use percentage", self)

        self.rootPerCentCheckbox = QtGui.QCheckBox(self)
        self.rootPerCentCheckbox.setCheckState(QtCore.Qt.Unchecked)

        self.rootLength1Label = QtGui.QLabel("Length 1", self)

        self.rootLength1Validator = QtGui.QDoubleValidator(self)
        self.rootLength1Validator.setBottom(0.0)

        self.rootLength1Input = QtGui.QLineEdit(self)
        self.rootLength1Input.setFixedWidth(100)
        self.rootLength1Input.setValidator(self.rootLength1Validator)

        self.rootLength2Label = QtGui.QLabel("Length 2", self)

        self.rootLength2Validator = QtGui.QDoubleValidator(self)
        self.rootLength2Validator.setBottom(0.0)

        self.rootLength2Input = QtGui.QLineEdit(self)
        self.rootLength2Input.setFixedWidth(100)
        self.rootLength2Input.setValidator(self.rootLength2Validator)

        self.tipLabel = QtGui.QLabel("Fin Tip", self)

        # Select the type of cross section
        self.tipCrossSectionLabel = QtGui.QLabel("Cross Section", self)

        self.tipCrossSections = (FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE,
            FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE)
        self.tipCrossSectionsCombo = QtGui.QComboBox(self)
        self.tipCrossSectionsCombo.addItems(self.tipCrossSections)

        self.tipChordLabel = QtGui.QLabel("Chord", self)

        self.tipChordValidator = QtGui.QDoubleValidator(self)
        self.tipChordValidator.setBottom(0.0)

        self.tipChordInput = QtGui.QLineEdit(self)
        self.tipChordInput.setFixedWidth(100)
        self.tipChordInput.setValidator(self.tipChordValidator)

        self.tipThicknessLabel = QtGui.QLabel("Thickness", self)

        self.tipThicknessValidator = QtGui.QDoubleValidator(self)
        self.tipThicknessValidator.setBottom(0.0)

        self.tipThicknessInput = QtGui.QLineEdit(self)
        self.tipThicknessInput.setFixedWidth(100)
        self.tipThicknessInput.setValidator(self.tipThicknessValidator)

        self.tipPerCentLabel = QtGui.QLabel("Use percentage", self)

        self.tipPerCentCheckbox = QtGui.QCheckBox(self)
        self.tipPerCentCheckbox.setCheckState(QtCore.Qt.Unchecked)

        self.tipLength1Label = QtGui.QLabel("Length 1", self)

        self.tipLength1Validator = QtGui.QDoubleValidator(self)
        self.tipLength1Validator.setBottom(0.0)

        self.tipLength1Input = QtGui.QLineEdit(self)
        self.tipLength1Input.setFixedWidth(100)
        self.tipLength1Input.setValidator(self.tipLength1Validator)

        self.tipLength2Label = QtGui.QLabel("Length 2", self)

        self.tipLength2Validator = QtGui.QDoubleValidator(self)
        self.tipLength2Validator.setBottom(0.0)

        self.tipLength2Input = QtGui.QLineEdit(self)
        self.tipLength2Input.setFixedWidth(100)
        self.tipLength2Input.setValidator(self.tipLength2Validator)

        self.heightLabel = QtGui.QLabel("Height", self)

        self.heightValidator = QtGui.QDoubleValidator(self)
        self.heightValidator.setBottom(0.0)

        self.heightInput = QtGui.QLineEdit(self)
        self.heightInput.setFixedWidth(100)
        self.heightInput.setValidator(self.heightValidator)

        # Sweep can be forward (-sweep) or backward (+sweep)
        self.sweepLengthLabel = QtGui.QLabel("Sweep Length", self)

        self.sweepLengthInput = QtGui.QLineEdit(self)
        self.sweepLengthInput.setFixedWidth(100)

        # Sweep angle is tied to sweep length. It can be forward (> -90) or backward (< 90)
        self.sweepAngleLabel = QtGui.QLabel("Sweep Angle", self)

        self.sweepAngleValidator = QtGui.QDoubleValidator(self)
        self.sweepAngleValidator.setBottom(-90.0)
        self.sweepAngleValidator.setTop(90.0)

        self.sweepAngleInput = QtGui.QLineEdit(self)
        self.sweepAngleInput.setFixedWidth(100)
        self.sweepAngleInput.setValidator(self.sweepAngleValidator)

        self.ttwLabel = QtGui.QLabel("TTW Tab", self)

        self.ttwCheckbox = QtGui.QCheckBox(self)
        self.ttwCheckbox.setCheckState(QtCore.Qt.Unchecked)

        self.ttwOffsetLabel = QtGui.QLabel("Offset", self)

        self.ttwOffsetValidator = QtGui.QDoubleValidator(self)
        self.ttwOffsetValidator.setBottom(0.0)

        self.ttwOffsetInput = QtGui.QLineEdit(self)
        self.ttwOffsetInput.setFixedWidth(100)
        self.ttwOffsetInput.setValidator(self.ttwOffsetValidator)

        self.ttwLengthLabel = QtGui.QLabel("Length", self)

        self.ttwLengthValidator = QtGui.QDoubleValidator(self)
        self.ttwLengthValidator.setBottom(0.0)

        self.ttwLengthInput = QtGui.QLineEdit(self)
        self.ttwLengthInput.setFixedWidth(100)
        self.ttwLengthInput.setValidator(self.ttwLengthValidator)

        self.ttwHeightLabel = QtGui.QLabel("Height", self)

        self.ttwHeightValidator = QtGui.QDoubleValidator(self)
        self.ttwHeightValidator.setBottom(0.0)

        self.ttwHeightInput = QtGui.QLineEdit(self)
        self.ttwHeightInput.setFixedWidth(100)
        self.ttwHeightInput.setValidator(self.ttwHeightValidator)

        self.ttwThicknessLabel = QtGui.QLabel("Thickness", self)

        self.ttwThicknessValidator = QtGui.QDoubleValidator(self)
        self.ttwThicknessValidator.setBottom(0.0)

        self.ttwThicknessInput = QtGui.QLineEdit(self)
        self.ttwThicknessInput.setFixedWidth(100)
        self.ttwThicknessInput.setValidator(self.ttwThicknessValidator)

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
        self.form.setWindowIcon(QtGui.QIcon(":/icons/Rocket_Fin.svg"))
        
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
        self.obj.RootChord = _toFloat(self.form.rootChordInput.text())
        self.obj.RootThickness = _toFloat(self.form.rootThicknessInput.text())
        self.obj.RootPerCent = self.form.rootPerCentCheckbox.isChecked()
        self.obj.RootLength1 = _toFloat(self.form.rootLength1Input.text())
        self.obj.RootLength2 = _toFloat(self.form.rootLength2Input.text())

        self.obj.TipCrossSection = str(self.form.tipCrossSectionsCombo.currentText())
        self.obj.TipChord = _toFloat(self.form.tipChordInput.text())
        self.obj.TipThickness = _toFloat(self.form.tipThicknessInput.text())
        self.obj.TipPerCent = self.form.tipPerCentCheckbox.isChecked()
        self.obj.TipLength1 = _toFloat(self.form.tipLength1Input.text())
        self.obj.TipLength2 = _toFloat(self.form.tipLength2Input.text())

        self.obj.Height = _toFloat(self.form.heightInput.text())
        self.obj.SweepLength = _toFloat(self.form.sweepLengthInput.text())
        self.obj.SweepAngle = _toFloat(self.form.sweepAngleInput.text())

        self.obj.Ttw = self.form.ttwCheckbox.isChecked()
        self.obj.TtwOffset = _toFloat(self.form.ttwOffsetInput.text())
        self.obj.TtwLength = _toFloat(self.form.ttwLengthInput.text())
        self.obj.TtwHeight = _toFloat(self.form.ttwHeightInput.text())
        self.obj.TtwThickness = _toFloat(self.form.ttwThicknessInput.text())

    def transferFrom(self):
        "Transfer from the object to the dialog"
        self.form.finTypesCombo.setCurrentText(self.obj.FinType)

        self.form.rootCrossSectionsCombo.setCurrentText(self.obj.RootCrossSection)
        self.form.rootChordInput.setText("%f" % self.obj.RootChord)
        self.form.rootThicknessInput.setText("%f" % self.obj.RootThickness)
        self.form.rootPerCentCheckbox.setChecked(self.obj.RootPerCent)
        self.form.rootLength1Input.setText("%f" % self.obj.RootLength1)
        self.form.rootLength2Input.setText("%f" % self.obj.RootLength2)

        self.form.tipCrossSectionsCombo.setCurrentText(self.obj.TipCrossSection)
        self.form.tipChordInput.setText("%f" % self.obj.TipChord)
        self.form.tipThicknessInput.setText("%f" % self.obj.TipThickness)
        self.form.tipPerCentCheckbox.setChecked(self.obj.TipPerCent)
        self.form.tipLength1Input.setText("%f" % self.obj.TipLength1)
        self.form.tipLength2Input.setText("%f" % self.obj.TipLength2)

        self.form.heightInput.setText("%f" % self.obj.Height)
        self.form.sweepLengthInput.setText("%f" % self.obj.SweepLength)
        self.form.sweepAngleInput.setText("%f" % self.obj.SweepAngle)

        self.form.ttwCheckbox.setChecked(self.obj.Ttw)
        self.form.ttwOffsetInput.setText("%f" % self.obj.TtwOffset)
        self.form.ttwLengthInput.setText("%f" % self.obj.TtwLength)
        self.form.ttwHeightInput.setText("%f" % self.obj.TtwHeight)
        self.form.ttwThicknessInput.setText("%f" % self.obj.TtwThickness)

        self._enableRootLengths()
        self._enableTipLengths()
        self._sweepAngleFromLength()
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
        self.obj.RootChord = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onRootThickness(self, value):
        self.obj.RootThickness = _toFloat(value)
        self.obj.Proxy.execute(self.obj)

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
        
    def onRootPerCent(self, value):
        self.obj.RootPerCent = self.form.rootPerCentCheckbox.isChecked()
        if self.obj.RootPerCent:
            # Convert to percentages
            self.obj.RootLength1 = self._toPercent(float(self.obj.RootLength1), float(self.obj.RootChord))
            self.obj.RootLength2 = self._toPercent(float(self.obj.RootLength2), float(self.obj.RootChord))
            self.form.rootLength1Input.setText("%f" % self.obj.RootLength1)
            self.form.rootLength2Input.setText("%f" % self.obj.RootLength2)
        else:
            # Convert to lengths
            self.obj.RootLength1 = self._toLength(float(self.obj.RootLength1), float(self.obj.RootChord))
            self.obj.RootLength2 = self._toLength(float(self.obj.RootLength2), float(self.obj.RootChord))
            self.form.rootLength1Input.setText("%f" % self.obj.RootLength1)
            self.form.rootLength2Input.setText("%f" % self.obj.RootLength2)

        self.obj.Proxy.execute(self.obj)
        
    def onRootLength1(self, value):
        self.obj.RootLength1 = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onRootLength2(self, value):
        self.obj.RootLength2 = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onTipCrossSection(self, value):
        self.obj.TipCrossSection = value
        self._enableTipLengths()

        self.obj.Proxy.execute(self.obj)
        
    def onTipChord(self, value):
        self.obj.TipChord = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onTipThickness(self, value):
        self.obj.TipThickness = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onTipPerCent(self, value):
        self.obj.TipPerCent = self.form.tipPerCentCheckbox.isChecked()
        if self.obj.TipPerCent:
            # Convert to percentages
            self.obj.TipLength1 = self._toPercent(float(self.obj.TipLength1), float(self.obj.TipChord))
            self.obj.TipLength2 = self._toPercent(float(self.obj.TipLength2), float(self.obj.TipChord))
            self.form.tipLength1Input.setText("%f" % self.obj.TipLength1)
            self.form.tipLength2Input.setText("%f" % self.obj.TipLength2)
        else:
            # Convert to lengths
            self.obj.TipLength1 = self._toLength(float(self.obj.TipLength1), float(self.obj.TipChord))
            self.obj.TipLength2 = self._toLength(float(self.obj.TipLength2), float(self.obj.TipChord))
            self.form.tipLength1Input.setText("%f" % self.obj.TipLength1)
            self.form.tipLength2Input.setText("%f" % self.obj.TipLength2)

        self.obj.Proxy.execute(self.obj)
        
    def onTipLength1(self, value):
        self.obj.TipLength1 = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onTipLength2(self, value):
        self.obj.TipLength2 = _toFloat(value)
        self.obj.Proxy.execute(self.obj)

    def onHeight(self, value):
        self._sweepAngleFromLength()
        self.obj.Height = _toFloat(value)
        self.obj.Proxy.execute(self.obj)

    def _sweepLengthFromAngle(self):
        theta = _toFloat(self.form.sweepAngleInput.text())
        if theta <= -90.0 or theta >= 90.0:
            _err("Sweep angle must be greater than -90 and less than +90")
            return
        theta = math.radians(-1.0 * (theta + 90.0))
        length = _toFloat(self.form.heightInput.text()) / math.tan(theta)
        self.form.sweepLengthInput.setText("%f" % length)
        self.obj.SweepLength = length

    def _sweepAngleFromLength(self):
        theta = 90.0 - math.degrees(math.atan2(_toFloat(self.form.heightInput.text()), _toFloat(self.form.sweepLengthInput.text())))
        self.form.sweepAngleInput.setText("%f" % theta)
        self.obj.SweepAngle = theta
        
    def onSweepLength(self, value):
        self._sweepAngleFromLength()
        self.obj.SweepLength = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onSweepAngle(self, value):
        self._sweepLengthFromAngle()
        self.obj.SweepAngle = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
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
        self.obj.TtwOffset = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onTTWLength(self, value):
        self.obj.TtwLength = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onTTWHeight(self, value):
        self.obj.TtwHeight = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onTTWThickness(self, value):
        self.obj.TtwThickness = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
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
