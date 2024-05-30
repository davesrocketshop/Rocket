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
"""Class for drawing nose cones"""

__title__ = "FreeCAD Nose Cones"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    

import FreeCAD
import FreeCADGui
import Materials

from DraftTools import translate

from PySide import QtGui
from PySide2.QtWidgets import QDialog, QGridLayout, QVBoxLayout

from Ui.TaskPanelDatabase import TaskPanelDatabase
from Ui.TaskPanelLocation import TaskPanelLocation
from Ui.Widgets.MaterialTab import MaterialTab
from Ui.Widgets.CommentTab import CommentTab

from Rocket.Constants import COMPONENT_TYPE_LAUNCHLUG

from Rocket.Utilities import _valueOnly

class _LaunchLugDialog(QDialog):

    def __init__(self, parent=None):
        super(_LaunchLugDialog, self).__init__(parent)

        self.tabWidget = QtGui.QTabWidget()
        self.tabGeneral = QtGui.QWidget()
        self.tabMaterial = MaterialTab()
        self.tabComment = CommentTab()
        self.tabWidget.addTab(self.tabGeneral, translate('Rocket', "General"))
        self.tabWidget.addTab(self.tabMaterial, translate('Rocket', "Material"))
        self.tabWidget.addTab(self.tabComment, translate('Rocket', "Comment"))

        layout = QVBoxLayout()
        layout.addWidget(self.tabWidget)
        self.setLayout(layout)

        self.setTabGeneral()

    def setTabGeneral(self):

        ui = FreeCADGui.UiLoader()

        # define our window
        self.setGeometry(250, 250, 400, 350)
        self.setWindowTitle(translate('Rocket', "Launch Lug Parameter"))

        # Get the body tube parameters: length, ID, etc...
        self.idLabel = QtGui.QLabel(translate('Rocket', "Inner Diameter"), self)

        self.idInput = ui.createWidget("Gui::InputField")
        self.idInput.unit = 'mm'
        self.idInput.setMinimumWidth(100)

        self.odLabel = QtGui.QLabel(translate('Rocket', "Outer Diameter"), self)

        self.odInput = ui.createWidget("Gui::InputField")
        self.odInput.unit = 'mm'
        self.odInput.setMinimumWidth(100)

        self.thicknessLabel = QtGui.QLabel(translate('Rocket', "Wall Thickness"), self)

        self.thicknessInput = ui.createWidget("Gui::InputField")
        self.thicknessInput.unit = 'mm'
        self.thicknessInput.setMinimumWidth(80)

        self.lengthLabel = QtGui.QLabel(translate('Rocket', "Length"), self)

        self.lengthInput = ui.createWidget("Gui::InputField")
        self.lengthInput.unit = 'mm'
        self.lengthInput.setMinimumWidth(100)

        # Sweep parameters
        self.forwardSweepGroup = QtGui.QGroupBox(translate('Rocket', "Forward Sweep"), self)
        self.forwardSweepGroup.setCheckable(True)

        self.forwardSweepLabel = QtGui.QLabel(translate('Rocket', "Sweep Angle"), self)

        self.forwardSweepInput = ui.createWidget("Gui::InputField")
        self.forwardSweepInput.unit = 'deg'
        self.forwardSweepInput.setMinimumWidth(100)

        self.aftSweepGroup = QtGui.QGroupBox(translate('Rocket', "Aft Sweep"), self)
        self.aftSweepGroup.setCheckable(True)

        self.aftSweepLabel = QtGui.QLabel(translate('Rocket', "Sweep Angle"), self)

        self.aftSweepInput = ui.createWidget("Gui::InputField")
        self.aftSweepInput.unit = 'deg'
        self.aftSweepInput.setMinimumWidth(100)

        # Forward sweep group
        row = 0
        grid = QGridLayout()

        grid.addWidget(self.forwardSweepLabel, row, 0)
        grid.addWidget(self.forwardSweepInput, row, 1)
        row += 1

        self.forwardSweepGroup.setLayout(grid)

        # Aft sweep group
        row = 0
        grid = QGridLayout()

        grid.addWidget(self.aftSweepLabel, row, 0)
        grid.addWidget(self.aftSweepInput, row, 1)
        row += 1

        self.aftSweepGroup.setLayout(grid)

        # General parameters
        row = 0
        grid = QGridLayout()

        grid.addWidget(self.odLabel, row, 0)
        grid.addWidget(self.odInput, row, 1)
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
        layout.addWidget(self.forwardSweepGroup)
        layout.addWidget(self.aftSweepGroup)

        self.tabGeneral.setLayout(layout)

class TaskPanelLaunchLug:

    def __init__(self,obj,mode):
        self._obj = obj
        
        self._lugForm = _LaunchLugDialog()
        self._db = TaskPanelDatabase(obj, COMPONENT_TYPE_LAUNCHLUG)
        self._dbForm = self._db.getForm()

        self._location = TaskPanelLocation(obj)
        self._locationForm = self._location.getForm()

        self.form = [self._lugForm, self._locationForm, self._dbForm]
        self._lugForm.setWindowIcon(QtGui.QIcon(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_LaunchLug.svg"))
        
        self._lugForm.odInput.textEdited.connect(self.onOd)
        self._lugForm.idInput.textEdited.connect(self.onId)
        self._lugForm.thicknessInput.textEdited.connect(self.onThickness)
        self._lugForm.lengthInput.textEdited.connect(self.onLength)
        self._lugForm.forwardSweepGroup.toggled.connect(self.onForwardSweep)
        self._lugForm.forwardSweepInput.textEdited.connect(self.onForwardSweepAngle)
        self._lugForm.aftSweepGroup.toggled.connect(self.onAftSweep)
        self._lugForm.aftSweepInput.textEdited.connect(self.onAftSweepAngle)

        self._db.dbLoad.connect(self.onLookup)
        self._location.locationChange.connect(self.onLocation)
        
        self.update()
        
        if mode == 0: # fresh created
            self._obj.Proxy.execute(self._obj)  # calculate once 
            FreeCAD.Gui.SendMsgToActiveView("ViewFit")
        
    def transferTo(self):
        "Transfer from the dialog to the object" 
        self._obj.Proxy.setOuterDiameter(FreeCAD.Units.Quantity(self._lugForm.odInput.text()).Value)
        self._obj.Proxy.setThickness(FreeCAD.Units.Quantity(self._lugForm.thicknessInput.text()).Value)
        self._obj.Proxy.setLength(FreeCAD.Units.Quantity(self._lugForm.lengthInput.text()).Value)
        self._obj.ForwardSweep = self._lugForm.forwardSweepGroup.isChecked()
        self._obj.ForwardSweepAngle = self._lugForm.forwardSweepInput.text()
        self._obj.AftSweep = self._lugForm.aftSweepGroup.isChecked()
        self._obj.AftSweepAngle = self._lugForm.aftSweepInput.text()

        self._lugForm.tabMaterial.transferTo(self._obj)
        self._lugForm.tabComment.transferTo(self._obj)

    def transferFrom(self):
        "Transfer from the object to the dialog"
        self._lugForm.odInput.setText(self._obj.Diameter.UserString)
        self._lugForm.idInput.setText("0.0")
        self._lugForm.thicknessInput.setText(self._obj.Thickness.UserString)
        self._lugForm.lengthInput.setText(self._obj.Length.UserString)
        self._lugForm.forwardSweepGroup.setChecked(self._obj.ForwardSweep)
        self._lugForm.forwardSweepInput.setText(self._obj.ForwardSweepAngle.UserString)
        self._lugForm.aftSweepGroup.setChecked(self._obj.AftSweep)
        self._lugForm.aftSweepInput.setText(self._obj.AftSweepAngle.UserString)

        self._lugForm.tabMaterial.transferFrom(self._obj)
        self._lugForm.tabComment.transferFrom(self._obj)

        self._setIdFromThickness()
        self._setForwardSweepState()
        self._setAftSweepState()

    def redraw(self):
        self._obj.Proxy.execute(self._obj)

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
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
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
        self._lugForm.thicknessInput.setText(self._obj.Thickness.UserString)
        
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
            self._lugForm.idInput.setText(FreeCAD.Units.Quantity(id).UserString)
        else:
            self._lugForm.idInput.setText(FreeCAD.Units.Quantity(0.0).UserString)
        
    def onThickness(self, value):
        try:
            # self._obj.Thickness = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.setThickness(FreeCAD.Units.Quantity(value).Value)
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
        
    def onLookup(self):
        result = self._db.getLookupResult()

        diameter = _valueOnly(result["inner_diameter"], result["inner_diameter_units"])
        self._obj.Proxy.setOuterDiameter(_valueOnly(result["outer_diameter"], result["outer_diameter_units"]))
        self._obj.Proxy.setThickness((self._obj.Diameter.Value - diameter) / 2.0)
        self._obj.Proxy.setLength(_valueOnly(result["length"], result["length_units"]))
        self._obj.ShapeMaterial = Materials.MaterialManager().getMaterial(result["uuid"])

        self.update()
        self._obj.Proxy.execute(self._obj) 
        self.setEdited()

    def onLocation(self):
        self._obj.Proxy.updateChildren()
        self._obj.Proxy.execute(self._obj) 
        self.setEdited()
        
    def _setForwardSweepState(self):
        self._lugForm.forwardSweepInput.setEnabled(self._obj.ForwardSweep)
        self._lugForm.forwardSweepGroup.setChecked(self._obj.ForwardSweep)
        
    def onForwardSweep(self, value):
        self._obj.ForwardSweep = value
        self._setForwardSweepState()

        self.redraw()
        self.setEdited()
        
    def onForwardSweepAngle(self, value):
        try:
            self._obj.ForwardSweepAngle = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass
        self.setEdited()
        
    def _setAftSweepState(self):
        self._lugForm.aftSweepInput.setEnabled(self._obj.AftSweep)
        self._lugForm.aftSweepGroup.setChecked(self._obj.AftSweep)
        
    def onAftSweep(self, value):
        self._obj.AftSweep = value
        self._setAftSweepState()

        self.redraw()
        self.setEdited()
        
    def onAftSweepAngle(self, value):
        try:
            self._obj.AftSweepAngle = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass
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
