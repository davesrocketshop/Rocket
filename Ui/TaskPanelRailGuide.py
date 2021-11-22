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
from PySide2.QtWidgets import QDialog, QGridLayout

from Ui.TaskPanelLocation import TaskPanelLocation

from App.Constants import RAIL_GUIDE_BASE_FLAT, RAIL_GUIDE_BASE_CONFORMAL, RAIL_GUIDE_BASE_V

class _RailGuideDialog(QDialog):

    def __init__(self, parent=None):
        super(_RailGuideDialog, self).__init__(parent)

        ui = FreeCADGui.UiLoader()

        # define our window
        self.setGeometry(250, 250, 400, 350)
        self.setWindowTitle(translate('Rocket', "Rail Guide Parameter"))

        # Get the rail guide parameters
        self.railGuideBaseTypeLabel = QtGui.QLabel(translate('Rocket', "Rail Guide Base"), self)

        self.railGuideBaseTypes = (RAIL_GUIDE_BASE_FLAT,
                                RAIL_GUIDE_BASE_CONFORMAL,
                                RAIL_GUIDE_BASE_V)
        self.railGuideBaseTypeCombo = QtGui.QComboBox(self)
        self.railGuideBaseTypeCombo.addItems(self.railGuideBaseTypes)

        self.topWidthLabel = QtGui.QLabel(translate('Rocket', "Top Width"), self)

        self.topWidthInput = ui.createWidget("Gui::InputField")
        self.topWidthInput.unit = 'mm'
        self.topWidthInput.setFixedWidth(80)

        self.middleWidthLabel = QtGui.QLabel(translate('Rocket', "Middle Width"), self)

        self.middleWidthInput = ui.createWidget("Gui::InputField")
        self.middleWidthInput.unit = 'mm'
        self.middleWidthInput.setFixedWidth(80)

        self.baseWidthLabel = QtGui.QLabel(translate('Rocket', "Base Width"), self)

        self.baseWidthInput = ui.createWidget("Gui::InputField")
        self.baseWidthInput.unit = 'mm'
        self.baseWidthInput.setFixedWidth(80)

        self.topThicknessLabel = QtGui.QLabel(translate('Rocket', "Top Thickness"), self)

        self.topThicknessInput = ui.createWidget("Gui::InputField")
        self.topThicknessInput.unit = 'mm'
        self.topThicknessInput.setFixedWidth(80)

        self.baseThicknessLabel = QtGui.QLabel(translate('Rocket', "Base Thickness"), self)

        self.baseThicknessInput = ui.createWidget("Gui::InputField")
        self.baseThicknessInput.unit = 'mm'
        self.baseThicknessInput.setFixedWidth(80)

        self.thicknessLabel = QtGui.QLabel(translate('Rocket', "Total Thickness"), self)

        self.thicknessInput = ui.createWidget("Gui::InputField")
        self.thicknessInput.unit = 'mm'
        self.thicknessInput.setFixedWidth(80)

        self.lengthLabel = QtGui.QLabel(translate('Rocket', "Length"), self)

        self.lengthInput = ui.createWidget("Gui::InputField")
        self.lengthInput.unit = 'mm'
        self.lengthInput.setFixedWidth(80)

        # Conformal base parameters
        self.diameterLabel = QtGui.QLabel(translate('Rocket', "Body Tube Diameter"), self)

        self.diameterInput = ui.createWidget("Gui::InputField")
        self.diameterInput.unit = 'mm'
        self.diameterInput.setFixedWidth(80)

        self.autoDiameterCheckbox = QtGui.QCheckBox(translate('Rocket', "auto"), self)
        self.autoDiameterCheckbox.setCheckState(QtCore.Qt.Unchecked)

        # V base parameters
        self.vAngleLabel = QtGui.QLabel(translate('Rocket', "V Angle"), self)

        self.vAngleInput = ui.createWidget("Gui::InputField")
        self.vAngleInput.unit = 'deg'
        self.vAngleInput.setFixedWidth(80)

        # General paramaters
        row = 0
        grid = QGridLayout()

        grid.addWidget(self.railGuideBaseTypeLabel, row, 0)
        grid.addWidget(self.railGuideBaseTypeCombo, row, 1)
        row += 1

        grid.addWidget(self.topWidthLabel, row, 0)
        grid.addWidget(self.topWidthInput, row, 1)
        row += 1

        grid.addWidget(self.middleWidthLabel, row, 0)
        grid.addWidget(self.middleWidthInput, row, 1)
        row += 1

        grid.addWidget(self.baseWidthLabel, row, 0)
        grid.addWidget(self.baseWidthInput, row, 1)
        row += 1

        grid.addWidget(self.topThicknessLabel, row, 0)
        grid.addWidget(self.topThicknessInput, row, 1)
        row += 1

        grid.addWidget(self.baseThicknessLabel, row, 0)
        grid.addWidget(self.baseThicknessInput, row, 1)
        row += 1

        grid.addWidget(self.thicknessLabel, row, 0)
        grid.addWidget(self.thicknessInput, row, 1)
        row += 1

        grid.addWidget(self.lengthLabel, row, 0)
        grid.addWidget(self.lengthInput, row, 1)
        row += 1

        grid.addWidget(self.diameterLabel, row, 0)
        grid.addWidget(self.diameterInput, row, 1)
        row += 1
        grid.addWidget(self.autoDiameterCheckbox, row, 1)
        row += 1

        grid.addWidget(self.vAngleLabel, row, 0)
        grid.addWidget(self.vAngleInput, row, 1)
        row += 1

        self.setLayout(grid)

class TaskPanelRailGuide:

    def __init__(self,obj,mode):
        self._obj = obj
        
        self._btForm = _RailGuideDialog()

        self._location = TaskPanelLocation(obj)
        self._locationForm = self._location.getForm()

        self.form = [self._btForm, self._locationForm]
        self._btForm.setWindowIcon(QtGui.QIcon(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_BodyTube.svg"))
        
        self._btForm.railGuideBaseTypeCombo.currentTextChanged.connect(self.onRailGuideBaseType)
        
        self._btForm.topWidthInput.textEdited.connect(self.onTopWidth)
        self._btForm.middleWidthInput.textEdited.connect(self.onMiddleWidth)
        self._btForm.baseWidthInput.textEdited.connect(self.onBaseWidth)
        self._btForm.topThicknessInput.textEdited.connect(self.onTopThickness)
        self._btForm.baseThicknessInput.textEdited.connect(self.onBaseThickness)
        self._btForm.thicknessInput.textEdited.connect(self.onThickness)
        self._btForm.lengthInput.textEdited.connect(self.onLength)
        self._btForm.diameterInput.textEdited.connect(self.onDiameter)
        self._btForm.autoDiameterCheckbox.stateChanged.connect(self.onAutoDiameter)
        self._btForm.vAngleInput.textEdited.connect(self.onVAngle)

        self._location.locationChange.connect(self.onLocation)
        
        self.update()
        
        if mode == 0: # fresh created
            self._obj.Proxy.execute(self._obj)  # calculate once 
            FreeCAD.Gui.SendMsgToActiveView("ViewFit")
  
    def transferTo(self):
        "Transfer from the dialog to the object" 
        self._obj.RailGuideBaseType = str(self._btForm.railGuideBaseTypeCombo.currentText())
        self._obj.TopWidth = self._btForm.topWidthInput.text()
        self._obj.MiddleWidth = self._btForm.middleWidthInput.text()
        self._obj.BaseWidth = self._btForm.baseWidthInput.text()
        self._obj.TopThickness = self._btForm.topThicknessInput.text()
        self._obj.BaseThickness = self._btForm.baseThicknessInput.text()
        self._obj.Thickness = self._btForm.thicknessInput.text()
        self._obj.Length = self._btForm.lengthInput.text()
        self._obj.Diameter = self._btForm.diameterInput.text()
        self._obj.AutoDiameter = self._btForm.autoDiameterCheckbox.isChecked()
        self._obj.VAngle = self._btForm.vAngleInput.text()

    def transferFrom(self):
        "Transfer from the object to the dialog"
        self._btForm.railGuideBaseTypeCombo.setCurrentText(self._obj.RailGuideBaseType)
        self._btForm.topWidthInput.setText(self._obj.TopWidth.UserString)
        self._btForm.middleWidthInput.setText(self._obj.MiddleWidth.UserString)
        self._btForm.baseWidthInput.setText(self._obj.BaseWidth.UserString)
        self._btForm.topThicknessInput.setText(self._obj.TopThickness.UserString)
        self._btForm.baseThicknessInput.setText(self._obj.BaseThickness.UserString)
        self._btForm.thicknessInput.setText(self._obj.Thickness.UserString)
        self._btForm.lengthInput.setText(self._obj.Length.UserString)
        self._btForm.diameterInput.setText(self._obj.Diameter.UserString)
        self._btForm.autoDiameterCheckbox.setChecked(self._obj.AutoDiameter)
        self._btForm.vAngleInput.setText(self._obj.VAngle.UserString)

        self._setTypeState()

    def setEdited(self):
        try:
            self._obj.Proxy.setEdited()
        except ReferenceError:
            # Object may be deleted
            pass
        
    def _setTypeState(self):
        value = self._obj.RailGuideBaseType

        if value == RAIL_GUIDE_BASE_FLAT:
            self._btForm.diameterLabel.setVisible(False)
            self._btForm.diameterInput.setVisible(False)
            self._btForm.autoDiameterCheckbox.setVisible(False)
            self._btForm.vAngleLabel.setVisible(False)
            self._btForm.vAngleInput.setVisible(False)
        elif value == RAIL_GUIDE_BASE_CONFORMAL:
            self._btForm.diameterLabel.setVisible(True)
            self._btForm.diameterInput.setVisible(True)
            self._btForm.autoDiameterCheckbox.setVisible(True)
            self._btForm.vAngleLabel.setVisible(False)
            self._btForm.vAngleInput.setVisible(False)
        else:
            self._btForm.diameterLabel.setVisible(False)
            self._btForm.diameterInput.setVisible(False)
            self._btForm.autoDiameterCheckbox.setVisible(False)
            self._btForm.vAngleLabel.setVisible(True)
            self._btForm.vAngleInput.setVisible(True)

    def onRailGuideBaseType(self, value):
        self._obj.RailGuideBaseType = value
        self._setTypeState()

        self._obj.Proxy.execute(self._obj)
        self.setEdited()

    def onTopWidth(self, value):
        try:
            self._obj.TopWidth = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()
        
    def onMiddleWidth(self, value):
        try:
            self._obj.MiddleWidth = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()
        
    def onBaseWidth(self, value):
        try:
            self._obj.BaseWidth = FreeCAD.Units.Quantity(value).Value
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
        
    def onBaseThickness(self, value):
        try:
            self._obj.BaseThickness = FreeCAD.Units.Quantity(value).Value
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
        
    def onDiameter(self, value):
        try:
            self._obj.Diameter = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()
        
    def _setAutoDiameterState(self):
        self._btForm.diameterInput.setEnabled(not self._obj.AutoDiameter)
        self._btForm.autoDiameterCheckbox.setChecked(self._obj.AutoDiameter)

        # if self._obj.AutoDiameter:
        #     self._obj.Diameter = 2.0 * self._obj.Proxy.getRadius()
        #     self._btForm.diameterInput.setText(self._obj.Diameter.UserString)

    def onAutoDiameter(self, value):
        self._obj.AutoDiameter = value
        self._setAutoDiameterState()

        self._obj.Proxy.execute(self._obj)
        self.setEdited()
        
    def onVAngle(self, value):
        try:
            self._obj.VAngle = FreeCAD.Units.Quantity(value).Value
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
