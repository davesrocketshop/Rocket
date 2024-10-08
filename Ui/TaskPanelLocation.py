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
"""Class for setting object location"""

__title__ = "FreeCAD Location"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"


import FreeCAD
import FreeCADGui

from DraftTools import translate

from PySide import QtGui, QtCore
from PySide.QtCore import QObject, Signal
from PySide6.QtWidgets import QDialog, QGridLayout

from Rocket.Utilities import _toFloat, _valueWithUnits
from Rocket.Constants import LOCATION_PARENT_TOP, LOCATION_PARENT_MIDDLE, LOCATION_PARENT_BOTTOM, LOCATION_BASE
from Rocket.Constants import LOCATION_SURFACE, LOCATION_CENTER

from Rocket.Parts.PartDatabase import PartDatabase
from Ui.DialogLookup import DialogLookup, userOK, userCancelled

class _locationDialog(QDialog):

    def __init__(self, radial, axial, parent=None):
        super().__init__(parent)

        ui = FreeCADGui.UiLoader()

        # define our window
        self.setGeometry(250, 250, 400, 350)
        self.setWindowTitle(translate('Rocket', "Location Parameter"))

        if radial:
            self.radialReferenceLabel = QtGui.QLabel(translate('Rocket', "Radial Reference"), self)

            self.radialReferenceTypes = (
                LOCATION_SURFACE,
                LOCATION_CENTER
                )
            self.radialReferenceCombo = QtGui.QComboBox(self)
            self.radialReferenceCombo.addItems(self.radialReferenceTypes)

            self.radialOffsetLabel = QtGui.QLabel(translate('Rocket', "Radial Offset"), self)

            self.radialOffsetInput = ui.createWidget("Gui::InputField")
            self.radialOffsetInput.unit = 'mm'
            self.radialOffsetInput.setMinimumWidth(80)

        # Select the location reference
        if axial:
            self.referenceLabel = QtGui.QLabel(translate('Rocket', "Location Reference"), self)

            self.referenceTypes = (
                LOCATION_PARENT_TOP,
                LOCATION_PARENT_MIDDLE,
                LOCATION_PARENT_BOTTOM,
                LOCATION_BASE,
                )
            self.referenceCombo = QtGui.QComboBox(self)
            self.referenceCombo.addItems(self.referenceTypes)

            self.locationLabel = QtGui.QLabel(translate('Rocket', "Location"), self)

            self.locationInput = ui.createWidget("Gui::InputField")
            self.locationInput.unit = 'mm'
            self.locationInput.setMinimumWidth(80)

        self.angleOffsetLabel = QtGui.QLabel(translate('Rocket', "Angle Offset"), self)

        self.angleOffsetInput = ui.createWidget("Gui::InputField")
        self.angleOffsetInput.unit = 'deg'
        self.angleOffsetInput.setMinimumWidth(80)

        layout = QGridLayout()

        n = 0
        if radial:
            layout.addWidget(self.radialReferenceLabel, n, 0, 1, 2)
            layout.addWidget(self.radialReferenceCombo, n, 1)
            n += 1

            layout.addWidget(self.radialOffsetLabel, n, 0)
            layout.addWidget(self.radialOffsetInput, n, 1)
            n += 1

        if axial:
            layout.addWidget(self.referenceLabel, n, 0, 1, 2)
            layout.addWidget(self.referenceCombo, n, 1)
            n += 1

            layout.addWidget(self.locationLabel, n, 0)
            layout.addWidget(self.locationInput, n, 1)
            n += 1

        layout.addWidget(self.angleOffsetLabel, n, 0)
        layout.addWidget(self.angleOffsetInput, n, 1)

        self.setLayout(layout)

class TaskPanelLocation(QObject):

    locationChange = Signal()   # emitted when location has changed

    def __init__(self, obj, radial=False, parent=None):
        super().__init__()

        self._obj = obj
        self._radial = radial
        self._axial = not obj.Proxy.isAfter()
        self._form = _locationDialog(radial, self._axial, parent)

        # self._form.setWindowIcon(QtGui.QIcon(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Location.svg"))

        if self._axial:
            self._form.referenceCombo.currentTextChanged.connect(self.onReference)
            self._form.locationInput.textEdited.connect(self.onLocation)
        self._form.angleOffsetInput.textEdited.connect(self.onAngleOffset)

        if self._radial:
            self._form.radialReferenceCombo.currentIndexChanged.connect(self.onRadialReference)
            self._form.radialOffsetInput.textEdited.connect(self.onRadialOffset)

        self.update()

    def getForm(self):
        return self._form

    def transferTo(self):
        "Transfer from the dialog to the object"
        if self._axial:
            self._obj.Proxy.setLocationReference(str(self._form.referenceCombo.currentText()))
            self._obj.AxialOffset = self._form.locationInput.text()
        self._obj.AngleOffset = self._form.angleOffsetInput.text()

        if self._radial:
            self._obj.RadialReference = str(self._form.radialReferenceCombo.currentText())
            self._obj.RadialOffset = self._form.radialOffsetInput.text()

    def transferFrom(self):
        "Transfer from the object to the dialog"
        if self._axial:
            self._form.referenceCombo.setCurrentText(self._obj.AxialMethod.getMethodName())
            self._form.locationInput.setText(self._obj.AxialOffset.UserString)
        self._form.angleOffsetInput.setText(self._obj.AngleOffset.UserString)

        if self._radial:
            self._form.radialReferenceCombo.setCurrentText(self._obj.RadialReference)
            self._form.radialOffsetInput.setText(self._obj.RadialOffset.UserString)

    def setEdited(self):
        self.locationChange.emit()

    def onReference(self, value):
        # self._obj.LocationReference = value
        self._obj.Proxy.setLocationReference(value)
        self._form.locationInput.setText(self._obj.AxialOffset.UserString)
        self.setEdited()

    def onRadialReference(self, value):
        try:
            self._obj.RadialReference = FreeCAD.Units.Quantity(value).Value
        except ValueError:
            pass
        self.setEdited()

    def onLocation(self, value):
        try:
            self._obj.AxialOffset = FreeCAD.Units.Quantity(value).Value
        except ValueError:
            pass
        self.setEdited()

    def onAngleOffset(self, value):
        try:
            self._obj.AngleOffset = FreeCAD.Units.Quantity(value).Value
        except ValueError:
            pass
        self.setEdited()

    def onRadialOffset(self, value):
        try:
            self._obj.RadialOffset = FreeCAD.Units.Quantity(value).Value
        except ValueError:
            pass
        self.setEdited()

    def update(self):
        'fills the widgets'
        self.transferFrom()
