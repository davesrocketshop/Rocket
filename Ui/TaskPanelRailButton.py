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
"""Class for drawing rail buttons"""

__title__ = "FreeCAD Rail Buttons"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    

import FreeCAD
import FreeCADGui

from DraftTools import translate

from PySide import QtGui, QtCore
from PySide2.QtWidgets import QDialog, QGridLayout, QVBoxLayout

from Ui.TaskPanelLocation import TaskPanelLocation

from App.Utilities import _valueWithUnits, _valueOnly

class _RailButtonDialog(QDialog):

    def __init__(self, parent=None):
        super(_RailButtonDialog, self).__init__(parent)

        ui = FreeCADGui.UiLoader()

        # define our window
        self.setGeometry(250, 250, 400, 350)
        self.setWindowTitle(translate('Rocket', "Rail Button Parameter"))

        # Get the body tube parameters: length, ID, etc...
        self.odLabel = QtGui.QLabel(translate('Rocket', "Outer Diameter"), self)

        self.odInput = ui.createWidget("Gui::InputField")
        self.odInput.unit = 'mm'
        self.odInput.setFixedWidth(80)

        self.autoDiameterCheckbox = QtGui.QCheckBox(translate('Rocket', "auto"), self)
        self.autoDiameterCheckbox.setCheckState(QtCore.Qt.Unchecked)

        self.idLabel = QtGui.QLabel(translate('Rocket', "Inner Diameter"), self)

        self.idInput = ui.createWidget("Gui::InputField")
        self.idInput.unit = 'mm'
        self.idInput.setFixedWidth(80)

        self.thicknessLabel = QtGui.QLabel(translate('Rocket', "Wall Thickness"), self)

        self.thicknessInput = ui.createWidget("Gui::InputField")
        self.thicknessInput.unit = 'mm'
        self.thicknessInput.setFixedWidth(80)

        self.lengthLabel = QtGui.QLabel(translate('Rocket', "Length"), self)

        self.lengthInput = ui.createWidget("Gui::InputField")
        self.lengthInput.unit = 'mm'
        self.lengthInput.setFixedWidth(80)

        self.motorGroup = QtGui.QGroupBox(translate('Rocket', "Motor Mount"), self)
        self.motorGroup.setCheckable(True)

        self.overhangLabel = QtGui.QLabel(translate('Rocket', "Overhang"), self)

        self.overhangInput = ui.createWidget("Gui::InputField")
        self.overhangInput.unit = 'mm'
        self.overhangInput.setFixedWidth(80)

        # Motor group
        row = 0
        grid = QGridLayout()

        grid.addWidget(self.overhangLabel, row, 0)
        grid.addWidget(self.overhangInput, row, 1)

        self.motorGroup.setLayout(grid)

        # General paramaters
        row = 0
        grid = QGridLayout()

        grid.addWidget(self.odLabel, row, 0)
        grid.addWidget(self.odInput, row, 1)
        grid.addWidget(self.autoDiameterCheckbox, row, 2)
        row += 1

        grid.addWidget(self.idLabel, row, 0)
        grid.addWidget(self.idInput, row, 1)
        row += 1

        grid.addWidget(self.thicknessLabel, row, 0)
        grid.addWidget(self.thicknessInput, row, 1)
        row += 1

        grid.addWidget(self.lengthLabel, row, 0)
        grid.addWidget(self.lengthInput, row, 1)

        layout = QVBoxLayout()
        layout.addItem(grid)
        layout.addWidget(self.motorGroup)

        self.setLayout(layout)

class TaskPanelRailButton:

    def __init__(self,obj,mode):
        self._obj = obj
        
        self._btForm = _RailButtonDialog()

        self._location = TaskPanelLocation(obj)
        self._locationForm = self._location.getForm()

        self.form = [self._btForm, self._locationForm]
        self._btForm.setWindowIcon(QtGui.QIcon(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_BodyTube.svg"))
        
        self._btForm.odInput.textEdited.connect(self.onOd)
        self._btForm.autoDiameterCheckbox.stateChanged.connect(self.onAutoDiameter)
        self._btForm.idInput.textEdited.connect(self.onId)
        self._btForm.thicknessInput.textEdited.connect(self.onThickness)
        self._btForm.lengthInput.textEdited.connect(self.onLength)

        self._btForm.motorGroup.toggled.connect(self.onMotor)
        self._btForm.overhangInput.textEdited.connect(self.onOverhang)

        self._location.locationChange.connect(self.onLocation)
        
        self.update()
        
        if mode == 0: # fresh created
            self._obj.Proxy.execute(self._obj)  # calculate once 
            FreeCAD.Gui.SendMsgToActiveView("ViewFit")
        
    def transferTo(self):
        "Transfer from the dialog to the object" 
        self._obj.OuterDiameter = self._btForm.odInput.text()
        self._obj.AutoDiameter = self._btForm.autoDiameterCheckbox.isChecked()
        self._obj.Thickness = self._btForm.thicknessInput.text()
        self._obj.Length = self._btForm.lengthInput.text()
        self._obj.MotorMount = self._btForm.motorGroup.isChecked()
        self._obj.Overhang = self._btForm.overhangInput.text()

    def transferFrom(self):
        "Transfer from the object to the dialog"
        self._btForm.odInput.setText(self._obj.OuterDiameter.UserString)
        self._btForm.autoDiameterCheckbox.setChecked(self._obj.AutoDiameter)
        self._btForm.idInput.setText("0.0")
        self._btForm.thicknessInput.setText(self._obj.Thickness.UserString)
        self._btForm.lengthInput.setText(self._obj.Length.UserString)
        self._btForm.motorGroup.setChecked(self._obj.MotorMount)
        self._btForm.overhangInput.setText(self._obj.Overhang.UserString)

        self._setAutoDiameterState()
        self._setIdFromThickness()
        self._setMotorState()

    def setEdited(self):
        try:
            self._obj.Proxy.setEdited()
        except ReferenceError:
            # Object may be deleted
            pass
        
    def onOd(self, value):
        try:
            self._obj.OuterDiameter = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()
        
    def _setAutoDiameterState(self):
        self._btForm.odInput.setEnabled(not self._obj.AutoDiameter)
        self._btForm.autoDiameterCheckbox.setChecked(self._obj.AutoDiameter)

        if self._obj.AutoDiameter:
            self._obj.OuterDiameter = 2.0 * self._obj.Proxy.getRadius()
            self._btForm.odInput.setText(self._obj.OuterDiameter.UserString)

    def onAutoDiameter(self, value):
        self._obj.AutoDiameter = value
        self._setAutoDiameterState()

        self._obj.Proxy.execute(self._obj)
        self.setEdited()

    def _setThicknessFromId(self, value):
        od = float(self._obj.OuterDiameter.Value)
        if od > 0.0:
            id = FreeCAD.Units.Quantity(value).Value
            thickness = (od - id) / 2.0
            self._obj.Thickness = FreeCAD.Units.Quantity(thickness).Value
        else:
            self._obj.Thickness = FreeCAD.Units.Quantity(0.0).Value
        self._btForm.thicknessInput.setText(self._obj.Thickness.UserString)
        
    def onId(self, value):
        try:
            self._setThicknessFromId(value)
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def _setIdFromThickness(self):
        od = float(self._obj.OuterDiameter.Value)
        if od > 0.0:
            id = od - 2.0 * float(self._obj.Thickness)
            self._btForm.idInput.setText(FreeCAD.Units.Quantity(id).UserString)
        else:
            self._btForm.idInput.setText(FreeCAD.Units.Quantity(0.0).UserString)
        
    def onThickness(self, value):
        try:
            self._obj.Thickness = FreeCAD.Units.Quantity(value).Value
            self._setIdFromThickness()
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()
        
    def onLength(self, value):
        try:
            self._obj.Length = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()
        
    def _setMotorState(self):
        if self._obj.Proxy.Type == FEATURE_LAUNCH_LUG:
            self._btForm.overhangInput.setHidden(True)
            self._btForm.motorGroup.setHidden(True)
        else:
            self._btForm.overhangInput.setEnabled(self._obj.MotorMount)
            self._btForm.motorGroup.setChecked(self._obj.MotorMount)

    def onMotor(self, value):
        self._obj.MotorMount = value
        self._setMotorState()

        self._obj.Proxy.execute(self._obj)
        self.setEdited()
        
    def onOverhang(self, value):
        try:
            self._obj.Overhang = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def onLocation(self):
        self._obj.Proxy.execute(self._obj) 
        self.setEdited()
        
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
        self.setEdited()
