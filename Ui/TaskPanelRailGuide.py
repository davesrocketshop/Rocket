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

class _RailGuideDialog(QDialog):

    def __init__(self, parent=None):
        super(_RailGuideDialog, self).__init__(parent)

        ui = FreeCADGui.UiLoader()

        # define our window
        self.setGeometry(250, 250, 400, 350)
        self.setWindowTitle(translate('Rocket', "Rail Guide Parameter"))

        # Get the rail guide parameters
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

        grid.addWidget(self.bottomThicknessLabel, row, 0)
        grid.addWidget(self.bottomThicknessInput, row, 1)
        row += 1

        grid.addWidget(self.thicknessLabel, row, 0)
        grid.addWidget(self.thicknessInput, row, 1)
        row += 1

        grid.addWidget(self.lengthLabel, row, 0)
        grid.addWidget(self.lengthInput, row, 1)

        self.setLayout(grid)

class TaskPanelRailGuide:

    def __init__(self,obj,mode):
        self._obj = obj
        
        self._btForm = _RailGuideDialog()

        self._location = TaskPanelLocation(obj)
        self._locationForm = self._location.getForm()

        self.form = [self._btForm, self._locationForm]
        self._btForm.setWindowIcon(QtGui.QIcon(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_BodyTube.svg"))
        
        self._btForm.topWidthInput.textEdited.connect(self.onTopWidth)
        self._btForm.middleWidthInput.textEdited.connect(self.onMiddleWidth)
        self._btForm.baseWidthInput.textEdited.connect(self.onBaseWidth)
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
        self._obj.TopWidth = self._btForm.topWidthInput.text()
        self._obj.MiddleWidth = self._btForm.middleWidthInput.text()
        self._obj.BaseWidth = self._btForm.baseWidthInput.text()
        self._obj.TopThickness = self._btForm.topThicknessInput.text()
        self._obj.BottomThickness = self._btForm.bottomThicknessInput.text()
        self._obj.Thickness = self._btForm.thicknessInput.text()
        self._obj.Length = self._btForm.lengthInput.text()

    def transferFrom(self):
        "Transfer from the object to the dialog"
        self._btForm.topWidthInput.setText(self._obj.TopWidth.UserString)
        self._btForm.middleWidthInput.setText(self._obj.MiddleWidth.UserString)
        self._btForm.baseWidthInput.setText(self._obj.BaseWidth.UserString)
        self._btForm.topThicknessInput.setText(self._obj.TopThickness.UserString)
        self._btForm.bottomThicknessInput.setText(self._obj.BottomThickness.UserString)
        self._btForm.thicknessInput.setText(self._obj.Thickness.UserString)
        self._btForm.lengthInput.setText(self._obj.Length.UserString)

    def setEdited(self):
        try:
            self._obj.Proxy.setEdited()
        except ReferenceError:
            # Object may be deleted
            pass

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
