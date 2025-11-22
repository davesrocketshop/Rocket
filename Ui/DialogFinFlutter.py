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
"""Class for Fin Flutter calculator"""

__title__ = "FreeCAD Fin Flutter Calculator"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui
import Materials
import MatGui
import math
import numpy as np
import os

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure

translate = FreeCAD.Qt.translate

from PySide import QtGui, QtCore
from PySide.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QSizePolicy

from Analyzers.FinFlutter import FinFlutter

from Ui.UIPaths import getUIPath
from Ui.UiDialog import UiDialog

class DialogFinFlutter(UiDialog):
    def __init__(self, fin):
        super().__init__("DialogFinFlutter", "DialogFinFlutter.ui")

        self._fin = fin
        self._flutter = FinFlutter(fin)
        self._materials = []
        self._cards = None
        self._material = None

        self._materialManager = Materials.MaterialManager()

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
        super().initUI()

        ui = FreeCADGui.UiLoader()

        # create our window
        self._ui.setWindowTitle(translate('Rocket', "Fin Flutter Analysis"))
        self._ui.resize(QtCore.QSize(640,700).expandedTo(self.minimumSizeHint())) # sets size of the widget
        self._ui.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self._ui.materialGroup.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)

        self.materialTreeWidget = ui.createWidget("MatGui::MaterialTreeWidget")
        self.materialTreePy = MatGui.MaterialTreeWidget(self.materialTreeWidget)
        self.materialTreePy.expanded = self._param.GetBool("MaterialTreeExpanded", False)

        # Create the filters
        self.filter = Materials.MaterialFilter()
        self.filter.Name = "Isotropic Linear Elastic"
        self.filter.RequiredModels = [Materials.UUIDs().IsotropicLinearElastic]
        self.allFilter = Materials.MaterialFilter()
        self.allFilter.Name = "All"
        self.materialTreePy.setFilter([self.filter, self.allFilter])

        self._ui.materialGridLayout.replaceWidget(self._ui.materialTreeWidget, self.materialTreeWidget)

        self._ui.shearInput.unit = FreeCAD.Units.ShearModulus #self._shearUnits()
        self._ui.shearInput.setText(FreeCAD.Units.Quantity("2.620008e+9Pa").UserString)

        self._ui.calculatedCheckbox.setCheckState(QtCore.Qt.Unchecked)

        self._ui.youngsInput.unit = FreeCAD.Units.ShearModulus #'Unit::ShearModulus'
        self._ui.youngsInput.setText(FreeCAD.Units.Quantity("2.620008e+9Pa").UserString)
        self._ui.youngsInput.setEnabled(False)

        self._ui.poissonInput.setText("0.0")
        self._ui.poissonInput.setEnabled(False)

        self.fillAltitudeCombo()

        self._ui.altitudeInput.unit = FreeCAD.Units.Length
        self._ui.altitudeInput.setText("914.4m")

        # Creating graph
        plt.rcParams['figure.constrained_layout.use'] = True
        plt.rcParams["figure.facecolor"] = 'white'
        plt.rcParams["figure.edgecolor"] = 'white'
        plt.rcParams["axes.facecolor"] = 'white'
        self.static_canvas = FigureCanvas(Figure(figsize=(5,3)))

        self._static_ax = self.static_canvas.figure.subplots()
        t = np.linspace(0, 10, 501)
        self._flutterLine, = self._static_ax.plot(t, t, label=translate('Rocket', "Flutter"))
        self._divergenceLine, = self._static_ax.plot(t, t, label=translate('Rocket', "Divergence"))
        self._cursorLine, = self._static_ax.plot([0,0], [0,0])
        self._static_ax.set_xlabel("Altitude (km)")
        self._static_ax.set_ylabel("Velocity (m/s)")
        self._static_ax.grid(visible=True)
        # self._static_ax.set_title("Flutter")
        self._static_ax.legend()

        self._ui.flutterGroupLayout.replaceWidget(self._ui.widgetGraph, self.static_canvas)

        # flutter and divergence min/max
        self._yMin = 0
        self._yMax = 0

        self._ui.flutterInput.unit = FreeCAD.Units.Velocity
        self._ui.flutterInput.setText("0")
        self._ui.flutterInput.setReadOnly(True)

        self._ui.divergenceInput.unit = FreeCAD.Units.Velocity #"Unit::Velocity"
        self._ui.divergenceInput.setText("0")
        self._ui.divergenceInput.setReadOnly(True)

        self._ui.flutterMachInput.setText("0")
        self._ui.flutterMachInput.setReadOnly(True)

        self._ui.divergenceMachInput.setText("0")
        self._ui.divergenceMachInput.setReadOnly(True)

        self.materialTreeWidget.onMaterial.connect(self.onMaterial)
        self.materialTreeWidget.onExpanded.connect(self.onExpanded)
        self._ui.calculatedCheckbox.clicked.connect(self.onCalculated)
        self._ui.shearInput.textEdited.connect(self.onShear)
        self._ui.youngsInput.textEdited.connect(self.onYoungs)
        self._ui.poissonInput.textEdited.connect(self.onPoisson)
        self._ui.altitudeInput.textEdited.connect(self.onAltitude)
        self._ui.maxAltitudeCombo.currentTextChanged.connect(self.onMaxAltitude)
        self._ui.altitudeSlider.valueChanged.connect(self.onSlider)

        self._setSlider()

        self.update()

        # now make the window visible
        self._ui.show()

    def transferFrom(self):
        "Transfer from the object to the dialog"
        self.materialTreePy.UUID = self._fin.ShapeMaterial.UUID

    def _setSeries(self):

        modulus = float(FreeCAD.Units.Quantity(str(self._ui.shearInput.text())))
        maxHeight = int(FreeCAD.Units.Quantity(self._ui.maxAltitudeCombo.currentText()).getValueAs(FreeCAD.Units.Quantity(self._heightUnits())) / 1000)

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

    def fillAltitudeCombo(self):
        self._ui.maxAltitudeCombo.addItem("{0:d}".format(1000) + ' ' + self._heightUnits())
        self._ui.maxAltitudeCombo.addItem("{0:d}".format(5000) + ' ' + self._heightUnits())
        for i in range(10, 110, 10):
            self._ui.maxAltitudeCombo.addItem("{0:d}".format(i * 1000) + ' ' + self._heightUnits())
        self._ui.maxAltitudeCombo.setCurrentText("{0:d}".format(10000) + ' ' + self._heightUnits())

    def setShearSpecified(self):
        self._ui.shearInput.setEnabled(True)
        self._ui.calculatedCheckbox.setChecked(False)

        self._ui.youngsInput.setEnabled(False)
        self._ui.poissonInput.setEnabled(False)

    def setShearCalculated(self):
        self._ui.shearInput.setEnabled(False)
        self._ui.calculatedCheckbox.setChecked(True)

        self._ui.youngsInput.setEnabled(True)
        self._ui.poissonInput.setEnabled(True)

    def calculateShear(self):
        young = float(FreeCAD.Units.Quantity(self._ui.youngsInput.text()).getValueAs(FreeCAD.Units.Pascal))
        poisson = float(FreeCAD.Units.Quantity(self._ui.poissonInput.text()))
        shear = self._flutter.shearModulus(young, poisson)

        self._ui.shearInput.setText(FreeCAD.Units.Quantity(str(shear) + " Pa").UserString)

    def interpolateProperties(self):
        """ Infer missing properties from those available """
        shearModulus = self._material.getPhysicalValue("ShearModulus")
        youngsModulus = self._material.getPhysicalValue("YoungsModulus")
        poissonRatio = self._material.getPhysicalValue("PoissonRatio")
        hasShear = not (shearModulus is None or math.isnan(shearModulus))
        hasYoungs = not (youngsModulus is None or math.isnan(youngsModulus))
        hasPoisson = not (poissonRatio is None or math.isnan(poissonRatio))
        if hasShear:
            self._ui.shearInput.setText(self._formatPressure(FreeCAD.Units.Quantity(shearModulus)))
        else:
            self._ui.shearInput.setText(self._formatPressure(FreeCAD.Units.Quantity("0 kPa")))
        if hasYoungs:
            self._ui.youngsInput.setText(self._formatPressure(FreeCAD.Units.Quantity(youngsModulus)))
        else:
            self._ui.youngsInput.setText(self._formatPressure(FreeCAD.Units.Quantity("0 kPa")))
        if hasPoisson:
            self._ui.poissonInput.setText("{0:.4f}".format(poissonRatio))
        else:
            self._ui.poissonInput.setText("0")

        if hasShear:
            self.setShearSpecified()
        elif hasYoungs and hasPoisson:
            self.setShearCalculated()
            self.calculateShear()
        else:
            self.setShearSpecified()

    def onMaterial(self, uuid):
        self._material = self._materialManager.getMaterial(uuid)
        self.interpolateProperties()

        self._setSeries()
        self.onFlutter(None)

    def onExpanded(self, expanded):
        self._ui.materialGroup.adjustSize()
        self._ui.window().adjustSize()

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
            max = float(FreeCAD.Units.Quantity(self._ui.maxAltitudeCombo.currentText()).getValueAs(FreeCAD.Units.Quantity(self._heightUnits())))
            current = float(FreeCAD.Units.Quantity(self._ui.altitudeInput.text()).getValueAs(FreeCAD.Units.Quantity(self._heightUnits())))

            self._ui.altitudeSlider.setMinimum(0)
            self._ui.altitudeSlider.setMaximum(max)
            self._ui.altitudeSlider.setValue(current)
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
        current = float(FreeCAD.Units.Quantity(self._ui.altitudeInput.text()).getValueAs(FreeCAD.Units.Quantity(self._heightUnits())))
        x = current / 1000.0

        xSeries = [x, x]
        ySeries = [self._yMin, self._yMax]
        self._cursorLine.set_data(xSeries, ySeries)

        self._redraw()

    def onSlider(self, value):
        self._ui.altitudeInput.setText(self._formatAltitude(FreeCAD.Units.Quantity(str(value) + self._heightUnits())))

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
            modulus = float(FreeCAD.Units.Quantity(str(self._ui.shearInput.text())))
            altitude = float(FreeCAD.Units.Quantity(str(self._ui.altitudeInput.text())))
            flutter = self._flutter.flutter(altitude, modulus)
            divergence = self._flutter.divergence(altitude, modulus)

            Vf = FreeCAD.Units.Quantity(str(flutter[1]) + " m/s")
            self._ui.flutterInput.setText(self._formatVelocity(Vf))
            self._ui.flutterMachInput.setText("{0:.2f}".format(flutter[0]))

            Vd = FreeCAD.Units.Quantity(str(divergence[1]) + " m/s")
            self._ui.divergenceInput.setText(self._formatVelocity(Vd))
            self._ui.divergenceMachInput.setText("{0:.2f}".format(divergence[0]))

        except ValueError:
            pass

    def update(self):
        'fills the widgets'
        self.transferFrom()

    def onFinished(self, result) -> None:
        print('onFinished')
        self._param.SetBool("MaterialTreeExpanded", self.materialTreePy.expanded)

        super().onFinished(result)
