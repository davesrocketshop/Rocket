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

from App.Utilities import _toFloat, _toInt

class _BulkheadDialog(QDialog):

    def __init__(self, crPanel, parent=None):
        super(_BulkheadDialog, self).__init__(parent)


        # define our window
        self.setGeometry(250, 250, 400, 350)
        if crPanel:
            self.setWindowTitle("Centering Ring Parameter")
        else:
            self.setWindowTitle("Bulkhead Parameter")

        # Get the body tube parameters: length, ID, etc...
        self.diameterLabel = QtGui.QLabel("Diameter", self)

        self.diameterValidator = QtGui.QDoubleValidator(self)
        self.diameterValidator.setBottom(0.0)

        self.diameterInput = QtGui.QLineEdit(self)
        self.diameterInput.setFixedWidth(100)
        self.diameterInput.setValidator(self.diameterValidator)

        self.thicknessLabel = QtGui.QLabel("Thickness", self)

        self.thicknessValidator = QtGui.QDoubleValidator(self)
        self.thicknessValidator.setBottom(0.0)

        self.thicknessInput = QtGui.QLineEdit(self)
        self.thicknessInput.setFixedWidth(100)
        self.thicknessInput.setValidator(self.thicknessValidator)

        if crPanel:
            self.centerDiameterLabel = QtGui.QLabel("Center Diameter", self)

            self.centerDiameterValidator = QtGui.QDoubleValidator(self)
            self.centerDiameterValidator.setBottom(0.0)

            self.centerDiameterInput = QtGui.QLineEdit(self)
            self.centerDiameterInput.setFixedWidth(100)
            self.centerDiameterInput.setValidator(self.centerDiameterValidator)

            self.notchedLabel = QtGui.QLabel("Notched", self)

            self.notchedCheckbox = QtGui.QCheckBox(self)
            self.notchedCheckbox.setCheckState(QtCore.Qt.Unchecked)

            self.notchWidthLabel = QtGui.QLabel("Width", self)

            self.notchWidthValidator = QtGui.QDoubleValidator(self)
            self.notchWidthValidator.setBottom(0.0)

            self.notchWidthInput = QtGui.QLineEdit(self)
            self.notchWidthInput.setFixedWidth(100)
            self.notchWidthInput.setValidator(self.notchWidthValidator)

            self.notchHeightLabel = QtGui.QLabel("Height", self)

            self.notchHeightValidator = QtGui.QDoubleValidator(self)
            self.notchHeightValidator.setBottom(0.0)

            self.notchHeightInput = QtGui.QLineEdit(self)
            self.notchHeightInput.setFixedWidth(100)
            self.notchHeightInput.setValidator(self.notchHeightValidator)

        self.stepLabel = QtGui.QLabel("Step", self)

        self.stepCheckbox = QtGui.QCheckBox(self)
        self.stepCheckbox.setCheckState(QtCore.Qt.Unchecked)

        self.stepDiameterLabel = QtGui.QLabel("Step Diameter", self)

        self.stepDiameterValidator = QtGui.QDoubleValidator(self)
        self.stepDiameterValidator.setBottom(0.0)

        self.stepDiameterInput = QtGui.QLineEdit(self)
        self.stepDiameterInput.setFixedWidth(100)
        self.stepDiameterInput.setValidator(self.stepDiameterValidator)

        self.stepThicknessLabel = QtGui.QLabel("Step Thickness", self)

        self.stepThicknessValidator = QtGui.QDoubleValidator(self)
        self.stepThicknessValidator.setBottom(0.0)

        self.stepThicknessInput = QtGui.QLineEdit(self)
        self.stepThicknessInput.setFixedWidth(100)
        self.stepThicknessInput.setValidator(self.stepThicknessValidator)

        self.holeLabel = QtGui.QLabel("Holes", self)

        self.holeCheckbox = QtGui.QCheckBox(self)
        self.holeCheckbox.setCheckState(QtCore.Qt.Unchecked)

        self.holeDiameterLabel = QtGui.QLabel("Hole Diameter", self)

        self.holeDiameterValidator = QtGui.QDoubleValidator(self)
        self.holeDiameterValidator.setBottom(0.0)

        self.holeDiameterInput = QtGui.QLineEdit(self)
        self.holeDiameterInput.setFixedWidth(100)
        self.holeDiameterInput.setValidator(self.holeDiameterValidator)

        self.holeCenterLabel = QtGui.QLabel("Hole Center", self)

        self.holeCenterValidator = QtGui.QDoubleValidator(self)
        self.holeCenterValidator.setBottom(0.0)

        self.holeCenterInput = QtGui.QLineEdit(self)
        self.holeCenterInput.setFixedWidth(100)
        self.holeCenterInput.setValidator(self.holeCenterValidator)

        self.holeCountLabel = QtGui.QLabel("Hole Count", self)

        self.holeCountValidator = QtGui.QIntValidator(self)
        self.holeCountValidator.setBottom(0)

        self.holeCountInput = QtGui.QLineEdit(self)
        self.holeCountInput.setFixedWidth(100)
        self.holeCountInput.setValidator(self.holeCountValidator)

        self.holeOffsetLabel = QtGui.QLabel("Hole Offset", self)

        # Offsets can be positive or negative so no validator required
        self.holeOffsetInput = QtGui.QLineEdit(self)
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
        layout.addWidget(self.holeCountInput, row, 2)
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
            self.form.setWindowIcon(QtGui.QIcon(":/icons/Rocket_CenterinRing.svg"))
        else:
            self.form.setWindowIcon(QtGui.QIcon(":/icons/Rocket_Bulkhead.svg"))
        
        self.form.diameterInput.textEdited.connect(self.onDiameter)
        self.form.thicknessInput.textEdited.connect(self.onThickness)

        self.form.stepCheckbox.stateChanged.connect(self.onStep)
        self.form.stepDiameterInput.textEdited.connect(self.onStepDiameter)
        self.form.stepThicknessInput.textEdited.connect(self.onStepThickness)

        self.form.holeCheckbox.stateChanged.connect(self.onHole)
        self.form.holeDiameterInput.textEdited.connect(self.onHoleDiameter)
        self.form.holeCenterInput.textEdited.connect(self.onHoleCenter)
        self.form.holeCountInput.textEdited.connect(self.onHoleCount)
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
        self.obj.Diameter = _toFloat(self.form.diameterInput.text())
        self.obj.Thickness = _toFloat(self.form.thicknessInput.text())

        self.obj.Step = self.form.stepCheckbox.isChecked()
        self.obj.StepDiameter = _toFloat(self.form.stepDiameterInput.text())
        self.obj.StepThickness = _toFloat(self.form.stepThicknessInput.text())

        self.obj.Holes = self.form.holeCheckbox.isChecked()
        self.obj.HoleDiameter = _toFloat(self.form.holeDiameterInput.text())
        self.obj.HoleCenter = _toFloat(self.form.holeCenterInput.text())
        self.obj.HoleCount = _toInt(self.form.holeCountInput.text())
        self.obj.HoleOffset = _toFloat(self.form.holeOffsetInput.text())

        if self._crPanel:
            self.obj.CenterDiameter = _toFloat(self.form.centerDiameterInput.text())

            self.obj.Notched = self.form.notchedCheckbox.isChecked()
            self.obj.NotchWidth = _toFloat(self.form.notchWidthInput.text())
            self.obj.NotchHeight = _toFloat(self.form.notchHeightInput.text())
    
    def transferFrom(self):
        "Transfer from the object to the dialog"
        self.form.diameterInput.setText("%f" % self.obj.Diameter)
        self.form.thicknessInput.setText("%f" % self.obj.Thickness)

        self.form.stepCheckbox.setChecked(self.obj.Step)
        self.form.stepDiameterInput.setText("%f" % self.obj.StepDiameter)
        self.form.stepThicknessInput.setText("%f" % self.obj.StepThickness)

        self.form.holeCheckbox.setChecked(self.obj.Holes)
        self.form.holeDiameterInput.setText("%f" % self.obj.HoleDiameter)
        self.form.holeCenterInput.setText("%f" % self.obj.HoleCenter)
        self.form.holeCountInput.setText("%d" % self.obj.HoleCount)
        self.form.holeOffsetInput.setText("%f" % self.obj.HoleOffset)

        if self._crPanel:
            self.form.centerDiameterInput.setText("%f" % self.obj.CenterDiameter)

            self.form.notchedCheckbox.setChecked(self.obj.Notched)
            self.form.notchWidthInput.setText("%f" % self.obj.NotchWidth)
            self.form.notchHeightInput.setText("%f" % self.obj.NotchHeight)
            self._setNotchedState()

        self._setStepState()
        self._setHoleState()
        
    def onDiameter(self, value):
        self.obj.Diameter = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onThickness(self, value):
        self.obj.Thickness = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onCenterDiameter(self, value):
        self.obj.CenterDiameter = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def _setStepState(self):
        self.form.stepDiameterInput.setEnabled(self.obj.Step)
        self.form.stepThicknessInput.setEnabled(self.obj.Step)
        
    def onStep(self, value):
        self.obj.Step = self.form.stepCheckbox.isChecked()
        self._setStepState()

        self.obj.Proxy.execute(self.obj)
        
    def onStepDiameter(self, value):
        self.obj.StepDiameter = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onStepThickness(self, value):
        self.obj.StepThickness = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def _setHoleState(self):
        self.form.holeDiameterInput.setEnabled(self.obj.Holes)
        self.form.holeCenterInput.setEnabled(self.obj.Holes)
        self.form.holeCountInput.setEnabled(self.obj.Holes)
        self.form.holeOffsetInput.setEnabled(self.obj.Holes)
        
    def onHole(self, value):
        self.obj.Holes = self.form.holeCheckbox.isChecked()
        self._setHoleState()

        self.obj.Proxy.execute(self.obj)
        
    def onHoleDiameter(self, value):
        self.obj.HoleDiameter = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onHoleCenter(self, value):
        self.obj.HoleCenter = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onHoleCount(self, value):
        self.obj.HoleCount = _toInt(value)
        self.obj.Proxy.execute(self.obj)
        
    def onHoleOffset(self, value):
        self.obj.HoleOffset = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def _setNotchedState(self):
        self.form.notchWidthInput.setEnabled(self.obj.Notched)
        self.form.notchHeightInput.setEnabled(self.obj.Notched)
        
    def onNotched(self, value):
        self.obj.Notched = self.form.notchedCheckbox.isChecked()
        self._setNotchedState()

        self.obj.Proxy.execute(self.obj)
        
    def onNotchWidth(self, value):
        self.obj.NotchWidth = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onNotchHeight(self, value):
        self.obj.NotchHeight = _toFloat(value)
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
        FreeCADGui.ActiveDocument.resetEdit()
        FreeCAD.ActiveDocument.abortTransaction()
        FreeCAD.ActiveDocument.recompute() #??? Should the object not be created?
