# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for Vent Hole calculator"""

__title__ = "FreeCAD Vent Hole Calculator"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import math

import FreeCAD
import FreeCADGui

translate = FreeCAD.Qt.translate

from PySide import QtGui, QtCore
from PySide.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGridLayout

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

        self.diameterLabel = QtGui.QLabel(translate('Rocket', "Body tube diameter"), self)

        self.diameterInput = ui.createWidget("Gui::InputField")
        self.diameterInput.unit = FreeCAD.Units.Length
        self.diameterInput.setMinimumWidth(100)
        self.diameterInput.setText("54.0")
        self.diameterInput.textEdited.connect(self.onDiameter)

        self.lengthLabel = QtGui.QLabel(translate('Rocket', "Body tube length"), self)

        self.lengthInput = ui.createWidget("Gui::InputField")
        self.lengthInput.unit = FreeCAD.Units.Length
        self.lengthInput.setMinimumWidth(100)
        self.lengthInput.setText("1000.0")
        self.lengthInput.textEdited.connect(self.onLength)

        self.holeCountLabel = QtGui.QLabel(translate('Rocket', "Vent hole count"), self)

        self.holeCountSpinBox = QtGui.QSpinBox(self)
        self.holeCountSpinBox.setMinimumWidth(100)
        self.holeCountSpinBox.setMinimum(1)
        self.holeCountSpinBox.setMaximum(10000)
        self.holeCountSpinBox.setValue(3)
        self.holeCountSpinBox.valueChanged.connect(self.onHoleCount)

        self.sizeLabel = QtGui.QLabel(translate('Rocket', "Vent hole size"), self)

        self.sizeInput = ui.createWidget("Gui::InputField")
        self.sizeInput.unit = FreeCAD.Units.Length
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
