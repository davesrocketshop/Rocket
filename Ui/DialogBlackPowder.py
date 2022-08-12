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
"""Class for Black Powder calculator"""

__title__ = "FreeCAD Black Powder Calculator"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import math
    
import FreeCAD
import FreeCADGui

from DraftTools import translate

from PySide import QtGui, QtCore
from PySide2.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGridLayout

FORCE_CUSTOM = translate('Rocket', 'Custom')
FORCE_LOW = translate('Rocket', 'Low')
FORCE_HIGH = translate('Rocket', 'High')

class DialogBlackPowder(QDialog):
    def __init__(self):
        super().__init__()


        self.initUI()

    def initUI(self):

        ui = FreeCADGui.UiLoader()

        # create our window
        # define window		xLoc,yLoc,xDim,yDim
        self.setGeometry(	250, 250, 640, 480)
        self.setWindowTitle(translate('Rocket', "Ejection Charge Calculator"))
        self.resize(QtCore.QSize(100,100).expandedTo(self.minimumSizeHint())) # sets size of the widget
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.warningLabel = QtGui.QTextEdit()
        self.warningLabel.setLineWrapMode(QtGui.QTextEdit.WidgetWidth)
        self.warningLabel.setHtml(translate('Rocket','''
        <html>
        <h1>WARNING</h1>
        <p>This calculator is an estimate only. Ground test your ejection system before flying. In certain cases this calculation may overestimate the amount of powder required</p>
        </html>
        '''))
        # self.warningLabel.setMinimumWidth(250)
        self.warningLabel.setReadOnly(True)

        self.diameterLabel = QtGui.QLabel(translate('Rocket', "Body Tube Diameter"), self)

        self.diameterInput = ui.createWidget("Gui::InputField")
        self.diameterInput.unit = 'mm'
        self.diameterInput.setMinimumWidth(100)
        self.diameterInput.setText("98.0 mm")
        self.diameterInput.textEdited.connect(self.onDiameter)

        self.lengthLabel = QtGui.QLabel(translate('Rocket', "Body Tube Length"), self)

        self.lengthInput = ui.createWidget("Gui::InputField")
        self.lengthInput.unit = 'mm'
        self.lengthInput.setText("300.0 mm")
        self.lengthInput.setMinimumWidth(100)
        self.lengthInput.textEdited.connect(self.onLength)

        self.forceLabel = QtGui.QLabel(translate('Rocket', "Force"), self)

        self.forceInput = ui.createWidget("Gui::InputField")
        self.forceInput.unit = 'N'
        self.forceInput.setText("667.233 N")
        self.forceInput.setMinimumWidth(100)
        self.forceInput.textEdited.connect(self.onForce)

        self.pressureLabel = QtGui.QLabel(translate('Rocket', "Pressure"), self)

        self.pressureInput = ui.createWidget("Gui::InputField")
        self.pressureInput.unit = 'kPa'
        self.pressureInput.setText("1034.25 kPa")
        self.pressureInput.setMinimumWidth(100)
        self.pressureInput.textEdited.connect(self.onPressure)

        self.forceTypes = (
            FORCE_CUSTOM,
            FORCE_LOW,
            FORCE_HIGH
        )
        self.forceCombo = QtGui.QComboBox(self)
        self.forceCombo.addItems(self.forceTypes)
        self.forceCombo.setCurrentText(FORCE_LOW)
        self.forceCombo.currentTextChanged.connect(self.onForceCombo)

        self.powderLabel = QtGui.QLabel(translate('Rocket', "FFFFg Powder"), self)

        self.powderInput = QtGui.QLineEdit()
        self.powderInput.setText("49.0 g")
        self.powderInput.setMinimumWidth(100)
        self.powderInput.setReadOnly(True)

        # OK button
        okButton = QtGui.QPushButton('OK', self)
        okButton.setDefault(False)
        okButton.setAutoDefault(False)
        okButton.clicked.connect(self.onOk)

        layout = QVBoxLayout()

        line = QHBoxLayout()
        line.addWidget(self.warningLabel)
        layout.addLayout(line)

        line = QGridLayout()

        row = 0
        line.addWidget(self.diameterLabel, row, 0, 1, 2)
        line.addWidget(self.diameterInput, row, 1)
        row += 1

        line.addWidget(self.lengthLabel, row, 0)
        line.addWidget(self.lengthInput, row, 1)
        row += 1

        line.addWidget(self.forceLabel, row, 0)
        line.addWidget(self.forceInput, row, 1)
        line.addWidget(self.forceCombo, row, 2)
        row += 1

        line.addWidget(self.pressureLabel, row, 0)
        line.addWidget(self.pressureInput, row, 1)
        row += 1

        line.addWidget(self.powderLabel, row, 0)
        line.addWidget(self.powderInput, row, 1)

        layout.addLayout(line)

        line = QHBoxLayout()
        line.addStretch()
        line.addWidget(okButton)
        layout.addLayout(line)

        self.setLayout(layout)

        self._setPressureFromForce()
        self._calc()

        # now make the window visible
        self.show()

    def _calc(self):
        # Use the quantity object for units conversion
        diameter = float(FreeCAD.Units.Quantity(self.diameterInput.text()).Value) / 1000.0 # Convert to meters
        length = float(FreeCAD.Units.Quantity(self.lengthInput.text()).Value) / 1000.0
        pressure = float(FreeCAD.Units.Quantity(self.pressureInput.text()).Value) * 1000.0

        coefficient = 1.0 / (9.807 * 12.1579 * 1739.0) # 1 / (g * R * T) [(m / sec /sec) (m / K) (K)]
        bp = coefficient * pressure * (diameter * diameter) / 4.0 * math.pi * length

        self.powderInput.setText("%f g" % (bp * 1000.0)) # Always report in grams

    def onDiameter(self, value):
        try:
            self.diameterInput.setText(value)
            self._setPressureFromForce()
            self._calc()
        except ValueError:
            pass

    def onLength(self, value):
        try:
            self.lengthInput.setText(value)
            self._calc()
        except ValueError:
            pass

    def _setPressureFromForce(self):
        diameter = float(FreeCAD.Units.Quantity(self.diameterInput.text()).Value) / 1000.0 # Convert to meters
        force = float(FreeCAD.Units.Quantity(self.forceInput.text()).Value) / 1000.0

        area = (diameter * diameter) / 4.0 * math.pi
        pressure = force / area
        self.pressureInput.setText(FreeCAD.Units.Quantity(str(pressure) + "Pa").UserString)

    def onForce(self, value):
        try:
            self.forceCombo.setCurrentText(FORCE_CUSTOM)
            self.forceInput.setText(value)
            self._setPressureFromForce()
            self._calc()
        except ValueError:
            pass

    def _setForceFromPressure(self):
        diameter = float(FreeCAD.Units.Quantity(self.diameterInput.text()).Value) / 1000.0 # Convert to meters
        pressure = float(FreeCAD.Units.Quantity(self.pressureInput.text()).Value) * 1000.0

        area = (diameter * diameter) / 4.0 * math.pi
        force = pressure * area
        self.forceInput.setText(FreeCAD.Units.Quantity(str(force) + "N").UserString)

    def onPressure(self, value):
        try:
            self.forceCombo.setCurrentText(FORCE_CUSTOM)
            self.pressureInput.setText(value)
            self._setForceFromPressure()
            self._calc()
        except ValueError:
            pass

    def onForceCombo(self, value):
        if value == FORCE_HIGH:
            self.forceInput.setText("889.644 N")
        elif value == FORCE_LOW:
            self.forceInput.setText("667.233 N")
        self._setPressureFromForce()
        self._calc()

    def onOk(self):
        self.close()
