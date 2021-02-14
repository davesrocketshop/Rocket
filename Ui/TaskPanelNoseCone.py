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
"""Class for drawing nose cones"""

__title__ = "FreeCAD Nose Cones"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    

import FreeCAD
import FreeCADGui

from PySide import QtGui, QtCore
from PySide2.QtWidgets import QDialog, QGridLayout

from DraftTools import translate

from Ui.TaskPanelDatabase import TaskPanelDatabase
from App.Constants import TYPE_CONE, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_VON_KARMAN, TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_POWER
from App.Constants import STYLE_CAPPED, STYLE_HOLLOW, STYLE_SOLID
from App.Constants import COMPONENT_TYPE_NOSECONE

from App.Utilities import _toFloat

class _testDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)


        # define our window
        self.setGeometry(250, 250, 400, 350)
        self.setWindowTitle(translate('Rocket', "Component Lookup"))

        # Select the type of nose cone
        self.testTypeLabel = QtGui.QLabel(translate('Rocket', "Test type"), self)

        self.testTypes = ("Test 1",
                                "Test 2")
        self.testTypesCombo = QtGui.QComboBox(self)
        self.testTypesCombo.addItems(self.testTypes)

        layout = QGridLayout()

        layout.addWidget(self.testTypeLabel, 0, 0, 1, 2)
        layout.addWidget(self.testTypesCombo, 0, 1)

        self.setLayout(layout)

class _NoseConeDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)


        # define our window
        self.setGeometry(250, 250, 400, 350)
        self.setWindowTitle(translate('Rocket', "Nose Cone Parameter"))

        # Select the type of nose cone
        self.noseConeTypeLabel = QtGui.QLabel(translate('Rocket', "Nose cone type"), self)

        self.noseConeTypes = (TYPE_CONE,
                                TYPE_ELLIPTICAL,
                                TYPE_OGIVE,
                                TYPE_PARABOLA,
                                TYPE_PARABOLIC,
                                TYPE_POWER,
                                TYPE_VON_KARMAN,
                                TYPE_HAACK)
        self.noseConeTypesCombo = QtGui.QComboBox(self)
        self.noseConeTypesCombo.addItems(self.noseConeTypes)

        # Select the type of sketch
        self.noseStyleLabel = QtGui.QLabel(translate('Rocket', "Nose Style"), self)

        self.noseStyles = (STYLE_SOLID,
                                STYLE_HOLLOW,
                                STYLE_CAPPED)
        self.noseStylesCombo = QtGui.QComboBox(self)
        self.noseStylesCombo.addItems(self.noseStyles)

        # Get the nose cone parameters: length, width, etc...
        self.lengthLabel = QtGui.QLabel(translate('Rocket', "Length"), self)

        self.lengthValidator = QtGui.QDoubleValidator(self)
        self.lengthValidator.setBottom(0.0)

        self.lengthInput = QtGui.QLineEdit(self)
        self.lengthInput.setFixedWidth(100)
        self.lengthInput.setValidator(self.lengthValidator)

        self.radiusLabel = QtGui.QLabel(translate('Rocket', "Radius"), self)

        self.radiusValidator = QtGui.QDoubleValidator(self)
        self.radiusValidator.setBottom(0.0)

        self.radiusInput = QtGui.QLineEdit(self)
        self.radiusInput.setFixedWidth(100)
        self.radiusInput.setValidator(self.radiusValidator)

        self.thicknessLabel = QtGui.QLabel(translate('Rocket', "Thickness"), self)

        self.thicknessValidator = QtGui.QDoubleValidator(self)
        self.thicknessValidator.setBottom(0.0)

        self.thicknessInput = QtGui.QLineEdit(self)
        self.thicknessInput.setFixedWidth(100)
        self.thicknessInput.setValidator(self.thicknessValidator)

        self.coefficientLabel = QtGui.QLabel(translate('Rocket', "Coefficient"), self)

        self.coefficientValidator = QtGui.QDoubleValidator(self)
        self.coefficientValidator.setBottom(0.0)

        self.coefficientInput = QtGui.QLineEdit(self)
        self.coefficientInput.setFixedWidth(100)
        self.coefficientInput.setValidator(self.coefficientValidator)
        self.coefficientInput.setEnabled(False)

        self.shoulderLabel = QtGui.QLabel(translate('Rocket', "Shoulder"), self)

        self.shoulderCheckbox = QtGui.QCheckBox(self)
        self.shoulderCheckbox.setCheckState(QtCore.Qt.Unchecked)

        self.shoulderRadiusLabel = QtGui.QLabel(translate('Rocket', "Radius"), self)

        self.shoulderRadiusValidator = QtGui.QDoubleValidator(self)
        self.shoulderRadiusValidator.setBottom(0.0)

        self.shoulderRadiusInput = QtGui.QLineEdit(self)
        self.shoulderRadiusInput.setFixedWidth(100)
        self.shoulderRadiusInput.setValidator(self.shoulderRadiusValidator)
        self.shoulderRadiusInput.setEnabled(False)

        self.shoulderLengthLabel = QtGui.QLabel(translate('Rocket', "Length"), self)

        self.shoulderLengthValidator = QtGui.QDoubleValidator(self)
        self.shoulderLengthValidator.setBottom(0.0)

        self.shoulderLengthInput = QtGui.QLineEdit(self)
        self.shoulderLengthInput.setFixedWidth(100)
        self.shoulderLengthInput.setValidator(self.shoulderLengthValidator)
        self.shoulderLengthInput.setEnabled(False)

        self.shoulderThicknessLabel = QtGui.QLabel(translate('Rocket', "Thickness"), self)

        self.shoulderThicknessValidator = QtGui.QDoubleValidator(self)
        self.shoulderThicknessValidator.setBottom(0.0)

        self.shoulderThicknessInput = QtGui.QLineEdit(self)
        self.shoulderThicknessInput.setFixedWidth(100)
        self.shoulderThicknessInput.setValidator(self.shoulderThicknessValidator)
        self.shoulderThicknessInput.setEnabled(False)

        layout = QGridLayout()

        layout.addWidget(self.noseConeTypeLabel, 0, 0, 1, 2)
        layout.addWidget(self.noseConeTypesCombo, 0, 1)

        layout.addWidget(self.noseStyleLabel, 1, 0)
        layout.addWidget(self.noseStylesCombo, 1, 1)

        layout.addWidget(self.lengthLabel, 2, 0)
        layout.addWidget(self.lengthInput, 2, 1)

        layout.addWidget(self.radiusLabel, 3, 0)
        layout.addWidget(self.radiusInput, 3, 1)

        layout.addWidget(self.thicknessLabel, 4, 0)
        layout.addWidget(self.thicknessInput, 4, 1)

        layout.addWidget(self.coefficientLabel, 5, 0)
        layout.addWidget(self.coefficientInput, 5, 1)

        layout.addWidget(self.shoulderLabel, 6, 0)
        layout.addWidget(self.shoulderCheckbox, 6, 1)

        layout.addWidget(self.shoulderLengthLabel, 7, 1)
        layout.addWidget(self.shoulderLengthInput, 7, 2)

        layout.addWidget(self.shoulderRadiusLabel, 8, 1)
        layout.addWidget(self.shoulderRadiusInput, 8, 2)

        layout.addWidget(self.shoulderThicknessLabel, 9, 1)
        layout.addWidget(self.shoulderThicknessInput, 9, 2)

        self.setLayout(layout)

class TaskPanelNoseCone:

    def __init__(self,obj,mode):
        self.obj = obj
        
        self._noseForm = _NoseConeDialog()
        self._dbForm = TaskPanelDatabase.getForm(COMPONENT_TYPE_NOSECONE)

        self.form = [self._dbForm, self._noseForm]
        self._noseForm.setWindowIcon(QtGui.QIcon(":/icons/Rocket_NoseCone.svg"))
        
        QtCore.QObject.connect(self._noseForm.noseConeTypesCombo, QtCore.SIGNAL("currentTextChanged(QString)"), self.onNoseType)
        QtCore.QObject.connect(self._noseForm.noseStylesCombo, QtCore.SIGNAL("currentTextChanged(QString)"), self.onNoseStyle)

        self._noseForm.lengthInput.textEdited.connect(self.onLengthChanged)
        self._noseForm.radiusInput.textEdited.connect(self.onRadiusChanged)
        self._noseForm.thicknessInput.textEdited.connect(self.onThicknessChanged)
        self._noseForm.coefficientInput.textEdited.connect(self.onCoefficientChanged)

        self._noseForm.shoulderCheckbox.stateChanged.connect(self.onShoulderChanged)
        self._noseForm.shoulderRadiusInput.textEdited.connect(self.onShoulderRadiusChanged)
        self._noseForm.shoulderLengthInput.textEdited.connect(self.onShoulderLengthChanged)
        self._noseForm.shoulderThicknessInput.textEdited.connect(self.onShoulderThicknessChanged)
        
        self.update()
        
        if mode == 0: # fresh created
            self.obj.Proxy.execute(self.obj)  # calculate once 
            FreeCAD.Gui.SendMsgToActiveView("ViewFit")
        
    def transferTo(self):
        "Transfer from the dialog to the object" 
        self.obj.NoseType = str(self._noseForm.noseConeTypesCombo.currentText())
        self.obj.NoseStyle = str(self._noseForm.noseStylesCombo.currentText())
        self.obj.Length = _toFloat(self._noseForm.lengthInput.text())
        self.obj.Radius = _toFloat(self._noseForm.radiusInput.text())
        self.obj.Thickness = _toFloat(self._noseForm.thicknessInput.text())
        self.obj.Coefficient = _toFloat(self._noseForm.coefficientInput.text())
        self.obj.Shoulder = self._noseForm.shoulderCheckbox.isChecked()
        self.obj.ShoulderRadius = _toFloat(self._noseForm.shoulderRadiusInput.text())
        self.obj.ShoulderLength = _toFloat(self._noseForm.shoulderLengthInput.text())
        self.obj.ShoulderThickness = _toFloat(self._noseForm.shoulderThicknessInput.text())

    def transferFrom(self):
        "Transfer from the object to the dialog"
        self._noseForm.noseConeTypesCombo.setCurrentText(self.obj.NoseType)
        self._noseForm.noseStylesCombo.setCurrentText(self.obj.NoseStyle)
        self._noseForm.lengthInput.setText("%f" % self.obj.Length)
        self._noseForm.radiusInput.setText("%f" % self.obj.Radius)
        self._noseForm.thicknessInput.setText("%f" % self.obj.Thickness)
        self._noseForm.coefficientInput.setText("%f" % self.obj.Coefficient)
        self._noseForm.shoulderCheckbox.setChecked(self.obj.Shoulder)
        self._noseForm.shoulderRadiusInput.setText("%f" % self.obj.ShoulderRadius)
        self._noseForm.shoulderLengthInput.setText("%f" % self.obj.ShoulderLength)
        self._noseForm.shoulderThicknessInput.setText("%f" % self.obj.ShoulderThickness)
        
    def onNoseType(self, value):
        if value == TYPE_HAACK or value == TYPE_PARABOLIC:
            self._noseForm.coefficientInput.setEnabled(True)
        elif value == TYPE_POWER:
            self._noseForm.coefficientInput.setEnabled(True)
        else:
            self._noseForm.coefficientInput.setEnabled(False)

        self.obj.NoseType = value
        self.obj.Proxy.execute(self.obj)
        
    def onNoseStyle(self, value):
        if value == STYLE_HOLLOW or value == STYLE_CAPPED:
            self._noseForm.thicknessInput.setEnabled(True)

            if self._noseForm.shoulderCheckbox.isChecked():
                self._noseForm.shoulderThicknessInput.setEnabled(True)
            else:
                self._noseForm.shoulderThicknessInput.setEnabled(False)
        else:
            self._noseForm.thicknessInput.setEnabled(False)
            self._noseForm.shoulderThicknessInput.setEnabled(False)

        self.obj.NoseStyle = value
        self.obj.Proxy.execute(self.obj)
        
    def onLengthChanged(self, value):
        self.obj.Length = _toFloat(value)
        self.obj.Proxy.execute(self.obj)

        
    def onRadiusChanged(self, value):
        self.obj.Radius = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onThicknessChanged(self, value):
        self.obj.Thickness = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onCoefficientChanged(self, value):
        self.obj.Coefficient = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onShoulderChanged(self, value):
        self.obj.Shoulder = self._noseForm.shoulderCheckbox.isChecked()
        if self.obj.Shoulder:
            self._noseForm.shoulderRadiusInput.setEnabled(True)
            self._noseForm.shoulderLengthInput.setEnabled(True)

            selectedText = self._noseForm.noseStylesCombo.currentText()
            if selectedText == STYLE_HOLLOW or selectedText == STYLE_CAPPED:
                self._noseForm.shoulderThicknessInput.setEnabled(True)
            else:
                self._noseForm.shoulderThicknessInput.setEnabled(False)
        else:
            self._noseForm.shoulderRadiusInput.setEnabled(False)
            self._noseForm.shoulderLengthInput.setEnabled(False)
            self._noseForm.shoulderThicknessInput.setEnabled(False)

        self.obj.Proxy.execute(self.obj)
        
    def onShoulderRadiusChanged(self, value):
        self.obj.ShoulderRadius = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onShoulderLengthChanged(self, value):
        self.obj.ShoulderLength = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onShoulderThicknessChanged(self, value):
        self.obj.ShoulderThickness = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def getStandardButtons(self):
        return int(QtGui.QDialogButtonBox.Ok) | int(QtGui.QDialogButtonBox.Cancel)| int(QtGui.QDialogButtonBox.Apply)

    def clicked(self,button):
        if button == QtGui.QDialogButtonBox.Apply:
            #print "Apply"
            self.transferTo()
            self.obj.Proxy.execute(self.obj) 
        
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
