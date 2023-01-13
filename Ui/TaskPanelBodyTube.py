# ***************************************************************************
# *   Copyright (c) 2021-2023 David Carter <dcarter@davidcarter.ca>         *
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
from PySide2.QtWidgets import QDialog, QGridLayout, QVBoxLayout

from Ui.TaskPanelDatabase import TaskPanelDatabase
from Ui.TaskPanelLocation import TaskPanelLocation
from App.Constants import COMPONENT_TYPE_BODYTUBE, COMPONENT_TYPE_LAUNCHLUG
from App.Constants import FEATURE_LAUNCH_LUG

from App.Utilities import _valueWithUnits, _valueOnly

class _BodyTubeDialog(QDialog):

    def __init__(self, parent=None):
        super(_BodyTubeDialog, self).__init__(parent)

        ui = FreeCADGui.UiLoader()

        # define our window
        self.setGeometry(250, 250, 400, 350)
        self.setWindowTitle(translate('Rocket', "Body Tube Parameter"))

        # Get the body tube parameters: length, ID, etc...
        self.idLabel = QtGui.QLabel(translate('Rocket', "Inner Diameter"), self)

        self.idInput = ui.createWidget("Gui::InputField")
        self.idInput.unit = 'mm'
        self.idInput.setMinimumWidth(100)

        self.odLabel = QtGui.QLabel(translate('Rocket', "Outer Diameter"), self)

        self.odInput = ui.createWidget("Gui::InputField")
        self.odInput.unit = 'mm'
        self.odInput.setMinimumWidth(100)

        self.autoDiameterCheckbox = QtGui.QCheckBox(translate('Rocket', "auto"), self)
        self.autoDiameterCheckbox.setCheckState(QtCore.Qt.Unchecked)

        self.thicknessLabel = QtGui.QLabel(translate('Rocket', "Wall Thickness"), self)

        self.thicknessInput = ui.createWidget("Gui::InputField")
        self.thicknessInput.unit = 'mm'
        self.thicknessInput.setMinimumWidth(80)

        self.autoThicknessCheckbox = QtGui.QCheckBox(translate('Rocket', "auto"), self)
        self.autoThicknessCheckbox.setCheckState(QtCore.Qt.Unchecked)

        self.lengthLabel = QtGui.QLabel(translate('Rocket', "Length"), self)

        self.lengthInput = ui.createWidget("Gui::InputField")
        self.lengthInput.unit = 'mm'
        self.lengthInput.setMinimumWidth(100)

        self.motorGroup = QtGui.QGroupBox(translate('Rocket', "Motor Mount"), self)
        self.motorGroup.setCheckable(True)

        self.overhangLabel = QtGui.QLabel(translate('Rocket', "Overhang"), self)

        self.overhangInput = ui.createWidget("Gui::InputField")
        self.overhangInput.unit = 'mm'
        self.overhangInput.setMinimumWidth(80)

        # Motor group
        row = 0
        grid = QGridLayout()

        grid.addWidget(self.overhangLabel, row, 0)
        grid.addWidget(self.overhangInput, row, 1)

        self.motorGroup.setLayout(grid)

        # General parameters
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
        grid.addWidget(self.autoThicknessCheckbox, row, 2)
        row += 1

        grid.addWidget(self.lengthLabel, row, 0)
        grid.addWidget(self.lengthInput, row, 1)

        layout = QVBoxLayout()
        layout.addItem(grid)
        layout.addWidget(self.motorGroup)

        self.setLayout(layout)

class TaskPanelBodyTube:

    def __init__(self,obj,mode):
        self._obj = obj
        self._isAssembly = self._obj.Proxy.isRocketAssembly()
        self._motorMount = hasattr(self._obj, "MotorMount")
        
        self._btForm = _BodyTubeDialog()
        if self._obj.Proxy.Type == FEATURE_LAUNCH_LUG:
            self._db = TaskPanelDatabase(obj, COMPONENT_TYPE_LAUNCHLUG)
        else:
            self._db = TaskPanelDatabase(obj, COMPONENT_TYPE_BODYTUBE)
        self._dbForm = self._db.getForm()

        self._location = TaskPanelLocation(obj)
        self._locationForm = self._location.getForm()

        self.form = [self._btForm, self._locationForm, self._dbForm]
        self._btForm.setWindowIcon(QtGui.QIcon(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_BodyTube.svg"))
        
        self._btForm.odInput.textEdited.connect(self.onOd)
        self._btForm.autoDiameterCheckbox.stateChanged.connect(self.onAutoDiameter)
        self._btForm.idInput.textEdited.connect(self.onId)
        self._btForm.thicknessInput.textEdited.connect(self.onThickness)
        self._btForm.autoThicknessCheckbox.stateChanged.connect(self.onAutoThickness)
        self._btForm.lengthInput.textEdited.connect(self.onLength)

        if self._motorMount:
            self._btForm.motorGroup.toggled.connect(self.onMotor)
            self._btForm.overhangInput.textEdited.connect(self.onOverhang)

        self._db.dbLoad.connect(self.onLookup)
        self._location.locationChange.connect(self.onLocation)
        
        self.update()
        
        if mode == 0: # fresh created
            self._obj.Proxy.execute(self._obj)  # calculate once 
            FreeCAD.Gui.SendMsgToActiveView("ViewFit")
        
    def transferTo(self):
        "Transfer from the dialog to the object" 
        self._obj.Proxy.setOuterDiameter(FreeCAD.Units.Quantity(self._btForm.odInput.text()).Value)
        self._obj.Proxy.setOuterDiameterAutomatic(self._btForm.autoDiameterCheckbox.isChecked())
        self._obj.Proxy.setThickness(FreeCAD.Units.Quantity(self._btForm.thicknessInput.text()).Value)
        self._obj.Thickness = self._btForm.autoThicknessCheckbox.isChecked()
        self._obj.Proxy.setLength(FreeCAD.Units.Quantity(self._btForm.lengthInput.text()).Value)
        if self._motorMount:
            self._obj.MotorMount = self._btForm.motorGroup.isChecked()
            self._obj.Overhang = self._btForm.overhangInput.text()

    def transferFrom(self):
        "Transfer from the object to the dialog"
        self._btForm.odInput.setText(self._obj.Diameter.UserString)
        self._btForm.autoDiameterCheckbox.setChecked(self._obj.AutoDiameter)
        self._btForm.idInput.setText("0.0")
        self._btForm.thicknessInput.setText(self._obj.Thickness.UserString)
        self._btForm.autoThicknessCheckbox.setChecked(self._obj.AutoThickness)
        self._btForm.lengthInput.setText(self._obj.Length.UserString)
        if self._motorMount:
            self._btForm.motorGroup.setChecked(self._obj.MotorMount)
            self._btForm.overhangInput.setText(self._obj.Overhang.UserString)

        self._setAutoDiameterState()
        self._setAutoThicknessState()
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
            # self._obj.Diameter = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.setOuterDiameter(FreeCAD.Units.Quantity(value).Value)
            self._setIdFromThickness()
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()
        
    def _setAutoDiameterState(self):
        if self._isAssembly:
            self._btForm.odInput.setEnabled(not self._obj.AutoDiameter)
            self._btForm.autoDiameterCheckbox.setChecked(self._obj.AutoDiameter)
            self._btForm.autoDiameterCheckbox.setEnabled(True)
        else:
            self._btForm.odInput.setEnabled(True)
            self._obj.AutoDiameter = False
            self._btForm.autoDiameterCheckbox.setChecked(self._obj.AutoDiameter)
            self._btForm.autoDiameterCheckbox.setEnabled(False)

        if self._obj.AutoDiameter:
            self._obj.Diameter = self._obj.Proxy.getOuterDiameter()
            self._btForm.odInput.setText(self._obj.Diameter.UserString)
            self._setIdFromThickness()

    def onAutoDiameter(self, value):
        self._obj.Proxy.setOuterDiameterAutomatic(value)
        self._setAutoDiameterState()

        self._obj.Proxy.execute(self._obj)
        self.setEdited()

    def _setThicknessFromId(self, value):
        od = float(self._obj.Diameter.Value)
        if od > 0.0:
            id = FreeCAD.Units.Quantity(value).Value
            thickness = (od - id) / 2.0
            # self._obj.Thickness = FreeCAD.Units.Quantity(thickness).Value
            self._obj.Proxy.setThickness(FreeCAD.Units.Quantity(thickness).Value)
        else:
            # self._obj.Thickness = FreeCAD.Units.Quantity(0.0).Value
            self._obj.Proxy.setThickness(FreeCAD.Units.Quantity(0.0).Value)
        self._btForm.thicknessInput.setText(self._obj.Thickness.UserString)
        
    def onId(self, value):
        try:
            self._setThicknessFromId(value)
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def _setIdFromThickness(self):
        od = float(self._obj.Diameter.Value)
        if od > 0.0:
            id = od - 2.0 * float(self._obj.Thickness)
            self._btForm.idInput.setText(FreeCAD.Units.Quantity(id).UserString)
        else:
            self._btForm.idInput.setText(FreeCAD.Units.Quantity(0.0).UserString)
        
    def onThickness(self, value):
        try:
            self._obj.Proxy.setThickness(FreeCAD.Units.Quantity(value).Value)
            self._setIdFromThickness()
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()
        
    def _setAutoThicknessState(self):
        if self._isAssembly:
            self._btForm.idInput.setEnabled(not self._obj.AutoThickness)
            self._btForm.thicknessInput.setEnabled(not self._obj.AutoThickness)
            self._btForm.autoThicknessCheckbox.setChecked(self._obj.AutoThickness)
            self._btForm.autoThicknessCheckbox.setEnabled(True)
        else:
            self._btForm.idInput.setEnabled(True)
            self._btForm.thicknessInput.setEnabled(True)
            self._obj.AutoThickness = False
            self._btForm.autoThicknessCheckbox.setChecked(self._obj.AutoThickness)
            self._btForm.autoThicknessCheckbox.setEnabled(False)

        if self._obj.AutoThickness:
            self._obj.Proxy.getInnerDiameter()  # Do the autosizing calcs
            self._btForm.thicknessInput.setText(self._obj.Thickness.UserString)
            self._setIdFromThickness()

    def onAutoThickness(self, value):
        self._obj.AutoThickness = value
        self._setAutoThicknessState()

        self._obj.Proxy.execute(self._obj)
        self.setEdited()
        
    def onLength(self, value):
        try:
            self._obj.Proxy.setLength(FreeCAD.Units.Quantity(value).Value)
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()
        
    def _setMotorState(self):
        if not self._motorMount: #self._obj.Proxy.Type == FEATURE_LAUNCH_LUG:
            self._btForm.overhangInput.setHidden(True)
            self._btForm.motorGroup.setHidden(True)
        else:
            if self._isAssembly:
                self._btForm.motorGroup.setEnabled(True)
                self._btForm.overhangInput.setEnabled(self._obj.MotorMount)
                self._btForm.motorGroup.setChecked(self._obj.MotorMount)
            else:
                self._obj.MotorMount = False
                self._btForm.motorGroup.setEnabled(False)
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
        
    def onLookup(self):
        result = self._db.getLookupResult()

        diameter = _valueOnly(result["inner_diameter"], result["inner_diameter_units"])
        self._obj.Proxy.setOuterDiameter(_valueOnly(result["outer_diameter"], result["outer_diameter_units"]))
        self._obj.Proxy.setThickness((self._obj.Diameter.Value - diameter) / 2.0)
        self._obj.Proxy.setLength(_valueOnly(result["length"], result["length_units"]))

        self.update()
        self._obj.Proxy.execute(self._obj) 
        self.setEdited()

    def onLocation(self):
        self._obj.Proxy.updateChildren()
        self._obj.Proxy.execute(self._obj) 
        self.setEdited()
        
    def getStandardButtons(self):
        return int(QtGui.QDialogButtonBox.Ok) | int(QtGui.QDialogButtonBox.Cancel)| int(QtGui.QDialogButtonBox.Apply)

    def clicked(self,button):
        if button == QtGui.QDialogButtonBox.Apply:
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
