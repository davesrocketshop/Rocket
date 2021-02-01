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
    

from PySide import QtGui, QtCore
import FreeCAD
import FreeCADGui
import Part
import math
import os

import sys
from PySide2.QtWidgets import QApplication, QDialog, QLineEdit, QPushButton,QHBoxLayout,QVBoxLayout,QGridLayout

from App.Constants import TYPE_CONE, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_VON_KARMAN, TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_POWER
from App.Constants import STYLE_CAPPED, STYLE_HOLLOW, STYLE_SOLID, STYLE_SOLID_CORE

from App.ShapeTransition import ShapeTransition
from Gui.ViewTransition import ViewProviderTransition

userCancelled = "Cancelled"
userOK = "OK"

class CmdTransitionDialog(QDialog):

    def __init__(self, parent=None):
        super(CmdTransitionDialog, self).__init__(parent)


        # define our window
        self.setGeometry(250, 250, 400, 350)
        self.setWindowTitle("Transition Design Wizard")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        # Select the type of nose cone
        self.transitionTypeLabel = QtGui.QLabel("Transition type", self)

        self.transitionTypes = (TYPE_CONE,
                                #TYPE_ELLIPTICAL,
                                #TYPE_OGIVE,
                                #TYPE_PARABOLA,
                                #TYPE_PARABOLIC,
                                #TYPE_POWER,
                                #TYPE_VON_KARMAN,
                                #TYPE_HAACK
                                )
        self.transitionTypesCombo = QtGui.QComboBox(self)
        self.transitionTypesCombo.addItems(self.transitionTypes)
        self.transitionTypesCombo.setCurrentIndex(self.transitionTypes.index(TYPE_CONE))
        self.transitionTypesCombo.activated[str].connect(self.onTransitionType)

        self.clippedLabel = QtGui.QLabel("Clipped", self)

        self.clippedCheckbox = QtGui.QCheckBox(self)
        self.clippedCheckbox.setCheckState(QtCore.Qt.Checked)
        # self.clippedCheckbox.stateChanged.connect(self.onClipped)

        # Select the type of sketch
        self.transitionStyleLabel = QtGui.QLabel("Transition Style", self)

        self.transitionStyles = (STYLE_SOLID,
                                STYLE_SOLID_CORE,
                                STYLE_HOLLOW,
                                STYLE_CAPPED)
        self.transitionStylesCombo = QtGui.QComboBox(self)
        self.transitionStylesCombo.addItems(self.transitionStyles)
        self.transitionStylesCombo.setCurrentIndex(self.transitionStyles.index(STYLE_SOLID))
        self.transitionStylesCombo.activated[str].connect(self.onTransitionStyle)

        # Get the nose cone paramters: length, width, etc...
        self.lengthLabel = QtGui.QLabel("Length", self)

        self.lengthValidator = QtGui.QDoubleValidator(self)
        self.lengthValidator.setBottom(0.0)

        self.lengthInput = QtGui.QLineEdit(self)
        self.lengthInput.setText("30.00")
        self.lengthInput.setFixedWidth(100)
        self.lengthInput.setValidator(self.lengthValidator)

        self.foreRadiusLabel = QtGui.QLabel("Forward Radius", self)

        self.foreRadiusValidator = QtGui.QDoubleValidator(self)
        self.foreRadiusValidator.setBottom(0.0)

        self.foreRadiusInput = QtGui.QLineEdit(self)
        self.foreRadiusInput.setText("10.00")
        self.foreRadiusInput.setFixedWidth(100)
        self.foreRadiusInput.setValidator(self.foreRadiusValidator)

        self.aftRadiusLabel = QtGui.QLabel("Aft Radius", self)

        self.aftRadiusValidator = QtGui.QDoubleValidator(self)
        self.aftRadiusValidator.setBottom(0.0)

        self.aftRadiusInput = QtGui.QLineEdit(self)
        self.aftRadiusInput.setText("20.00")
        self.aftRadiusInput.setFixedWidth(100)
        self.aftRadiusInput.setValidator(self.aftRadiusValidator)

        self.coreRadiusLabel = QtGui.QLabel("Core Radius", self)

        self.coreRadiusValidator = QtGui.QDoubleValidator(self)
        self.coreRadiusValidator.setBottom(0.0)

        self.coreRadiusInput = QtGui.QLineEdit(self)
        self.coreRadiusInput.setText("")
        self.coreRadiusInput.setFixedWidth(100)
        self.coreRadiusInput.setValidator(self.aftRadiusValidator)
        self.coreRadiusInput.setEnabled(False)

        self.thicknessLabel = QtGui.QLabel("Thickness", self)

        self.thicknessValidator = QtGui.QDoubleValidator(self)
        self.thicknessValidator.setBottom(0.0)

        self.thicknessInput = QtGui.QLineEdit(self)
        self.thicknessInput.setText("2.00")
        self.thicknessInput.setFixedWidth(100)
        self.thicknessInput.setValidator(self.thicknessValidator)

        self.coefficientLabel = QtGui.QLabel("Coefficient", self)

        self.coefficientValidator = QtGui.QDoubleValidator(self)
        self.coefficientValidator.setBottom(0.0)

        self.coefficientInput = QtGui.QLineEdit(self)
        self.coefficientInput.setText("")
        self.coefficientInput.setFixedWidth(100)
        self.coefficientInput.setValidator(self.coefficientValidator)
        self.coefficientInput.setEnabled(False)

        self.foreShoulderLabel = QtGui.QLabel("Forward Shoulder", self)

        self.foreShoulderCheckbox = QtGui.QCheckBox(self)
        self.foreShoulderCheckbox.setCheckState(QtCore.Qt.Unchecked)
        self.foreShoulderCheckbox.stateChanged.connect(self.onForeShoulder)

        self.foreShoulderRadiusLabel = QtGui.QLabel("Radius", self)

        self.foreShoulderRadiusValidator = QtGui.QDoubleValidator(self)
        self.foreShoulderRadiusValidator.setBottom(0.0)

        self.foreShoulderRadiusInput = QtGui.QLineEdit(self)
        self.foreShoulderRadiusInput.setText("")
        self.foreShoulderRadiusInput.setFixedWidth(100)
        self.foreShoulderRadiusInput.setValidator(self.foreShoulderRadiusValidator)
        self.foreShoulderRadiusInput.setEnabled(False)

        self.foreShoulderLengthLabel = QtGui.QLabel("Length", self)

        self.foreShoulderLengthValidator = QtGui.QDoubleValidator(self)
        self.foreShoulderLengthValidator.setBottom(0.0)

        self.foreShoulderLengthInput = QtGui.QLineEdit(self)
        self.foreShoulderLengthInput.setText("")
        self.foreShoulderLengthInput.setFixedWidth(100)
        self.foreShoulderLengthInput.setValidator(self.foreShoulderLengthValidator)
        self.foreShoulderLengthInput.setEnabled(False)

        self.foreShoulderThicknessLabel = QtGui.QLabel("Thickness", self)

        self.foreShoulderThicknessValidator = QtGui.QDoubleValidator(self)
        self.foreShoulderThicknessValidator.setBottom(0.0)

        self.foreShoulderThicknessInput = QtGui.QLineEdit(self)
        self.foreShoulderThicknessInput.setText("")
        self.foreShoulderThicknessInput.setFixedWidth(100)
        self.foreShoulderThicknessInput.setValidator(self.foreShoulderThicknessValidator)
        self.foreShoulderThicknessInput.setEnabled(False)

        self.aftShoulderLabel = QtGui.QLabel("Aft Shoulder", self)

        self.aftShoulderCheckbox = QtGui.QCheckBox(self)
        self.aftShoulderCheckbox.setCheckState(QtCore.Qt.Unchecked)
        self.aftShoulderCheckbox.stateChanged.connect(self.onAftShoulder)

        self.aftShoulderRadiusLabel = QtGui.QLabel("Radius", self)

        self.aftShoulderRadiusValidator = QtGui.QDoubleValidator(self)
        self.aftShoulderRadiusValidator.setBottom(0.0)

        self.aftShoulderRadiusInput = QtGui.QLineEdit(self)
        self.aftShoulderRadiusInput.setText("")
        self.aftShoulderRadiusInput.setFixedWidth(100)
        self.aftShoulderRadiusInput.setValidator(self.aftShoulderRadiusValidator)
        self.aftShoulderRadiusInput.setEnabled(False)

        self.aftShoulderLengthLabel = QtGui.QLabel("Length", self)

        self.aftShoulderLengthValidator = QtGui.QDoubleValidator(self)
        self.aftShoulderLengthValidator.setBottom(0.0)

        self.aftShoulderLengthInput = QtGui.QLineEdit(self)
        self.aftShoulderLengthInput.setText("")
        self.aftShoulderLengthInput.setFixedWidth(100)
        self.aftShoulderLengthInput.setValidator(self.aftShoulderLengthValidator)
        self.aftShoulderLengthInput.setEnabled(False)

        self.aftShoulderThicknessLabel = QtGui.QLabel("Thickness", self)

        self.aftShoulderThicknessValidator = QtGui.QDoubleValidator(self)
        self.aftShoulderThicknessValidator.setBottom(0.0)

        self.aftShoulderThicknessInput = QtGui.QLineEdit(self)
        self.aftShoulderThicknessInput.setText("")
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


    def onTransitionType(self, selectedText):
        if selectedText == TYPE_HAACK or selectedText == TYPE_PARABOLIC:
            self.coefficientInput.setText("1.00")
            self.coefficientInput.setEnabled(True)
        elif selectedText == TYPE_POWER:
            self.coefficientInput.setText("1.00")
            self.coefficientInput.setEnabled(True)
        else:
            self.coefficientInput.setText("")
            self.coefficientInput.setEnabled(False)

    def onTransitionStyle(self, selectedText):
        if selectedText == STYLE_HOLLOW or selectedText == STYLE_CAPPED:
            self.thicknessInput.setText("2.00")
            self.thicknessInput.setEnabled(True)
            self.coreRadiusInput.setText("")
            self.coreRadiusInput.setEnabled(False)

            if self.foreShoulderCheckbox.isChecked():
                self.foreShoulderThicknessInput.setText("2.00")
                self.foreShoulderThicknessInput.setEnabled(True)
            else:
                self.foreShoulderThicknessInput.setText("")
                self.foreShoulderThicknessInput.setEnabled(False)

            if self.aftShoulderCheckbox.isChecked():
                self.aftShoulderThicknessInput.setText("2.00")
                self.aftShoulderThicknessInput.setEnabled(True)
            else:
                self.aftShoulderThicknessInput.setText("")
                self.aftShoulderThicknessInput.setEnabled(False)
        elif selectedText == STYLE_SOLID_CORE:
            self.thicknessInput.setText("")
            self.thicknessInput.setEnabled(False)
            self.coreRadiusInput.setText("5.00")
            self.coreRadiusInput.setEnabled(True)

            self.foreShoulderThicknessInput.setText("")
            self.foreShoulderThicknessInput.setEnabled(False)
            self.aftShoulderThicknessInput.setText("")
            self.aftShoulderThicknessInput.setEnabled(False)
        else:
            self.thicknessInput.setText("")
            self.thicknessInput.setEnabled(False)
            self.coreRadiusInput.setText("")
            self.coreRadiusInput.setEnabled(False)

            self.foreShoulderThicknessInput.setText("")
            self.foreShoulderThicknessInput.setEnabled(False)
            self.aftShoulderThicknessInput.setText("")
            self.aftShoulderThicknessInput.setEnabled(False)

    def onForeShoulder(self, state):
        if self.foreShoulderCheckbox.isChecked():
            self.foreShoulderRadiusInput.setText("8.00")
            self.foreShoulderRadiusInput.setEnabled(True)

            self.foreShoulderLengthInput.setText("10.00")
            self.foreShoulderLengthInput.setEnabled(True)

            selectedText = self.transitionStylesCombo.currentText()
            if selectedText == STYLE_HOLLOW or selectedText == STYLE_CAPPED:
                self.foreShoulderThicknessInput.setText("2.00")
                self.foreShoulderThicknessInput.setEnabled(True)
            else:
                self.foreShoulderThicknessInput.setText("")
                self.foreShoulderThicknessInput.setEnabled(False)
        else:
            self.foreShoulderRadiusInput.setText("")
            self.foreShoulderRadiusInput.setEnabled(False)

            self.foreShoulderLengthInput.setText("")
            self.foreShoulderLengthInput.setEnabled(False)

            self.foreShoulderThicknessInput.setText("")
            self.foreShoulderThicknessInput.setEnabled(False)

    def onAftShoulder(self, state):
        if self.aftShoulderCheckbox.isChecked():
            self.aftShoulderRadiusInput.setText("18.00")
            self.aftShoulderRadiusInput.setEnabled(True)

            self.aftShoulderLengthInput.setText("10.00")
            self.aftShoulderLengthInput.setEnabled(True)

            selectedText = self.transitionStylesCombo.currentText()
            if selectedText == STYLE_HOLLOW or selectedText == STYLE_CAPPED:
                self.aftShoulderThicknessInput.setText("2.00")
                self.aftShoulderThicknessInput.setEnabled(True)
            else:
                self.aftShoulderThicknessInput.setText("")
                self.aftShoulderThicknessInput.setEnabled(False)
        else:
            self.aftShoulderRadiusInput.setText("")
            self.aftShoulderRadiusInput.setEnabled(False)

            self.aftShoulderLengthInput.setText("")
            self.aftShoulderLengthInput.setEnabled(False)

            self.aftShoulderThicknessInput.setText("")
            self.aftShoulderThicknessInput.setEnabled(False)

    def onCancel(self):
        self.result = userCancelled
        self.close()

class CmdTransitionTaskPanel:
    def __init__(self):
        self.form = CmdTransitionDialog()

    def _toFloat(self, input, defaultValue = 0.0):
        if input == '':
            return defaultValue
        return float(input)

        
    def accept(self):
    
        if FreeCAD.ActiveDocument == None:
            FreeCAD.newDocument("Transition")


        transitionType = self.form.transitionTypesCombo.currentText()
        clipped = self.form.clippedCheckbox.isChecked()
        transitionStyle = self.form.transitionStylesCombo.currentText()
        length = self._toFloat(self.form.lengthInput.text())
        foreRadius = self._toFloat(self.form.foreRadiusInput.text())
        aftRadius = self._toFloat(self.form.aftRadiusInput.text())
        coreRadius = self._toFloat(self.form.coreRadiusInput.text())
        thickness = self._toFloat(self.form.thicknessInput.text())
        coefficient = self._toFloat(self.form.coefficientInput.text())

        foreShoulder = self.form.foreShoulderCheckbox.isChecked()
        foreShoulderRadius = self._toFloat(self.form.foreShoulderRadiusInput.text())
        foreShoulderLength = self._toFloat(self.form.foreShoulderLengthInput.text())
        foreShoulderThickness = self._toFloat(self.form.foreShoulderThicknessInput.text())

        aftShoulder = self.form.aftShoulderCheckbox.isChecked()
        aftShoulderRadius = self._toFloat(self.form.aftShoulderRadiusInput.text())
        aftShoulderLength = self._toFloat(self.form.aftShoulderLengthInput.text())
        aftShoulderThickness = self._toFloat(self.form.aftShoulderThicknessInput.text())

        transition = FreeCAD.ActiveDocument.addObject('Part::FeaturePython', 'Transition')
        ShapeTransition(transition)
        ViewProviderTransition(transition.ViewObject)

        transition.Clipped = clipped
        transition.Length = length
        transition.ForeRadius = foreRadius
        transition.AftRadius = aftRadius
        transition.CoreRadius = coreRadius
        transition.Thickness = thickness
        transition.Coefficient = coefficient
        transition.ForeShoulder = foreShoulder
        transition.ForeShoulderRadius = foreShoulderRadius
        transition.ForeShoulderLength = foreShoulderLength
        transition.ForeShoulderThickness = foreShoulderThickness
        transition.AftShoulder = aftShoulder
        transition.AftShoulderRadius = aftShoulderRadius
        transition.AftShoulderLength = aftShoulderLength
        transition.AftShoulderThickness = aftShoulderThickness

        transition.TransitionType = str(transitionType)
        transition.TransitionStyle = str(transitionStyle)

        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.SendMsgToActiveView('ViewFit')

        self.form.result = userOK

        FreeCADGui.Control.closeDialog()

class CmdTransition:
    def Activated(self):
        panel = CmdTransitionTaskPanel()
        FreeCADGui.Control.showDialog(panel)

    def IsActive(self):
        if FreeCAD.ActiveDocument == None:
            return False
        return True
        
    def GetResources(self):
        return {'MenuText': 'Transition',
                'ToolTip': 'Transition design',
                'Pixmap': 'freecad'}
