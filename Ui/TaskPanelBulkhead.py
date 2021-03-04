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
"""Class for drawing bulkheads"""

__title__ = "FreeCAD Bulkheads"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    

import FreeCAD
import FreeCADGui

from PySide import QtGui, QtCore
from PySide2.QtWidgets import QDialog, QGridLayout

from DraftTools import translate

from Ui.TaskPanelDatabase import TaskPanelDatabase
from App.Constants import COMPONENT_TYPE_BULKHEAD, COMPONENT_TYPE_CENTERINGRING

from App.Utilities import _toFloat, _toInt, _valueWithUnits

class _BulkheadDialog(QDialog):

    def __init__(self, crPanel, parent=None):
        super(_BulkheadDialog, self).__init__(parent)

        ui = FreeCADGui.UiLoader()

        # define our window
        self.setGeometry(250, 250, 400, 350)
        if crPanel:
            self.setWindowTitle(translate('Rocket', "Centering Ring Parameter"))
        else:
            self.setWindowTitle(translate('Rocket', "Bulkhead Parameter"))

        # Get the body tube parameters: length, ID, etc...
        self.diameterLabel = QtGui.QLabel(translate('Rocket', "Diameter"), self)

        self.diameterInput = ui.createWidget("Gui::InputField")
        self.diameterInput.unit = 'mm'
        self.diameterInput.setFixedWidth(100)

        self.thicknessLabel = QtGui.QLabel(translate('Rocket', "Thickness"), self)

        self.thicknessInput = ui.createWidget("Gui::InputField")
        self.thicknessInput.unit = 'mm'
        self.thicknessInput.setFixedWidth(100)

        if crPanel:
            self.centerDiameterLabel = QtGui.QLabel(translate('Rocket', "Center Diameter"), self)

            self.centerDiameterInput = ui.createWidget("Gui::InputField")
            self.centerDiameterInput.unit = 'mm'
            self.centerDiameterInput.setFixedWidth(100)
            self.notchedLabel = QtGui.QLabel(translate('Rocket', "Notched"), self)

            self.notchedCheckbox = QtGui.QCheckBox(self)
            self.notchedCheckbox.setCheckState(QtCore.Qt.Unchecked)

            self.notchWidthLabel = QtGui.QLabel(translate('Rocket', "Width"), self)

            self.notchWidthInput = ui.createWidget("Gui::InputField")
            self.notchWidthInput.unit = 'mm'
            self.notchWidthInput.setFixedWidth(100)

            self.notchHeightLabel = QtGui.QLabel(translate('Rocket', "Height"), self)

            self.notchHeightInput = ui.createWidget("Gui::InputField")
            self.notchHeightInput.unit = 'mm'
            self.notchHeightInput.setFixedWidth(100)

        self.stepLabel = QtGui.QLabel(translate('Rocket', "Step"), self)

        self.stepCheckbox = QtGui.QCheckBox(self)
        self.stepCheckbox.setCheckState(QtCore.Qt.Unchecked)

        self.stepDiameterLabel = QtGui.QLabel(translate('Rocket', "Diameter"), self)

        self.stepDiameterInput = ui.createWidget("Gui::InputField")
        self.stepDiameterInput.unit = 'mm'
        self.stepDiameterInput.setFixedWidth(100)

        self.stepThicknessLabel = QtGui.QLabel(translate('Rocket', "Thickness"), self)

        self.stepThicknessInput = ui.createWidget("Gui::InputField")
        self.stepThicknessInput.unit = 'mm'
        self.stepThicknessInput.setFixedWidth(100)

        self.holeLabel = QtGui.QLabel(translate('Rocket', "Holes"), self)

        self.holeCheckbox = QtGui.QCheckBox(self)
        self.holeCheckbox.setCheckState(QtCore.Qt.Unchecked)

        self.holeDiameterLabel = QtGui.QLabel(translate('Rocket', "Diameter"), self)

        self.holeDiameterInput = ui.createWidget("Gui::InputField")
        self.holeDiameterInput.unit = 'mm'
        self.holeDiameterInput.setFixedWidth(100)

        self.holeCenterLabel = QtGui.QLabel(translate('Rocket', "Center"), self)

        self.holeCenterInput = ui.createWidget("Gui::InputField")
        self.holeCenterInput.unit = 'mm'
        self.holeCenterInput.setFixedWidth(100)

        self.holeCountLabel = QtGui.QLabel(translate('Rocket', "Count"), self)

        self.holeCountSpinBox = QtGui.QSpinBox(self)
        self.holeCountSpinBox.setFixedWidth(100)
        self.holeCountSpinBox.setMinimum(1)
        self.holeCountSpinBox.setMaximum(10000)

        self.holeOffsetLabel = QtGui.QLabel(translate('Rocket', "Offset"), self)

        # Offsets can be positive or negative so no validator required
        self.holeOffsetInput = ui.createWidget("Gui::InputField")
        self.holeOffsetInput.unit = 'deg'
        self.holeOffsetInput.setFixedWidth(100)

        row = 0
        layout = QGridLayout()

        layout.addWidget(self.diameterLabel, row, 0, 1, 2)
        layout.addWidget(self.diameterInput, row, 1)
        row += 1

        layout.addWidget(self.thicknessLabel, row, 0)
        layout.addWidget(self.thicknessInput, row, 1)
        row += 1

        if crPanel:
            layout.addWidget(self.centerDiameterLabel, row, 0)
            layout.addWidget(self.centerDiameterInput, row, 1)
            row += 1

            layout.addWidget(self.notchedLabel, row, 0)
            layout.addWidget(self.notchedCheckbox, row, 1)
            row += 1

            layout.addWidget(self.notchWidthLabel, row, 1)
            layout.addWidget(self.notchWidthInput, row, 2)
            row += 1

            layout.addWidget(self.notchHeightLabel, row, 1)
            layout.addWidget(self.notchHeightInput, row, 2)
            row += 1

        layout.addWidget(self.stepLabel, row, 0)
        layout.addWidget(self.stepCheckbox, row, 1)
        row += 1

        layout.addWidget(self.stepDiameterLabel, row, 1)
        layout.addWidget(self.stepDiameterInput, row, 2)
        row += 1

        layout.addWidget(self.stepThicknessLabel, row, 1)
        layout.addWidget(self.stepThicknessInput, row, 2)
        row += 1

        layout.addWidget(self.holeLabel, row, 0)
        layout.addWidget(self.holeCheckbox, row, 1)
        row += 1

        layout.addWidget(self.holeDiameterLabel, row, 1)
        layout.addWidget(self.holeDiameterInput, row, 2)
        row += 1

        layout.addWidget(self.holeCenterLabel, row, 1)
        layout.addWidget(self.holeCenterInput, row, 2)
        row += 1

        layout.addWidget(self.holeCountLabel, row, 1)
        layout.addWidget(self.holeCountSpinBox, row, 2)
        row += 1

        layout.addWidget(self.holeOffsetLabel, row, 1)
        layout.addWidget(self.holeOffsetInput, row, 2)
        row += 1

        self.setLayout(layout)

class TaskPanelBulkhead:

    def __init__(self, obj, crPanel, mode):
        self._obj = obj
        self._crPanel = crPanel
        
        self._bulkForm = _BulkheadDialog(self._crPanel)
        if crPanel:
            self._db = TaskPanelDatabase(obj, COMPONENT_TYPE_CENTERINGRING)
        else:
            self._db = TaskPanelDatabase(obj, COMPONENT_TYPE_BULKHEAD)
        self._dbForm = self._db.getForm()

        self.form = [self._bulkForm, self._dbForm]
        if self._crPanel:
            self._bulkForm.setWindowIcon(QtGui.QIcon(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_CenterinRing.svg"))
        else:
            self._bulkForm.setWindowIcon(QtGui.QIcon(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Bulkhead.svg"))
        
        self._bulkForm.diameterInput.textEdited.connect(self.onDiameter)
        self._bulkForm.thicknessInput.textEdited.connect(self.onThickness)

        self._bulkForm.stepCheckbox.stateChanged.connect(self.onStep)
        self._bulkForm.stepDiameterInput.textEdited.connect(self.onStepDiameter)
        self._bulkForm.stepThicknessInput.textEdited.connect(self.onStepThickness)

        self._bulkForm.holeCheckbox.stateChanged.connect(self.onHole)
        self._bulkForm.holeDiameterInput.textEdited.connect(self.onHoleDiameter)
        self._bulkForm.holeCenterInput.textEdited.connect(self.onHoleCenter)
        self._bulkForm.holeCountSpinBox.valueChanged.connect(self.onHoleCount)
        self._bulkForm.holeOffsetInput.textEdited.connect(self.onHoleOffset)

        if self._crPanel:
            self._bulkForm.centerDiameterInput.textEdited.connect(self.onCenterDiameter)

            self._bulkForm.notchedCheckbox.stateChanged.connect(self.onNotched)
            self._bulkForm.notchWidthInput.textEdited.connect(self.onNotchWidth)
            self._bulkForm.notchHeightInput.textEdited.connect(self.onNotchHeight)

        self._db.dbLoad.connect(self.onLookup)
        
        self.update()
        
        if mode == 0: # fresh created
            self._obj.Proxy.execute(self._obj)  # calculate once 
            FreeCAD.Gui.SendMsgToActiveView("ViewFit")
        
    def transferTo(self):
        "Transfer from the dialog to the object" 
        self._obj.Diameter = self._bulkForm.diameterInput.text()
        self._obj.Thickness = self._bulkForm.thicknessInput.text()

        self._obj.Step = self._bulkForm.stepCheckbox.isChecked()
        self._obj.StepDiameter = self._bulkForm.stepDiameterInput.text()
        self._obj.StepThickness = self._bulkForm.stepThicknessInput.text()

        self._obj.Holes = self._bulkForm.holeCheckbox.isChecked()
        self._obj.HoleDiameter = self._bulkForm.holeDiameterInput.text()
        self._obj.HoleCenter = self._bulkForm.holeCenterInput.text()
        self._obj.HoleCount = self._bulkForm.holeCountSpinBox.value()
        self._obj.HoleOffset = self._bulkForm.holeOffsetInput.text()

        if self._crPanel:
            self._obj.CenterDiameter = self._bulkForm.centerDiameterInput.text()

            self._obj.Notched = self._bulkForm.notchedCheckbox.isChecked()
            self._obj.NotchWidth = self._bulkForm.notchWidthInput.text()
            self._obj.NotchHeight = self._bulkForm.notchHeightInput.text()

    def transferFrom(self):
        "Transfer from the object to the dialog"
        self._bulkForm.diameterInput.setText(self._obj.Diameter.UserString)
        self._bulkForm.thicknessInput.setText(self._obj.Thickness.UserString)

        self._bulkForm.stepCheckbox.setChecked(self._obj.Step)
        self._bulkForm.stepDiameterInput.setText(self._obj.StepDiameter.UserString)
        self._bulkForm.stepThicknessInput.setText(self._obj.StepThickness.UserString)

        self._bulkForm.holeCheckbox.setChecked(self._obj.Holes)
        self._bulkForm.holeDiameterInput.setText(self._obj.HoleDiameter.UserString)
        self._bulkForm.holeCenterInput.setText(self._obj.HoleCenter.UserString)
        self._bulkForm.holeCountSpinBox.setValue(self._obj.HoleCount)
        self._bulkForm.holeOffsetInput.setText(self._obj.HoleOffset.UserString)

        if self._crPanel:
            self._bulkForm.centerDiameterInput.setText(self._obj.CenterDiameter.UserString)

            self._bulkForm.notchedCheckbox.setChecked(self._obj.Notched)
            self._bulkForm.notchWidthInput.setText(self._obj.NotchWidth.UserString)
            self._bulkForm.notchHeightInput.setText(self._obj.NotchHeight.UserString)
            self._setNotchedState()

        self._setStepState()
        self._setHoleState()
        
    def onDiameter(self, value):
        try:
            self._obj.Diameter = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        
    def onThickness(self, value):
        try:
            self._obj.Thickness = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        
    def onCenterDiameter(self, value):
        try:
            self._obj.CenterDiameter = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        
    def _setStepState(self):
        self._bulkForm.stepDiameterInput.setEnabled(self._obj.Step)
        self._bulkForm.stepThicknessInput.setEnabled(self._obj.Step)
        
    def onStep(self, value):
        self._obj.Step = self._bulkForm.stepCheckbox.isChecked()
        self._setStepState()

        self._obj.Proxy.execute(self._obj)
        
    def onStepDiameter(self, value):
        try:
            self._obj.StepDiameter = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        
    def onStepThickness(self, value):
        try:
            self._obj.StepThickness = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        
    def _setHoleState(self):
        self._bulkForm.holeDiameterInput.setEnabled(self._obj.Holes)
        self._bulkForm.holeCenterInput.setEnabled(self._obj.Holes)
        self._bulkForm.holeCountSpinBox.setEnabled(self._obj.Holes)
        self._bulkForm.holeOffsetInput.setEnabled(self._obj.Holes)
        
    def onHole(self, value):
        self._obj.Holes = self._bulkForm.holeCheckbox.isChecked()
        self._setHoleState()

        self._obj.Proxy.execute(self._obj)
        
    def onHoleDiameter(self, value):
        try:
            self._obj.HoleDiameter = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        
    def onHoleCenter(self, value):
        try:
            self._obj.HoleCenter = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        
    def onHoleCount(self, value):
        self._obj.HoleCount = int(value)
        self._obj.Proxy.execute(self._obj)
        
    def onHoleOffset(self, value):
        try:
            self._obj.HoleOffset = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        
    def _setNotchedState(self):
        self._bulkForm.notchWidthInput.setEnabled(self._obj.Notched)
        self._bulkForm.notchHeightInput.setEnabled(self._obj.Notched)
        
    def onNotched(self, value):
        self._obj.Notched = self._bulkForm.notchedCheckbox.isChecked()
        self._setNotchedState()

        self._obj.Proxy.execute(self._obj)
        
    def onNotchWidth(self, value):
        try:
            self._obj.NotchWidth = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        
    def onNotchHeight(self, value):
        try:
            self._obj.NotchHeight = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        
    def onLookup(self):
        result = self._db.getLookupResult()

        self._obj.Diameter = _valueWithUnits(result["outer_diameter"], result["outer_diameter_units"])
        self._obj.Thickness =_valueWithUnits(result["length"], result["length_units"])

        self._obj.Step = False
        self._obj.StepDiameter = 0.0
        self._obj.StepThickness = 0.0

        self._obj.Holes = False
        self._obj.HoleDiameter = 0.0
        self._obj.HoleCenter = 0.0
        self._obj.HoleCount = 1
        self._obj.HoleOffset = 0.0

        if self._crPanel:
            self._obj.CenterDiameter = _valueWithUnits(result["inner_diameter"], result["inner_diameter_units"])

            self._obj.Notched = False
            self._obj.NotchWidth = 0.0
            self._obj.NotchHeight = 0.0
        
        self.update()
        self._obj.Proxy.execute(self._obj) 
        
    def getStandardButtons(self):
        return int(QtGui.QDialogButtonBox.Ok) | int(QtGui.QDialogButtonBox.Cancel)| int(QtGui.QDialogButtonBox.Apply)

    def clicked(self,button):
        if button == QtGui.QDialogButtonBox.Apply:
            #print "Apply"
            self.transferTo()
            self._obj.Proxy.execute(self._obj) 
        
    def update(self):
        'fills the widgets'
        self.transferFrom()
                
    def accept(self):
        self.transferTo()
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.resetEdit()
        
                    
    def reject(self):
        FreeCAD.ActiveDocument.abortTransaction()
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.resetEdit()
