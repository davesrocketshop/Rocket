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

userCancelled = "Cancelled"
# userOK = "OK"

class _NoseConeDialog(QDialog):

    def __init__(self, parent=None):
        super(_NoseConeDialog, self).__init__(parent)


        # define our window
        self.setGeometry(250, 250, 400, 350)
        self.setWindowTitle("Nose Cone Parameter")
        # self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

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
        self.noseConeTypesCombo.activated[str].connect(self.onNoseConeType)

        # Select the type of sketch
        self.noseStyleLabel = QtGui.QLabel("Nose Style", self)

        self.noseStyles = (STYLE_SOLID,
                                STYLE_HOLLOW,
                                STYLE_CAPPED)
        self.noseStylesCombo = QtGui.QComboBox(self)
        self.noseStylesCombo.addItems(self.noseStyles)
        self.noseStylesCombo.setCurrentIndex(self.noseStyles.index(STYLE_HOLLOW))
        self.noseStylesCombo.activated[str].connect(self.onNoseStyle)

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
        self.shoulderCheckbox.stateChanged.connect(self.onShoulder)

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


    def onNoseConeType(self, selectedText):
        if selectedText == TYPE_HAACK or selectedText == TYPE_PARABOLIC:
            self.coefficientInput.setText("1.00")
            self.coefficientInput.setEnabled(True)
        elif selectedText == TYPE_POWER:
            self.coefficientInput.setText("1.00")
            self.coefficientInput.setEnabled(True)
        else:
            self.coefficientInput.setText("")
            self.coefficientInput.setEnabled(False)

    def onNoseStyle(self, selectedText):
        if selectedText == STYLE_HOLLOW or selectedText == STYLE_CAPPED:
            self.thicknessInput.setText("2.00")
            self.thicknessInput.setEnabled(True)

            if self.shoulderCheckbox.isChecked():
                self.shoulderThicknessInput.setText("2.00")
                self.shoulderThicknessInput.setEnabled(True)
            else:
                self.shoulderThicknessInput.setText("")
                self.shoulderThicknessInput.setEnabled(False)
        else:
            self.thicknessInput.setText("")
            self.thicknessInput.setEnabled(False)

            self.shoulderThicknessInput.setText("")
            self.shoulderThicknessInput.setEnabled(False)

    def onShoulder(self, state):
        if self.shoulderCheckbox.isChecked():
            self.shoulderRadiusInput.setText("8.00")
            self.shoulderRadiusInput.setEnabled(True)

            self.shoulderLengthInput.setText("10.00")
            self.shoulderLengthInput.setEnabled(True)

            selectedText = self.noseStylesCombo.currentText()
            if selectedText == STYLE_HOLLOW or selectedText == STYLE_CAPPED:
                self.shoulderThicknessInput.setText("2.00")
                self.shoulderThicknessInput.setEnabled(True)
            else:
                self.shoulderThicknessInput.setText("")
                self.shoulderThicknessInput.setEnabled(False)
        else:
            self.shoulderRadiusInput.setText("")
            self.shoulderRadiusInput.setEnabled(False)

            self.shoulderLengthInput.setText("")
            self.shoulderLengthInput.setEnabled(False)

            self.shoulderThicknessInput.setText("")
            self.shoulderThicknessInput.setEnabled(False)

    # def onCancel(self):
    #     self.result = userCancelled
    #     self.close()

class TaskPanelNoseCone:

    def __init__(self,obj,mode):
        self.obj = obj
        
        self.form = _NoseConeDialog()
        self.form.setWindowIcon(QtGui.QIcon(":/icons/Rocket_NoseCone.svg"))
        
        # QtCore.QObject.connect(self.form.Quantity_Modules, QtCore.SIGNAL("valueChanged(double)"), self.modulesChanged)
        # QtCore.QObject.connect(self.form.Quantity_PressureAngle, QtCore.SIGNAL("valueChanged(double)"), self.angleChanged)
        # QtCore.QObject.connect(self.form.spinBox_NumberOfTeeth, QtCore.SIGNAL("valueChanged(int)"), self.numTeethChanged)
        # QtCore.QObject.connect(self.form.comboBox_HighPrecision, QtCore.SIGNAL("currentIndexChanged(int)"), self.numCurvesChanged)
        # #QtCore.QObject.connect(self.form.comboBox_ExternalGear, QtCore.SIGNAL("activated(QString)"), self.externalGearChanged)
        # #QtCore.QObject.connect(self.form.comboBox_ExternalGear, QtCore.SIGNAL("currentIndexChanged(int)"), self.externalGearChanged)
        # QtCore.QObject.connect(self.form.comboBox_ExternalGear, QtCore.SIGNAL("currentIndexChanged(int)"), self.externalGearChanged)
        
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
