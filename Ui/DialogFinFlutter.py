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
import os

from DraftTools import translate
import importFCMat

from PySide import QtGui, QtCore
from PySide2.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QGraphicsView

from Analyzers.FinFlutter import FinFlutter

class DialogFinFlutter(QDialog):
    def __init__(self, fin):
        super().__init__()

        self._fin = fin
        self._flutter = FinFlutter(fin)
        self._materials = []
        self._cards = None
        self._material = None

        # self._form = FreeCADGui.PySideUic.loadUi(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/ui/FlutterAnalysis.ui")
        self.initUI()
        self.onFlutter(None)

    def _shearUnits(self):
        return "GPa"

    def _heightUnits(self):
        return "m"

    def _velocityUnits(self):
        return "m/s"

    def _formatted(self, value, units):
        qty = FreeCAD.Units.Quantity(value)
        return str(qty.getValueAs(FreeCAD.Units.Quantity(units))) #+ " " + units

    def initUI(self):

        ui = FreeCADGui.UiLoader()

        # create our window
        # define window		xLoc,yLoc,xDim,yDim
        self.setGeometry(	250, 250, 640, 480)
        self.setWindowTitle(translate('Rocket', "Fin Flutter Analysis"))
        self.resize(QtCore.QSize(100,100).expandedTo(self.minimumSizeHint())) # sets size of the widget
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.materialGroup = QtGui.QGroupBox(translate('Rocket', "Material"), self)

        self.materialPresetLabel = QtGui.QLabel(translate('Rocket', "Preset"), self)

        self.materialPresetCombo = QtGui.QComboBox(self)
        self.fillExistingCombo()
        # self.materialPresetCombo.textEdited.connect(self.onFlutter)
        self.materialPresetCombo.currentTextChanged.connect(self.onMaterialChanged)

        self.shearLabel = QtGui.QLabel(translate('Rocket', "Sheer Modulus"), self)

        self.shearInput = ui.createWidget("Gui::InputField")
        self.shearInput.unit = self._shearUnits() #'Unit::ShearModulus'
        self.shearInput.setMinimumWidth(100)
        self.shearInput.setText(self._formatted("2.620008e+9Pa", self._shearUnits()))
        self.shearInput.textEdited.connect(self.onFlutter)

        self.calculatedCheckbox = QtGui.QCheckBox(translate('Rocket', "Calculated"), self)
        self.calculatedCheckbox.setCheckState(QtCore.Qt.Unchecked)

        self.youngsLabel = QtGui.QLabel(translate('Rocket', "Youngs Modulus"), self)

        self.youngsInput = ui.createWidget("Gui::InputField")
        self.youngsInput.unit = self._shearUnits() #'Unit::ShearModulus'
        self.youngsInput.setMinimumWidth(100)
        self.youngsInput.setText(self._formatted("2.620008e+9Pa", self._shearUnits()))
        self.youngsInput.textEdited.connect(self.onFlutter)

        self.poissonLabel = QtGui.QLabel(translate('Rocket', "Poisson Ratio"), self)

        self.poissonInput = ui.createWidget("Gui::InputField")
        # self.poissonInput.unit = self._shearUnits() #'Unit::ShearModulus'
        self.poissonInput.setMinimumWidth(100)
        self.poissonInput.setText("0.0")
        self.poissonInput.textEdited.connect(self.onFlutter)

        self.flutterGroup = QtGui.QGroupBox(translate('Rocket', "Fin Flutter"), self)

        self.maxAltitudeLabel = QtGui.QLabel(translate('Rocket', "Maximum Altitude"), self)

        self.maxAltitudeCombo = QtGui.QComboBox(self)

        self.altitudeLabel = QtGui.QLabel(translate('Rocket', "Target Altitude"), self)

        self.altitudeInput = ui.createWidget("Gui::InputField")
        self.altitudeInput.unit = 'Unit::Length'
        self.altitudeInput.setText("914.4m")
        self.altitudeInput.setMinimumWidth(100)
        self.altitudeInput.textEdited.connect(self.onFlutter)

        self.altitudeSlider = QtGui.QSlider(QtCore.Qt.Horizontal, self)

        self.chart = QGraphicsView(self)

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

        self.flutterMachLabel = QtGui.QLabel(translate('Rocket', "Mach"), self)

        self.flutterMachInput = ui.createWidget("Gui::InputField")
        # self.flutterMachInput.unit = 'Unit::Velocity'
        self.flutterMachInput.setText("0")
        self.flutterMachInput.setMinimumWidth(100)
        self.flutterMachInput.setReadOnly(True)

        self.divergenceMachLabel = QtGui.QLabel(translate('Rocket', "Mach"), self)

        self.divergenceMachInput = ui.createWidget("Gui::InputField")
        # self.divergenceMachInput.unit = 'Unit::Velocity'
        self.divergenceMachInput.setText("0")
        self.divergenceMachInput.setMinimumWidth(100)
        self.divergenceMachInput.setReadOnly(True)

        # OK button
        okButton = QtGui.QPushButton('OK', self)
        okButton.setDefault(False)
        okButton.setAutoDefault(False)
        okButton.clicked.connect(self.onOk)

        # Material group
        row = 0
        grid = QGridLayout()

        grid.addWidget(self.materialPresetLabel, row, 0)
        grid.addWidget(self.materialPresetCombo, row, 1)
        row += 1

        grid.addWidget(self.shearLabel, row, 0)
        grid.addWidget(self.shearInput, row, 1)
        grid.addWidget(self.calculatedCheckbox, row, 2)
        row += 1

        grid.addWidget(self.youngsLabel, row, 0)
        grid.addWidget(self.youngsInput, row, 1)
        row += 1

        grid.addWidget(self.poissonLabel, row, 0)
        grid.addWidget(self.poissonInput, row, 1)
        row += 1

        self.materialGroup.setLayout(grid)

        # Fin Flutter group
        vbox = QVBoxLayout()

        row = 0
        grid = QGridLayout()

        grid.addWidget(self.maxAltitudeLabel, row, 0)
        grid.addWidget(self.maxAltitudeCombo, row, 1)
        row += 1

        grid.addWidget(self.altitudeLabel, row, 0)
        grid.addWidget(self.altitudeInput, row, 1)
        row += 1

        vbox.addLayout(grid)

        sliderLine = QHBoxLayout()
        sliderLine.addWidget(self.altitudeSlider)

        vbox.addLayout(sliderLine)

        graph = QHBoxLayout()
        graph.addWidget(self.chart)

        vbox.addLayout(graph)

        # layout = QVBoxLayout()
        line = QGridLayout()

        row = 0

        line.addWidget(self.flutterLabel, row, 0)
        line.addWidget(self.flutterInput, row, 1)
        line.addWidget(self.flutterMachLabel, row, 2)
        line.addWidget(self.flutterMachInput, row, 3)
        row += 1

        line.addWidget(self.divergenceLabel, row, 0)
        line.addWidget(self.divergenceInput, row, 1)
        line.addWidget(self.divergenceMachLabel, row, 2)
        line.addWidget(self.divergenceMachInput, row, 3)
        vbox.addLayout(line)
        self.flutterGroup.setLayout(vbox)

        line = QHBoxLayout()
        line.addStretch()
        line.addWidget(okButton)

        layout = QVBoxLayout()
        layout.addWidget(self.materialGroup)
        layout.addWidget(self.flutterGroup)
        layout.addLayout(line)
        self.setLayout(layout)

        # now make the window visible
        self.show()
    
    def fillExistingCombo(self):
        "fills the combo with the existing FCMat cards"
        # look for cards in both resources dir and a Materials sub-folder in the user folder.
        # User cards with same name will override system cards
        paths = [FreeCAD.getResourceDir() + os.sep + "Mod" + os.sep + "Material" + os.sep + "StandardMaterial"]
        ap = FreeCAD.ConfigGet("UserAppData") + os.sep + "Materials"
        if os.path.exists(ap):
            paths.append(ap)

        self._cards = {}
        for p in paths:
            for f in os.listdir(p):
                b,e = os.path.splitext(f)
                if e.upper() == ".FCMAT":
                    self._cards[b] = p + os.sep + f

        self.materialPresetCombo.addItem('')
        if self._cards:
            for k in sorted(self._cards.keys()):
                self.materialPresetCombo.addItem(k)

    def setShearSpecified(self):
        self.shearInput.setEnabled(True)
        self.calculatedCheckbox.setChecked(False)

        self.youngsInput.setEnabled(False)
        self.poissonInput.setEnabled(False)

    def setShearCalculated(self):
        self.shearInput.setEnabled(False)
        self.calculatedCheckbox.setChecked(True)

        self.youngsInput.setEnabled(True)
        self.poissonInput.setEnabled(True)

    def onMaterialChanged(self, card):
        "sets self._material from a card"
        # print("onMaterialChanged()")
        if card in self._cards:
            # print(card)
            # print(self._cards[card])
            self._material = importFCMat.read(self._cards[card])
            if "ShearModulus" in self._material:
                self.shearInput.setText(self._material["ShearModulus"])
            else:
                self.shearInput.setText("0 kPa")
            if "YoungsModulus" in self._material:
                self.youngsInput.setText(self._material["YoungsModulus"])
            else:
                self.youngsInput.setText("0 kPa")
            if "PoissonRatio" in self._material:
                self.poissonInput.setText(self._material["PoissonRatio"])
            else:
                self.poissonInput.setText("0")

            if "ShearModulus" in self._material:
                self.setShearSpecified()
            elif "YoungsModulus" in self._material and "PoissonRatio" in self._material:
                young = float(FreeCAD.Units.Quantity(self._material["YoungsModulus"])) * 1000.0
                poisson = float(FreeCAD.Units.Quantity(self._material["PoissonRatio"]))
                shear = self._flutter.shearModulus(young, poisson)

                self.shearInput.setText(FreeCAD.Units.Quantity(str(shear) + " Pa").UserString)
                self.setShearCalculated()
            else:
                self.setShearSpecified()
            print(self._material)

            self.onFlutter(None)

    def _graphFlutter(self):
        pass

    def onFlutter(self, value):
        self._graphFlutter()
        try:
            modulus = float(FreeCAD.Units.Quantity(str(self.shearInput.text())))
            altitude = float(FreeCAD.Units.Quantity(str(self.altitudeInput.text())))
            flutter = self._flutter.flutter(altitude, modulus)
            divergence = self._flutter.divergence(altitude, modulus)

            Vf = FreeCAD.Units.Quantity(str(flutter[1]) + " m/s")
            # self.flutterInput.quantity = Vf
            self.flutterInput.setText(Vf.UserString)
            # self.flutterInput.setText(Vf.quantityString)
            # self.flutterInput.setText(str(flutter[1]) + "m/s")
            self.flutterMachInput.setText("{0:.2f}".format(flutter[0]))

            Vd = FreeCAD.Units.Quantity(str(divergence[1]) + " m/s")
            print(self.divergenceInput.unit)
            # # self.divergenceInput.quantity = Vd
            print(Vd.getUserPreferred())
            self.divergenceInput.setText(Vd.UserString)
            # # self.divergenceInput.setText(Vd.getValueAs(self.divergenceInput.unit).UserString + ' ' + self.flutterInput.unit)
            # print(Vd.getValueAs(FreeCAD.Units.Quantity(FreeCAD.Units.Unit(1,0,-1))))
            # self.divergenceInput.setText(str(Vd.getValueAs(FreeCAD.Units.Quantity('m/s'))))
            self.divergenceMachInput.setText("{0:.2f}".format(divergence[0]))
        except ValueError:
            pass

    def onOk(self):
        self.close()
