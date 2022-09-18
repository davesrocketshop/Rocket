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
"""Class for Parachute calculator"""

__title__ = "FreeCAD Parachute Calculator"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import math
    
import FreeCAD
import FreeCADGui

from DraftTools import translate

from PySide import QtGui, QtCore
from PySide2.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGridLayout

VELOCITY_CUSTOM = translate('Rocket', 'Custom')
VELOCITY_DROGUE = translate('Rocket', 'Drogue')
VELOCITY_MAIN = translate('Rocket', 'Main')

DRAG_CUSTOM = translate('Rocket', 'Custom')
DRAG_DOME = translate('Rocket', 'Dome')
DRAG_ROUND = translate('Rocket', 'Round')
DRAG_HEX = translate('Rocket', 'Hexagonal')
DRAG_SQUARE = translate('Rocket', 'Square')

class DialogParachute(QDialog):
    def __init__(self):
        super().__init__()


        self.initUI()

    def initUI(self):

        ui = FreeCADGui.UiLoader()

        # create our window
        # define window		xLoc,yLoc,xDim,yDim
        self.setGeometry(	250, 250, 640, 480)
        self.setWindowTitle(translate('Rocket', "Parachute Calculator"))
        self.resize(QtCore.QSize(100,100).expandedTo(self.minimumSizeHint())) # sets size of the widget
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.weightLabel = QtGui.QLabel(translate('Rocket', "Rocket Weight"), self)

        self.weightInput = ui.createWidget("Gui::InputField")
        self.weightInput.unit = 'kg'
        self.weightInput.setMinimumWidth(100)
        self.weightInput.setText("0.0")
        self.weightInput.textEdited.connect(self.onWeight)

        self.velocityLabel = QtGui.QLabel(translate('Rocket', "Terminal Velocity"), self)

        self.velocityInput = ui.createWidget("Gui::InputField")
        self.velocityInput.unit = "m/s"
        self.velocityInput.setText("6.1")
        self.velocityInput.setMinimumWidth(100)
        self.velocityInput.textEdited.connect(self.onVelocity)

        self.velocityTypes = (
            VELOCITY_CUSTOM,
            VELOCITY_DROGUE,
            VELOCITY_MAIN
        )
        self.velocityCombo = QtGui.QComboBox(self)
        self.velocityCombo.addItems(self.velocityTypes)
        self.velocityCombo.setCurrentText(VELOCITY_MAIN)
        self.velocityCombo.currentTextChanged.connect(self.onVelocityCombo)

        self.dragLabel = QtGui.QLabel(translate('Rocket', "Drag Coefficient"), self)

        self.dragInput = QtGui.QLineEdit()
        self.dragInput.setText("0.75")
        self.dragInput.setMinimumWidth(100)
        self.dragInput.textEdited.connect(self.onDrag)

        self.dragShapes = (
            DRAG_CUSTOM,
            DRAG_DOME,
            DRAG_ROUND,
            DRAG_HEX,
            DRAG_SQUARE
        )
        self.dragCombo = QtGui.QComboBox(self)
        self.dragCombo.addItems(self.dragShapes)
        self.dragCombo.setCurrentText(DRAG_ROUND)
        self.dragCombo.currentTextChanged.connect(self.onDragCombo)

        self.diameterLabel = QtGui.QLabel(translate('Rocket', "Diameter"), self)

        self.diameterInput = QtGui.QLineEdit() # ui.createWidget("Gui::InputField")
        # self.diameterInput.unit = 'mm'
        self.diameterInput.setText("0.0 N")
        self.diameterInput.setMinimumWidth(100)
        # self.diameterInput.textEdited.connect(self.onDiameter)
        self.diameterInput.setReadOnly(True)

        # OK button
        okButton = QtGui.QPushButton('OK', self)
        okButton.setDefault(False)
        okButton.setAutoDefault(False)
        okButton.clicked.connect(self.onOk)

        layout = QVBoxLayout()

        line = QGridLayout()

        row = 0
        line.addWidget(self.weightLabel, row, 0, 1, 2)
        line.addWidget(self.weightInput, row, 1)
        row += 1

        line.addWidget(self.velocityLabel, row, 0)
        line.addWidget(self.velocityInput, row, 1)
        line.addWidget(self.velocityCombo, row, 2)
        row += 1

        line.addWidget(self.dragLabel, row, 0)
        line.addWidget(self.dragInput, row, 1)
        line.addWidget(self.dragCombo, row, 2)
        row += 1

        line.addWidget(self.diameterLabel, row, 0)
        line.addWidget(self.diameterInput, row, 1)

        layout.addLayout(line)

        line = QHBoxLayout()
        line.addStretch()
        line.addWidget(okButton)
        layout.addLayout(line)

        self.setLayout(layout)

        self._calcDiameter()

        # now make the window visible
        self.show()

    def _calcDiameter(self):
        # Use the quantity object for units conversion
        M = float(FreeCAD.Units.Quantity(self.weightInput.text()).Value) #/ 1000.0 # Convert to kg
        V = float(FreeCAD.Units.Quantity(self.velocityInput.text()).Value) / 1000.0 # m/s
        Cd = float(FreeCAD.Units.Quantity(self.dragInput.text()).Value)

        rho = 1.22 # air density, average at sea level in kg/m^3 at 15C
        g = 9.807 # gravity in m/s^2, standard model at sea level on 45 latitude
        A = float(2*M*g)/(rho*V**2*Cd) # Calculate nominal surface area (So)
        shape = self.dragCombo.currentText()
        if shape == DRAG_HEX:
            D = math.sqrt(2.0 * A / math.sqrt(3.0))
        elif shape == DRAG_SQUARE:
            D = math.sqrt(A)
        else: # Assume round
            D = math.sqrt((4*A)/(math.pi))

        self.diameterInput.setText(FreeCAD.Units.Quantity(str(D) + "m").UserString)

    def onWeight(self, value):
        try:
            self.weightInput.setText(value)
            self._calcDiameter()
        except ValueError:
            pass

    def onVelocity(self, value):
        try:
            self.velocityInput.setText(value)
            self.velocityCombo.setCurrentText(VELOCITY_CUSTOM)
            self._calcDiameter()
        except ValueError:
            pass

    def onVelocityCombo(self, value):
        if value == VELOCITY_DROGUE:
            self.velocityInput.setText("19.8 m/s")
        elif value == VELOCITY_MAIN:
            self.velocityInput.setText("6.1 m/s")
        self._calcDiameter()


    def onDrag(self, value):
        try:
            self.dragInput.setText(value)
            self.dragCombo.setCurrentText(DRAG_CUSTOM)
            self._calcDiameter()
        except ValueError:
            pass

    def onDragCombo(self, value):
        if value == DRAG_DOME:
            self.dragInput.setText("1.5")
        elif value in [DRAG_ROUND, DRAG_HEX, DRAG_SQUARE]:
            self.dragInput.setText("0.75")
        self._calcDiameter()

    def onDiameter(self, value):
        # try:
        #     self.diameterInput.setText(value)
        #     self._setPressureFromForce()
        #     self._calcDiameter()
        # except ValueError:
        pass

    def onOk(self):
        self.close()
