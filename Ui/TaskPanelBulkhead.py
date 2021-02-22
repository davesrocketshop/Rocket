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

from App.Utilities import _toFloat, _toInt

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
        self.obj = obj
        self._crPanel = crPanel
        
        self.form = _BulkheadDialog(self._crPanel)
        if self._crPanel:
            self.form.setWindowIcon(QtGui.QIcon(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_CenterinRing.svg"))
        else:
            self.form.setWindowIcon(QtGui.QIcon(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Bulkhead.svg"))
        
        self.form.diameterInput.textEdited.connect(self.onDiameter)
        self.form.thicknessInput.textEdited.connect(self.onThickness)

        self.form.stepCheckbox.stateChanged.connect(self.onStep)
        self.form.stepDiameterInput.textEdited.connect(self.onStepDiameter)
        self.form.stepThicknessInput.textEdited.connect(self.onStepThickness)

        self.form.holeCheckbox.stateChanged.connect(self.onHole)
        self.form.holeDiameterInput.textEdited.connect(self.onHoleDiameter)
        self.form.holeCenterInput.textEdited.connect(self.onHoleCenter)
        self.form.holeCountSpinBox.valueChanged.connect(self.onHoleCount)
        self.form.holeOffsetInput.textEdited.connect(self.onHoleOffset)

        if self._crPanel:
            self.form.centerDiameterInput.textEdited.connect(self.onCenterDiameter)

            self.form.notchedCheckbox.stateChanged.connect(self.onNotched)
            self.form.notchWidthInput.textEdited.connect(self.onNotchWidth)
            self.form.notchHeightInput.textEdited.connect(self.onNotchHeight)
        
        self.update()
        
        if mode == 0: # fresh created
            self.obj.Proxy.execute(self.obj)  # calculate once 
            FreeCAD.Gui.SendMsgToActiveView("ViewFit")
        
    def transferTo(self):
        "Transfer from the dialog to the object" 
        self.obj.Diameter = self.form.diameterInput.text()
        self.obj.Thickness = self.form.thicknessInput.text()

        self.obj.Step = self.form.stepCheckbox.isChecked()
        self.obj.StepDiameter = self.form.stepDiameterInput.text()
        self.obj.StepThickness = self.form.stepThicknessInput.text()

        self.obj.Holes = self.form.holeCheckbox.isChecked()
        self.obj.HoleDiameter = self.form.holeDiameterInput.text()
        self.obj.HoleCenter = self.form.holeCenterInput.text()
        self.obj.HoleCount = self.form.holeCountSpinBox.value()
        self.obj.HoleOffset = self.form.holeOffsetInput.text()

        if self._crPanel:
            self.obj.CenterDiameter = self.form.centerDiameterInput.text()

            self.obj.Notched = self.form.notchedCheckbox.isChecked()
            self.obj.NotchWidth = self.form.notchWidthInput.text()
            self.obj.NotchHeight = self.form.notchHeightInput.text()

    def transferFrom(self):
        "Transfer from the object to the dialog"
        self.form.diameterInput.setText(self.obj.Diameter.UserString)
        self.form.thicknessInput.setText(self.obj.Thickness.UserString)

        self.form.stepCheckbox.setChecked(self.obj.Step)
        self.form.stepDiameterInput.setText(self.obj.StepDiameter.UserString)
        self.form.stepThicknessInput.setText(self.obj.StepThickness.UserString)

        self.form.holeCheckbox.setChecked(self.obj.Holes)
        self.form.holeDiameterInput.setText(self.obj.HoleDiameter.UserString)
        self.form.holeCenterInput.setText(self.obj.HoleCenter.UserString)
        self.form.holeCountSpinBox.setValue(self.obj.HoleCount)
        self.form.holeOffsetInput.setText(self.obj.HoleOffset.UserString)

        if self._crPanel:
            self.form.centerDiameterInput.setText(self.obj.CenterDiameter.UserString)

            self.form.notchedCheckbox.setChecked(self.obj.Notched)
            self.form.notchWidthInput.setText(self.obj.NotchWidth.UserString)
            self.form.notchHeightInput.setText(self.obj.NotchHeight.UserString)
            self._setNotchedState()

        self._setStepState()
        self._setHoleState()
        
    def onDiameter(self, value):
        self.obj.Diameter = value
        self.obj.Proxy.execute(self.obj)
        
    def onThickness(self, value):
        self.obj.Thickness = value
        self.obj.Proxy.execute(self.obj)
        
    def onCenterDiameter(self, value):
        self.obj.CenterDiameter = value
        self.obj.Proxy.execute(self.obj)
        
    def _setStepState(self):
        self.form.stepDiameterInput.setEnabled(self.obj.Step)
        self.form.stepThicknessInput.setEnabled(self.obj.Step)
        
    def onStep(self, value):
        self.obj.Step = self.form.stepCheckbox.isChecked()
        self._setStepState()

        self.obj.Proxy.execute(self.obj)
        
    def onStepDiameter(self, value):
        self.obj.StepDiameter = value
        self.obj.Proxy.execute(self.obj)
        
    def onStepThickness(self, value):
        self.obj.StepThickness = value
        self.obj.Proxy.execute(self.obj)
        
    def _setHoleState(self):
        self.form.holeDiameterInput.setEnabled(self.obj.Holes)
        self.form.holeCenterInput.setEnabled(self.obj.Holes)
        self.form.holeCountSpinBox.setEnabled(self.obj.Holes)
        self.form.holeOffsetInput.setEnabled(self.obj.Holes)
        
    def onHole(self, value):
        self.obj.Holes = self.form.holeCheckbox.isChecked()
        self._setHoleState()

        self.obj.Proxy.execute(self.obj)
        
    def onHoleDiameter(self, value):
        self.obj.HoleDiameter = value
        self.obj.Proxy.execute(self.obj)
        
    def onHoleCenter(self, value):
        self.obj.HoleCenter = value
        self.obj.Proxy.execute(self.obj)
        
    def onHoleCount(self, value):
        self.obj.HoleCount = int(value)
        self.obj.Proxy.execute(self.obj)
        
    def onHoleOffset(self, value):
        self.obj.HoleOffset = value
        self.obj.Proxy.execute(self.obj)
        
    def _setNotchedState(self):
        self.form.notchWidthInput.setEnabled(self.obj.Notched)
        self.form.notchHeightInput.setEnabled(self.obj.Notched)
        
    def onNotched(self, value):
        self.obj.Notched = self.form.notchedCheckbox.isChecked()
        self._setNotchedState()

        self.obj.Proxy.execute(self.obj)
        
    def onNotchWidth(self, value):
        self.obj.NotchWidth = value
        self.obj.Proxy.execute(self.obj)
        
    def onNotchHeight(self, value):
        self.obj.NotchHeight = value
        self.obj.Proxy.execute(self.obj)
        
    def getStandardButtons(self):
        return int(QtGui.QDialogButtonBox.Ok) | int(QtGui.QDialogButtonBox.Cancel)| int(QtGui.QDialogButtonBox.Apply)

    def clicked(self,button):
        if button == QtGui.QDialogButtonBox.Apply:
            #print "Apply"
            self.transferTo()
            self.obj.Proxy.execute(self.obj) 
        
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
