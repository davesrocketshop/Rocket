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
"""Class for Vent Hole calculator"""

__title__ = "FreeCAD Vent Hole Calculator"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import math

import FreeCAD
import FreeCADGui

from DraftTools import translate

from PySide import QtGui, QtCore
from PySide2.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGridLayout

class DialogVentHole(QDialog):
    def __init__(self):
        super().__init__()


        self.initUI()

    def initUI(self):

        ui = FreeCADGui.UiLoader()

        # create our window
        # define window		xLoc,yLoc,xDim,yDim
        self.setGeometry(	250, 250, 640, 480)
        self.setWindowTitle(translate('Rocket', "Vent Hole Size Calculator"))
        self.resize(QtCore.QSize(100,100).expandedTo(self.minimumSizeHint())) # sets size of the widget
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.diameterLabel = QtGui.QLabel(translate('Rocket', "Body Tube Diameter"), self)

        self.diameterInput = ui.createWidget("Gui::InputField")
        self.diameterInput.unit = 'mm'
        self.diameterInput.setMinimumWidth(100)
        self.diameterInput.setText("54.0")
        self.diameterInput.textEdited.connect(self.onDiameter)

        self.lengthLabel = QtGui.QLabel(translate('Rocket', "Body Tube Length"), self)

        self.lengthInput = ui.createWidget("Gui::InputField")
        self.lengthInput.unit = 'mm'
        self.lengthInput.setMinimumWidth(100)
        self.lengthInput.setText("1000.0")
        self.lengthInput.textEdited.connect(self.onLength)

        self.holeCountLabel = QtGui.QLabel(translate('Rocket', "Vent Hole Count"), self)

        self.holeCountSpinBox = QtGui.QSpinBox(self)
        self.holeCountSpinBox.setMinimumWidth(100)
        self.holeCountSpinBox.setMinimum(1)
        self.holeCountSpinBox.setMaximum(10000)
        self.holeCountSpinBox.setValue(3)
        self.holeCountSpinBox.valueChanged.connect(self.onHoleCount)

        self.sizeLabel = QtGui.QLabel(translate('Rocket', "Vent Hole Size"), self)

        self.sizeInput = ui.createWidget("Gui::InputField")
        self.sizeInput.unit = 'mm'
        self.sizeInput.setText("49.0")
        self.sizeInput.setMinimumWidth(100)
        self.sizeInput.setReadOnly(True)

        # OK button
        okButton = QtGui.QPushButton('OK', self)
        okButton.setDefault(False)
        okButton.setAutoDefault(False)
        okButton.clicked.connect(self.onOk)

        layout = QVBoxLayout()
        line = QGridLayout()
        row = 0

        line.addWidget(self.diameterLabel, row, 0, 1, 2)
        line.addWidget(self.diameterInput, row, 1)
        row += 1

        line.addWidget(self.lengthLabel, row, 0)
        line.addWidget(self.lengthInput, row, 1)
        layout.addLayout(line)
        row += 1

        line.addWidget(self.holeCountLabel, row, 0)
        line.addWidget(self.holeCountSpinBox, row, 1)
        layout.addLayout(line)
        row += 1

        line.addWidget(self.sizeLabel, row, 0)
        line.addWidget(self.sizeInput, row, 1)
        layout.addLayout(line)
        row += 1

        # layout.addStretch()

        line = QHBoxLayout()
        line.addStretch()
        line.addWidget(okButton)
        layout.addLayout(line)

        self.setLayout(layout)

        self._calc()

        # now make the window visible
        self.show()

    def _calc(self):
        # Use the quantity object for units conversion
        diameter = float(FreeCAD.Units.Quantity(self.diameterInput.text()).Value)
        length = float(FreeCAD.Units.Quantity(self.lengthInput.text()).Value)
        count = int(self.holeCountSpinBox.value())

        size = 0.004396 * diameter * math.sqrt(length / count)

        self.sizeInput.setText(FreeCAD.Units.Quantity(str(size) + "mm").UserString)

    def onDiameter(self, value):
        try:
            self._calc()
        except ValueError:
            pass

    def onLength(self, value):
        try:
            self._calc()
        except ValueError:
            pass

    def onHoleCount(self, value):
        try:
            self._calc()
        except ValueError:
            pass

    def onOk(self):
        self.close()
