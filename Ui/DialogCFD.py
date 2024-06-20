# ***************************************************************************
# *   Copyright (c) 2021-2024 David Carter <dcarter@davidcarter.ca>         *
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
import math
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure

from DraftTools import translate

from PySide import QtGui, QtCore
from PySide2.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGridLayout

from Analyzers.FinFlutter import FinFlutter

from Rocket.Material import Material

class DialogCFD(QDialog):
    def __init__(self, fin):
        super().__init__()

        self._fin = fin
        self._flutter = FinFlutter(fin)
        self._materials = []
        self._cards = None
        self._material = None

        self.initUI()
        self._setSeries()
        self.onFlutter(None)

    def _isMetricUnitPref(self):
            param = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Units")
            schema = param.GetInt('UserSchema')
            if schema in [2,3,5,7]:
                return False

            return True

    def _shearUnits(self):
        if self._isMetricUnitPref():
            return "GPa"
        return "psi"

    def _heightUnits(self):
        if self._isMetricUnitPref():
            return "m"
        return "ft"

    def _velocityUnits(self):
        if self._isMetricUnitPref():
            return "m/s"
        return "ft/s"

    def _formatted(self, value, units):
        qty = FreeCAD.Units.Quantity(value)
        return str(qty.getValueAs(FreeCAD.Units.Quantity(units))) #+ " " + units

    def initUI(self):

        ui = FreeCADGui.UiLoader()

        # create our window
        # define window		xLoc,yLoc,xDim,yDim
        self.setGeometry(250, 250, 640, 480)
        self.setWindowTitle(translate('Rocket', "Fin Flutter Analysis"))
        self.resize(QtCore.QSize(640,700).expandedTo(self.minimumSizeHint())) # sets size of the widget
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.materialGroup = QtGui.QGroupBox(translate('Rocket', "Material"), self)

        self.materialPresetLabel = QtGui.QLabel(translate('Rocket', "Preset"), self)

        self.materialPresetCombo = QtGui.QComboBox(self)
        self.fillExistingCombo()

        self.shearLabel = QtGui.QLabel(translate('Rocket', "Shear Modulus"), self)

        self.shearInput = ui.createWidget("Gui::InputField")
        self.shearInput.unit = self._shearUnits() #'Unit::ShearModulus'
        self.shearInput.setMinimumWidth(100)
        self.shearInput.setText(self._formatPressure(FreeCAD.Units.Quantity("2.620008e+9Pa")))

        self.calculatedCheckbox = QtGui.QCheckBox(translate('Rocket', "Calculated"), self)
        self.calculatedCheckbox.setCheckState(QtCore.Qt.Unchecked)

        self.youngsLabel = QtGui.QLabel(translate('Rocket', "Young's Modulus"), self)

        self.youngsInput = ui.createWidget("Gui::InputField")
        self.youngsInput.unit = self._shearUnits() #'Unit::ShearModulus'
        self.youngsInput.setMinimumWidth(100)
        self.youngsInput.setText(self._formatPressure(FreeCAD.Units.Quantity("2.620008e+9Pa")))
        self.youngsInput.setEnabled(False)

        self.poissonLabel = QtGui.QLabel(translate('Rocket', "Poisson Ratio"), self)

        self.poissonInput = ui.createWidget("Gui::InputField")
        self.poissonInput.setMinimumWidth(100)
        self.poissonInput.setText("0.0")
        self.poissonInput.setEnabled(False)

        self.flutterGroup = QtGui.QGroupBox(translate('Rocket', "Fin Flutter"), self)

        self.maxAltitudeLabel = QtGui.QLabel(translate('Rocket', "Maximum Altitude"), self)

        self.maxAltitudeCombo = QtGui.QComboBox(self)
        self.fillAltitudeCombo()

        self.altitudeLabel = QtGui.QLabel(translate('Rocket', "Altitude at Max Speed"), self)

        self.altitudeInput = ui.createWidget("Gui::InputField")
        self.altitudeInput.unit = 'Unit::Length'
        self.altitudeInput.setText("914.4m")
        self.altitudeInput.setMinimumWidth(100)

        self.altitudeSlider = QtGui.QSlider(QtCore.Qt.Horizontal, self)

        # Creating graph
        plt.rcParams['figure.constrained_layout.use'] = True
        plt.rcParams["figure.facecolor"] = 'white'
        plt.rcParams["figure.edgecolor"] = 'white'
        plt.rcParams["axes.facecolor"] = 'white'
        self.static_canvas = FigureCanvas(Figure(figsize=(5,3)))
 
        self._static_ax = self.static_canvas.figure.subplots()
        t = np.linspace(0, 10, 501)
        self._flutterLine, = self._static_ax.plot(t, t, label="flutter")
        self._divergenceLine, = self._static_ax.plot(t, t, label="divergence")
        self._cursorLine, = self._static_ax.plot([0,0], [0,0])
        self._static_ax.set_xlabel("Altitude (km)")
        self._static_ax.set_ylabel("Velocity (m/s)")
        self._static_ax.grid(visible=True)
        # self._static_ax.set_title("Flutter")
        self._static_ax.legend()

        # flutter and divergence min/max
        self._yMin = 0
        self._yMax = 0

        self.flutterLabel = QtGui.QLabel(translate('Rocket', "Flutter Speed"), self)

        self.flutterInput = ui.createWidget("Gui::InputField")
        self.flutterInput.unit = 'Unit::Velocity'
        self.flutterInput.setText("0")
        self.flutterInput.setMinimumWidth(100)
        self.flutterInput.setReadOnly(True)

        self.divergenceLabel = QtGui.QLabel(translate('Rocket', "Divergence Speed"), self)

        self.divergenceInput = ui.createWidget("Gui::InputField")
        self.divergenceInput.unit = self._velocityUnits() #"Unit::Velocity"
        self.divergenceInput.setText("0")
        self.divergenceInput.setMinimumWidth(100)
        self.divergenceInput.setReadOnly(True)

        self.flutterMachLabel = QtGui.QLabel(translate('Rocket', "Mach"), self)

        self.flutterMachInput = ui.createWidget("Gui::InputField")
        self.flutterMachInput.setText("0")
        self.flutterMachInput.setMinimumWidth(100)
        self.flutterMachInput.setReadOnly(True)

        self.divergenceMachLabel = QtGui.QLabel(translate('Rocket', "Mach"), self)

        self.divergenceMachInput = ui.createWidget("Gui::InputField")
        self.divergenceMachInput.setText("0")
        self.divergenceMachInput.setMinimumWidth(100)
        self.divergenceMachInput.setReadOnly(True)

        # OK button
        okButton = QtGui.QPushButton('OK', self)
        okButton.setDefault(False)
        okButton.setAutoDefault(False)

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

        # vbox.addWidget(NavigationToolbar(static_canvas, self))
        vbox.addWidget(self.static_canvas)

        sliderLine = QHBoxLayout()
        sliderLine.addWidget(self.altitudeSlider)

        vbox.addLayout(sliderLine)

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

        self.materialPresetCombo.currentTextChanged.connect(self.onMaterialChanged)
        self.calculatedCheckbox.clicked.connect(self.onCalculated)
        self.shearInput.textEdited.connect(self.onShear)
        self.youngsInput.textEdited.connect(self.onYoungs)
        self.poissonInput.textEdited.connect(self.onPoisson)
        self.altitudeInput.textEdited.connect(self.onAltitude)
        self.maxAltitudeCombo.currentTextChanged.connect(self.onMaxAltitude)
        self.altitudeSlider.valueChanged.connect(self.onSlider)
        okButton.clicked.connect(self.onOk)

        self._setSlider()
        
        self.update()

        # now make the window visible
        self.show()

    def transferFrom(self):
        "Transfer from the object to the dialog"
        self.materialPresetCombo.setCurrentText(self._fin.Material)

    def _setSeries(self):

        modulus = float(FreeCAD.Units.Quantity(str(self.shearInput.text())))
        maxHeight = int(FreeCAD.Units.Quantity(self.maxAltitudeCombo.currentText()).getValueAs(FreeCAD.Units.Quantity(self._heightUnits())) / 1000)

        x_axis = []
        flutterSeries = []
        divergenceSeries = []
        for i in range(0, maxHeight+1):
            altitude = i * 1000000.0 # to mm
            flutter = self._flutter.flutter(altitude, modulus)
            divergence = self._flutter.divergence(altitude, modulus)
            # Getting the data
            x = float(i)
            x_axis.append(x)

            flutterY = float(flutter[1])
            if x >= 0:
                if (flutterY >=0):
                    flutterSeries.append(flutterY)
                else:
                    flutterSeries.append(0)

            divergenceY = float(divergence[1])
            if x >= 0:
                if (divergenceY >=0):
                    divergenceSeries.append(divergenceY)
                else:
                    divergenceSeries.append(0)

            if (i == 0):
                self._yMin = min(flutterY, divergenceY)
            else:
                self._yMax = max(flutterY, divergenceY)

        self._flutterLine.set_data(x_axis, flutterSeries)
        self._divergenceLine.set_data(x_axis, divergenceSeries)

        self.showSlider() # calls _redraw()
        # self._redraw()

    def _redraw(self):
        # recompute the ax.dataLim
        self._static_ax.relim()
        # update ax.viewLim using the new dataLim
        self._static_ax.autoscale()
        
        self.static_canvas.draw()
    
    def fillExistingCombo(self):
        "fills the combo with the existing FCMat cards"
        self.materialPresetCombo.addItem('')
        self._cards = Material.materialDictionary()
        if self._cards:
            for k in sorted(self._cards.keys()):
                self.materialPresetCombo.addItem(k)

    def fillAltitudeCombo(self):
        for i in range(0, 110, 10):
            self.maxAltitudeCombo.addItem("{0:d}".format(i * 1000) + ' ' + self._heightUnits())
        self.maxAltitudeCombo.setCurrentText("{0:d}".format(10000) + ' ' + self._heightUnits())

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

    def calculateShear(self):
        young = float(FreeCAD.Units.Quantity(self.youngsInput.text()).getValueAs(FreeCAD.Units.Pascal))
        poisson = float(FreeCAD.Units.Quantity(self.poissonInput.text()))
        shear = self._flutter.shearModulus(young, poisson)

        self.shearInput.setText(FreeCAD.Units.Quantity(str(shear) + " Pa").UserString)

    def onMaterialChanged(self, card):
        "sets self._material from a card"
        if card in self._cards:
            self._material = Material.lookup(card)
            if "ShearModulus" in self._material:
                self.shearInput.setText(self._formatPressure(FreeCAD.Units.Quantity(self._material["ShearModulus"])))
            else:
                self.shearInput.setText(self._formatPressure(FreeCAD.Units.Quantity("0 kPa")))
            if "YoungsModulus" in self._material:
                self.youngsInput.setText(self._formatPressure(FreeCAD.Units.Quantity(self._material["YoungsModulus"])))
            else:
                self.youngsInput.setText(self._formatPressure(FreeCAD.Units.Quantity("0 kPa")))
            if "PoissonRatio" in self._material:
                self.poissonInput.setText(self._material["PoissonRatio"])
            else:
                self.poissonInput.setText("0")

            if "ShearModulus" in self._material:
                self.setShearSpecified()
            elif "YoungsModulus" in self._material and "PoissonRatio" in self._material:
                self.setShearCalculated()
                self.calculateShear()
            else:
                self.setShearSpecified()

            self._setSeries()
            self.onFlutter(None)
        
    def onCalculated(self, value):
        if value:
            self.setShearCalculated()
            self.calculateShear()
        else:
            self.setShearSpecified()

    def onShear(self, value):
        self._setSeries()
        self.onFlutter(None)

    def onYoungs(self, value):
        self.calculateShear()
        self._setSeries()
        self.onFlutter(None)

    def onPoisson(self, value):
        self.calculateShear()
        self._setSeries()
        self.onFlutter(None)

    def _setSlider(self):
        try:
            max = float(FreeCAD.Units.Quantity(self.maxAltitudeCombo.currentText()).getValueAs(FreeCAD.Units.Quantity(self._heightUnits())))
            current = float(FreeCAD.Units.Quantity(self.altitudeInput.text()).getValueAs(FreeCAD.Units.Quantity(self._heightUnits())))

            self.altitudeSlider.setMinimum(0)
            self.altitudeSlider.setMaximum(max)
            self.altitudeSlider.setValue(current)
        except ValueError:
            # This can happen when editing a field and not yet complete
            pass

    def onMaxAltitude(self, value):
        self._setSeries()
        self._setSlider()

    def onAltitude(self, value):
        self._setSeries()
        self._setSlider()
        self.onFlutter(None)

    def showSlider(self):
        current = float(FreeCAD.Units.Quantity(self.altitudeInput.text()).getValueAs(FreeCAD.Units.Quantity(self._heightUnits())))
        x = current / 1000.0

        xSeries = [x, x]
        ySeries = [self._yMin, self._yMax]
        self._cursorLine.set_data(xSeries, ySeries)

        self._redraw()

    def onSlider(self, value):
        self.altitudeInput.setText(self._formatAltitude(FreeCAD.Units.Quantity(str(value) + self._heightUnits())))

        self.showSlider()
        self._redraw()
        self.onFlutter(None)

    def _graphFlutter(self):
        pass

    def _formatQuantity(self, formatString, quantity, units):
        return formatString.format(float(quantity.getValueAs(FreeCAD.Units.Quantity(units)))) + ' ' + units

    def _formatIntQuantity(self, formatString, quantity, units):
        return formatString.format(int(quantity.getValueAs(FreeCAD.Units.Quantity(units)))) + ' ' + units

    def _formatVelocity(self, quantity):
        return self._formatQuantity("{0:.2f}", quantity, self._velocityUnits())

    def _formatPressure(self, quantity):
        return self._formatQuantity("{0:.4f}", quantity, self._shearUnits())

    def _formatAltitude(self, quantity):
        return self._formatIntQuantity("{0:d}", quantity, self._heightUnits())

    def onFlutter(self, value):
        self._graphFlutter()
        try:
            modulus = float(FreeCAD.Units.Quantity(str(self.shearInput.text())))
            altitude = float(FreeCAD.Units.Quantity(str(self.altitudeInput.text())))
            flutter = self._flutter.flutter(altitude, modulus)
            divergence = self._flutter.divergence(altitude, modulus)

            Vf = FreeCAD.Units.Quantity(str(flutter[1]) + " m/s")
            self.flutterInput.setText(self._formatVelocity(Vf))
            self.flutterMachInput.setText("{0:.2f}".format(flutter[0]))

            Vd = FreeCAD.Units.Quantity(str(divergence[1]) + " m/s")
            self.divergenceInput.setText(self._formatVelocity(Vd))
            self.divergenceMachInput.setText("{0:.2f}".format(divergence[0]))

        except ValueError:
            pass
        
    def update(self):
        'fills the widgets'
        self.transferFrom()

    def onOk(self):
        self.close()
