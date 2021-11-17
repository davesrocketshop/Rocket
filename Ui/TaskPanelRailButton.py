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

from PySide import QtGui
from PySide2.QtWidgets import QDialog, QGridLayout

from Ui.TaskPanelLocation import TaskPanelLocation

from App.Constants import RAIL_BUTTON_ROUND, RAIL_BUTTON_AIRFOIL

class _RailButtonDialog(QDialog):

    def __init__(self, parent=None):
        super(_RailButtonDialog, self).__init__(parent)

        ui = FreeCADGui.UiLoader()

        # define our window
        self.setGeometry(250, 250, 400, 350)
        self.setWindowTitle(translate('Rocket', "Rail Button Parameter"))

        self.railButtonTypeLabel = QtGui.QLabel(translate('Rocket', "Rail Button Shape"), self)

        self.railButtonTypes = (RAIL_BUTTON_ROUND,
                                RAIL_BUTTON_AIRFOIL)
        self.railButtonTypeCombo = QtGui.QComboBox(self)
        self.railButtonTypeCombo.addItems(self.railButtonTypes)

        # Get the rail button parameters
        self.odLabel = QtGui.QLabel(translate('Rocket', "Outer Diameter"), self)

        self.odInput = ui.createWidget("Gui::InputField")
        self.odInput.unit = 'mm'
        self.odInput.setFixedWidth(80)

        self.idLabel = QtGui.QLabel(translate('Rocket', "Inner Diameter"), self)

        self.idInput = ui.createWidget("Gui::InputField")
        self.idInput.unit = 'mm'
        self.idInput.setFixedWidth(80)

        self.topThicknessLabel = QtGui.QLabel(translate('Rocket', "Top Thickness"), self)

        self.topThicknessInput = ui.createWidget("Gui::InputField")
        self.topThicknessInput.unit = 'mm'
        self.topThicknessInput.setFixedWidth(80)

        self.bottomThicknessLabel = QtGui.QLabel(translate('Rocket', "Bottom Thickness"), self)

        self.bottomThicknessInput = ui.createWidget("Gui::InputField")
        self.bottomThicknessInput.unit = 'mm'
        self.bottomThicknessInput.setFixedWidth(80)

        self.thicknessLabel = QtGui.QLabel(translate('Rocket', "Total Thickness"), self)

        self.thicknessInput = ui.createWidget("Gui::InputField")
        self.thicknessInput.unit = 'mm'
        self.thicknessInput.setFixedWidth(80)

        self.lengthLabel = QtGui.QLabel(translate('Rocket', "Length"), self)

        self.lengthInput = ui.createWidget("Gui::InputField")
        self.lengthInput.unit = 'mm'
        self.lengthInput.setFixedWidth(80)

        # General paramaters
        row = 0
        grid = QGridLayout()

        grid.addWidget(self.railButtonTypeLabel, row, 0)
        grid.addWidget(self.railButtonTypeCombo, row, 1)
        row += 1

        grid.addWidget(self.odLabel, row, 0)
        grid.addWidget(self.odInput, row, 1)
        row += 1

        grid.addWidget(self.idLabel, row, 0)
        grid.addWidget(self.idInput, row, 1)
        row += 1

        grid.addWidget(self.topThicknessLabel, row, 0)
        grid.addWidget(self.topThicknessInput, row, 1)
        row += 1

        grid.addWidget(self.bottomThicknessLabel, row, 0)
        grid.addWidget(self.bottomThicknessInput, row, 1)
        row += 1

        grid.addWidget(self.thicknessLabel, row, 0)
        grid.addWidget(self.thicknessInput, row, 1)
        row += 1

        grid.addWidget(self.lengthLabel, row, 0)
        grid.addWidget(self.lengthInput, row, 1)

        self.setLayout(grid)

class TaskPanelRailButton:

    def __init__(self,obj,mode):
        self._obj = obj
        
        self._btForm = _RailButtonDialog()

        self._location = TaskPanelLocation(obj)
        self._locationForm = self._location.getForm()

        self.form = [self._btForm, self._locationForm]
        self._btForm.setWindowIcon(QtGui.QIcon(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_BodyTube.svg"))
        
        self._btForm.railButtonTypeCombo.currentTextChanged.connect(self.onRailButtonType)
        
        self._btForm.odInput.textEdited.connect(self.onOd)
        self._btForm.idInput.textEdited.connect(self.onId)
        self._btForm.topThicknessInput.textEdited.connect(self.onTopThickness)
        self._btForm.bottomThicknessInput.textEdited.connect(self.onBottomThickness)
        self._btForm.thicknessInput.textEdited.connect(self.onThickness)
        self._btForm.lengthInput.textEdited.connect(self.onLength)

        self._location.locationChange.connect(self.onLocation)
        
        self.update()
        
        if mode == 0: # fresh created
            self._obj.Proxy.execute(self._obj)  # calculate once 
            FreeCAD.Gui.SendMsgToActiveView("ViewFit")
        
    def transferTo(self):
        "Transfer from the dialog to the object" 
        self._obj.RailButtonType = str(self._btForm.railButtonTypeCombo.currentText())
        self._obj.OuterDiameter = self._btForm.odInput.text()
        self._obj.InnerDiameter = self._btForm.idInput.text()
        self._obj.TopThickness = self._btForm.topThicknessInput.text()
        self._obj.BottomThickness = self._btForm.bottomThicknessInput.text()
        self._obj.Thickness = self._btForm.thicknessInput.text()
        self._obj.Length = self._btForm.lengthInput.text()

    def transferFrom(self):
        "Transfer from the object to the dialog"
        self._btForm.railButtonTypeCombo.setCurrentText(self._obj.RailButtonType)
        self._btForm.odInput.setText(self._obj.OuterDiameter.UserString)
        self._btForm.idInput.setText(self._obj.InnerDiameter.UserString)
        self._btForm.topThicknessInput.setText(self._obj.TopThickness.UserString)
        self._btForm.bottomThicknessInput.setText(self._obj.BottomThickness.UserString)
        self._btForm.thicknessInput.setText(self._obj.Thickness.UserString)
        self._btForm.lengthInput.setText(self._obj.Length.UserString)

        self._setTypeState()

    def setEdited(self):
        try:
            self._obj.Proxy.setEdited()
        except ReferenceError:
            # Object may be deleted
            pass
        
    def _setTypeState(self):
        value = self._obj.RailButtonType
        if value == RAIL_BUTTON_AIRFOIL:
            self._btForm.lengthInput.setEnabled(True)
        else:
            self._btForm.lengthInput.setEnabled(False)

    def onRailButtonType(self, value):
        self._obj.RailButtonType = value
        self._setTypeState()

        self._obj.Proxy.execute(self._obj)
        self.setEdited()
        
    def onOd(self, value):
        try:
            self._obj.OuterDiameter = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()
        
    def onId(self, value):
        try:
            self._obj.InnerDiameter = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()
        
    def onTopThickness(self, value):
        try:
            self._obj.TopThickness = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()
        
    def onBottomThickness(self, value):
        try:
            self._obj.BottomThickness = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()
        
    def onThickness(self, value):
        try:
            self._obj.Thickness = FreeCAD.Units.Quantity(value).Value
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
