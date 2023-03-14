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
from PySide2.QtWidgets import QDialog, QGridLayout, QVBoxLayout, QTextEdit

from Ui.TaskPanelLocation import TaskPanelLocation

from Rocket.Constants import RAIL_BUTTON_ROUND, RAIL_BUTTON_AIRFOIL
from Rocket.Constants import CONTERSINK_ANGLE_60, CONTERSINK_ANGLE_82, CONTERSINK_ANGLE_90, CONTERSINK_ANGLE_100, \
                            CONTERSINK_ANGLE_110, CONTERSINK_ANGLE_120
from Rocket.Constants import FASTENER_PRESET_6, FASTENER_PRESET_8, FASTENER_PRESET_10, FASTENER_PRESET_1_4
from Rocket.Constants import FASTENER_PRESET_6_HEAD, FASTENER_PRESET_6_SHANK
from Rocket.Constants import FASTENER_PRESET_8_HEAD, FASTENER_PRESET_8_SHANK
from Rocket.Constants import FASTENER_PRESET_10_HEAD, FASTENER_PRESET_10_SHANK
from Rocket.Constants import FASTENER_PRESET_1_4_HEAD, FASTENER_PRESET_1_4_SHANK



class _RailButtonDialog(QDialog):

    def __init__(self, parent=None):
        super(_RailButtonDialog, self).__init__(parent)

        self.tabWidget = QtGui.QTabWidget()
        self.tabGeneral = QtGui.QWidget()
        self.tabComment = QtGui.QWidget()
        self.tabWidget.addTab(self.tabGeneral, translate('Rocket', "General"))
        self.tabWidget.addTab(self.tabComment, translate('Rocket', "Comment"))

        layout = QVBoxLayout()
        layout.addWidget(self.tabWidget)
        self.setLayout(layout)

        self.setTabGeneral()
        self.setTabComment()

    def setTabGeneral(self):

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
        self.odInput.setMinimumWidth(100)

        self.idLabel = QtGui.QLabel(translate('Rocket', "Inner Diameter"), self)

        self.idInput = ui.createWidget("Gui::InputField")
        self.idInput.unit = 'mm'
        self.idInput.setMinimumWidth(100)

        self.topThicknessLabel = QtGui.QLabel(translate('Rocket', "Top Thickness"), self)

        self.topThicknessInput = ui.createWidget("Gui::InputField")
        self.topThicknessInput.unit = 'mm'
        self.topThicknessInput.setMinimumWidth(100)

        self.baseThicknessLabel = QtGui.QLabel(translate('Rocket', "Base Thickness"), self)

        self.baseThicknessInput = ui.createWidget("Gui::InputField")
        self.baseThicknessInput.unit = 'mm'
        self.baseThicknessInput.setMinimumWidth(100)

        self.thicknessLabel = QtGui.QLabel(translate('Rocket', "Total Thickness"), self)

        self.thicknessInput = ui.createWidget("Gui::InputField")
        self.thicknessInput.unit = 'mm'
        self.thicknessInput.setMinimumWidth(100)

        self.lengthLabel = QtGui.QLabel(translate('Rocket', "Length"), self)

        self.lengthInput = ui.createWidget("Gui::InputField")
        self.lengthInput.unit = 'mm'
        self.lengthInput.setMinimumWidth(100)

        self.fastenerGroup = QtGui.QGroupBox(translate('Rocket', "Fastener"), self)
        self.fastenerGroup.setCheckable(True)

        self.countersinkLabel = QtGui.QLabel(translate('Rocket', "Countersink Angle"), self)

        self.countersinkTypes = (CONTERSINK_ANGLE_60,
                                    CONTERSINK_ANGLE_82,
                                    CONTERSINK_ANGLE_90,
                                    CONTERSINK_ANGLE_100,
                                    CONTERSINK_ANGLE_110,
                                    CONTERSINK_ANGLE_120)
        self.countersinkTypeCombo = QtGui.QComboBox(self)
        self.countersinkTypeCombo.addItems(self.countersinkTypes)

        self.headDiameterLabel = QtGui.QLabel(translate('Rocket', "Head Diameter"), self)

        self.headDiameterInput = ui.createWidget("Gui::InputField")
        self.headDiameterInput.unit = 'mm'
        self.headDiameterInput.setMinimumWidth(100)

        self.shankDiameterLabel = QtGui.QLabel(translate('Rocket', "Shank Diameter"), self)

        self.shankDiameterInput = ui.createWidget("Gui::InputField")
        self.shankDiameterInput.unit = 'mm'
        self.shankDiameterInput.setMinimumWidth(100)

        self.fastenerPresetLabel = QtGui.QLabel(translate('Rocket', "Presets"), self)

        self.fastenerPresetTypes = ("",
                                    FASTENER_PRESET_6,
                                    FASTENER_PRESET_8,
                                    FASTENER_PRESET_10,
                                    FASTENER_PRESET_1_4)
        self.fastenerPresetCombo = QtGui.QComboBox(self)
        self.fastenerPresetCombo.addItems(self.fastenerPresetTypes)

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

        layout = QVBoxLayout()
        layout.addItem(grid)
        layout.addWidget(self.fastenerGroup)
        layout.addWidget(self.filletGroup)

        self.tabGeneral.setLayout(layout)

    def setTabComment(self):

        ui = FreeCADGui.UiLoader()

        self.commentLabel = QtGui.QLabel(translate('Rocket', "Comment"), self)

        self.commentInput = QTextEdit()

        layout = QVBoxLayout()
        layout.addWidget(self.commentLabel)
        layout.addWidget(self.commentInput)

        self.tabComment.setLayout(layout)

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
        self._btForm.baseThicknessInput.textEdited.connect(self.onBaseThickness)
        self._btForm.thicknessInput.textEdited.connect(self.onThickness)
        self._btForm.lengthInput.textEdited.connect(self.onLength)

        self._btForm.fastenerGroup.toggled.connect(self.onFastener)
        self._btForm.countersinkTypeCombo.currentTextChanged.connect(self.onCountersink)
        self._btForm.headDiameterInput.textEdited.connect(self.onHeadDiameter)
        self._btForm.shankDiameterInput.textEdited.connect(self.onShankDiameter)
        self._btForm.fastenerPresetCombo.currentTextChanged.connect(self.onFastenerPreset)

        self._btForm.filletGroup.toggled.connect(self.onFillet)
        self._btForm.filletRadiusInput.textEdited.connect(self.onFilletRadius)

        self._location.locationChange.connect(self.onLocation)
        
        self.update()
        
        if mode == 0: # fresh created
            self._obj.Proxy.execute(self._obj)  # calculate once 
            FreeCAD.Gui.SendMsgToActiveView("ViewFit")
        
    def transferTo(self):
        "Transfer from the dialog to the object" 
        self._obj.RailButtonType = str(self._btForm.railButtonTypeCombo.currentText())
        self._obj.Diameter = self._btForm.odInput.text()
        self._obj.InnerDiameter = self._btForm.idInput.text()
        self._obj.TopThickness = self._btForm.topThicknessInput.text()
        self._obj.BaseThickness = self._btForm.baseThicknessInput.text()
        self._obj.Thickness = self._btForm.thicknessInput.text()
        self._obj.Length = self._btForm.lengthInput.text()

        self._obj.Fastener = self._btForm.fastenerGroup.isChecked()
        self._obj.CountersinkAngle = str(self._btForm.countersinkTypeCombo.currentText())
        self._obj.HeadDiameter = self._btForm.headDiameterInput.text()
        self._obj.ShankDiameter = self._btForm.shankDiameterInput.text()

        self._obj.FilletedTop = self._btForm.filletGroup.isChecked()
        self._obj.FilletRadius = self._btForm.filletRadiusInput.text()

        self._obj.Comment = self._btForm.commentInput.toPlainText()

    def transferFrom(self):
        "Transfer from the object to the dialog"
        self._btForm.railButtonTypeCombo.setCurrentText(self._obj.RailButtonType)
        self._btForm.odInput.setText(self._obj.Diameter.UserString)
        self._btForm.idInput.setText(self._obj.InnerDiameter.UserString)
        self._btForm.topThicknessInput.setText(self._obj.TopThickness.UserString)
        self._btForm.baseThicknessInput.setText(self._obj.BaseThickness.UserString)
        self._btForm.thicknessInput.setText(self._obj.Thickness.UserString)
        self._btForm.lengthInput.setText(self._obj.Length.UserString)

        self._btForm.fastenerGroup.setChecked(self._obj.Fastener)
        self._btForm.countersinkTypeCombo.setCurrentText(self._obj.CountersinkAngle)
        self._btForm.headDiameterInput.setText(self._obj.HeadDiameter.UserString)
        self._btForm.shankDiameterInput.setText(self._obj.ShankDiameter.UserString)
        self._btForm.fastenerPresetCombo.setCurrentText("")

        self._btForm.filletGroup.setChecked(self._obj.FilletedTop)
        self._btForm.filletRadiusInput.setText(self._obj.FilletRadius.UserString)

        self._btForm.commentInput.setPlainText(self._obj.Comment)

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

    def onFastener(self, value):
        self._obj.Fastener = value
        self._obj.Proxy.execute(self._obj)
        self.setEdited()

    def _setFasteners(self):
        self._btForm.countersinkTypeCombo.setCurrentText(self._obj.CountersinkAngle)
        self._btForm.headDiameterInput.setText(self._obj.HeadDiameter.UserString)
        self._btForm.shankDiameterInput.setText(self._obj.ShankDiameter.UserString)

    def onCountersink(self, value):
        self._obj.CountersinkAngle = value
        self._btForm.fastenerPresetCombo.setCurrentText("")
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
            self._obj.CountersinkAngle = CONTERSINK_ANGLE_82
            self._obj.HeadDiameter = FreeCAD.Units.Quantity(FASTENER_PRESET_6_HEAD).Value
            self._obj.ShankDiameter = FreeCAD.Units.Quantity(FASTENER_PRESET_6_SHANK).Value
            self._setFasteners()
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def preset8(self):
        try:
            self._obj.CountersinkAngle = CONTERSINK_ANGLE_82
            self._obj.HeadDiameter = FreeCAD.Units.Quantity(FASTENER_PRESET_8_HEAD).Value
            self._obj.ShankDiameter = FreeCAD.Units.Quantity(FASTENER_PRESET_8_SHANK).Value
            self._setFasteners()
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def preset10(self):
        try:
            self._obj.CountersinkAngle = CONTERSINK_ANGLE_82
            self._obj.HeadDiameter = FreeCAD.Units.Quantity(FASTENER_PRESET_10_HEAD).Value
            self._obj.ShankDiameter = FreeCAD.Units.Quantity(FASTENER_PRESET_10_SHANK).Value
            self._setFasteners()
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def preset1_4(self):
        try:
            self._obj.CountersinkAngle = CONTERSINK_ANGLE_82
            self._obj.HeadDiameter = FreeCAD.Units.Quantity(FASTENER_PRESET_1_4_HEAD).Value
            self._obj.ShankDiameter = FreeCAD.Units.Quantity(FASTENER_PRESET_1_4_SHANK).Value
            self._setFasteners()
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()
    
    def onFastenerPreset(self, value):
        if value == FASTENER_PRESET_6:
            self.preset6()
        elif value == FASTENER_PRESET_8:
            self.preset8()
        elif value == FASTENER_PRESET_10:
            self.preset10()
        elif value == FASTENER_PRESET_1_4:
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
