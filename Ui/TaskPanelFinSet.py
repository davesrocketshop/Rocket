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
from PySide.QtCore import QObject, Signal
from PySide2.QtWidgets import QDialog, QGridLayout

from App.Utilities import _toFloat, _valueWithUnits
from App.Constants import LOCATION_PARENT_TOP, LOCATION_PARENT_MIDDLE, LOCATION_PARENT_BOTTOM, LOCATION_BASE

from App.Parts.PartDatabase import PartDatabase
from Ui.DialogLookup import DialogLookup, userOK, userCancelled

class _finSetDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        ui = FreeCADGui.UiLoader()

        # define our window
        self.setGeometry(250, 250, 400, 350)
        self.setWindowTitle(translate('Rocket', "Fin Set Parameter"))

        self.finSetLabel = QtGui.QLabel(translate('Rocket', "Fin Set"), self)

        self.finSetCheckbox = QtGui.QCheckBox(self)
        self.finSetCheckbox.setCheckState(QtCore.Qt.Unchecked)
        
        self.finCountLabel = QtGui.QLabel(translate('Rocket', "Fin Count"), self)

        self.finCountSpinBox = QtGui.QSpinBox(self)
        self.finCountSpinBox.setFixedWidth(80)
        self.finCountSpinBox.setMinimum(1)
        self.finCountSpinBox.setMaximum(10000)

        self.finSpacingLabel = QtGui.QLabel(translate('Rocket', "Fin Spacing"), self)

        self.finSpacingInput = ui.createWidget("Gui::InputField")
        self.finSpacingInput.unit = 'deg'
        self.finSpacingInput.setFixedWidth(80)

        self.offsetLabel = QtGui.QLabel(translate('Rocket', "Fin Offset"), self)

        self.offsetInput = ui.createWidget("Gui::InputField")
        self.offsetInput.unit = 'deg'
        self.offsetInput.setFixedWidth(80)

        # Select the fin set location reference
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

        layout = QGridLayout()

        n = 0
        layout.addWidget(self.finSetLabel, n, 0, 1, 2)
        layout.addWidget(self.finSetCheckbox, n, 1)
        n += 1

        layout.addWidget(self.finCountLabel, n, 0)
        layout.addWidget(self.finCountSpinBox, n, 1)
        n += 1

        layout.addWidget(self.finSpacingLabel, n, 0)
        layout.addWidget(self.finSpacingInput, n, 1)
        n += 1

        layout.addWidget(self.offsetLabel, n, 0)
        layout.addWidget(self.offsetInput, n, 1)
        n += 1

        layout.addWidget(self.referenceLabel, n, 0)
        layout.addWidget(self.referenceCombo, n, 1)
        n += 1

        layout.addWidget(self.locationLabel, n, 0)
        layout.addWidget(self.locationInput, n, 1)
        n += 1

        self.setLayout(layout)

class TaskPanelFinSet(QObject):

    finSetChange = Signal()   # emitted when a database lookup has completed

    def __init__(self, obj, parent=None):
        super().__init__()

        self._obj = obj
        self._form = _finSetDialog(parent)
        
        self._form.setWindowIcon(QtGui.QIcon(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_FinCan.svg"))
        
        self._form.finSetCheckbox.stateChanged.connect(self.onFinSet)
        self._form.finCountSpinBox.valueChanged.connect(self.onCount)
        self._form.finSpacingInput.textEdited.connect(self.onSpacing)
        self._form.offsetInput.textEdited.connect(self.onOffset)
        self._form.referenceCombo.currentIndexChanged.connect(self.onReference)
        self._form.locationInput.textEdited.connect(self.onLocation)

        
        self.update()

    def getForm(self):
        return self._form

    def getLookupResult(self):
        return self._lookupResult
        
    def transferTo(self):
        "Transfer from the dialog to the object" 
        self._obj.FinSet = self._form.finSetCheckbox.isChecked()
        self._obj.FinCount = self._form.finCountSpinBox.value()
        self._obj.FinSpacing = self._form.finSpacingInput.text()
        self._obj.RadialOffset = self._form.offsetInput.text()
        self._obj.LocationReference = str(self._form.referenceCombo.currentText())
        self._obj.Location = self._form.locationInput.text()

    def transferFrom(self):
        "Transfer from the object to the dialog"
        self._form.finSetCheckbox.setChecked(self._obj.FinSet)
        self._form.finCountSpinBox.setValue(self._obj.FinCount)
        self._form.finSpacingInput.setText(self._obj.FinSpacing.UserString)
        self._form.offsetInput.setText(self._obj.RadialOffset.UserString)
        self._form.referenceCombo.setCurrentText(self._obj.LocationReference)
        self._form.locationInput.setText(self._obj.Location.UserString)

        self._setFinSetState()
        
    def _setFinSetState(self):
        checked = self._form.finSetCheckbox.isChecked()

        self._form.finCountSpinBox.setEnabled(checked)
        self._form.finSpacingInput.setEnabled(checked)
        self._form.offsetInput.setEnabled(checked)
        self._form.referenceCombo.setEnabled(checked)
        self._form.locationInput.setEnabled(checked)

    def onFinSet(self, value):
        self._obj.FinSet = self._form.finSetCheckbox.isChecked()
        self._setFinSetState()
        
    def onCount(self, value):
        self._obj.FinCount = value
        self._obj.FinSpacing = 360.0 / float(value)
        self._form.finSpacingInput.setText(self._obj.FinSpacing.UserString)
        
    def onSpacing(self, value):
        self._obj.FinSpacing = value
        
    def onOffset(self, value):
        self._obj.RadialOffset = value
        
    def onReference(self, value):
        self._obj.LocationReference = value
        
    def onLocation(self, value):
        self._obj.Location = value
        
    def update(self):
        'fills the widgets'
        self.transferFrom()
