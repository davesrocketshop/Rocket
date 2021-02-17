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
"""Class for drawing nose cones"""

__title__ = "FreeCAD Nose Cones"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    

import FreeCAD
import FreeCADGui

from DraftTools import translate

from PySide import QtGui, QtCore
from PySide2.QtWidgets import QDialog, QGridLayout

from App.Utilities import _toFloat
from App.Constants import COMPONENT_TYPE_BODYTUBE, COMPONENT_TYPE_BULKHEAD, COMPONENT_TYPE_CENTERINGRING, COMPONENT_TYPE_COUPLER, \
    COMPONENT_TYPE_ENGINEBLOCK, COMPONENT_TYPE_LAUNCHLUG, COMPONENT_TYPE_NOSECONE, COMPONENT_TYPE_PARACHUTE, COMPONENT_TYPE_STREAMER, COMPONENT_TYPE_TRANSITION

from App.Parts.PartDatabase import PartDatabase

class _databaseLookupDialog(QDialog):

    def __init__(self, lookup, parent=None):
        super().__init__(parent)

        self._database = PartDatabase(FreeCAD.getUserAppDataDir() + "Mod/Rocket/")

        # define our window
        self.setGeometry(250, 250, 400, 350)
        self.setWindowTitle(translate('Rocket', "Rocket Component Parameter"))

        self.manufacturerLabel = QtGui.QLabel(translate('Rocket', "Manufacturer"), self)

        self.manufacturerInput = QtGui.QLineEdit(self)
        self.manufacturerInput.setFixedWidth(100)
        
        self.partNumberLabel = QtGui.QLabel(translate('Rocket', "Part Number"), self)

        self.partNumberInput = QtGui.QLineEdit(self)
        self.partNumberInput.setFixedWidth(100)

        self.descriptionLabel = QtGui.QLabel(translate('Rocket', "Description"), self)

        self.descriptionInput = QtGui.QLineEdit(self)
        self.descriptionInput.setFixedWidth(100)

        self.materialLabel = QtGui.QLabel(translate('Rocket', "Material"), self)

        self.materialInput = QtGui.QLineEdit(self)
        self.materialInput.setFixedWidth(100)

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

        self.setLayout(layout)

class TaskPanelDatabase:

    def __init__(self, form):
        self._form = form
        # self._form.setWindowIcon(QtGui.QIcon(":/icons/Rocket_BodyTube.svg"))
        
        self._form.manufacturerInput.textEdited.connect(self.onManufacturer)
        self._form.partNumberInput.textEdited.connect(self.onPartNumber)
        self._form.descriptionInput.textEdited.connect(self.onDescription)
        self._form.materialInput.textEdited.connect(self.onMaterial)
        
        self.update()

    def getForm(lookup, parent=None):
        return _databaseLookupDialog(lookup, parent)
        
    def transferTo(self):
        "Transfer from the dialog to the object" 
        self.obj.Manufacturer = self._form.manufacturerInput.text()
        self.obj.PartNumber = self._form.partNumberInput.text()
        self.obj.Description = self._form.descriptionInput.text()
        self.obj.Material = self._form.materialInput.text()

    def transferFrom(self):
        "Transfer from the object to the dialog"
        self._form.manufacturerInput.setText(self.obj.Manufacturer)
        self._form.partNumberInput.setText(self.obj.PartNumber)
        self._form.descriptionInput.setText(self.obj.Description)
        self._form.materialInput.setText(self.obj.Material)
        
    def onManufacturer(self, value):
        self.obj.Manufacturer = value
        
    def onPartNumber(self, value):
        self.obj.PartNumber = value
        
    def onDescription(self, value):
        self.obj.Description = value
        
    def onMaterial(self, value):
        self.obj.Material = value
        
    def update(self):
        'fills the widgets'
        self.transferFrom()
