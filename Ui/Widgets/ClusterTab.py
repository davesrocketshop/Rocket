# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

################################################################################
#                                                                              #
#   © 2026 David Carter <dcarter@davidcarter.ca>                               #
#                                                                              #
#   This addon is free software: you can redistribute it and/or modify         #
#   it under the terms of the GNU Lesser General Public License as             #
#   published by the Free Software Foundation, either version 2.1              #
#   of the License, or (at your option) any later version.                     #
#                                                                              #
#   This addon is distributed in the hope that it will be useful,              #
#   but WITHOUT ANY WARRANTY; without even the implied warranty                #
#   of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                    #
#   See the GNU Lesser General Public License for more details.                #
#                                                                              #
#   You should have received a copy of the GNU Lesser General Public           #
#   License along with this addon. If not, see https://www.gnu.org/licenses    #
#                                                                              #
################################################################################


"""Class for specifying cluster configuration"""

__title__ = "FreeCAD Cluster Tab"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"


import os
from typing import Any

import FreeCAD
import FreeCADGui
from FreeCAD import Units
from Ui.UIPaths import getUIPath
from Ui.Widgets.WaitCursor import WaitCursor
translate = FreeCAD.Qt.translate

from PySide import QtGui
from PySide.QtCore import QObject, Signal
from PySide.QtWidgets import QVBoxLayout, QTextEdit

class ClusterTab(QObject):
    cluster = Signal()   # emitted when cluster parameters have changed

    def __init__(self, obj : Any, parent=None):
        super().__init__(parent)

        try:
            self._obj = obj
            self._loading = False # Prevent updates when loading
            self._isAssembly = self._obj.Proxy.isRocketAssembly()
            self._form = FreeCADGui.PySideUic.loadUi(os.path.join(getUIPath(), 'Ui', "Widgets", "ClusterTab.ui"))
            self.setTabCluster()
        except Exception as e:
            print("Error occurred while initializing ClusterTab: {}".format(e))

    def widget(self) -> QtGui.QWidget:
        return self._form

    def setTabCluster(self):
        # self._form.separationSpinBox.unit = FreeCAD.Units.Length
        self._form.rotationSpinBox.unit = FreeCAD.Units.Angle
        self._form.cantAngleSpinBox.unit = FreeCAD.Units.Angle
        self._form.cantFocusSpinBox.unit = FreeCAD.Units.Length

        self._setConnections()
        self._setClusterState()

    def _setConnections(self) -> None:
        self._form.clusterGroup.toggled.connect(self.onClusterGroup)
        self._form.clusterRadialRadio.toggled.connect(self.onClusterRadial)
        self._form.clusterRadialCountSpinBox.valueChanged.connect(self.onClusterRadialCount)
        self._form.clusterXYRadio.toggled.connect(self.onClusterXY)
        self._form.clusterRowsSpinBox.valueChanged.connect(self.onClusterRows)
        self._form.clusterColumnsSpinBox.valueChanged.connect(self.onClusterColumns)
        self._form.clusterIncludeCenterCheckbox.toggled.connect(self.onClusterIncludeCenter)
        self._form.separationSpinBox.valueChanged.connect(self.onClusterSeparation)
        self._form.separationRelativeRadio.toggled.connect(self.onClusterSeparationRelative)
        self._form.separationAbsoluteRadio.toggled.connect(self.onClusterSeparationAbsolute)
        self._form.rotationSpinBox.valueChanged.connect(self.onClusterRotation)
        self._form.cantGroupBox.toggled.connect(self.onClusterCant)
        self._form.cantAngleRadio.toggled.connect(self.onClusterCantAngle)
        self._form.cantAngleSpinBox.valueChanged.connect(self.onClusterCantAngleValue)
        self._form.cantFocusRadio.toggled.connect(self.onClusterCantFocus)
        self._form.cantFocusSpinBox.valueChanged.connect(self.onClusterCantFocusValue)
        self._form.cantFocusRelativeRadio.toggled.connect(self.onClusterCantFocusRelative)
        self._form.cantFocusAbsoluteRadio.toggled.connect(self.onClusterCantFocusAbsolute)
        self._form.splitClusterButton.clicked.connect(self.onSplitCluster)
        self._form.resetButton.clicked.connect(self.onResetCluster)


    def transferTo(self, obj):
        "Transfer from the dialog to the object"
        try:
            obj.Clustered = self._form.clusterGroup.isChecked()
            obj.ClusterRadial = self._form.clusterRadialRadio.isChecked()
            obj.ClusterRadialCount = self._form.clusterRadialCountSpinBox.value()
            obj.ClusterRows = self._form.clusterRowsSpinBox.value()
            obj.ClusterColumns = self._form.clusterColumnsSpinBox.value()
            obj.ClusterIncludeCenter = self._form.clusterIncludeCenterCheckbox.isChecked()
            if obj.ClusterSeparationAbsolute:
                obj.Proxy.setClusterScaleAbsolute(self._form.separationSpinBox.property("value").Value)
            else:
                obj.Proxy.setClusterScale(self._form.separationSpinBox.property("value").Value)
            obj.ClusterRotation = self._form.rotationSpinBox.property("value")
            obj.ClusterCant = self._form.cantGroupBox.isChecked()
            obj.ClusterCantUseAngle = self._form.cantAngleRadio.isChecked()
            obj.ClusterCantAngle = self._form.cantAngleSpinBox.property("value")
            obj.ClusterCantFocus = self._form.cantFocusSpinBox.property("value")
            obj.ClusterCantFocusAbsolute = self._form.cantFocusAbsoluteRadio.isChecked()
        except Exception as e:
            print(f"transferTo: {e}")

    def transferFrom(self, obj):
        "Transfer from the object to the dialog"
        try:
            self._loading = True

            self._form.clusterGroup.setChecked(obj.Clustered)
            self._form.clusterRadialRadio.setChecked(obj.ClusterRadial)
            self._form.clusterXYRadio.setChecked(not obj.ClusterRadial)
            self._form.clusterRadialCountSpinBox.setValue(int(obj.ClusterRadialCount))
            self._form.clusterRowsSpinBox.setValue(int(obj.ClusterRows))
            self._form.clusterColumnsSpinBox.setValue(int(obj.ClusterColumns))
            self._form.clusterIncludeCenterCheckbox.setChecked(obj.ClusterIncludeCenter)
            self._form.separationRelativeRadio.setChecked(not obj.ClusterSeparationAbsolute)
            self._form.separationAbsoluteRadio.setChecked(obj.ClusterSeparationAbsolute)
            if obj.ClusterSeparationAbsolute:
                quantity = obj.Proxy.getClusterScaleAbsoluteQuantity()
            else:
                quantity = obj.Proxy.getClusterScaleQuantity()
            self._form.separationSpinBox.setProperty("value", quantity)
            self._form.rotationSpinBox.setProperty("value", obj.ClusterRotation)
            self._form.cantGroupBox.setChecked(obj.ClusterCant)
            self._form.cantAngleRadio.setChecked(obj.ClusterCantUseAngle)
            self._form.cantFocusRadio.setChecked(not obj.ClusterCantUseAngle)
            self._form.cantAngleSpinBox.setProperty("value", obj.ClusterCantAngle)
            self._form.cantFocusSpinBox.setProperty("value", obj.ClusterCantFocus)
            self._form.cantFocusRelativeRadio.setChecked(not obj.ClusterCantFocusAbsolute)
            self._form.cantFocusAbsoluteRadio.setChecked(obj.ClusterCantFocusAbsolute)
        except Exception as e:
            print(f"transferFrom: {e}")

        self._loading = False
        self._setClusterState()

    def setEdited(self) -> None:
        try:
            self._obj.Proxy.setEdited()
            self.cluster.emit()
        except ReferenceError:
            # Object may be deleted
            pass

    def _setClusterState(self) -> None:
        try:
            enabled = self._form.clusterGroup.isChecked()
            self._form.separationGroupBox.setEnabled(enabled)
            self._form.rotationGroupBox.setEnabled(enabled)
            self._form.cantGroupBox.setEnabled(enabled)
            if enabled:
                radial = self._obj.ClusterRadial

                if radial:
                    self._form.clusterRadialCountSpinBox.setEnabled(True)
                    self._form.clusterRowsSpinBox.setEnabled(False)
                    self._form.clusterColumnsSpinBox.setEnabled(False)
                else:
                    self._form.clusterRadialCountSpinBox.setEnabled(False)
                    self._form.clusterRowsSpinBox.setEnabled(True)
                    self._form.clusterColumnsSpinBox.setEnabled(True)

                if self._obj.ClusterSeparationAbsolute:
                    self._form.separationSpinBox.units = FreeCAD.Units.Length
                    self._form.separationSpinBox.setToolTip(translate('Rocket', "The separation of the tubes. 0.0 = touching each other"))
                    self._form.separationSpinBox.minimum = 0.0
                else:
                    self._form.separationSpinBox.units = ''
                    self._form.separationSpinBox.setToolTip(translate('Rocket', "The separation of the tubes. 1.0 = touching each other"))
                    self._form.separationSpinBox.minimum = 1.0

                if self._obj.ClusterCant:
                    if self._obj.ClusterCantUseAngle:
                        self._form.cantAngleSpinBox.setEnabled(True)
                        self._form.cantFocusSpinBox.setEnabled(False)
                        self._form.cantFocusRelativeRadio.setEnabled(False)
                        self._form.cantFocusAbsoluteRadio.setEnabled(False)
                    else:
                        self._form.cantAngleSpinBox.setEnabled(False)
                        self._form.cantFocusSpinBox.setEnabled(True)
                        self._form.cantFocusRelativeRadio.setEnabled(True)
                        self._form.cantFocusAbsoluteRadio.setEnabled(True)
        except Exception as e:
            print(f"setClusterState: {e}")

    def onClusterGroup(self, checked: bool) -> None:
        if self._loading:
            return
        with WaitCursor():
            self._obj.Clustered = checked
            self._setClusterState()
            self.setEdited()

    def onClusterRadial(self, checked: bool) -> None:
        if self._loading:
            return
        with WaitCursor():
            self._obj.ClusterRadial = checked
            self._setClusterState()
            self.setEdited()

    def onClusterRadialCount(self, value: int) -> None:
        if self._loading:
            return
        with WaitCursor():
            try:
                self._obj.ClusterRadialCount = value
            except ValueError:
                pass
            self.setEdited()

    def onClusterXY(self, checked: bool) -> None:   
        if self._loading:
            return
        with WaitCursor():
            self._obj.ClusterRadial = not checked
            self._setClusterState()
            self.setEdited()

    def onClusterRows(self, value: int) -> None:
        if self._loading:
            return
        with WaitCursor():
            try:
                self._obj.ClusterRows = value
            except ValueError:
                pass
            self.setEdited()

    def onClusterColumns(self, value: int) -> None:
        if self._loading:
            return
        with WaitCursor():
            try:
                self._obj.ClusterColumns = value
            except ValueError:
                pass
            self.setEdited()

    def onClusterIncludeCenter(self, checked: bool) -> None:
        if self._loading:
            return
        with WaitCursor():
            self._obj.ClusterIncludeCenter = checked
            self.setEdited()

    def onClusterSeparation(self, value: float | Units.Quantity) -> None:
        if self._loading:
            return
        with WaitCursor():
            try:
                value = float(value)
                if value < self._form.separationSpinBox.minimum:
                    # This should be handled by the spin box, but for some reason it isn't. So we handle it here.
                    value = self._form.separationSpinBox.minimum
                if self._obj.ClusterSeparationAbsolute:
                    self._obj.Proxy.setClusterScaleAbsolute(value)
                    quantity = self._obj.Proxy.getClusterScaleAbsoluteQuantity()
                else:
                    self._obj.Proxy.setClusterScale(value)
                    quantity = self._obj.Proxy.getClusterScaleQuantity()
                self._form.separationSpinBox.setProperty("value", quantity)
            except ValueError:
                pass
            self.setEdited()

    def onClusterSeparationRelative(self, checked: bool) -> None:
        self.onClusterSeparationAbsolute(not checked)

    def onClusterSeparationAbsolute(self, checked: bool) -> None:
        if self._loading:
            return
        with WaitCursor():
            try:
                self._obj.ClusterSeparationAbsolute = checked
                if checked:
                    quantity = self._obj.Proxy.getClusterScaleAbsoluteQuantity()
                else:
                    quantity = self._obj.Proxy.getClusterScaleQuantity()
                self._form.separationSpinBox.setProperty("value", quantity)
            except ValueError:
                pass
            self._setClusterState()
            self.setEdited()

    def onClusterRotation(self, value: float) -> None:
        if self._loading:
            return
        with WaitCursor():
            try:
                self._obj.ClusterRotation = value
            except ValueError:
                pass
            self.setEdited()

    def onClusterCant(self, checked: bool) -> None:
        if self._loading:
            return
        with WaitCursor():
            self._obj.ClusterCant = checked
            self._setClusterState()
            self.setEdited()

    def onClusterCantAngle(self, checked: bool) -> None:
        if self._loading:
            return
        with WaitCursor():
            self._obj.ClusterCantUseAngle = checked
            self._setClusterState()
            self.setEdited()

    def onClusterCantAngleValue(self, value: float) -> None:
        if self._loading:
            return
        with WaitCursor():
            try:
                self._obj.ClusterCantAngle = value
            except ValueError:
                pass
            self.setEdited()

    def onClusterCantFocus(self, checked: bool) -> None:
        self.onClusterCantAngle(not checked)

    def onClusterCantFocusValue(self, value: float) -> None:
        if self._loading:
            return
        with WaitCursor():
            try:
                self._obj.ClusterCantFocus = value
            except ValueError:
                pass
            self.setEdited()

    def onClusterCantFocusRelative(self, checked: bool) -> None:
        self.onClusterCantFocusAbsolute(not checked)

    def onClusterCantFocusAbsolute(self, checked: bool) -> None:
        if self._loading:
            return
        with WaitCursor():
            self._obj.ClusterCantFocusAbsolute = checked
            self.setEdited()

    def onSplitCluster(self) -> None:
        if self._loading:
            return
        with WaitCursor():
            pass # To be implemented
            self.setEdited()

    def onResetCluster(self) -> None:
        if self._loading:
            return
        with WaitCursor():
            self._obj.Proxy.resetCluster()
            self.transferFrom(self._obj)
            self.setEdited()