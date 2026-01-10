# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for Thrust To Weight calculator"""

__title__ = "FreeCAD Thrust To Weight Calculator"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

translate = FreeCAD.Qt.translate

from PySide import QtGui, QtCore
from PySide.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGridLayout

class DialogThrustToWeight(QDialog):
    def __init__(self):
        super().__init__()


        self.initUI()

    def initUI(self):

        ui = FreeCADGui.UiLoader()

        # create our window
        # define window		xLoc,yLoc,xDim,yDim
        self.setGeometry(	250, 250, 640, 480)
        self.setWindowTitle(translate('Rocket', "Minimum Thrust to Weight Calculator"))
        self.resize(QtCore.QSize(100,100).expandedTo(self.minimumSizeHint())) # sets size of the widget
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.weightLabel = QtGui.QLabel(translate('Rocket', "Weight"), self)

        self.weightInput = ui.createWidget("Gui::InputField")
        self.weightInput.unit = 'kg'
        self.weightInput.setMinimumWidth(100)
        self.weightInput.setText("1.0")
        self.weightInput.textEdited.connect(self.onWeight)

        self.thrustLabel = QtGui.QLabel(translate('Rocket', "Minimum thrust"), self)

        self.thrustInput = ui.createWidget("Gui::InputField")
        self.thrustInput.unit = 'N'
        self.thrustInput.setText("49.0")
        self.thrustInput.setMinimumWidth(100)
        self.thrustInput.setReadOnly(True)

        # OK button
        okButton = QtGui.QPushButton('OK', self)
        okButton.setDefault(False)
        okButton.setAutoDefault(False)
        okButton.clicked.connect(self.onOk)

        layout = QVBoxLayout()
        line = QGridLayout()

        line.addWidget(self.weightLabel, 0, 0, 1, 2)
        line.addWidget(self.weightInput, 0, 1)

        line.addWidget(self.thrustLabel, 1, 0)
        line.addWidget(self.thrustInput, 1, 1)
        layout.addLayout(line)

        # layout.addStretch()

        line = QHBoxLayout()
        line.addStretch()
        line.addWidget(okButton)
        layout.addLayout(line)

        self.setLayout(layout)

        # now make the window visible
        self.show()

    def onWeight(self, value):
        # Use the quantity object for units conversion
        try:
            weight = FreeCAD.Units.Quantity(str(value))
            thrust = FreeCAD.Units.Quantity(str(weight.Value * (9.807 * 5)) + "N")
            self.thrustInput.setText(thrust.UserString)
        except ValueError:
            pass

    def onOk(self):
        self.close()
