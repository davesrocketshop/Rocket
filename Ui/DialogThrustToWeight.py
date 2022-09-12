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
"""Class for Thrust To Weight calculator"""

__title__ = "FreeCAD Thrust To Weight Calculator"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import FreeCADGui

from DraftTools import translate

from PySide import QtGui, QtCore
from PySide2.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGridLayout

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

        self.thrustLabel = QtGui.QLabel(translate('Rocket', "Minimum Thrust"), self)

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
