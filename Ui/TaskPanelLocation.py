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
"""Class for setting object location"""

__title__ = "FreeCAD Location"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    

import FreeCAD
import FreeCADGui

from DraftTools import translate

from PySide import QtGui, QtCore
from PySide.QtCore import QObject, Signal
from PySide2.QtWidgets import QDialog, QGridLayout

from App.Utilities import _toFloat, _valueWithUnits
from App.Constants import LOCATION_PARENT_TOP, LOCATION_PARENT_MIDDLE, LOCATION_PARENT_BOTTOM, LOCATION_BASE
from App.Constants import LOCATION_SURFACE, LOCATION_CENTER

from App.Parts.PartDatabase import PartDatabase
from Ui.DialogLookup import DialogLookup, userOK, userCancelled

class _locationDialog(QDialog):

    def __init__(self, axial, parent=None):
        super().__init__(parent)

        ui = FreeCADGui.UiLoader()

        # define our window
        self.setGeometry(250, 250, 400, 350)
        self.setWindowTitle(translate('Rocket', "Location Parameter"))

        if axial:
            self.axialReferenceLabel = QtGui.QLabel(translate('Rocket', "Axial Reference"), self)

            self.axialReferenceTypes = (
                LOCATION_SURFACE,
                LOCATION_CENTER
                )
            self.axialReferenceCombo = QtGui.QComboBox(self)
            self.axialReferenceCombo.addItems(self.axialReferenceTypes)

            self.axialOffsetLabel = QtGui.QLabel(translate('Rocket', "Axial Offset"), self)

            self.axialOffsetInput = ui.createWidget("Gui::InputField")
            self.axialOffsetInput.unit = 'mm'
            self.axialOffsetInput.setFixedWidth(80)

        # Select the location reference
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
        self.locationInput.setFixedWidth(80)

        self.radialOffsetLabel = QtGui.QLabel(translate('Rocket', "Radial Offset"), self)

        self.radialOffsetInput = ui.createWidget("Gui::InputField")
        self.radialOffsetInput.unit = 'deg'
        self.radialOffsetInput.setFixedWidth(80)

        layout = QGridLayout()

        n = 0
        if axial:
            layout.addWidget(self.axialReferenceLabel, n, 0, 1, 2)
            layout.addWidget(self.axialReferenceCombo, n, 1)
            n += 1

            layout.addWidget(self.axialOffsetLabel, n, 0)
            layout.addWidget(self.axialOffsetInput, n, 1)
            n += 1

        layout.addWidget(self.referenceLabel, n, 0, 1, 2)
        layout.addWidget(self.referenceCombo, n, 1)
        n += 1

        layout.addWidget(self.locationLabel, n, 0)
        layout.addWidget(self.locationInput, n, 1)
        n += 1

        layout.addWidget(self.radialOffsetLabel, n, 0)
        layout.addWidget(self.radialOffsetInput, n, 1)

        self.setLayout(layout)

class TaskPanelLocation(QObject):

    locationChange = Signal()   # emitted when location has changed

    def __init__(self, obj, axial=False, parent=None):
        super().__init__()

        self._obj = obj
        self._axial = axial
        self._form = _locationDialog(axial, parent)
        
        self._form.setWindowIcon(QtGui.QIcon(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Location.svg"))
        
        self._form.referenceCombo.currentIndexChanged.connect(self.onReference)
        self._form.locationInput.textEdited.connect(self.onLocation)
        self._form.radialOffsetInput.textEdited.connect(self.onRadialOffset)

        if self._axial:
            self._form.axialReferenceCombo.currentIndexChanged.connect(self.onAxialReference)
            self._form.axialOffsetInput.textEdited.connect(self.onAxialOffset)
        
        self.update()

    def getForm(self):
        return self._form

    def getLookupResult(self):
        return self._lookupResult
        
    def transferTo(self):
        "Transfer from the dialog to the object" 
        self._obj.LocationReference = str(self._form.referenceCombo.currentText())
        self._obj.Location = self._form.locationInput.text()
        self._obj.RadialOffset = self._form.radialOffsetInput.text()

        if self._axial:
            self._obj.AxialReference = str(self._form.axialReferenceCombo.currentText())
            self._obj.AxialOffset = self._form.axialOffsetInput.text()

    def transferFrom(self):
        "Transfer from the object to the dialog"
        self._form.referenceCombo.setCurrentText(self._obj.LocationReference)
        self._form.locationInput.setText(self._obj.Location.UserString)
        self._form.radialOffsetInput.setText(self._obj.RadialOffset.UserString)

        if self._axial:
            self._form.axialReferenceCombo.setCurrentText(self._obj.AxialReference)
            self._form.axialOffsetInput.setText(self._obj.AxialOffset.UserString)
 
    def setEdited(self):
        self.locationChange.emit()
       
    def onReference(self, value):
        self._obj.LocationReference = value
        self.setEdited()
       
    def onAxialReference(self, value):
        self._obj.AxialReference = value
        self.setEdited()
        
    def onLocation(self, value):
        self._obj.Location = value
        self.setEdited()
        
    def onAxialOffset(self, value):
        self._obj.AxialOffset = value
        self.setEdited()
        
    def onRadialOffset(self, value):
        self._obj.RadialOffset = value
        self.setEdited()
        
    def update(self):
        'fills the widgets'
        self.transferFrom()
