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

from PySide import QtGui
from PySide2.QtWidgets import QDialog, QGridLayout, QVBoxLayout

from Ui.TaskPanelDatabase import TaskPanelDatabase
from Ui.TaskPanelLocation import TaskPanelLocation
from Ui.Widgets.MaterialTab import MaterialTab
from Ui.Widgets.CommentTab import CommentTab

from Rocket.Constants import RAIL_BUTTON_ROUND, RAIL_BUTTON_AIRFOIL
from Rocket.Constants import COUNTERSINK_ANGLE_60, COUNTERSINK_ANGLE_82, COUNTERSINK_ANGLE_90, COUNTERSINK_ANGLE_100, \
                            COUNTERSINK_ANGLE_110, COUNTERSINK_ANGLE_120, COUNTERSINK_ANGLE_NONE
from Rocket.Constants import FASTENER_PRESET_6, FASTENER_PRESET_8, FASTENER_PRESET_10, FASTENER_PRESET_1_4
from Rocket.Constants import FASTENER_PRESET_6_HEAD, FASTENER_PRESET_6_SHANK
from Rocket.Constants import FASTENER_PRESET_8_HEAD, FASTENER_PRESET_8_SHANK
from Rocket.Constants import FASTENER_PRESET_10_HEAD, FASTENER_PRESET_10_SHANK
from Rocket.Constants import FASTENER_PRESET_1_4_HEAD, FASTENER_PRESET_1_4_SHANK
from Rocket.Constants import COMPONENT_TYPE_RAILBUTTON

from Rocket.Utilities import _valueOnly

class _RailButtonDialog(QDialog):

    def __init__(self, parent=None):
        super(_RailButtonDialog, self).__init__(parent)

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
        self.setWindowTitle(translate('Rocket', "Rail Button Parameter"))

        self.railButtonTypeLabel = QtGui.QLabel(translate('Rocket', "Rail Button Shape"), self)

        self.railButtonTypeCombo = QtGui.QComboBox(self)
        self.railButtonTypeCombo.addItem(translate('Rocket', RAIL_BUTTON_ROUND), RAIL_BUTTON_ROUND)
        self.railButtonTypeCombo.addItem(translate('Rocket', RAIL_BUTTON_AIRFOIL), RAIL_BUTTON_AIRFOIL)

        # Get the rail button parameters
        self.odLabel = QtGui.QLabel(translate('Rocket', "Outer Diameter"), self)

        self.odInput = ui.createWidget("Gui::InputField")
        self.odInput.unit = 'mm'
        self.odInput.setMinimumWidth(100)

        self.idLabel = QtGui.QLabel(translate('Rocket', "Inner Diameter"), self)

        self.idInput = ui.createWidget("Gui::InputField")
        self.idInput.unit = 'mm'
        self.idInput.setMinimumWidth(100)

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

        self.fastenerGroup = QtGui.QGroupBox(translate('Rocket', "Fastener"), self)
        self.fastenerGroup.setCheckable(True)

        self.countersinkLabel = QtGui.QLabel(translate('Rocket', "Countersink Angle"), self)

        self.countersinkTypeCombo = QtGui.QComboBox(self)
        self.countersinkTypeCombo.addItem(translate('Rocket', COUNTERSINK_ANGLE_NONE), COUNTERSINK_ANGLE_NONE)
        self.countersinkTypeCombo.addItem(translate('Rocket', COUNTERSINK_ANGLE_60), COUNTERSINK_ANGLE_60)
        self.countersinkTypeCombo.addItem(translate('Rocket', COUNTERSINK_ANGLE_82), COUNTERSINK_ANGLE_82)
        self.countersinkTypeCombo.addItem(translate('Rocket', COUNTERSINK_ANGLE_90), COUNTERSINK_ANGLE_90)
        self.countersinkTypeCombo.addItem(translate('Rocket', COUNTERSINK_ANGLE_100), COUNTERSINK_ANGLE_100)
        self.countersinkTypeCombo.addItem(translate('Rocket', COUNTERSINK_ANGLE_110), COUNTERSINK_ANGLE_110)
        self.countersinkTypeCombo.addItem(translate('Rocket', COUNTERSINK_ANGLE_120), COUNTERSINK_ANGLE_120)

        self.headDiameterLabel = QtGui.QLabel(translate('Rocket', "Head Diameter"), self)

        self.headDiameterInput = ui.createWidget("Gui::InputField")
        self.headDiameterInput.unit = 'mm'
        self.headDiameterInput.setMinimumWidth(100)

        self.shankDiameterLabel = QtGui.QLabel(translate('Rocket', "Shank Diameter"), self)

        self.shankDiameterInput = ui.createWidget("Gui::InputField")
        self.shankDiameterInput.unit = 'mm'
        self.shankDiameterInput.setMinimumWidth(100)

        self.fastenerPresetLabel = QtGui.QLabel(translate('Rocket', "Presets"), self)

        self.fastenerPresetCombo = QtGui.QComboBox(self)
        self.fastenerPresetCombo.addItem("", "")
        self.fastenerPresetCombo.addItem(translate('Rocket', FASTENER_PRESET_6), FASTENER_PRESET_6)
        self.fastenerPresetCombo.addItem(translate('Rocket', FASTENER_PRESET_8), FASTENER_PRESET_8)
        self.fastenerPresetCombo.addItem(translate('Rocket', FASTENER_PRESET_10), FASTENER_PRESET_10)
        self.fastenerPresetCombo.addItem(translate('Rocket', FASTENER_PRESET_1_4), FASTENER_PRESET_1_4)

        self.filletGroup = QtGui.QGroupBox(translate('Rocket', "Top Fillet"), self)
        self.filletGroup.setCheckable(True)

        self.filletRadiusLevel = QtGui.QLabel(translate('Rocket', "Radius"), self)

        self.filletRadiusInput = ui.createWidget("Gui::InputField")
        self.filletRadiusInput.unit = 'mm'
        self.filletRadiusInput.setMinimumWidth(100)

        # Fastener group
        row = 0
        grid = QGridLayout()

        grid.addWidget(self.countersinkLabel, row, 0)
        grid.addWidget(self.countersinkTypeCombo, row, 1)
        row += 1

        grid.addWidget(self.headDiameterLabel, row, 0)
        grid.addWidget(self.headDiameterInput, row, 1)
        row += 1

        grid.addWidget(self.shankDiameterLabel, row, 0)
        grid.addWidget(self.shankDiameterInput, row, 1)
        row += 1

        grid.addWidget(self.fastenerPresetLabel, row, 0)
        grid.addWidget(self.fastenerPresetCombo, row, 1)

        self.fastenerGroup.setLayout(grid)

        # Fillet group
        row = 0
        grid = QGridLayout()

        grid.addWidget(self.filletRadiusLevel, row, 0)
        grid.addWidget(self.filletRadiusInput, row, 1)
        row += 1

        self.filletGroup.setLayout(grid)

        # General parameters
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

        layout = QVBoxLayout()
        layout.addItem(grid)
        layout.addWidget(self.fastenerGroup)
        layout.addWidget(self.filletGroup)

        self.tabGeneral.setLayout(layout)

class TaskPanelRailButton:

    def __init__(self,obj,mode):
        self._obj = obj
        
        self._btForm = _RailButtonDialog()
        self._db = TaskPanelDatabase(obj, COMPONENT_TYPE_RAILBUTTON)
        self._dbForm = self._db.getForm()

        self._location = TaskPanelLocation(obj)
        self._locationForm = self._location.getForm()

        self.form = [self._btForm, self._locationForm, self._dbForm]
        self._btForm.setWindowIcon(QtGui.QIcon(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_BodyTube.svg"))
        
        self._btForm.railButtonTypeCombo.currentTextChanged.connect(self.onRailButtonType)
        
        self._btForm.odInput.textEdited.connect(self.onOd)
        self._btForm.idInput.textEdited.connect(self.onId)
        self._btForm.flangeHeightInput.textEdited.connect(self.onFlangeHeight)
        self._btForm.baseHeightInput.textEdited.connect(self.onBaseHeight)
        self._btForm.heightInput.textEdited.connect(self.onHeight)
        self._btForm.lengthInput.textEdited.connect(self.onLength)

        self._btForm.fastenerGroup.toggled.connect(self.onFastener)
        self._btForm.countersinkTypeCombo.currentTextChanged.connect(self.onCountersink)
        self._btForm.headDiameterInput.textEdited.connect(self.onHeadDiameter)
        self._btForm.shankDiameterInput.textEdited.connect(self.onShankDiameter)
        self._btForm.fastenerPresetCombo.currentTextChanged.connect(self.onFastenerPreset)

        self._btForm.filletGroup.toggled.connect(self.onFillet)
        self._btForm.filletRadiusInput.textEdited.connect(self.onFilletRadius)

        self._db.dbLoad.connect(self.onLookup)
        self._location.locationChange.connect(self.onLocation)
        
        self.update()
        
        if mode == 0: # fresh created
            self._obj.Proxy.execute(self._obj)  # calculate once 
            FreeCAD.Gui.SendMsgToActiveView("ViewFit")
        
    def transferTo(self):
        "Transfer from the dialog to the object" 
        self._obj.RailButtonType = str(self._btForm.railButtonTypeCombo.currentData())
        self._obj.Diameter = self._btForm.odInput.text()
        self._obj.InnerDiameter = self._btForm.idInput.text()
        self._obj.FlangeHeight = self._btForm.flangeHeightInput.text()
        self._obj.BaseHeight = self._btForm.baseHeightInput.text()
        self._obj.Height = self._btForm.heightInput.text()
        self._obj.Length = self._btForm.lengthInput.text()

        self._obj.Fastener = self._btForm.fastenerGroup.isChecked()
        self._obj.CountersinkAngle = str(self._btForm.countersinkTypeCombo.currentData())
        self._obj.HeadDiameter = self._btForm.headDiameterInput.text()
        self._obj.ShankDiameter = self._btForm.shankDiameterInput.text()

        self._obj.FilletedTop = self._btForm.filletGroup.isChecked()
        self._obj.FilletRadius = self._btForm.filletRadiusInput.text()

        self._btForm.tabMaterial.transferTo(self._obj)
        self._btForm.tabComment.transferTo(self._obj)

    def transferFrom(self):
        "Transfer from the object to the dialog"
        self._btForm.railButtonTypeCombo.setCurrentIndex(self._btForm.railButtonTypeCombo.findData(self._obj.RailButtonType))
        self._btForm.odInput.setText(self._obj.Diameter.UserString)
        self._btForm.idInput.setText(self._obj.InnerDiameter.UserString)
        self._btForm.flangeHeightInput.setText(self._obj.FlangeHeight.UserString)
        self._btForm.baseHeightInput.setText(self._obj.BaseHeight.UserString)
        self._btForm.heightInput.setText(self._obj.Height.UserString)
        self._btForm.lengthInput.setText(self._obj.Length.UserString)

        self._btForm.fastenerGroup.setChecked(self._obj.Fastener)
        self._btForm.countersinkTypeCombo.setCurrentIndex(self._btForm.countersinkTypeCombo.findData(self._obj.CountersinkAngle))
        self._btForm.headDiameterInput.setText(self._obj.HeadDiameter.UserString)
        self._btForm.shankDiameterInput.setText(self._obj.ShankDiameter.UserString)
        self._btForm.fastenerPresetCombo.setCurrentText("")

        self._btForm.filletGroup.setChecked(self._obj.FilletedTop)
        self._btForm.filletRadiusInput.setText(self._obj.FilletRadius.UserString)

        self._btForm.tabMaterial.transferFrom(self._obj)
        self._btForm.tabComment.transferFrom(self._obj)

        self._setTypeState()
        self._setFastenerState()

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
            self._btForm.lengthInput.setVisible(True)
            self._btForm.lengthLabel.setVisible(True)
        else:
            self._btForm.lengthInput.setEnabled(False)
            self._btForm.lengthInput.setVisible(False)
            self._btForm.lengthLabel.setVisible(False)

    def onRailButtonType(self, value):
        self._obj.RailButtonType = value
        self._setTypeState()

        self._obj.Proxy.execute(self._obj)
        self.setEdited()
        
    def onOd(self, value):
        try:
            self._obj.Diameter = FreeCAD.Units.Quantity(value).Value
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
        
    def onFlangeHeight(self, value):
        try:
            self._obj.FlangeHeight = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()
        
    def onBaseHeight(self, value):
        try:
            self._obj.BaseHeight = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()
        
    def onHeight(self, value):
        try:
            self._obj.Height = FreeCAD.Units.Quantity(value).Value
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

    def onFastener(self, value):
        self._obj.Fastener = value
        self._obj.Proxy.execute(self._obj)
        self.setEdited()

    def _setFastenerState(self):
        value = (self._obj.CountersinkAngle != COUNTERSINK_ANGLE_NONE)
        self._btForm.headDiameterInput.setEnabled(value)

    def _setFasteners(self):
        self._btForm.countersinkTypeCombo.setCurrentIndex(self._btForm.countersinkTypeCombo.findData(self._obj.CountersinkAngle))
        self._btForm.headDiameterInput.setText(self._obj.HeadDiameter.UserString)
        self._btForm.shankDiameterInput.setText(self._obj.ShankDiameter.UserString)
        self._setFastenerState()

    def onCountersink(self, value):
        self._obj.CountersinkAngle = value
        self._btForm.fastenerPresetCombo.setCurrentText("")
        self._setFastenerState()

        self._obj.Proxy.execute(self._obj)
        self.setEdited()
    
    def onHeadDiameter(self, value):
        try:
            self._obj.HeadDiameter = FreeCAD.Units.Quantity(value).Value
            self._btForm.fastenerPresetCombo.setCurrentText("")
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()
    
    def onShankDiameter(self, value):
        try:
            self._obj.ShankDiameter = FreeCAD.Units.Quantity(value).Value
            self._btForm.fastenerPresetCombo.setCurrentText("")
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def preset6(self):
        try:
            self._obj.CountersinkAngle = COUNTERSINK_ANGLE_82
            self._obj.HeadDiameter = FreeCAD.Units.Quantity(FASTENER_PRESET_6_HEAD).Value
            self._obj.ShankDiameter = FreeCAD.Units.Quantity(FASTENER_PRESET_6_SHANK).Value
            self._setFasteners()
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def preset8(self):
        try:
            self._obj.CountersinkAngle = COUNTERSINK_ANGLE_82
            self._obj.HeadDiameter = FreeCAD.Units.Quantity(FASTENER_PRESET_8_HEAD).Value
            self._obj.ShankDiameter = FreeCAD.Units.Quantity(FASTENER_PRESET_8_SHANK).Value
            self._setFasteners()
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def preset10(self):
        try:
            self._obj.CountersinkAngle = COUNTERSINK_ANGLE_82
            self._obj.HeadDiameter = FreeCAD.Units.Quantity(FASTENER_PRESET_10_HEAD).Value
            self._obj.ShankDiameter = FreeCAD.Units.Quantity(FASTENER_PRESET_10_SHANK).Value
            self._setFasteners()
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def preset1_4(self):
        try:
            self._obj.CountersinkAngle = COUNTERSINK_ANGLE_82
            self._obj.HeadDiameter = FreeCAD.Units.Quantity(FASTENER_PRESET_1_4_HEAD).Value
            self._obj.ShankDiameter = FreeCAD.Units.Quantity(FASTENER_PRESET_1_4_SHANK).Value
            self._setFasteners()
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()
    
    def onFastenerPreset(self, value):
        data = self._btForm.fastenerPresetCombo.currentData()
        if data == FASTENER_PRESET_6:
            self.preset6()
        elif data == FASTENER_PRESET_8:
            self.preset8()
        elif data == FASTENER_PRESET_10:
            self.preset10()
        elif data == FASTENER_PRESET_1_4:
            self.preset1_4()

    def onFillet(self, value):
        self._obj.FilletedTop = value
        self._obj.Proxy.execute(self._obj)
        self.setEdited()
    
    def onFilletRadius(self, value):
        try:
            self._obj.FilletRadius = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def getCountersinkAngle(self, angleString):
        angle = int(angleString)
        if angle == 60:
            return COUNTERSINK_ANGLE_60
        if angle == 82:
            return COUNTERSINK_ANGLE_82
        if angle == 90:
            return COUNTERSINK_ANGLE_90
        if angle == 100:
            return COUNTERSINK_ANGLE_100
        if angle == 110:
            return COUNTERSINK_ANGLE_110
        if angle == 120:
            return COUNTERSINK_ANGLE_120
        return COUNTERSINK_ANGLE_NONE

        
    def onLookup(self):
        result = self._db.getLookupResult()

        self._obj.RailButtonType = str(RAIL_BUTTON_ROUND)
        self._obj.Diameter = _valueOnly(result["outer_diameter"], result["outer_diameter_units"])
        self._obj.InnerDiameter = _valueOnly(result["inner_diameter"], result["inner_diameter_units"])
        self._obj.FlangeHeight = _valueOnly(result["flange_height"], result["flange_height_units"])
        self._obj.BaseHeight = _valueOnly(result["base_height"], result["base_height_units"])
        self._obj.Height = _valueOnly(result["height"], result["height_units"])
        self._obj.ShankDiameter =  _valueOnly(result["screw_diameter"], result["screw_diameter_units"])
        self._obj.HeadDiameter =  _valueOnly(result["countersink_diameter"], result["countersink_diameter_units"])
        self._obj.CountersinkAngle =  self.getCountersinkAngle(result["countersink_angle"])
        self._obj.Fastener = (self._obj.ShankDiameter > 0)

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
