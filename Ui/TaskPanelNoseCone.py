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

from PySide import QtGui, QtCore
from PySide2.QtWidgets import QDialog, QGridLayout, QVBoxLayout, QSizePolicy, QTextEdit

from DraftTools import translate

from Ui.TaskPanelDatabase import TaskPanelDatabase
from App.Constants import TYPE_CONE, TYPE_BLUNTED_CONE, TYPE_SPHERICAL, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_BLUNTED_OGIVE, TYPE_SECANT_OGIVE, TYPE_VON_KARMAN, TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_POWER
from App.Constants import STYLE_CAPPED, STYLE_HOLLOW, STYLE_SOLID
from App.Constants import STYLE_CAP_SOLID, STYLE_CAP_BAR, STYLE_CAP_CROSS
from App.Constants import COMPONENT_TYPE_NOSECONE

from App.Utilities import _toFloat, _valueWithUnits, _valueOnly

class _NoseConeDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        # define our window
        self.setGeometry(250, 250, 400, 350)
        self.setWindowTitle(translate('Rocket', "Nose Cone Parameter"))

        self.tabWidget = QtGui.QTabWidget()
        self.tabGeneral = QtGui.QWidget()
        self.tabShoulder = QtGui.QWidget()
        self.tabComment = QtGui.QWidget()
        self.tabWidget.addTab(self.tabGeneral, translate('Rocket', "General"))
        self.tabWidget.addTab(self.tabShoulder, translate('Rocket', "Shoulder"))
        self.tabWidget.addTab(self.tabComment, translate('Rocket', "Comment"))

        layout = QVBoxLayout()
        layout.addWidget(self.tabWidget)
        self.setLayout(layout)

        self.setTabGeneral()
        self.setTabShoulder()
        self.setTabComment()

    def setTabGeneral(self):
        ui = FreeCADGui.UiLoader()

        # Select the type of nose cone
        self.noseConeTypeLabel = QtGui.QLabel(translate('Rocket', "Nose Cone Shape"), self)

        self.noseConeTypes = (TYPE_CONE,
                                TYPE_BLUNTED_CONE,
                                TYPE_SPHERICAL,
                                TYPE_ELLIPTICAL,
                                TYPE_OGIVE,
                                TYPE_BLUNTED_OGIVE,
                                TYPE_SECANT_OGIVE,
                                TYPE_PARABOLA,
                                TYPE_PARABOLIC,
                                TYPE_POWER,
                                TYPE_VON_KARMAN,
                                TYPE_HAACK)
        self.noseConeTypesCombo = QtGui.QComboBox(self)
        self.noseConeTypesCombo.addItems(self.noseConeTypes)

        # Select the type of sketch
        self.noseStyleLabel = QtGui.QLabel(translate('Rocket', "Style"), self)

        self.noseStyles = (STYLE_SOLID,
                                STYLE_HOLLOW,
                                STYLE_CAPPED)
        self.noseStylesCombo = QtGui.QComboBox(self)
        self.noseStylesCombo.addItems(self.noseStyles)

        # Get the nose cone parameters: length, width, etc...
        self.lengthLabel = QtGui.QLabel(translate('Rocket', "Length"), self)

        self.lengthInput = ui.createWidget("Gui::InputField")
        self.lengthInput.unit = 'mm'
        self.lengthInput.setMinimumWidth(100)

        self.diameterLabel = QtGui.QLabel(translate('Rocket', "Diameter"), self)

        self.diameterInput = ui.createWidget("Gui::InputField")
        self.diameterInput.unit = 'mm'
        self.diameterInput.setMinimumWidth(80)

        self.autoDiameterCheckbox = QtGui.QCheckBox(translate('Rocket', "auto"), self)
        self.autoDiameterCheckbox.setCheckState(QtCore.Qt.Unchecked)

        self.thicknessLabel = QtGui.QLabel(translate('Rocket', "Thickness"), self)

        self.thicknessInput = ui.createWidget("Gui::InputField")
        self.thicknessInput.unit = 'mm'
        self.thicknessInput.setMinimumWidth(100)
        self.thicknessInput.setEnabled(False)

        self.coefficientLabel = QtGui.QLabel(translate('Rocket', "Shape Parameter"), self)

        #
        # Type dependent parameters
        self.coefficientValidator = QtGui.QDoubleValidator(self)
        self.coefficientValidator.setBottom(0.0)

        self.coefficientInput = QtGui.QLineEdit(self)
        self.coefficientInput.setMinimumWidth(100)
        self.coefficientInput.setValidator(self.coefficientValidator)
        self.coefficientInput.setEnabled(False)

        self.bluntedLabel = QtGui.QLabel(translate('Rocket', "Blunted Diameter"), self)

        self.bluntedInput = ui.createWidget("Gui::InputField")
        self.bluntedInput.unit = 'mm'
        self.bluntedInput.setMinimumWidth(100)

        self.ogiveDiameterLabel = QtGui.QLabel(translate('Rocket', "Ogive Diameter"), self)

        self.ogiveDiameterInput = ui.createWidget("Gui::InputField")
        self.ogiveDiameterInput.unit = 'mm'
        self.ogiveDiameterInput.setMinimumWidth(100)

        # Nose cap styles
        self.noseCapGroup = QtGui.QGroupBox(translate('Rocket', "Nose Cap"), self)

        self.noseCapStyleLabel = QtGui.QLabel(translate('Rocket', "Cap style"), self)

        self.noseCapStyles = (STYLE_CAP_SOLID,
                                STYLE_CAP_BAR,
                                STYLE_CAP_CROSS)
        self.noseCapStylesCombo = QtGui.QComboBox(self)
        self.noseCapStylesCombo.addItems(self.noseCapStyles)

        self.noseCapBarWidthLabel = QtGui.QLabel(translate('Rocket', "Bar Width"), self)

        self.noseCapBarWidthInput = ui.createWidget("Gui::InputField")
        self.noseCapBarWidthInput.unit = 'mm'
        self.noseCapBarWidthInput.setMinimumWidth(100)

        # Nose cap group
        row = 0
        grid = QGridLayout()

        grid.addWidget(self.noseCapStyleLabel, row, 0)
        grid.addWidget(self.noseCapStylesCombo, row, 1)
        row += 1

        grid.addWidget(self.noseCapBarWidthLabel, row, 0)
        grid.addWidget(self.noseCapBarWidthInput, row, 1)

        self.noseCapGroup.setLayout(grid)

        layout = QGridLayout()
        row = 0

        layout.addWidget(self.noseConeTypeLabel, row, 0, 1, 2)
        layout.addWidget(self.noseConeTypesCombo, row, 1)
        row += 1

        layout.addWidget(self.noseStyleLabel, row, 0)
        layout.addWidget(self.noseStylesCombo, row, 1)
        row += 1

        layout.addWidget(self.noseCapGroup, row, 0, 1, 2)
        row += 1

        layout.addWidget(self.lengthLabel, row, 0)
        layout.addWidget(self.lengthInput, row, 1)
        row += 1

        layout.addWidget(self.diameterLabel, row, 0)
        layout.addWidget(self.diameterInput, row, 1)
        layout.addWidget(self.autoDiameterCheckbox, row, 2)
        row += 1

        layout.addWidget(self.thicknessLabel, row, 0)
        layout.addWidget(self.thicknessInput, row, 1)
        row += 1

        layout.addWidget(self.coefficientLabel, row, 0)
        layout.addWidget(self.coefficientInput, row, 1)
        row += 1

        layout.addWidget(self.ogiveDiameterLabel, row, 0)
        layout.addWidget(self.ogiveDiameterInput, row, 1)
        row += 1

        layout.addWidget(self.bluntedLabel, row, 0)
        layout.addWidget(self.bluntedInput, row, 1)
        row += 1

        layout.addItem(QtGui.QSpacerItem(0,0, QSizePolicy.Expanding, QSizePolicy.Expanding), row, 0)

        self.tabGeneral.setLayout(layout)

    def setTabShoulder(self):
        ui = FreeCADGui.UiLoader()

        self.shoulderLabel = QtGui.QLabel(translate('Rocket', "Shoulder"), self)

        self.shoulderCheckbox = QtGui.QCheckBox(self)
        self.shoulderCheckbox.setCheckState(QtCore.Qt.Unchecked)

        self.shoulderDiameterLabel = QtGui.QLabel(translate('Rocket', "Diameter"), self)

        self.shoulderDiameterInput = ui.createWidget("Gui::InputField")
        self.shoulderDiameterInput.unit = 'mm'
        self.shoulderDiameterInput.setMinimumWidth(100)
        self.shoulderDiameterInput.setEnabled(False)

        self.shoulderAutoDiameterCheckbox = QtGui.QCheckBox(translate('Rocket', "auto"), self)
        self.shoulderAutoDiameterCheckbox.setCheckState(QtCore.Qt.Unchecked)

        self.shoulderLengthLabel = QtGui.QLabel(translate('Rocket', "Length"), self)

        self.shoulderLengthInput = ui.createWidget("Gui::InputField")
        self.shoulderLengthInput.unit = 'mm'
        self.shoulderLengthInput.setMinimumWidth(100)
        self.shoulderLengthInput.setEnabled(False)

        self.shoulderThicknessLabel = QtGui.QLabel(translate('Rocket', "Thickness"), self)

        self.shoulderThicknessInput = ui.createWidget("Gui::InputField")
        self.shoulderThicknessInput.unit = 'mm'
        self.shoulderThicknessInput.setMinimumWidth(100)
        self.shoulderThicknessInput.setEnabled(False)

        layout = QGridLayout()
        row = 0

        layout.addWidget(self.shoulderLabel, row, 0, 1, 2)
        layout.addWidget(self.shoulderCheckbox, row, 1)
        row += 1

        layout.addWidget(self.shoulderLengthLabel, row, 0)
        layout.addWidget(self.shoulderLengthInput, row, 1)
        row += 1

        layout.addWidget(self.shoulderDiameterLabel, row, 0)
        layout.addWidget(self.shoulderDiameterInput, row, 1)
        layout.addWidget(self.shoulderAutoDiameterCheckbox, row, 2)
        row += 1

        layout.addWidget(self.shoulderThicknessLabel, row, 0)
        layout.addWidget(self.shoulderThicknessInput, row, 1)
        row += 1

        layout.addItem(QtGui.QSpacerItem(0,0, QSizePolicy.Expanding, QSizePolicy.Expanding), row, 0)

        self.tabShoulder.setLayout(layout)

    def setTabComment(self):

        ui = FreeCADGui.UiLoader()

        self.commentLabel = QtGui.QLabel(translate('Rocket', "Comment"), self)

        self.commentInput = QTextEdit()

        layout = QVBoxLayout()
        layout.addWidget(self.commentLabel)
        layout.addWidget(self.commentInput)

        self.tabComment.setLayout(layout)

class TaskPanelNoseCone:

    def __init__(self,obj,mode):
        self._obj = obj
        self._isAssembly = self._obj.Proxy.isRocketAssembly()
        
        self._noseForm = _NoseConeDialog()
        self._db = TaskPanelDatabase(obj, COMPONENT_TYPE_NOSECONE)
        self._dbForm = self._db.getForm()

        self.form = [self._noseForm, self._dbForm]
        self._noseForm.setWindowIcon(QtGui.QIcon(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_NoseCone.svg"))
        
        self._noseForm.noseConeTypesCombo.currentTextChanged.connect(self.onNoseType)
        self._noseForm.noseStylesCombo.currentTextChanged.connect(self.onNoseStyle)
        self._noseForm.noseCapStylesCombo.currentTextChanged.connect(self.onNoseCapStyle)
        self._noseForm.noseCapBarWidthInput.textEdited.connect(self.onBarWidthChanged)

        self._noseForm.lengthInput.textEdited.connect(self.onLength)
        self._noseForm.diameterInput.textEdited.connect(self.onDiameter)
        self._noseForm.autoDiameterCheckbox.stateChanged.connect(self.onAutoDiameter)
        self._noseForm.thicknessInput.textEdited.connect(self.onThickness)
        self._noseForm.coefficientInput.textEdited.connect(self.onCoefficient)
        self._noseForm.bluntedInput.textEdited.connect(self.onBlunted)
        self._noseForm.ogiveDiameterInput.textEdited.connect(self.onOgiveDiameter)

        self._noseForm.shoulderCheckbox.stateChanged.connect(self.onShoulder)
        self._noseForm.shoulderDiameterInput.textEdited.connect(self.onShoulderDiameter)
        self._noseForm.shoulderAutoDiameterCheckbox.stateChanged.connect(self.onShoulderAutoDiameter)
        self._noseForm.shoulderLengthInput.textEdited.connect(self.onShoulderLength)
        self._noseForm.shoulderThicknessInput.textEdited.connect(self.onShoulderThickness)

        self._db.dbLoad.connect(self.onLookup)
        
        self.update()
        
        if mode == 0: # fresh created
            self._obj.Proxy.execute(self._obj)  # calculate once 
            FreeCAD.Gui.SendMsgToActiveView("ViewFit")
        
    def transferTo(self):
        "Transfer from the dialog to the object" 
        self._obj.NoseType = str(self._noseForm.noseConeTypesCombo.currentText())
        self._obj.NoseStyle = str(self._noseForm.noseStylesCombo.currentText())
        self._obj.CapStyle = str(self._noseForm.noseCapStylesCombo.currentText())
        self._obj.CapBarWidth = self._noseForm.noseCapBarWidthInput.text()
        self._obj.Proxy.setLength(FreeCAD.Units.Quantity(self._noseForm.lengthInput.text()).Value)
        self._obj.Proxy.setAftDiameter(FreeCAD.Units.Quantity(self._noseForm.diameterInput.text()).Value)
        self._obj.Proxy.setAftDiameterAutomatic(self._noseForm.autoDiameterCheckbox.isChecked())
        self._obj.Proxy.setThickness(FreeCAD.Units.Quantity(self._noseForm.thicknessInput.text()).Value)
        self._obj.Coefficient = _toFloat(self._noseForm.coefficientInput.text())
        self._obj.BluntedDiameter = self._noseForm.bluntedInput.text()
        self._obj.OgiveDiameter = self._noseForm.ogiveDiameterInput.text()
        self._obj.Shoulder = self._noseForm.shoulderCheckbox.isChecked()
        self._obj.ShoulderDiameter = self._noseForm.shoulderDiameterInput.text()
        self._obj.ShoulderAutoDiameter = self._noseForm.shoulderAutoDiameterCheckbox.isChecked()
        self._obj.ShoulderLength = self._noseForm.shoulderLengthInput.text()
        self._obj.ShoulderThickness = self._noseForm.shoulderThicknessInput.text()

        self._obj.Comment = self._noseForm.commentInput.toPlainText()

    def transferFrom(self):
        "Transfer from the object to the dialog"
        self._noseForm.noseConeTypesCombo.setCurrentText(self._obj.NoseType)
        self._noseForm.noseStylesCombo.setCurrentText(self._obj.NoseStyle)
        self._noseForm.noseCapStylesCombo.setCurrentText(self._obj.CapStyle)
        self._noseForm.noseCapBarWidthInput.setText(self._obj.CapBarWidth.UserString)
        self._noseForm.lengthInput.setText(self._obj.Length.UserString)
        self._noseForm.diameterInput.setText(self._obj.Diameter.UserString)
        self._noseForm.autoDiameterCheckbox.setChecked(self._obj.AutoDiameter)
        self._noseForm.thicknessInput.setText(self._obj.Thickness.UserString)
        self._noseForm.coefficientInput.setText("%f" % self._obj.Coefficient)
        self._noseForm.bluntedInput.setText(self._obj.BluntedDiameter.UserString)
        self._noseForm.ogiveDiameterInput.setText(self._obj.OgiveDiameter.UserString)
        self._noseForm.shoulderCheckbox.setChecked(self._obj.Shoulder)
        self._noseForm.shoulderDiameterInput.setText(self._obj.ShoulderDiameter.UserString)
        self._noseForm.shoulderAutoDiameterCheckbox.setChecked(self._obj.ShoulderAutoDiameter)
        self._noseForm.shoulderLengthInput.setText(self._obj.ShoulderLength.UserString)
        self._noseForm.shoulderThicknessInput.setText(self._obj.ShoulderThickness.UserString)

        self._noseForm.commentInput.setPlainText(self._obj.Comment)

        self._setTypeState()
        self._setStyleState()
        self._setAutoDiameterState()
        self._setShoulderState()

    def setEdited(self):
        try:
            self._obj.Proxy.setEdited()
        except ReferenceError:
            # Object may be deleted
            pass
        
    def _setCoeffientState(self):
        value = self._obj.NoseType
        if value == TYPE_HAACK or value == TYPE_PARABOLIC:
            self._noseForm.coefficientInput.setEnabled(True)
        elif value == TYPE_POWER:
            self._noseForm.coefficientInput.setEnabled(True)
        elif value == TYPE_VON_KARMAN:
            self._obj.Coefficient = 0.0
            self._noseForm.coefficientInput.setText("%f" % self._obj.Coefficient)
            self._noseForm.coefficientInput.setEnabled(False)
        elif value == TYPE_PARABOLA:
            self._obj.Coefficient = 0.5
            self._noseForm.coefficientInput.setText("%f" % self._obj.Coefficient)
            self._noseForm.coefficientInput.setEnabled(False)
        else:
            self._noseForm.coefficientInput.setEnabled(False)
        
    def _setBluntState(self):
        value = self._obj.NoseType
        if value in [TYPE_BLUNTED_CONE, TYPE_BLUNTED_OGIVE]:
            self._noseForm.bluntedInput.setEnabled(True)
        else:
            self._noseForm.bluntedInput.setEnabled(False)
        
    def _setOgiveDiameterState(self):
        value = self._obj.NoseType
        if value == TYPE_SECANT_OGIVE:
            self._noseForm.ogiveDiameterInput.setEnabled(True)
        else:
            self._noseForm.ogiveDiameterInput.setEnabled(False)
        
    def _setLengthState(self):
        value = self._obj.NoseType
        if value == TYPE_SPHERICAL:
            self._obj.Proxy.setLength(float(self._obj.Diameter) / 2.0)
            self._noseForm.lengthInput.setText("%f" % self._obj.Length)
            self._noseForm.lengthInput.setEnabled(False)
        else:
            self._noseForm.lengthInput.setEnabled(True)
        
    def _setTypeState(self):
        self._setCoeffientState()
        self._setBluntState()
        self._setOgiveDiameterState()
        self._setLengthState()

    def onNoseType(self, value):
        self._obj.NoseType = value
        self._setTypeState()

        self._obj.Proxy.execute(self._obj)
        self.setEdited()

    def _setStyleState(self):
        value = self._obj.NoseStyle
        if value == STYLE_HOLLOW or value == STYLE_CAPPED:
            self._noseForm.thicknessInput.setEnabled(True)

            if self._noseForm.shoulderCheckbox.isChecked():
                self._noseForm.shoulderThicknessInput.setEnabled(True)
            else:
                self._noseForm.shoulderThicknessInput.setEnabled(False)
        else:
            self._noseForm.thicknessInput.setEnabled(False)
            self._noseForm.shoulderThicknessInput.setEnabled(False)

        if value == STYLE_CAPPED:
            self._noseForm.noseCapGroup.setEnabled(True)
            self._setCapStyleState()
        else:
            self._noseForm.noseCapGroup.setEnabled(False)
        
    def onNoseStyle(self, value):
        self._obj.NoseStyle = value
        self._setStyleState()

        self._obj.Proxy.execute(self._obj)

    def _setCapStyleState(self):
        value = self._obj.CapStyle
        if value == STYLE_CAP_SOLID:
            self._noseForm.noseCapBarWidthInput.setEnabled(False)
        else:
            self._noseForm.noseCapBarWidthInput.setEnabled(True)
        
    def onNoseCapStyle(self, value):
        self._obj.CapStyle = value
        self._setCapStyleState()

        self._obj.Proxy.execute(self._obj)
        
    def onBarWidthChanged(self, value):
        try:
            self._obj.CapBarWidth = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        
    def onLength(self, value):
        try:
            self._obj.Proxy.setLength(FreeCAD.Units.Quantity(value).Value)
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        
    def onBlunted(self, value):
        try:
            self._obj.BluntedDiameter = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        
    def onDiameter(self, value):
        try:
            self._obj.Proxy.setAftDiameter(FreeCAD.Units.Quantity(value).Value)
            self._obj.Proxy.setAftDiameterAutomatic(False)
            self._obj.Proxy.execute(self._obj)

            self._setLengthState() # Update for spherical noses
        except ValueError:
            pass
        self.setEdited()
        
    def _setAutoDiameterState(self):
        if self._isAssembly:
            self._noseForm.diameterInput.setEnabled(not self._obj.AutoDiameter)
            self._noseForm.autoDiameterCheckbox.setEnabled(True)
        else:
            self._noseForm.diameterInput.setEnabled(True)
            self._obj.AutoDiameter = False
            self._noseForm.autoDiameterCheckbox.setEnabled(False)
        self._noseForm.autoDiameterCheckbox.setChecked(self._obj.AutoDiameter)

        if self._obj.AutoDiameter:
            self._obj.Diameter = self._obj.Proxy.getAftDiameter()
            self._noseForm.diameterInput.setText(self._obj.Diameter.UserString)

    def onAutoDiameter(self, value):
        self._obj.Proxy.setAftDiameterAutomatic(value)
        self._setAutoDiameterState()

        self._obj.Proxy.execute(self._obj)
        self.setEdited()
         
    def onThickness(self, value):
        try:
            self._obj.Proxy.setThickness(FreeCAD.Units.Quantity(value).Value)
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()
        
    def onCoefficient(self, value):
        self._obj.Coefficient = _toFloat(value)
        self._obj.Proxy.execute(self._obj)
        self.setEdited()

    def onBlunted(self, value):
        try:
            self._obj.BluntedDiameter = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()
        
    def onOgiveDiameter(self, value):
        try:
            self._obj.OgiveDiameter = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def _setShoulderState(self):
        if self._obj.Shoulder:
            self._noseForm.shoulderDiameterInput.setEnabled(True)
            self._noseForm.shoulderLengthInput.setEnabled(True)

            selectedText = self._noseForm.noseStylesCombo.currentText()
            if selectedText == STYLE_HOLLOW or selectedText == STYLE_CAPPED:
                self._noseForm.shoulderThicknessInput.setEnabled(True)
            else:
                self._noseForm.shoulderThicknessInput.setEnabled(False)
        else:
            self._noseForm.shoulderDiameterInput.setEnabled(False)
            self._noseForm.shoulderLengthInput.setEnabled(False)
            self._noseForm.shoulderThicknessInput.setEnabled(False)

        self._setAutoShoulderDiameterState()
        
    def onShoulder(self, value):
        self._obj.Shoulder = self._noseForm.shoulderCheckbox.isChecked()
        self._setShoulderState()

        self._obj.Proxy.execute(self._obj)
        self.setEdited()
        
    def onShoulderDiameter(self, value):
        try:
            self._obj.ShoulderDiameter = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.setAftShoulderDiameterAutomatic(False)
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()
       
    def _setAutoShoulderDiameterState(self):
        if self._isAssembly:
            self._noseForm.shoulderDiameterInput.setEnabled((not self._obj.ShoulderAutoDiameter) and self._obj.Shoulder)
            self._noseForm.shoulderAutoDiameterCheckbox.setChecked(self._obj.ShoulderAutoDiameter)
            self._noseForm.shoulderAutoDiameterCheckbox.setEnabled(self._obj.Shoulder)
        else:
            self._obj.ShoulderAutoDiameter = False
            self._noseForm.shoulderDiameterInput.setEnabled(self._obj.Shoulder)
            self._noseForm.shoulderAutoDiameterCheckbox.setChecked(self._obj.ShoulderAutoDiameter)
            self._noseForm.shoulderAutoDiameterCheckbox.setEnabled(self._obj.ShoulderAutoDiameter)
        
    def onShoulderAutoDiameter(self, value):
        self._obj.Proxy.setAftShoulderDiameterAutomatic(value)
        self._setAutoShoulderDiameterState()

        self._obj.Proxy.execute(self._obj)
        self.setEdited()
        
    def onShoulderLength(self, value):
        try:
            self._obj.ShoulderLength = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()
        
    def onShoulderThickness(self, value):
        try:
            self._obj.ShoulderThickness = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()
       
    def onLookup(self):
        result = self._db.getLookupResult()

        self._obj.NoseType = str(result["shape"])
        self._obj.NoseStyle = str(result["style"])
        self._obj.Proxy.setLength(_valueOnly(result["length"], result["length_units"]))
        self._obj.Proxy.setAftDiameter(_valueOnly(result["diameter"], result["diameter_units"]))
        self._obj.Proxy.setThickness(_valueOnly(result["thickness"], result["thickness_units"]))
        # self._obj.Coefficient = _toFloat(self._noseForm.coefficientInput.text())
        # self._obj.BluntedDiameter = _valueWithUnits("0", "mm")
        self._obj.ShoulderDiameter = _valueWithUnits(result["shoulder_diameter"], result["shoulder_diameter_units"])
        self._obj.ShoulderLength = _valueWithUnits(result["shoulder_length"], result["shoulder_length_units"])
        self._obj.Shoulder = (self._obj.ShoulderDiameter > 0.0) and (self._obj.ShoulderLength >= 0)
        self._obj.ShoulderThickness = self._obj.Thickness
        self.update()
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
