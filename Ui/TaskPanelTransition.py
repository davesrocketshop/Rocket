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
"""Class for drawing transitions"""

__title__ = "FreeCAD Transitions"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    

import FreeCAD
import FreeCADGui

from PySide import QtGui, QtCore
from PySide2.QtWidgets import QDialog, QGridLayout

from App.Constants import TYPE_CONE, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_VON_KARMAN, TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_POWER
from App.Constants import STYLE_CAPPED, STYLE_HOLLOW, STYLE_SOLID, STYLE_SOLID_CORE

from App.Utilities import _toFloat, _msg

class _TransitionDialog(QDialog):

    def __init__(self, parent=None):
        super(_TransitionDialog, self).__init__(parent)


        # define our window
        self.setGeometry(250, 250, 400, 350)
        self.setWindowTitle("Transition Parameter")

        # Select the type of transition
        self.transitionTypeLabel = QtGui.QLabel("Transition type", self)

        self.transitionTypes = (TYPE_CONE,
                                TYPE_ELLIPTICAL,
                                #TYPE_OGIVE,
                                #TYPE_PARABOLA,
                                #TYPE_PARABOLIC,
                                #TYPE_POWER,
                                #TYPE_VON_KARMAN,
                                #TYPE_HAACK
                                )
        self.transitionTypesCombo = QtGui.QComboBox(self)
        self.transitionTypesCombo.addItems(self.transitionTypes)

        self.clippedLabel = QtGui.QLabel("Clipped", self)

        self.clippedCheckbox = QtGui.QCheckBox(self)
        self.clippedCheckbox.setCheckState(QtCore.Qt.Checked)

        # Select the type of sketch
        self.transitionStyleLabel = QtGui.QLabel("Transition Style", self)

        self.transitionStyles = (STYLE_SOLID,
                                STYLE_SOLID_CORE,
                                STYLE_HOLLOW,
                                STYLE_CAPPED)
        self.transitionStylesCombo = QtGui.QComboBox(self)
        self.transitionStylesCombo.addItems(self.transitionStyles)

        # Get the transition parameters: length, width, etc...
        self.lengthLabel = QtGui.QLabel("Length", self)

        self.lengthValidator = QtGui.QDoubleValidator(self)
        self.lengthValidator.setBottom(0.0)

        self.lengthInput = QtGui.QLineEdit(self)
        self.lengthInput.setFixedWidth(100)
        self.lengthInput.setValidator(self.lengthValidator)

        self.foreRadiusLabel = QtGui.QLabel("Forward Radius", self)

        self.foreRadiusValidator = QtGui.QDoubleValidator(self)
        self.foreRadiusValidator.setBottom(0.0)

        self.foreRadiusInput = QtGui.QLineEdit(self)
        self.foreRadiusInput.setFixedWidth(100)
        self.foreRadiusInput.setValidator(self.foreRadiusValidator)

        self.aftRadiusLabel = QtGui.QLabel("Aft Radius", self)

        self.aftRadiusValidator = QtGui.QDoubleValidator(self)
        self.aftRadiusValidator.setBottom(0.0)

        self.aftRadiusInput = QtGui.QLineEdit(self)
        self.aftRadiusInput.setFixedWidth(100)
        self.aftRadiusInput.setValidator(self.aftRadiusValidator)

        self.coreRadiusLabel = QtGui.QLabel("Core Radius", self)

        self.coreRadiusValidator = QtGui.QDoubleValidator(self)
        self.coreRadiusValidator.setBottom(0.0)

        self.coreRadiusInput = QtGui.QLineEdit(self)
        self.coreRadiusInput.setFixedWidth(100)
        self.coreRadiusInput.setValidator(self.aftRadiusValidator)
        self.coreRadiusInput.setEnabled(False)

        self.thicknessLabel = QtGui.QLabel("Thickness", self)

        self.thicknessValidator = QtGui.QDoubleValidator(self)
        self.thicknessValidator.setBottom(0.0)

        self.thicknessInput = QtGui.QLineEdit(self)
        self.thicknessInput.setFixedWidth(100)
        self.thicknessInput.setValidator(self.thicknessValidator)
        self.thicknessInput.setEnabled(False)

        self.coefficientLabel = QtGui.QLabel("Coefficient", self)

        self.coefficientValidator = QtGui.QDoubleValidator(self)
        self.coefficientValidator.setBottom(0.0)

        self.coefficientInput = QtGui.QLineEdit(self)
        self.coefficientInput.setFixedWidth(100)
        self.coefficientInput.setValidator(self.coefficientValidator)
        self.coefficientInput.setEnabled(False)

        self.foreShoulderLabel = QtGui.QLabel("Forward Shoulder", self)

        self.foreShoulderCheckbox = QtGui.QCheckBox(self)
        self.foreShoulderCheckbox.setCheckState(QtCore.Qt.Checked)

        self.foreShoulderRadiusLabel = QtGui.QLabel("Radius", self)

        self.foreShoulderRadiusValidator = QtGui.QDoubleValidator(self)
        self.foreShoulderRadiusValidator.setBottom(0.0)

        self.foreShoulderRadiusInput = QtGui.QLineEdit(self)
        self.foreShoulderRadiusInput.setFixedWidth(100)
        self.foreShoulderRadiusInput.setValidator(self.foreShoulderRadiusValidator)

        self.foreShoulderLengthLabel = QtGui.QLabel("Length", self)

        self.foreShoulderLengthValidator = QtGui.QDoubleValidator(self)
        self.foreShoulderLengthValidator.setBottom(0.0)

        self.foreShoulderLengthInput = QtGui.QLineEdit(self)
        self.foreShoulderLengthInput.setFixedWidth(100)
        self.foreShoulderLengthInput.setValidator(self.foreShoulderLengthValidator)

        self.foreShoulderThicknessLabel = QtGui.QLabel("Thickness", self)

        self.foreShoulderThicknessValidator = QtGui.QDoubleValidator(self)
        self.foreShoulderThicknessValidator.setBottom(0.0)

        self.foreShoulderThicknessInput = QtGui.QLineEdit(self)
        self.foreShoulderThicknessInput.setFixedWidth(100)
        self.foreShoulderThicknessInput.setValidator(self.foreShoulderThicknessValidator)
        self.foreShoulderThicknessInput.setEnabled(False)

        self.aftShoulderLabel = QtGui.QLabel("Aft Shoulder", self)

        self.aftShoulderCheckbox = QtGui.QCheckBox(self)
        self.aftShoulderCheckbox.setCheckState(QtCore.Qt.Checked)

        self.aftShoulderRadiusLabel = QtGui.QLabel("Radius", self)

        self.aftShoulderRadiusValidator = QtGui.QDoubleValidator(self)
        self.aftShoulderRadiusValidator.setBottom(0.0)

        self.aftShoulderRadiusInput = QtGui.QLineEdit(self)
        self.aftShoulderRadiusInput.setFixedWidth(100)
        self.aftShoulderRadiusInput.setValidator(self.aftShoulderRadiusValidator)

        self.aftShoulderLengthLabel = QtGui.QLabel("Length", self)

        self.aftShoulderLengthValidator = QtGui.QDoubleValidator(self)
        self.aftShoulderLengthValidator.setBottom(0.0)

        self.aftShoulderLengthInput = QtGui.QLineEdit(self)
        self.aftShoulderLengthInput.setFixedWidth(100)
        self.aftShoulderLengthInput.setValidator(self.aftShoulderLengthValidator)

        self.aftShoulderThicknessLabel = QtGui.QLabel("Thickness", self)

        self.aftShoulderThicknessValidator = QtGui.QDoubleValidator(self)
        self.aftShoulderThicknessValidator.setBottom(0.0)

        self.aftShoulderThicknessInput = QtGui.QLineEdit(self)
        self.aftShoulderThicknessInput.setFixedWidth(100)
        self.aftShoulderThicknessInput.setValidator(self.aftShoulderThicknessValidator)
        self.aftShoulderThicknessInput.setEnabled(False)

        layout = QGridLayout()

        layout.addWidget(self.transitionTypeLabel, 0, 0, 1, 2)
        layout.addWidget(self.transitionTypesCombo, 0, 1)

        layout.addWidget(self.transitionStyleLabel, 1, 0)
        layout.addWidget(self.transitionStylesCombo, 1, 1)

        layout.addWidget(self.lengthLabel, 2, 0)
        layout.addWidget(self.lengthInput, 2, 1)

        layout.addWidget(self.clippedLabel, 3, 0)
        layout.addWidget(self.clippedCheckbox, 3, 1)

        layout.addWidget(self.foreRadiusLabel, 4, 0)
        layout.addWidget(self.foreRadiusInput, 4, 1)

        layout.addWidget(self.aftRadiusLabel, 5, 0)
        layout.addWidget(self.aftRadiusInput, 5, 1)

        layout.addWidget(self.coreRadiusLabel, 6, 0)
        layout.addWidget(self.coreRadiusInput, 6, 1)

        layout.addWidget(self.thicknessLabel, 7, 0)
        layout.addWidget(self.thicknessInput, 7, 1)

        layout.addWidget(self.coefficientLabel, 8, 0)
        layout.addWidget(self.coefficientInput, 8, 1)

        layout.addWidget(self.foreShoulderLabel, 9, 0)
        layout.addWidget(self.foreShoulderCheckbox, 9, 1)

        layout.addWidget(self.foreShoulderLengthLabel, 10, 0)
        layout.addWidget(self.foreShoulderLengthInput, 10, 1)

        layout.addWidget(self.foreShoulderRadiusLabel, 11, 0)
        layout.addWidget(self.foreShoulderRadiusInput, 11, 1)

        layout.addWidget(self.foreShoulderThicknessLabel, 12, 0)
        layout.addWidget(self.foreShoulderThicknessInput, 12, 1)

        layout.addWidget(self.aftShoulderLabel, 13, 0)
        layout.addWidget(self.aftShoulderCheckbox, 13, 1)

        layout.addWidget(self.aftShoulderLengthLabel, 14, 0)
        layout.addWidget(self.aftShoulderLengthInput, 14, 1)

        layout.addWidget(self.aftShoulderRadiusLabel, 15, 0)
        layout.addWidget(self.aftShoulderRadiusInput, 15, 1)

        layout.addWidget(self.aftShoulderThicknessLabel, 16, 0)
        layout.addWidget(self.aftShoulderThicknessInput, 16, 1)

        self.setLayout(layout)


class TaskPanelTransition:

    def __init__(self,obj,mode):
        self.obj = obj
        
        self.form = _TransitionDialog()
        self.form.setWindowIcon(QtGui.QIcon(":/icons/Rocket_Transition.svg"))
        
        self.form.transitionTypesCombo.currentTextChanged.connect(self.onTransitionType)
        self.form.transitionStylesCombo.currentTextChanged.connect(self.onTransitionStyle)
        self.form.lengthInput.textEdited.connect(self.onLength)
        self.form.foreRadiusInput.textEdited.connect(self.onForeRadius)
        self.form.aftRadiusInput.textEdited.connect(self.onAftRadius)
        self.form.coreRadiusInput.textEdited.connect(self.onCoreRadius)
        self.form.thicknessInput.textEdited.connect(self.onThickness)
        self.form.coefficientInput.textEdited.connect(self.onCoefficient)
        self.form.clippedCheckbox.stateChanged.connect(self.onClipped)
        self.form.foreShoulderCheckbox.stateChanged.connect(self.onForeShoulder)
        self.form.foreShoulderRadiusInput.textEdited.connect(self.onForeShoulderRadius)
        self.form.foreShoulderLengthInput.textEdited.connect(self.onForeShoulderLength)
        self.form.foreShoulderThicknessInput.textEdited.connect(self.onForeShoulderThickness)
        self.form.aftShoulderCheckbox.stateChanged.connect(self.onAftShoulder)
        self.form.aftShoulderRadiusInput.textEdited.connect(self.onAftShoulderRadius)
        self.form.aftShoulderLengthInput.textEdited.connect(self.onAftShoulderLength)
        self.form.aftShoulderThicknessInput.textEdited.connect(self.onAftShoulderThickness)
        
        self.update()
        
        if mode == 0: # fresh created
            self.obj.Proxy.execute(self.obj)  # calculate once 
            FreeCAD.Gui.SendMsgToActiveView("ViewFit")
        
    def transferTo(self):
        "Transfer from the dialog to the object" 
        self.obj.TransitionType = str(self.form.transitionTypesCombo.currentText())
        self.obj.TransitionStyle = str(self.form.transitionStylesCombo.currentText())
        self.obj.Length = _toFloat(self.form.lengthInput.text())
        self.obj.ForeRadius = _toFloat(self.form.foreRadiusInput.text())
        self.obj.AftRadius = _toFloat(self.form.aftRadiusInput.text())
        self.obj.CoreRadius = _toFloat(self.form.coreRadiusInput.text())
        self.obj.Thickness = _toFloat(self.form.thicknessInput.text())
        self.obj.Coefficient = _toFloat(self.form.coefficientInput.text())
        self.obj.Clipped = self.form.clippedCheckbox.isChecked()
        self.obj.ForeShoulder = self.form.foreShoulderCheckbox.isChecked()
        self.obj.ForeShoulderRadius = _toFloat(self.form.foreShoulderRadiusInput.text())
        self.obj.ForeShoulderLength = _toFloat(self.form.foreShoulderLengthInput.text())
        self.obj.ForeShoulderThickness = _toFloat(self.form.foreShoulderThicknessInput.text())
        self.obj.AftShoulder = self.form.aftShoulderCheckbox.isChecked()
        self.obj.AftShoulderRadius = _toFloat(self.form.aftShoulderRadiusInput.text())
        self.obj.AftShoulderLength = _toFloat(self.form.aftShoulderLengthInput.text())
        self.obj.AftShoulderThickness = _toFloat(self.form.aftShoulderThicknessInput.text())
    
    def transferFrom(self):
        "Transfer from the object to the dialog"
        self.form.transitionTypesCombo.setCurrentText(self.obj.TransitionType)
        self.form.transitionStylesCombo.setCurrentText(self.obj.TransitionStyle)
        self.form.lengthInput.setText("%f" % self.obj.Length)
        self.form.foreRadiusInput.setText("%f" % self.obj.ForeRadius)
        self.form.aftRadiusInput.setText("%f" % self.obj.AftRadius)
        self.form.coreRadiusInput.setText("%f" % self.obj.CoreRadius)
        self.form.thicknessInput.setText("%f" % self.obj.Thickness)
        self.form.coefficientInput.setText("%f" % self.obj.Coefficient)
        self.form.clippedCheckbox.setChecked(self.obj.Clipped)
        self.form.foreShoulderCheckbox.setChecked(self.obj.ForeShoulder)
        self.form.foreShoulderRadiusInput.setText("%f" % self.obj.ForeShoulderRadius)
        self.form.foreShoulderLengthInput.setText("%f" % self.obj.ForeShoulderLength)
        self.form.foreShoulderThicknessInput.setText("%f" % self.obj.ForeShoulderThickness)
        self.form.aftShoulderCheckbox.setChecked(self.obj.AftShoulder)
        self.form.aftShoulderRadiusInput.setText("%f" % self.obj.AftShoulderRadius)
        self.form.aftShoulderLengthInput.setText("%f" % self.obj.AftShoulderLength)
        self.form.aftShoulderThicknessInput.setText("%f" % self.obj.AftShoulderThickness)
        
        
    def onTransitionType(self, value):
        _msg("onTransitionType(%s)" % str(value))

        if value == TYPE_HAACK or value == TYPE_PARABOLIC:
            self.form.coefficientInput.setEnabled(True)
        elif value == TYPE_POWER:
            self.form.coefficientInput.setEnabled(True)
        else:
            self.form.coefficientInput.setEnabled(False)

        self.obj.TransitionType = value
        self.obj.Proxy.execute(self.obj)
       
    def onTransitionStyle(self, value):
        _msg("onTransitionStyle(%s)" % str(value))

        if value == STYLE_HOLLOW or value == STYLE_CAPPED:
            self.form.thicknessInput.setEnabled(True)
            self.form.coreRadiusInput.setEnabled(False)

            if self.form.foreShoulderCheckbox.isChecked():
                self.form.foreShoulderThicknessInput.setEnabled(True)
            else:
                self.form.foreShoulderThicknessInput.setEnabled(False)

            if self.form.aftShoulderCheckbox.isChecked():
                self.form.aftShoulderThicknessInput.setEnabled(True)
            else:
                self.form.aftShoulderThicknessInput.setEnabled(False)
        elif value == STYLE_SOLID_CORE:
            self.form.thicknessInput.setEnabled(False)
            self.form.coreRadiusInput.setEnabled(True)

            self.form.foreShoulderThicknessInput.setEnabled(False)
            self.form.aftShoulderThicknessInput.setEnabled(False)
        else:
            self.form.thicknessInput.setEnabled(False)
            self.form.coreRadiusInput.setEnabled(False)

            self.form.foreShoulderThicknessInput.setEnabled(False)
            self.form.aftShoulderThicknessInput.setEnabled(False)

        self.obj.TransitionStyle = value
        self.obj.Proxy.execute(self.obj)
        
    def onLength(self, value):
        _msg("onLength(%s)" % str(value))

        self.obj.Length = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onForeRadius(self, value):
        _msg("onForeRadius(%s)" % str(value))

        self.obj.ForeRadius = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onAftRadius(self, value):
        _msg("onAftRadius(%s)" % str(value))

        self.obj.AftRadius = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onCoreRadius(self, value):
        _msg("onCoreRadius(%s)" % str(value))

        self.obj.CoreRadius = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onThickness(self, value):
        _msg("onThickness(%s)" % str(value))

        self.obj.Thickness = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onCoefficient(self, value):
        _msg("onCoefficient(%s)" % str(value))

        self.obj.Coefficient = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onClipped(self, value):
        _msg("onClipped(%s)" % str(value))

        self.obj.Clipped = self.form.clippedCheckbox.isChecked()
        self.obj.Proxy.execute(self.obj)
        
    def onForeShoulder(self, value):
        _msg("onForeShoulder(%s)" % str(value))

        self.obj.ForeShoulder = self.form.foreShoulderCheckbox.isChecked()
        if self.obj.ForeShoulder:
            self.form.foreShoulderRadiusInput.setEnabled(True)
            self.form.foreShoulderLengthInput.setEnabled(True)

            selectedText = self.form.transitionStylesCombo.currentText()
            if selectedText == STYLE_HOLLOW or selectedText == STYLE_CAPPED:
                self.form.foreShoulderThicknessInput.setEnabled(True)
            else:
                self.form.foreShoulderThicknessInput.setEnabled(False)
        else:
            self.form.foreShoulderRadiusInput.setEnabled(False)
            self.form.foreShoulderLengthInput.setEnabled(False)
            self.form.foreShoulderThicknessInput.setEnabled(False)

        self.obj.Proxy.execute(self.obj)
        
    def onForeShoulderRadius(self, value):
        _msg("onForeShoulderRadius(%s)" % str(value))

        self.obj.ForeShoulderRadius = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onForeShoulderLength(self, value):
        _msg("onForeShoulderLength(%s)" % str(value))

        self.obj.ForeShoulderLength = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onForeShoulderThickness(self, value):
        _msg("onForeShoulderThickness(%s)" % str(value))

        self.obj.ForeShoulderThickness = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onAftShoulder(self, value):
        _msg("onAftShoulder(%s)" % str(value))

        self.obj.AftShoulder = self.form.aftShoulderCheckbox.isChecked()
        if self.obj.AftShoulder:
            self.form.aftShoulderRadiusInput.setEnabled(True)
            self.form.aftShoulderLengthInput.setEnabled(True)

            selectedText = self.form.transitionStylesCombo.currentText()
            if selectedText == STYLE_HOLLOW or selectedText == STYLE_CAPPED:
                self.form.aftShoulderThicknessInput.setEnabled(True)
            else:
                self.form.aftShoulderThicknessInput.setEnabled(False)
        else:
            self.form.aftShoulderRadiusInput.setEnabled(False)
            self.form.aftShoulderLengthInput.setEnabled(False)
            self.form.aftShoulderThicknessInput.setEnabled(False)

        self.obj.Proxy.execute(self.obj)
        
    def onAftShoulderRadius(self, value):
        _msg("onAftShoulderRadius(%s)" % str(value))

        self.obj.AftShoulderRadius = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onAftShoulderLength(self, value):
        _msg("onAftShoulderLength(%s)" % str(value))

        self.obj.AftShoulderLength = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onAftShoulderThickness(self, value):
        _msg("onAftShoulderThickness(%s)" % str(value))

        self.obj.AftShoulderThickness = _toFloat(value)
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
        _msg('accept(self)')
        self.transferTo()
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.resetEdit()
        
                    
    def reject(self):
        _msg('reject(self)')
        FreeCADGui.ActiveDocument.resetEdit()
        FreeCAD.ActiveDocument.abortTransaction()
        FreeCAD.ActiveDocument.recompute() #??? Should the object not be created?
