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
"""Class for drawing rail buttons"""

__title__ = "FreeCAD Rail Buttons"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    

import FreeCAD
import FreeCADGui

from DraftTools import translate

from PySide import QtGui, QtCore
from PySide2.QtWidgets import QDialog, QGridLayout, QVBoxLayout, QSizePolicy

from Ui.TaskPanelLocation import TaskPanelLocation
from Ui.Widgets.MaterialTab import MaterialTab
from Ui.Widgets.CommentTab import CommentTab

from Rocket.Constants import RAIL_GUIDE_BASE_FLAT, RAIL_GUIDE_BASE_CONFORMAL, RAIL_GUIDE_BASE_V

class _RailGuideDialog(QDialog):

    def __init__(self, parent=None):
        super(_RailGuideDialog, self).__init__(parent)

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
        self.setWindowTitle(translate('Rocket', "Rail Guide Parameter"))

        # Get the rail guide parameters
        self.railGuideBaseTypeLabel = QtGui.QLabel(translate('Rocket', "Rail Guide Base"), self)

        self.railGuideBaseTypeCombo = QtGui.QComboBox(self)
        self.railGuideBaseTypeCombo.addItem(translate('Rocket', RAIL_GUIDE_BASE_FLAT), RAIL_GUIDE_BASE_FLAT)
        self.railGuideBaseTypeCombo.addItem(translate('Rocket', RAIL_GUIDE_BASE_CONFORMAL), RAIL_GUIDE_BASE_CONFORMAL)
        self.railGuideBaseTypeCombo.addItem(translate('Rocket', RAIL_GUIDE_BASE_V), RAIL_GUIDE_BASE_V)

        self.flangeWidthLabel = QtGui.QLabel(translate('Rocket', "Flange Width"), self)

        self.flangeWidthInput = ui.createWidget("Gui::InputField")
        self.flangeWidthInput.unit = 'mm'
        self.flangeWidthInput.setMinimumWidth(100)

        self.middleWidthLabel = QtGui.QLabel(translate('Rocket', "Middle Width"), self)

        self.middleWidthInput = ui.createWidget("Gui::InputField")
        self.middleWidthInput.unit = 'mm'
        self.middleWidthInput.setMinimumWidth(100)

        self.baseWidthLabel = QtGui.QLabel(translate('Rocket', "Base Width"), self)

        self.baseWidthInput = ui.createWidget("Gui::InputField")
        self.baseWidthInput.unit = 'mm'
        self.baseWidthInput.setMinimumWidth(100)

        self.flangeHeightLabel = QtGui.QLabel(translate('Rocket', "Flange Height"), self)

        self.flangeHeightInput = ui.createWidget("Gui::InputField")
        self.flangeHeightInput.unit = 'mm'
        self.flangeHeightInput.setMinimumWidth(100)

        self.baseHeightLabel = QtGui.QLabel(translate('Rocket', "Base Height"), self)

        self.baseHeightInput = ui.createWidget("Gui::InputField")
        self.baseHeightInput.unit = 'mm'
        self.baseHeightInput.setMinimumWidth(100)

        self.heightLabel = QtGui.QLabel(translate('Rocket', "Total Height"), self)

        self.heightInput = ui.createWidget("Gui::InputField")
        self.heightInput.unit = 'mm'
        self.heightInput.setMinimumWidth(100)

        self.lengthLabel = QtGui.QLabel(translate('Rocket', "Length"), self)

        self.lengthInput = ui.createWidget("Gui::InputField")
        self.lengthInput.unit = 'mm'
        self.lengthInput.setMinimumWidth(100)

        # Conformal base parameters
        self.diameterLabel = QtGui.QLabel(translate('Rocket', "Body Tube Diameter"), self)

        self.diameterInput = ui.createWidget("Gui::InputField")
        self.diameterInput.unit = 'mm'
        self.diameterInput.setMinimumWidth(100)

        self.autoDiameterCheckbox = QtGui.QCheckBox(translate('Rocket', "auto"), self)
        self.autoDiameterCheckbox.setCheckState(QtCore.Qt.Unchecked)

        # V base parameters
        self.vAngleLabel = QtGui.QLabel(translate('Rocket', "V Angle"), self)

        self.vAngleInput = ui.createWidget("Gui::InputField")
        self.vAngleInput.unit = 'deg'
        self.vAngleInput.setMinimumWidth(100)

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

        # Notch parameters
        self.notchGroup = QtGui.QGroupBox(translate('Rocket', "Notch"), self)
        self.notchGroup.setCheckable(True)

        self.notchWidthLabel = QtGui.QLabel(translate('Rocket', "Width"), self)

        self.notchWidthInput = ui.createWidget("Gui::InputField")
        self.notchWidthInput.unit = 'mm'
        self.notchWidthInput.setMinimumWidth(100)

        self.notchDepthLabel = QtGui.QLabel(translate('Rocket', "Depth"), self)

        self.notchDepthInput = ui.createWidget("Gui::InputField")
        self.notchDepthInput.unit = 'mm'
        self.notchDepthInput.setMinimumWidth(100)

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

        # Notch group
        row = 0
        grid = QGridLayout()

        grid.addWidget(self.notchWidthLabel, row, 0)
        grid.addWidget(self.notchWidthInput, row, 1)
        row += 1

        grid.addWidget(self.notchDepthLabel, row, 0)
        grid.addWidget(self.notchDepthInput, row, 1)
        row += 1

        self.notchGroup.setLayout(grid)

        # General parameters
        row = 0
        grid = QGridLayout()

        grid.addWidget(self.railGuideBaseTypeLabel, row, 0)
        grid.addWidget(self.railGuideBaseTypeCombo, row, 1)
        row += 1

        grid.addWidget(self.flangeWidthLabel, row, 0)
        grid.addWidget(self.flangeWidthInput, row, 1)
        row += 1

        grid.addWidget(self.middleWidthLabel, row, 0)
        grid.addWidget(self.middleWidthInput, row, 1)
        row += 1

        grid.addWidget(self.baseWidthLabel, row, 0)
        grid.addWidget(self.baseWidthInput, row, 1)
        row += 1

        grid.addWidget(self.flangeHeightLabel, row, 0)
        grid.addWidget(self.flangeHeightInput, row, 1)
        row += 1

        grid.addWidget(self.baseHeightLabel, row, 0)
        grid.addWidget(self.baseHeightInput, row, 1)
        row += 1

        grid.addWidget(self.heightLabel, row, 0)
        grid.addWidget(self.heightInput, row, 1)
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

        layout = QVBoxLayout()
        layout.addItem(grid)
        layout.addWidget(self.forwardSweepGroup)
        layout.addWidget(self.aftSweepGroup)
        layout.addWidget(self.notchGroup)
        layout.addItem(QtGui.QSpacerItem(0,0, QSizePolicy.Expanding, QSizePolicy.Expanding))

        self.tabGeneral.setLayout(layout)

class TaskPanelRailGuide:

    def __init__(self,obj,mode):
        self._obj = obj
        
        self._btForm = _RailGuideDialog()

        self._location = TaskPanelLocation(obj)
        self._locationForm = self._location.getForm()

        self.form = [self._btForm, self._locationForm]
        self._btForm.setWindowIcon(QtGui.QIcon(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_BodyTube.svg"))
        
        self._btForm.railGuideBaseTypeCombo.currentTextChanged.connect(self.onRailGuideBaseType)
        
        self._btForm.flangeWidthInput.textEdited.connect(self.onFlangeWidth)
        self._btForm.middleWidthInput.textEdited.connect(self.onMiddleWidth)
        self._btForm.baseWidthInput.textEdited.connect(self.onBaseWidth)
        self._btForm.flangeHeightInput.textEdited.connect(self.onFlangeHeight)
        self._btForm.baseHeightInput.textEdited.connect(self.onBaseHeight)
        self._btForm.heightInput.textEdited.connect(self.onHeight)
        self._btForm.lengthInput.textEdited.connect(self.onLength)
        self._btForm.diameterInput.textEdited.connect(self.onDiameter)
        self._btForm.autoDiameterCheckbox.stateChanged.connect(self.onAutoDiameter)
        self._btForm.vAngleInput.textEdited.connect(self.onVAngle)
        self._btForm.forwardSweepGroup.toggled.connect(self.onForwardSweep)
        self._btForm.forwardSweepInput.textEdited.connect(self.onForwardSweepAngle)
        self._btForm.aftSweepGroup.toggled.connect(self.onAftSweep)
        self._btForm.aftSweepInput.textEdited.connect(self.onAftSweepAngle)
        self._btForm.notchGroup.toggled.connect(self.onNotch)
        self._btForm.notchWidthInput.textEdited.connect(self.onNotchWidth)
        self._btForm.notchDepthInput.textEdited.connect(self.onNotchDepth)

        self._location.locationChange.connect(self.onLocation)
        
        self.update()
        
        if mode == 0: # fresh created
            self.redraw()  # calculate once 
            FreeCAD.Gui.SendMsgToActiveView("ViewFit")
  
    def transferTo(self):
        "Transfer from the dialog to the object" 
        self._obj.RailGuideBaseType = str(self._btForm.railGuideBaseTypeCombo.currentData())
        self._obj.FlangeWidth = self._btForm.flangeWidthInput.text()
        self._obj.MiddleWidth = self._btForm.middleWidthInput.text()
        self._obj.BaseWidth = self._btForm.baseWidthInput.text()
        self._obj.FlangeHeight = self._btForm.flangeHeightInput.text()
        self._obj.BaseHeight = self._btForm.baseHeightInput.text()
        self._obj.Height = self._btForm.heightInput.text()
        self._obj.Length = self._btForm.lengthInput.text()
        self._obj.Diameter = self._btForm.diameterInput.text()
        self._obj.AutoDiameter = self._btForm.autoDiameterCheckbox.isChecked()
        self._obj.VAngle = self._btForm.vAngleInput.text()
        self._obj.ForwardSweep = self._btForm.forwardSweepGroup.isChecked()
        self._obj.ForwardSweepAngle = self._btForm.forwardSweepInput.text()
        self._obj.AftSweep = self._btForm.aftSweepGroup.isChecked()
        self._obj.AftSweepAngle = self._btForm.aftSweepInput.text()
        self._obj.Notch = self._btForm.notchGroup.isChecked()
        self._obj.NotchWidth = self._btForm.notchWidthInput.text()
        self._obj.NotchDepth = self._btForm.notchDepthInput.text()

        self._btForm.tabMaterial.transferTo(self._obj)
        self._btForm.tabComment.transferTo(self._obj)

    def transferFrom(self):
        "Transfer from the object to the dialog"
        self._btForm.railGuideBaseTypeCombo.setCurrentIndex(self._btForm.railGuideBaseTypeCombo.findData(self._obj.RailGuideBaseType))
        self._btForm.flangeWidthInput.setText(self._obj.FlangeWidth.UserString)
        self._btForm.middleWidthInput.setText(self._obj.MiddleWidth.UserString)
        self._btForm.baseWidthInput.setText(self._obj.BaseWidth.UserString)
        self._btForm.flangeHeightInput.setText(self._obj.FlangeHeight.UserString)
        self._btForm.baseHeightInput.setText(self._obj.BaseHeight.UserString)
        self._btForm.heightInput.setText(self._obj.Height.UserString)
        self._btForm.lengthInput.setText(self._obj.Length.UserString)
        self._btForm.diameterInput.setText(self._obj.Diameter.UserString)
        self._btForm.autoDiameterCheckbox.setChecked(self._obj.AutoDiameter)
        self._btForm.vAngleInput.setText(self._obj.VAngle.UserString)
        self._btForm.forwardSweepGroup.setChecked(self._obj.ForwardSweep)
        self._btForm.forwardSweepInput.setText(self._obj.ForwardSweepAngle.UserString)
        self._btForm.aftSweepGroup.setChecked(self._obj.AftSweep)
        self._btForm.aftSweepInput.setText(self._obj.AftSweepAngle.UserString)
        self._btForm.notchGroup.setChecked(self._obj.Notch)
        self._btForm.notchWidthInput.setText(self._obj.NotchWidth.UserString)
        self._btForm.notchDepthInput.setText(self._obj.NotchDepth.UserString)

        self._btForm.tabMaterial.transferFrom(self._obj)
        self._btForm.tabComment.transferFrom(self._obj)

        self._setTypeState()
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

        self.redraw()
        self.setEdited()

    def onFlangeWidth(self, value):
        try:
            self._obj.FlangeWidth = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass
        self.setEdited()
        
    def onMiddleWidth(self, value):
        try:
            self._obj.MiddleWidth = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass
        self.setEdited()
        
    def onBaseWidth(self, value):
        try:
            self._obj.BaseWidth = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass
        self.setEdited()
        
    def onFlangeHeight(self, value):
        try:
            self._obj.FlangeHeight = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass
        self.setEdited()
        
    def onBaseHeight(self, value):
        try:
            self._obj.BaseHeight = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass
        self.setEdited()
        
    def onHeight(self, value):
        try:
            self._obj.Height = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass
        self.setEdited()
        
    def onLength(self, value):
        try:
            self._obj.Length = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass
        self.setEdited()
        
    def onDiameter(self, value):
        try:
            self._obj.Diameter = FreeCAD.Units.Quantity(value).Value
            self.redraw()
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

        self._obj.Proxy.update()
        self._btForm.diameterInput.setText(self._obj.Diameter.UserString)

        self.redraw()
        self.setEdited()
        
    def onVAngle(self, value):
        try:
            self._obj.VAngle = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass
        self.setEdited()
        
    def _setForwardSweepState(self):
        self._btForm.forwardSweepInput.setEnabled(self._obj.ForwardSweep)
        self._btForm.forwardSweepGroup.setChecked(self._obj.ForwardSweep)
        
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
        self._btForm.aftSweepInput.setEnabled(self._obj.AftSweep)
        self._btForm.aftSweepGroup.setChecked(self._obj.AftSweep)
        
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
        
    def onNotch(self, value):
        self._obj.Notch = value
        # self._setAftSweepState()

        self.redraw()
        self.setEdited()
        
    def onNotchWidth(self, value):
        try:
            self._obj.NotchWidth = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass
        self.setEdited()
        
    def onNotchDepth(self, value):
        try:
            self._obj.NotchDepth = FreeCAD.Units.Quantity(value).Value
            self.redraw()
        except ValueError:
            pass
        self.setEdited()

    def onLocation(self):
        self._obj.Proxy.updateChildren()
        self.redraw() 
        self.setEdited()
        
    def getStandardButtons(self):
        return int(QtGui.QDialogButtonBox.Ok) | int(QtGui.QDialogButtonBox.Cancel)| int(QtGui.QDialogButtonBox.Apply)

    def clicked(self,button):
        if button == QtGui.QDialogButtonBox.Apply:
            self.transferTo()
            self.redraw() 
        
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
