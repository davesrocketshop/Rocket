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
"""Class for database lookups"""

__title__ = "FreeCAD Database Lookup"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    

import FreeCAD

from DraftTools import translate

from PySide import QtGui
from PySide.QtCore import QObject, Signal
from PySide2.QtWidgets import QDialog, QGridLayout

from App.Parts.PartDatabase import PartDatabase
from Ui.DialogLookup import DialogLookup

class _databaseLookupDialog(QDialog):

    def __init__(self, lookup, parent=None):
        super().__init__(parent)

        self._database = PartDatabase(FreeCAD.getUserAppDataDir() + "Mod/Rocket/")

        # define our window
        self.setGeometry(250, 250, 400, 350)
        self.setWindowTitle(translate('Rocket', "Rocket Component Parameter"))

        self.manufacturerLabel = QtGui.QLabel(translate('Rocket', "Manufacturer"), self)

        self.manufacturerInput = QtGui.QLineEdit(self)
        self.manufacturerInput.setMinimumWidth(100)
        
        self.partNumberLabel = QtGui.QLabel(translate('Rocket', "Part Number"), self)

        self.partNumberInput = QtGui.QLineEdit(self)
        self.partNumberInput.setMinimumWidth(100)

        self.descriptionLabel = QtGui.QLabel(translate('Rocket', "Description"), self)

        self.descriptionInput = QtGui.QLineEdit(self)
        self.descriptionInput.setMinimumWidth(100)

        self.materialLabel = QtGui.QLabel(translate('Rocket', "Material"), self)

        self.materialInput = QtGui.QLineEdit(self)
        self.materialInput.setMinimumWidth(100)

        self.lookupButton = QtGui.QPushButton(translate('Rocket', "Lookup..."), self)

        layout = QGridLayout()

        n = 0
        layout.addWidget(self.manufacturerLabel, n, 0, 1, 2)
        layout.addWidget(self.manufacturerInput, n, 1)
        n += 1

        layout.addWidget(self.partNumberLabel, n, 0)
        layout.addWidget(self.partNumberInput, n, 1)
        n += 1

        layout.addWidget(self.descriptionLabel, n, 0)
        layout.addWidget(self.descriptionInput, n, 1)
        n += 1

        layout.addWidget(self.materialLabel, n, 0)
        layout.addWidget(self.materialInput, n, 1)
        n += 1

        layout.addWidget(self.lookupButton, n, 1)
        n += 1

        self.setLayout(layout)

class TaskPanelDatabase(QObject):

    dbLoad = Signal()   # emitted when a database lookup has completed

    def __init__(self, obj, lookup, parent=None):
        super().__init__()

        self._obj = obj
        self._lookup = lookup # Default component type
        self._lookupResult = None
        self._form = _databaseLookupDialog(lookup, parent)
        
        self._form.setWindowIcon(QtGui.QIcon(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/RocketWorkbench.svg"))
        
        self._form.manufacturerInput.textEdited.connect(self.onManufacturer)
        self._form.partNumberInput.textEdited.connect(self.onPartNumber)
        self._form.descriptionInput.textEdited.connect(self.onDescription)
        self._form.materialInput.textEdited.connect(self.onMaterial)

        self._form.lookupButton.clicked.connect(self.onLookup)
        
        self.update()

    def getForm(self):
        return self._form

    def getLookupResult(self):
        return self._lookupResult
        
    def transferTo(self):
        "Transfer from the dialog to the object" 
        self._obj.Manufacturer = self._form.manufacturerInput.text()
        self._obj.PartNumber = self._form.partNumberInput.text()
        self._obj.Description = self._form.descriptionInput.text()
        self._obj.Material = self._form.materialInput.text()

    def transferFrom(self):
        "Transfer from the object to the dialog"
        self._form.manufacturerInput.setText(self._obj.Manufacturer)
        self._form.partNumberInput.setText(self._obj.PartNumber)
        self._form.descriptionInput.setText(self._obj.Description)
        self._form.materialInput.setText(self._obj.Material)
        
    def onManufacturer(self, value):
        self._obj.Manufacturer = value
        
    def onPartNumber(self, value):
        self._obj.PartNumber = value
        
    def onDescription(self, value):
        self._obj.Description = value
        
    def onMaterial(self, value):
        self._obj.Material = value

    def _lookupUpdate(self, result):
        self._obj.Manufacturer = result["manufacturer"]
        self._obj.PartNumber = result["part_number"]
        self._obj.Description = result["description"]
        self._obj.Material = result["material_name"]

        # self._obj.NoseType = str(result["shape"])
        # self._obj.NoseStyle = str(result["style"])
        # self._obj.Length = _valueWithUnits(result["length"], result["length_units"])
        # self._obj.Radius = _valueWithUnits(result["diameter"], result["diameter_units"]) / 2.0
        # self._obj.Thickness = _valueWithUnits(result["thickness"], result["thickness_units"])
        # # self._obj.Coefficient = _toFloat(self._noseForm.coefficientInput.text())
        # self._obj.ShoulderRadius = _valueWithUnits(result["shoulder_diameter"], result["shoulder_diameter_units"]) / 2.0
        # self._obj.ShoulderLength = _valueWithUnits(result["shoulder_length"], result["shoulder_length_units"])
        # self._obj.Shoulder = (self._obj.ShoulderRadius > 0.0) or (self._obj.ShoulderLength >= 0)
        # self._obj.ShoulderThickness = self._obj.Thickness

        self.transferFrom()

        self.dbLoad.emit()
        
    def onLookup(self):
        form = DialogLookup(self._lookup)
        form.exec_()

        if len(form.result) > 0:
            self._lookupResult = form.result
            self._lookupUpdate(form.result)
        
    def update(self):
        'fills the widgets'
        self.transferFrom()
