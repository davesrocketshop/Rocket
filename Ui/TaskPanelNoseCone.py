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

from App.Constants import TYPE_CONE, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_VON_KARMAN, TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_POWER
from App.Constants import STYLE_CAPPED, STYLE_HOLLOW, STYLE_SOLID

from App.Utilities import _toFloat, _msg

class _NoseConeDialog(QDialog):

    def __init__(self, parent=None):
        super(_NoseConeDialog, self).__init__(parent)


        # define our window
        self.setGeometry(250, 250, 400, 350)
        self.setWindowTitle("Nose Cone Parameter")

        # Select the type of nose cone
        self.noseConeTypeLabel = QtGui.QLabel("Nose cone type", self)

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
        self.noseConeTypesCombo.setCurrentIndex(self.noseConeTypes.index(TYPE_VON_KARMAN))

        # Select the type of sketch
        self.noseStyleLabel = QtGui.QLabel("Nose Style", self)

        self.noseStyles = (STYLE_SOLID,
                                STYLE_HOLLOW,
                                STYLE_CAPPED)
        self.noseStylesCombo = QtGui.QComboBox(self)
        self.noseStylesCombo.addItems(self.noseStyles)
        self.noseStylesCombo.setCurrentIndex(self.noseStyles.index(STYLE_HOLLOW))

        # Get the nose cone parameters: length, width, etc...
        self.lengthLabel = QtGui.QLabel("Length (mm)", self)

        self.lengthValidator = QtGui.QDoubleValidator(self)
        self.lengthValidator.setBottom(0.0)

        self.lengthInput = QtGui.QLineEdit(self)
        self.lengthInput.setText("60.00")
        self.lengthInput.setFixedWidth(100)
        self.lengthInput.setValidator(self.lengthValidator)

        self.radiusLabel = QtGui.QLabel("Radius (mm)", self)

        self.radiusValidator = QtGui.QDoubleValidator(self)
        self.radiusValidator.setBottom(0.0)

        self.radiusInput = QtGui.QLineEdit(self)
        self.radiusInput.setText("10.00")
        self.radiusInput.setFixedWidth(100)
        self.radiusInput.setValidator(self.radiusValidator)

        self.thicknessLabel = QtGui.QLabel("Thickness (mm)", self)

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

        self.shoulderLabel = QtGui.QLabel("Shoulder", self)

        self.shoulderCheckbox = QtGui.QCheckBox(self)
        self.shoulderCheckbox.setCheckState(QtCore.Qt.Unchecked)

        self.shoulderRadiusLabel = QtGui.QLabel("Radius (mm)", self)

        self.shoulderRadiusValidator = QtGui.QDoubleValidator(self)
        self.shoulderRadiusValidator.setBottom(0.0)

        self.shoulderRadiusInput = QtGui.QLineEdit(self)
        self.shoulderRadiusInput.setText("")
        self.shoulderRadiusInput.setFixedWidth(100)
        self.shoulderRadiusInput.setValidator(self.shoulderRadiusValidator)
        self.shoulderRadiusInput.setEnabled(False)

        self.shoulderLengthLabel = QtGui.QLabel("Length (mm)", self)

        self.shoulderLengthValidator = QtGui.QDoubleValidator(self)
        self.shoulderLengthValidator.setBottom(0.0)

        self.shoulderLengthInput = QtGui.QLineEdit(self)
        self.shoulderLengthInput.setText("")
        self.shoulderLengthInput.setFixedWidth(100)
        self.shoulderLengthInput.setValidator(self.shoulderLengthValidator)
        self.shoulderLengthInput.setEnabled(False)

        self.shoulderThicknessLabel = QtGui.QLabel("Thickness (mm)", self)

        self.shoulderThicknessValidator = QtGui.QDoubleValidator(self)
        self.shoulderThicknessValidator.setBottom(0.0)

        self.shoulderThicknessInput = QtGui.QLineEdit(self)
        self.shoulderThicknessInput.setText("")
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

        layout.addWidget(self.shoulderLengthLabel, 7, 0)
        layout.addWidget(self.shoulderLengthInput, 7, 1)

        layout.addWidget(self.shoulderRadiusLabel, 8, 0)
        layout.addWidget(self.shoulderRadiusInput, 8, 1)

        layout.addWidget(self.shoulderThicknessLabel, 9, 0)
        layout.addWidget(self.shoulderThicknessInput, 9, 1)

        self.setLayout(layout)

class TaskPanelNoseCone:

    def __init__(self,obj,mode):
        self.obj = obj
        
        self.form = _NoseConeDialog()
        self.form.setWindowIcon(QtGui.QIcon(":/icons/Rocket_NoseCone.svg"))
        
        QtCore.QObject.connect(self.form.noseConeTypesCombo, QtCore.SIGNAL("currentTextChanged(QString)"), self.onNoseType)
        QtCore.QObject.connect(self.form.noseStylesCombo, QtCore.SIGNAL("currentTextChanged(QString)"), self.onNoseStyle)

        self.form.lengthInput.textEdited.connect(self.onLengthChanged)
        self.form.radiusInput.textEdited.connect(self.onRadiusChanged)
        self.form.thicknessInput.textEdited.connect(self.onThicknessChanged)
        self.form.coefficientInput.textEdited.connect(self.onCoefficientChanged)

        self.form.shoulderCheckbox.stateChanged.connect(self.onShoulderChanged)
        self.form.shoulderRadiusInput.textEdited.connect(self.onShoulderRadiusChanged)
        self.form.shoulderLengthInput.textEdited.connect(self.onShoulderLengthChanged)
        self.form.shoulderThicknessInput.textEdited.connect(self.onShoulderThicknessChanged)
        
        self.update()
        
        if mode == 0: # fresh created
            self.obj.Proxy.execute(self.obj)  # calculate once 
            FreeCAD.Gui.SendMsgToActiveView("ViewFit")
        
    def transferTo(self):
        "Transfer from the dialog to the object" 
        self.obj.NoseType = str(self.form.noseConeTypesCombo.currentText())
        self.obj.NoseStyle = str(self.form.noseStylesCombo.currentText())
        self.obj.Length = _toFloat(self.form.lengthInput.text())
        self.obj.Radius = _toFloat(self.form.radiusInput.text())
        self.obj.Thickness = _toFloat(self.form.thicknessInput.text())
        self.obj.Coefficient = _toFloat(self.form.coefficientInput.text())
        self.obj.Shoulder = self.form.shoulderCheckbox.isChecked()
        self.obj.ShoulderRadius = _toFloat(self.form.shoulderRadiusInput.text())
        self.obj.ShoulderLength = _toFloat(self.form.shoulderLengthInput.text())
        self.obj.ShoulderThickness = _toFloat(self.form.shoulderThicknessInput.text())
    
    def transferFrom(self):
        "Transfer from the object to the dialog"
        self.form.noseConeTypesCombo.setCurrentIndex(self.form.noseConeTypes.index(self.obj.NoseType))
        self.form.noseStylesCombo.setCurrentIndex(self.form.noseStyles.index(self.obj.NoseStyle))
        self.form.lengthInput.setText("%f" % self.obj.Length)
        self.form.radiusInput.setText("%f" % self.obj.Radius)
        self.form.thicknessInput.setText("%f" % self.obj.Thickness)
        self.form.coefficientInput.setText("%f" % self.obj.Coefficient)
        if self.obj.Shoulder:
            self.form.shoulderCheckbox.setCheckState(QtCore.Qt.Checked)
        else:
            self.form.shoulderCheckbox.setCheckState(QtCore.Qt.Unchecked)
        self.form.shoulderRadiusInput.setText("%f" % self.obj.ShoulderRadius)
        self.form.shoulderLengthInput.setText("%f" % self.obj.ShoulderLength)
        self.form.shoulderThicknessInput.setText("%f" % self.obj.ShoulderThickness)
        
    def onNoseType(self, value):
        _msg("onNoseType(%s)" % str(value))

        if value == TYPE_HAACK or value == TYPE_PARABOLIC:
            self.form.coefficientInput.setEnabled(True)
        elif value == TYPE_POWER:
            self.form.coefficientInput.setEnabled(True)
        else:
            self.form.coefficientInput.setEnabled(False)

        self.obj.NoseType = value
        self.obj.Proxy.execute(self.obj)
        
    def onNoseStyle(self, value):
        _msg("onNoseStyle(%s)" % str(value))

        if value == STYLE_HOLLOW or value == STYLE_CAPPED:
            self.form.thicknessInput.setEnabled(True)

            if self.form.shoulderCheckbox.isChecked():
                self.form.shoulderThicknessInput.setEnabled(True)
            else:
                self.form.shoulderThicknessInput.setEnabled(False)
        else:
            self.form.thicknessInput.setEnabled(False)
            self.form.shoulderThicknessInput.setEnabled(False)

        self.obj.NoseStyle = value
        self.obj.Proxy.execute(self.obj)
        
    def onLengthChanged(self, value):
        _msg("onLengthChanged(%s)" % str(value))

        self.obj.Length = _toFloat(value)
        self.obj.Proxy.execute(self.obj)

        
    def onRadiusChanged(self, value):
        _msg("onRadiusChanged(%s)" % str(value))

        self.obj.Radius = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onThicknessChanged(self, value):
        _msg("onThicknessChanged(%s)" % str(value))

        self.obj.Thickness = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onCoefficientChanged(self, value):
        _msg("onCoefficientChanged(%s)" % str(value))

        self.obj.Coefficient = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onShoulderChanged(self, value):
        _msg("onShoulderChanged(%s)" % str(value))

        self.obj.Shoulder = self.form.shoulderCheckbox.isChecked()
        if self.obj.Shoulder:
            self.form.shoulderRadiusInput.setEnabled(True)
            self.form.shoulderLengthInput.setEnabled(True)

            selectedText = self.form.noseStylesCombo.currentText()
            if selectedText == STYLE_HOLLOW or selectedText == STYLE_CAPPED:
                self.form.shoulderThicknessInput.setEnabled(True)
            else:
                self.form.shoulderThicknessInput.setEnabled(False)
        else:
            self.form.shoulderRadiusInput.setEnabled(False)
            self.form.shoulderLengthInput.setEnabled(False)
            self.form.shoulderThicknessInput.setEnabled(False)

        self.obj.Proxy.execute(self.obj)
        
    def onShoulderRadiusChanged(self, value):
        _msg("onShoulderRadiusChanged(%s)" % str(value))

        self.obj.ShoulderRadius = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onShoulderLengthChanged(self, value):
        _msg("onShoulderLengthChanged(%s)" % str(value))

        self.obj.ShoulderLength = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onShoulderThicknessChanged(self, value):
        _msg("onShoulderThicknessChanged(%s)" % str(value))

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
        _msg('accept(self)')
        self.transferTo()
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.resetEdit()
        
                    
    def reject(self):
        _msg('reject(self)')
        FreeCADGui.ActiveDocument.resetEdit()
        FreeCAD.ActiveDocument.abortTransaction()
        FreeCAD.ActiveDocument.recompute() #??? Should the object not be created?
