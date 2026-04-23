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
"""Class for Black Powder calculator"""

__title__ = "FreeCAD Black Powder Calculator"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import math

import FreeCAD
import FreeCADGui

translate = FreeCAD.Qt.translate

from PySide import QtCore
# from PySide import QtGui, QtCore
# from PySide.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGridLayout

from Ui.UiDialog import UiDialog

FORCE_CUSTOM = translate('Rocket', 'Custom')
FORCE_LOW = translate('Rocket', 'Low')
FORCE_HIGH = translate('Rocket', 'High')

SHEAR_TYPE_M2 = translate('Rocket', 'M2')
SHEAR_TYPE_2_56 = translate('Rocket', '2-56')
SHEAR_TYPE_4_40 = translate('Rocket', '4-40')
SHEAR_TYPE_M3 = translate('Rocket', 'M3')
SHEAR_TYPE_6_32 = translate('Rocket', '6-32')

class DialogBlackPowder(UiDialog):
    def __init__(self):
        super().__init__("DialogBlackPowder", "DialogBlackPowder.ui")


        self.initUI()

    def initUI(self):
        super().initUI()

        # create our window
        self._ui.setWindowTitle(translate('Rocket', "Ejection Charge Calculator"))
        self._ui.resize(QtCore.QSize(100,100).expandedTo(self.minimumSizeHint())) # sets size of the widget

        # self.warningLabel = QtGui.QTextEdit()
        # self.warningLabel.setLineWrapMode(QtGui.QTextEdit.WidgetWidth)
        # self.warningLabel.setHtml(translate('Rocket','''
        # <html>
        # <h1>WARNING</h1>
        # <p>This calculator is an estimate only. Ground test your ejection system before flying. In certain cases this calculation may overestimate the amount of powder required.</p>
        # </html>
        # '''))
        # # self.warningLabel.setMinimumWidth(250)
        # self.warningLabel.setReadOnly(True)

        # self.diameterLabel = QtGui.QLabel(translate('Rocket', "Body tube diameter"), self)

        # self.diameterInput = ui.createWidget("Gui::InputField")
        # self.diameterInput.unit = FreeCAD.Units.Length
        # self.diameterInput.setMinimumWidth(100)
        self._ui.diameterInput.setText("98.0 mm")
        self._ui.diameterInput.textEdited.connect(self.onDiameter)

        # self.lengthLabel = QtGui.QLabel(translate('Rocket', "Body tube length"), self)

        # self.lengthInput = ui.createWidget("Gui::InputField")
        # self.lengthInput.unit = FreeCAD.Units.Length
        self._ui.lengthInput.setText("300.0 mm")
        # self.lengthInput.setMinimumWidth(100)
        self._ui.lengthInput.textEdited.connect(self.onLength)

        self._ui.shearSpinBox.setValue(0)
        self._ui.shearSpinBox.valueChanged.connect(self.onShearSpinBox)

        self._ui.shearTypeCombo.addItem(translate('Rocket', SHEAR_TYPE_M2), SHEAR_TYPE_M2)
        self._ui.shearTypeCombo.addItem(translate('Rocket', SHEAR_TYPE_2_56), SHEAR_TYPE_2_56)
        self._ui.shearTypeCombo.addItem(translate('Rocket', SHEAR_TYPE_4_40), SHEAR_TYPE_4_40)
        self._ui.shearTypeCombo.addItem(translate('Rocket', SHEAR_TYPE_M3), SHEAR_TYPE_M3)
        self._ui.shearTypeCombo.addItem(translate('Rocket', SHEAR_TYPE_6_32), SHEAR_TYPE_6_32)
        self._ui.shearTypeCombo.setCurrentText(SHEAR_TYPE_2_56)
        self._ui.shearTypeCombo.currentTextChanged.connect(self.onShearTypeCombo)

        # self.forceLabel = QtGui.QLabel(translate('Rocket', "Force"), self)

        # self.forceInput = ui.createWidget("Gui::InputField")
        # self.forceInput.unit = 'N'
        self._ui.forceInput.setText("667.233 N")
        # self.forceInput.setMinimumWidth(100)
        self._ui.forceInput.textEdited.connect(self.onForce)

        # self.forceCombo = QtGui.QComboBox(self)
        self._ui.forceCombo.addItem(translate('Rocket', FORCE_CUSTOM), FORCE_CUSTOM)
        self._ui.forceCombo.addItem(translate('Rocket', FORCE_LOW), FORCE_LOW)
        self._ui.forceCombo.addItem(translate('Rocket', FORCE_HIGH), FORCE_HIGH)
        self._ui.forceCombo.setCurrentText(FORCE_LOW)
        self._ui.forceCombo.currentTextChanged.connect(self.onForceCombo)

        # self.pressureLabel = QtGui.QLabel(translate('Rocket', "Pressure"), self)

        # self.pressureInput = ui.createWidget("Gui::InputField")
        # self.pressureInput.unit = 'kPa'
        self._ui.pressureInput.setText("1034.25 kPa")
        # self.pressureInput.setMinimumWidth(100)
        self._ui.pressureInput.textEdited.connect(self.onPressure)

        # self.powderLabel = QtGui.QLabel(translate('Rocket', "FFFFg powder"), self)

        # self.powderInput = QtGui.QLineEdit()
        self._ui.powderInput.setText("49.0 g")
        # self.powderInput.setMinimumWidth(100)
        # self.powderInput.setReadOnly(True)

        # OK button
        # okButton = QtGui.QPushButton('OK', self)
        # okButton.setDefault(False)
        # okButton.setAutoDefault(False)
        # okButton.clicked.connect(self.onOk)

        # layout = QVBoxLayout()

        # line = QHBoxLayout()
        # line.addWidget(self.warningLabel)
        # layout.addLayout(line)

        # line = QGridLayout()

        # row = 0
        # line.addWidget(self.diameterLabel, row, 0, 1, 2)
        # line.addWidget(self.diameterInput, row, 1)
        # row += 1

        # line.addWidget(self.lengthLabel, row, 0)
        # line.addWidget(self.lengthInput, row, 1)
        # row += 1

        # line.addWidget(self.forceLabel, row, 0)
        # line.addWidget(self.forceInput, row, 1)
        # line.addWidget(self.forceCombo, row, 2)
        # row += 1

        # line.addWidget(self.pressureLabel, row, 0)
        # line.addWidget(self.pressureInput, row, 1)
        # row += 1

        # line.addWidget(self.powderLabel, row, 0)
        # line.addWidget(self.powderInput, row, 1)

        # layout.addLayout(line)

        # line = QHBoxLayout()
        # line.addStretch()
        # line.addWidget(okButton)
        # layout.addLayout(line)

        # self.setLayout(layout)

        self._setPressureFromForce()
        self._calc()

        # now make the window visible
        self._ui.show()

    def _calc(self):
        # Use the quantity object for units conversion
        diameter = float(FreeCAD.Units.Quantity(self._ui.diameterInput.text()).Value) / 1000.0 # Convert to meters
        length = float(FreeCAD.Units.Quantity(self._ui.lengthInput.text()).Value) / 1000.0
        pressure = float(FreeCAD.Units.Quantity(self._ui.pressureInput.text()).Value) * 1000.0

        coefficient = 1.0 / (9.807 * 12.1579 * 1739.0) # 1 / (g * R * T) [(m / sec /sec) (m / K) (K)]
        bp = coefficient * pressure * (diameter * diameter) / 4.0 * math.pi * length

        self._ui.powderInput.setText("%f g" % (bp * 1000.0)) # Always report in grams

    def onDiameter(self, value):
        try:
            self._ui.diameterInput.setText(value)
            self._setPressureFromForce()
            self._calc()
        except ValueError:
            pass

    def onLength(self, value):
        try:
            self._ui.lengthInput.setText(value)
            self._calc()
        except ValueError:
            pass

    def onShearSpinBox(self, value):
        try:
            self._ui.shearSpinBox.setValue(value)
            self._calc()
        except ValueError:
            pass

    def _setPressureFromForce(self):
        diameter = float(FreeCAD.Units.Quantity(self._ui.diameterInput.text()).Value) / 1000.0 # Convert to meters
        force = float(FreeCAD.Units.Quantity(self._ui.forceInput.text()).Value) / 1000.0

        area = (diameter * diameter) / 4.0 * math.pi
        pressure = force / area
        self._ui.pressureInput.setText(FreeCAD.Units.Quantity(str(pressure) + "Pa").UserString)

    def onForce(self, value):
        try:
            self._ui.forceCombo.setCurrentIndex(self._ui.forceCombo.findData(FORCE_CUSTOM))
            self._setPressureFromForce()
            self._calc()
        except ValueError:
            pass

    def _setForceFromPressure(self):
        diameter = float(FreeCAD.Units.Quantity(self._ui.diameterInput.text()).Value) / 1000.0 # Convert to meters
        pressure = float(FreeCAD.Units.Quantity(self._ui.pressureInput.text()).Value) * 1000.0

        area = (diameter * diameter) / 4.0 * math.pi
        force = pressure * area
        self._ui.forceInput.setText(FreeCAD.Units.Quantity(str(force) + "N").UserString)

    def onPressure(self, value):
        try:
            self._ui.forceCombo.setCurrentIndex(self._ui.forceCombo.findData(FORCE_CUSTOM))
            self._setForceFromPressure()
            self._calc()
        except ValueError:
            pass

    def onShearTypeCombo(self, value):
        data = self._ui.shearTypeCombo.currentData()
        # if data == SHEAR_TYPE_2_56:
        #     self._ui.forceInput.setText("889.644 N")
        # elif data == SHEAR_TYPE_M2:
        #     self._ui.forceInput.setText("667.233 N")
        # self._setPressureFromForce()
        # self._calc()

    def onForceCombo(self, value):
        data = self._ui.forceCombo.currentData()
        if data == FORCE_HIGH:
            self._ui.forceInput.setText("889.644 N")
        elif data == FORCE_LOW:
            self._ui.forceInput.setText("667.233 N")
        self._setPressureFromForce()
        self._calc()

    def onOk(self):
        self.close()
