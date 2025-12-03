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

from Rocket.Constants import ATMOS_POF_615, ATMOS_USSA, ATMOS_COESA_GEOMETRIC, ATMOS_COESA_GEOPOTENTIAL

from Ui.UIPaths import getUIPath
from Ui.UiDialog import UiDialog

class DialogFinFlutter(UiDialog):
    def __init__(self, fin) -> None:
        super().__init__("DialogFinFlutter", "DialogFinFlutter.ui")

        self._fin = fin
        self._flutter = FinFlutter(fin)
        self._materials = []
        self._cards = None
        self._material = None

        self._materialManager = Materials.MaterialManager()
        doc = FreeCADGui.ActiveDocument.Document
        self._schemas = doc.getEnumerationsOfProperty("UnitSystem")

        self.initUI()
        self._setSeries()
        self.updateFlutter()

    def _isMetricUnitPref(self) -> bool:
        doc = FreeCADGui.ActiveDocument.Document
        param = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Units")
        ignore = param.GetBool("IgnoreProjectSchema", False);
        if ignore:
            schema = param.GetInt('UserSchema', 0)
        else:
            schema = self._schemas.index(doc.UnitSystem)
        if schema in [2,3,5,7]:
            return False

        return True

    def _shearUnits(self) -> str:
        if self._isMetricUnitPref():
            return "GPa"
        return "psi"

    def _heightUnits(self) -> str:
        if self._isMetricUnitPref():
            return "m"
        return "ft"

    def _velocityUnits(self) -> str:
        if self._isMetricUnitPref():
            return "m/s"
        return "ft/s"

    def _temperatureUnits(self) -> str:
        if self._isMetricUnitPref():
            return "C"
        return "F"

    # def _formatted(self, value, units) -> str:
    #     qty = FreeCAD.Units.Quantity(value)
    #     return str(qty.getValueAs(FreeCAD.Units.Quantity(units))) #+ " " + units

    def initUI(self) -> None:
        super().initUI()

        ui = FreeCADGui.UiLoader()

        # create our window
        self._ui.setWindowTitle(translate('Rocket', "Fin Flutter Analysis"))
        self._ui.resize(QtCore.QSize(640,700).expandedTo(self.minimumSizeHint())) # sets size of the widget
        # self._ui.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        # self._ui.materialGroup.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)

        self.materialTreeWidget = ui.createWidget("MatGui::MaterialTreeWidget")
        self.materialTreePy = MatGui.MaterialTreeWidget(self.materialTreeWidget)

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

        # Launch conditions
        self.fillLaunchSiteCombo()
        self._ui.launchSiteAltitudeInput.unit = FreeCAD.Units.Length
        self._ui.launchSiteAltitudeInput.setText("0 m")

        self.fillTemperatureUnitsCombo()
        # self._ui.launchTemperatureInput.unit = FreeCAD.Units.Temperature
        self._ui.launchTemperatureInput.setText("15.0")

        self.fillAtmosphericModelCombo()

        self.fillAltitudeCombo()

        self._ui.speedInput.unit = self._velocityUnits() #FreeCAD.Units.Velocity
        self._ui.speedInput.setText("0.0 m/s")
        self._ui.altitudeInput.unit = FreeCAD.Units.Length
        self._ui.altitudeInput.setText("914.4 m")

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
        if self._isMetricUnitPref():
            self._static_ax.set_xlabel(translate('Rocket', "Altitude (km AGL)"))
            self._static_ax.set_ylabel(translate('Rocket', "Velocity (m/s)"))
        else:
            self._static_ax.set_xlabel(translate('Rocket', "Altitude (x1000 ft AGL)"))
            self._static_ax.set_ylabel(translate('Rocket', "Velocity (ft/s)"))
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

        self._ui.launchSiteCombo.currentTextChanged.connect(self.onLaunchSite)
        self._ui.temperatureUnitsCombo.currentTextChanged.connect(self.onTemperatureUnits)
        self._ui.launchTemperatureInput.textEdited.connect(self.onLaunchTemperature)
        self._ui.atmosphericModelCombo.currentTextChanged.connect(self.onAtmosphericModel)

        self._ui.speedInput.textChanged.connect(self.onSpeed)
        self._ui.altitudeInput.textEdited.connect(self.onAltitude)
        self._ui.maxAltitudeCombo.currentTextChanged.connect(self.onMaxAltitude)
        self._ui.altitudeSlider.valueChanged.connect(self.onSlider)

        self.restoreParameters()
        self._setSlider()

        self.update()

        # now make the window visible
        self._ui.show()

    def transferFrom(self) -> None:
        "Transfer from the object to the dialog"
        self.materialTreePy.UUID = self._fin.ShapeMaterial.UUID

    def tempToKelvin(self, temperature : float, units : str) -> float:
        if units == 'F':
            return (temperature - 32) * 5 / 9 + 273.15
        elif units == 'C':
            return temperature + 273.15
        return temperature

    def _getModulus(self) -> float:
        return float(FreeCAD.Units.Quantity(str(self._ui.shearInput.text())))

    def _formatFloat(self, value : float, units : str, metric : str, imperial : str) -> str:
        quantity = FreeCAD.Units.Quantity(f"{value:.8g} {units}")
        return f"{float(quantity.getValueAs(FreeCAD.Units.Quantity(metric))):.4f} {metric}, " \
            f"{float(quantity.getValueAs(FreeCAD.Units.Quantity(imperial))):.4f} {imperial}"

    def _setSeries(self) -> None:

        modulus = self._getModulus()
        maxHeight = int(FreeCAD.Units.Quantity(self._ui.maxAltitudeCombo.currentText()).getValueAs(FreeCAD.Units.Quantity(self._heightUnits())) / 1000)
        launchHeight = float(FreeCAD.Units.Quantity(self._ui.launchSiteAltitudeInput.text())) / 1000.0 # in meters

        temperatureUnits = self._ui.temperatureUnitsCombo.currentText()
        if self._ui.defaultTemperatureCheckbox.isChecked():
            launchTemperature = (15 + 273.15)
        else:
            launchTemperature = self.tempToKelvin(float(self._ui.launchTemperatureInput.text()), temperatureUnits)
        atmosphericModel = self.getAtmosphericModel()

        x_axis = []
        flutterSeries = []
        divergenceSeries = []
        for i in range(0, maxHeight+1):
            altitude = FreeCAD.Units.Quantity(f"{float(i * 1000.0)} {self._heightUnits()}").Value / 1000.0 # to m
            flutter = self._flutter.flutterPOF615(atmosphericModel, altitude, modulus, launchHeight, launchTemperature)
            divergence = self._flutter.divergence(atmosphericModel, altitude, modulus, launchHeight, launchTemperature)
            # Getting the data
            x = float(i)
            x_axis.append(x)

            quantity = FreeCAD.Units.Quantity(f"{float(flutter[1])} m/s")
            flutterY = quantity.getValueAs(FreeCAD.Units.Quantity(self._velocityUnits())).Value
            print(f"Altitude {self._formatFloat(altitude, 'm', 'm', 'ft')} -> {flutterY}")
            print(f"Flutter {self._formatFloat(float(flutter[1]), 'm/s', 'm/s', 'ft/s')} -> {flutterY}")
            if x >= 0:
                if (flutterY >=0):
                    flutterSeries.append(flutterY)
                else:
                    flutterSeries.append(0)

            quantity = FreeCAD.Units.Quantity(f"{float(divergence[1])} m/s")
            divergenceY = quantity.getValueAs(FreeCAD.Units.Quantity(self._velocityUnits())).Value
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

    def _redraw(self) -> None:
        # recompute the ax.dataLim
        self._static_ax.relim()
        # update ax.viewLim using the new dataLim
        self._static_ax.autoscale()

        self.static_canvas.draw()

    def fillLaunchSiteCombo(self) -> None:
        filename = os.path.join(getUIPath(), 'Resources', 'data', 'launch-sites.txt')
        altitude = 0
        self._ui.launchSiteCombo.addItem('', altitude)
        with open(filename, 'r', encoding="utf-8") as file:
            for line in file:
                if not line.startswith('#'):
                    data = line.split(":")
                    if len(data) >= 4:
                        # print(data)
                        if data[3]:
                            altitude = int(data[3])
                        else:
                            altitude = 0
                        self._ui.launchSiteCombo.addItem(data[0], altitude)

    def fillTemperatureUnitsCombo(self) -> None:
        self._ui.temperatureUnitsCombo.addItem('C')
        self._ui.temperatureUnitsCombo.addItem('F')
        self._ui.temperatureUnitsCombo.addItem('K')
        if self._isMetricUnitPref():
            self._ui.temperatureUnitsCombo.setCurrentText('C')
        else:
            self._ui.temperatureUnitsCombo.setCurrentText('F')

    def fillAtmosphericModelCombo(self) -> None:
        self._ui.atmosphericModelCombo.addItem(translate("Rocket", "Peak of Flight 615"), ATMOS_POF_615)
        self._ui.atmosphericModelCombo.addItem(translate("Rocket", "US Standard Atmosphere (USSA) 1976"), ATMOS_USSA)
        self._ui.atmosphericModelCombo.addItem(
            translate("Rocket", "Committee on Extension to the Standard Atmosphere (COESA) 1976 - Geometric"),
            ATMOS_COESA_GEOMETRIC)
        self._ui.atmosphericModelCombo.addItem(
            translate("Rocket", "Committee on Extension to the Standard Atmosphere (COESA) 1976 - Geopotential"),
            ATMOS_COESA_GEOPOTENTIAL)

    def fillAltitudeCombo(self) -> None:
        self._ui.maxAltitudeCombo.addItem("{0:d}".format(1000) + ' ' + self._heightUnits())
        self._ui.maxAltitudeCombo.addItem("{0:d}".format(5000) + ' ' + self._heightUnits())
        for i in range(10, 110, 10):
            self._ui.maxAltitudeCombo.addItem("{0:d}".format(i * 1000) + ' ' + self._heightUnits())
        self._ui.maxAltitudeCombo.setCurrentText("{0:d}".format(10000) + ' ' + self._heightUnits())

    def getAtmosphericModel(self) -> int:
        return int(self._ui.atmosphericModelCombo.currentData())

    def setShearSpecified(self) -> None:
        self._ui.shearInput.setEnabled(True)
        self._ui.calculatedCheckbox.setChecked(False)

        self._ui.youngsInput.setEnabled(False)
        self._ui.poissonInput.setEnabled(False)

    def setShearCalculated(self) -> None:
        self._ui.shearInput.setEnabled(False)
        self._ui.calculatedCheckbox.setChecked(True)

        self._ui.youngsInput.setEnabled(True)
        self._ui.poissonInput.setEnabled(True)

    def calculateShear(self) -> None:
        young = float(FreeCAD.Units.Quantity(self._ui.youngsInput.text()).getValueAs(FreeCAD.Units.Pascal))
        poisson = float(FreeCAD.Units.Quantity(self._ui.poissonInput.text()))
        shear = self._flutter.shearModulus(young, poisson)

        self._ui.shearInput.setText(FreeCAD.Units.Quantity(str(shear) + " Pa").UserString)

    def interpolateProperties(self) -> None:
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

    def onMaterial(self, uuid : str) -> None:
        self._material = self._materialManager.getMaterial(uuid)
        self.interpolateProperties()

        self._setSeries()
        self.updateFlutter()

    def onExpanded(self, expanded : bool) -> None:
        # self._ui.materialGroup.adjustSize()
        self._ui.window().adjustSize()

    def onCalculated(self, value : bool) -> None:
        if value:
            self.setShearCalculated()
            self.calculateShear()
        else:
            self.setShearSpecified()

    def onShear(self, value : str) -> None:
        self._setSeries()
        self.updateFlutter()

    def onYoungs(self, value : str) -> None:
        self.calculateShear()
        self._setSeries()
        self.updateFlutter()

    def onPoisson(self, value : str) -> None:
        self.calculateShear()
        self._setSeries()
        self.updateFlutter()

    def _setSlider(self) -> None:
        try:
            max = float(FreeCAD.Units.Quantity(self._ui.maxAltitudeCombo.currentText()).getValueAs(FreeCAD.Units.Quantity(self._heightUnits())))
            current = float(FreeCAD.Units.Quantity(self._ui.altitudeInput.text()).getValueAs(FreeCAD.Units.Quantity(self._heightUnits())))

            self._ui.altitudeSlider.setMinimum(0)
            self._ui.altitudeSlider.setMaximum(max)
            self._ui.altitudeSlider.setValue(current)
        except ValueError:
            # This can happen when editing a field and not yet complete
            pass

    def onLaunchSite(self, value : str) -> None:
        altitude = self._ui.launchSiteCombo.currentData()
        self._ui.launchSiteAltitudeInput.setText(self._formatAltitude(FreeCAD.Units.Quantity(f"{altitude}")))

    def onTemperatureUnits(self, value : str) -> None:
        self._setSeries()
        self._setSlider()
        self.updateFlutter()

    def onLaunchTemperature(self, value : str) -> None:
        self._setSeries()
        self._setSlider()
        self.updateFlutter()

    def onAtmosphericModel(self, value : str) -> None:
        self._setSeries()
        self._setSlider()
        self.updateFlutter()

    def onLaunchSiteAltitude(self, value : str) -> None:
        self._setSeries()
        self._setSlider()
        self.updateFlutter()

    def onMaxAltitude(self, value : str) -> None:
        self._setSeries()
        self._setSlider()

    def onSpeed(self, value : str) -> None:
        print(f"Cursor position {self._ui.speedInput.cursorPosition()}")
        ...

    def onAltitude(self, value : str) -> None:
        self._setSeries()
        self._setSlider()
        self.updateFlutter()

    def showSlider(self) -> None:
        current = float(FreeCAD.Units.Quantity(self._ui.altitudeInput.text()).getValueAs(FreeCAD.Units.Quantity(self._heightUnits())))
        x = current / 1000.0

        xSeries = [x, x]
        ySeries = [self._yMin, self._yMax]
        self._cursorLine.set_data(xSeries, ySeries)

        self._redraw()

    def onSlider(self, value : str) -> None:
        self._ui.altitudeInput.setText(self._formatAltitude(FreeCAD.Units.Quantity(str(value) + self._heightUnits())))

        self.showSlider()
        self._redraw()
        self.updateFlutter()

    def _graphFlutter(self) -> None:
        pass

    def _formatQuantity(self, formatString : str, quantity : FreeCAD.Units.Quantity, units : str) -> str:
        return formatString.format(float(quantity.getValueAs(FreeCAD.Units.Quantity(units)))) + ' ' + units

    def _formatIntQuantity(self, formatString, quantity : FreeCAD.Units.Quantity, units : str) -> str:
        return formatString.format(int(quantity.getValueAs(FreeCAD.Units.Quantity(units)))) + ' ' + units

    def _formatVelocity(self, quantity : FreeCAD.Units.Quantity) -> str:
        return self._formatQuantity("{0:.2f}", quantity, self._velocityUnits())

    def _formatPressure(self, quantity : FreeCAD.Units.Quantity) -> str:
        return self._formatQuantity("{0:.4f}", quantity, self._shearUnits())

    def _formatAltitude(self, quantity : FreeCAD.Units.Quantity) -> str:
        return self._formatQuantity("{0:.2f}", quantity, self._heightUnits())

    def updateFlutter(self) -> None:
        self._graphFlutter()
        try:
            modulus = self._getModulus()
            speed = float(FreeCAD.Units.Quantity(self._ui.speedInput.text()).Value)

            # Heights in meters
            altitude = float(FreeCAD.Units.Quantity(self._ui.altitudeInput.text()).Value) / 1000.0
            launchHeight = float(FreeCAD.Units.Quantity(self._ui.launchSiteAltitudeInput.text())) / 1000.0

            temperatureUnits = self._ui.temperatureUnitsCombo.currentText()
            if self._ui.defaultTemperatureCheckbox.isChecked():
                launchTemperature = (15 + 273.15)
            else:
                launchTemperature = self.tempToKelvin(float(self._ui.launchTemperatureInput.text()), temperatureUnits)
            atmosphericModel = self.getAtmosphericModel()

            flutter = self._flutter.flutterPOF615(atmosphericModel, altitude, modulus, launchHeight, launchTemperature)
            divergence = self._flutter.divergence(atmosphericModel, altitude, modulus, launchHeight, launchTemperature)

            Vf = FreeCAD.Units.Quantity(str(flutter[1]) + " m/s")
            self._ui.flutterInput.setText(self._formatVelocity(Vf))
            self._ui.flutterMachInput.setText("{0:.2f}".format(flutter[0]))
            if speed > 0.0:
                margin = (Vf.Value - speed)  * 100.0 / speed
                self._ui.flutterMarginInput.setText("{0:.1f} %".format(margin))
            else:
                self._ui.flutterMarginInput.setText("")

            Vd = FreeCAD.Units.Quantity(str(divergence[1]) + " m/s")
            self._ui.divergenceInput.setText(self._formatVelocity(Vd))
            self._ui.divergenceMachInput.setText("{0:.2f}".format(divergence[0]))
            if speed > 0.0:
                margin = (Vd.Value - speed)  * 100.0 / speed
                self._ui.divergenceMarginInput.setText("{0:.1f} %".format(margin))
            else:
                self._ui.divergenceMarginInput.setText("")

        except ValueError:
            pass

    def update(self) -> None:
        'fills the widgets'
        self.transferFrom()

    def onFinished(self, result : int) -> None:
        self.saveParameters()

        super().onFinished(result)

    def saveParameters(self) -> None:
        # Material tab
        self._param.SetBool("MaterialTreeExpanded", self.materialTreePy.expanded)

        # Launch conditions tab
        self._param.SetString("LaunchSite", self._ui.launchSiteCombo.currentText())
        self._param.SetString("LaunchAltitude", self._ui.launchSiteAltitudeInput.text())
        self._param.SetString("LaunchTemperature", self._ui.launchTemperatureInput.text())
        self._param.SetInt("LaunchTemperatureUnits", self._ui.temperatureUnitsCombo.currentIndex())
        self._param.SetBool("UseSeaLevelTemperature", self._ui.defaultTemperatureCheckbox.isChecked())
        self._param.SetInt("AtmosphericModel", self._ui.atmosphericModelCombo.currentIndex())

        # Flutter tab
        self._param.SetString("MaximumAltitude", self._ui.maxAltitudeCombo.currentText())
        self._param.SetString("MaximumSpeed", self._ui.speedInput.text())
        self._param.SetString("AltitudeAtMaximumSpeed", self._ui.altitudeInput.text())

    def restoreParameters(self) -> None:
        # Material tab
        self.materialTreePy.expanded = self._param.GetBool("MaterialTreeExpanded", False)

        # Launch conditions tab
        self._ui.launchSiteCombo.setCurrentText(self._param.GetString("LaunchSite", ""))
        self._ui.launchSiteAltitudeInput.setText(self._param.GetString("LaunchAltitude", "0.0 m"))
        self._ui.launchTemperatureInput.setText(self._param.GetString("LaunchTemperature", "15"))
        self._ui.temperatureUnitsCombo.setCurrentIndex(self._param.GetInt("LaunchTemperatureUnits", 0))
        self._ui.defaultTemperatureCheckbox.setChecked(self._param.GetBool("UseSeaLevelTemperature", True))
        self._ui.atmosphericModelCombo.setCurrentIndex(self._param.GetInt("AtmosphericModel", 0))

        # Flutter tab
        self._ui.maxAltitudeCombo.setCurrentText(self._param.GetString("MaximumAltitude", "10000 m"))
        self._ui.speedInput.setText(self._param.GetString("MaximumSpeed", "0.0 m/s"))
        self._ui.altitudeInput.setText(self._param.GetString("AltitudeAtMaximumSpeed", "914.00 m"))
