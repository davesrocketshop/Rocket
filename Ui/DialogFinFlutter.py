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

from Analyzers.FinFlutter import FinFlutter

class DialogFinFlutter(QDialog):
    def __init__(self, fin):
        super().__init__()

        self._fin = fin
        self._flutter = FinFlutter(fin)

        self.initUI()
        self.onFlutter(None)

    def initUI(self):

        ui = FreeCADGui.UiLoader()

        # create our window
        # define window		xLoc,yLoc,xDim,yDim
        self.setGeometry(	250, 250, 640, 480)
        self.setWindowTitle(translate('Rocket', "Fin Flutter Analysis"))
        self.resize(QtCore.QSize(100,100).expandedTo(self.minimumSizeHint())) # sets size of the widget
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.modulusLabel = QtGui.QLabel(translate('Rocket', "Sheer Modulus"), self)

        self.modulusInput = ui.createWidget("Gui::InputField")
        self.modulusInput.unit = 'Unit::ShearModulus'
        self.modulusInput.setMinimumWidth(100)
        self.modulusInput.setText("2.620008e+9Pa")
        self.modulusInput.textEdited.connect(self.onFlutter)

        self.altitudeLabel = QtGui.QLabel(translate('Rocket', "Altitude"), self)

        self.altitudeInput = ui.createWidget("Gui::InputField")
        self.altitudeInput.unit = 'Unit::Length'
        self.altitudeInput.setText("914.4m")
        self.altitudeInput.setMinimumWidth(100)
        self.altitudeInput.textEdited.connect(self.onFlutter)

        self.flutterLabel = QtGui.QLabel(translate('Rocket', "Flutter Speed"), self)

        self.flutterInput = ui.createWidget("Gui::InputField")
        self.flutterInput.unit = 'Unit::Velocity'
        self.flutterInput.setText("0")
        self.flutterInput.setMinimumWidth(100)
        self.flutterInput.setReadOnly(True)

        self.divergenceLabel = QtGui.QLabel(translate('Rocket', "Divergence Speed"), self)

        self.divergenceInput = ui.createWidget("Gui::InputField")
        self.divergenceInput.unit = "Unit::Velocity"
        self.divergenceInput.setText("0")
        self.divergenceInput.setMinimumWidth(100)
        self.divergenceInput.setReadOnly(True)

        # OK button
        okButton = QtGui.QPushButton('OK', self)
        okButton.setDefault(False)
        okButton.setAutoDefault(False)
        okButton.clicked.connect(self.onOk)

        layout = QVBoxLayout()
        line = QGridLayout()

        row = 0
        line.addWidget(self.modulusLabel, row, 0)
        line.addWidget(self.modulusInput, row, 1)
        row += 1

        line.addWidget(self.altitudeLabel, row, 0)
        line.addWidget(self.altitudeInput, row, 1)
        row += 1

        line.addWidget(self.flutterLabel, row, 0)
        line.addWidget(self.flutterInput, row, 1)
        row += 1

        line.addWidget(self.divergenceLabel, row, 0)
        line.addWidget(self.divergenceInput, row, 1)
        layout.addLayout(line)

        # layout.addStretch()

        line = QHBoxLayout()
        line.addStretch()
        line.addWidget(okButton)
        layout.addLayout(line)

        self.setLayout(layout)

        # now make the window visible
        self.show()

    def onFlutter(self, value):
        # Use the quantity object for units conversion
        try:
            modulus = float(FreeCAD.Units.Quantity(str(self.modulusInput.text())))
            # attr = dir(self.modulusInput)
            # for a in attr:
            #     print(a)
            # modulus = float(self.modulusInput.text())
            altitude = float(FreeCAD.Units.Quantity(str(self.altitudeInput.text())))
            flutter = self._flutter.flutter(altitude, modulus)

            Vf = FreeCAD.Units.Quantity(str(flutter[1]) + " m/s")
            # self.flutterInput.quantity = Vf
            self.flutterInput.setText(Vf.UserString)
            # self.flutterInput.setText(Vf.quantityString)
            # self.flutterInput.setText(str(flutter[1]) + "m/s")

            Vd = FreeCAD.Units.Quantity(str(flutter[3]) + " m/s")
            print(self.divergenceInput.unit)
            # # self.divergenceInput.quantity = Vd
            print(Vd.getUserPreferred())
            # self.divergenceInput.setText(Vd.UserString)
            # # self.divergenceInput.setText(Vd.getValueAs(self.divergenceInput.unit).UserString + ' ' + self.flutterInput.unit)
            # print(Vd.getValueAs(FreeCAD.Units.Quantity(FreeCAD.Units.Unit(1,0,-1))))
            self.divergenceInput.setText(str(Vd.getValueAs(FreeCAD.Units.Quantity('m/s'))))
        except ValueError:
            pass

    def onOk(self):
        self.close()
