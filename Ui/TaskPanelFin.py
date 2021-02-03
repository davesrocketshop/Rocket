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
"""Class for drawing fins"""

__title__ = "FreeCAD Fins"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    

import FreeCAD
import FreeCADGui

from PySide import QtGui, QtCore
from PySide2.QtWidgets import QDialog, QGridLayout
import math

from App.Constants import FIN_TYPE_TRAPEZOID, FIN_TYPE_ELLIPSE, FIN_TYPE_TUBE, FIN_TYPE_SKETCH
from App.Constants import FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL

from App.Utilities import _toFloat, _err

class _FinDialog(QDialog):

    def __init__(self, parent=None):
        super(_FinDialog, self).__init__(parent)


        # define our window
        self.setGeometry(250, 250, 400, 350)
        self.setWindowTitle("Fin Parameter")

        # Select the type of nose cone
        self.finTypeLabel = QtGui.QLabel("Fin type", self)

        self.finTypes = (FIN_TYPE_TRAPEZOID, FIN_TYPE_ELLIPSE, FIN_TYPE_TUBE, FIN_TYPE_SKETCH)
        self.finTypesCombo = QtGui.QComboBox(self)
        self.finTypesCombo.addItems(self.finTypes)

        # Select the type of cross section
        self.finCrossSectionLabel = QtGui.QLabel("Fin Cross Section", self)

        self.finCrossSections = (FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL)
        self.finCrossSectionsCombo = QtGui.QComboBox(self)
        self.finCrossSectionsCombo.addItems(self.finCrossSections)

        # Get the fin parameters: length, width, etc...
        self.rootChordLabel = QtGui.QLabel("Root Chord", self)

        self.rootChordValidator = QtGui.QDoubleValidator(self)
        self.rootChordValidator.setBottom(0.0)

        self.rootChordInput = QtGui.QLineEdit(self)
        self.rootChordInput.setFixedWidth(100)
        self.rootChordInput.setValidator(self.rootChordValidator)

        self.tipChordLabel = QtGui.QLabel("Tip Chord", self)

        self.tipChordValidator = QtGui.QDoubleValidator(self)
        self.tipChordValidator.setBottom(0.0)

        self.tipChordInput = QtGui.QLineEdit(self)
        self.tipChordInput.setFixedWidth(100)
        self.tipChordInput.setValidator(self.tipChordValidator)

        self.heightLabel = QtGui.QLabel("Height", self)

        self.heightValidator = QtGui.QDoubleValidator(self)
        self.heightValidator.setBottom(0.0)

        self.heightInput = QtGui.QLineEdit(self)
        self.heightInput.setFixedWidth(100)
        self.heightInput.setValidator(self.heightValidator)

        # Sweep can be forward (-sweep) or backward (+sweep)
        self.sweepLengthLabel = QtGui.QLabel("Sweep Length", self)

        self.sweepLengthInput = QtGui.QLineEdit(self)
        self.sweepLengthInput.setFixedWidth(100)

        # Sweep angle is tied to sweep length. It can be forward (> -90) or backward (< 90)
        self.sweepAngleLabel = QtGui.QLabel("Sweep Angle", self)

        self.sweepAngleValidator = QtGui.QDoubleValidator(self)
        self.sweepAngleValidator.setBottom(-90.0)
        self.sweepAngleValidator.setTop(90.0)

        self.sweepAngleInput = QtGui.QLineEdit(self)
        self.sweepAngleInput.setFixedWidth(100)
        self.sweepAngleInput.setValidator(self.sweepAngleValidator)

        self.thicknessLabel = QtGui.QLabel("Thickness", self)

        self.thicknessValidator = QtGui.QDoubleValidator(self)
        self.thicknessValidator.setBottom(0.0)

        self.thicknessInput = QtGui.QLineEdit(self)
        self.thicknessInput.setFixedWidth(100)
        self.thicknessInput.setValidator(self.thicknessValidator)

        layout = QGridLayout()

        layout.addWidget(self.finTypeLabel, 0, 0, 1, 2)
        layout.addWidget(self.finTypesCombo, 0, 1)

        layout.addWidget(self.finCrossSectionLabel, 1, 0)
        layout.addWidget(self.finCrossSectionsCombo, 1, 1)

        layout.addWidget(self.rootChordLabel, 2, 0)
        layout.addWidget(self.rootChordInput, 2, 1)

        layout.addWidget(self.tipChordLabel, 3, 0)
        layout.addWidget(self.tipChordInput, 3, 1)

        layout.addWidget(self.heightLabel, 4, 0)
        layout.addWidget(self.heightInput, 4, 1)

        layout.addWidget(self.sweepLengthLabel, 5, 0)
        layout.addWidget(self.sweepLengthInput, 5, 1)

        layout.addWidget(self.sweepAngleLabel, 6, 0)
        layout.addWidget(self.sweepAngleInput, 6, 1)

        layout.addWidget(self.thicknessLabel, 7, 0)
        layout.addWidget(self.thicknessInput, 7, 1)

        self.setLayout(layout)

class TaskPanelFin:

    def __init__(self,obj,mode):
        self.obj = obj
        
        self.form = _FinDialog()
        self.form.setWindowIcon(QtGui.QIcon(":/icons/Rocket_Fin.svg"))
        
        self.form.finTypesCombo.currentTextChanged.connect(self.onFinTypes)
        self.form.finCrossSectionsCombo.currentTextChanged.connect(self.onFinCrossSection)

        self.form.rootChordInput.textEdited.connect(self.onRootChord)
        self.form.tipChordInput.textEdited.connect(self.onTipChord)
        self.form.heightInput.textEdited.connect(self.onHeight)
        self.form.sweepLengthInput.textEdited.connect(self.onSweepLength)
        self.form.sweepAngleInput.textEdited.connect(self.onSweepAngle)
        self.form.thicknessInput.textEdited.connect(self.onThickness)
        
        self.update()
        
        if mode == 0: # fresh created
            self.obj.Proxy.execute(self.obj)  # calculate once 
            FreeCAD.Gui.SendMsgToActiveView("ViewFit")
        
    def transferTo(self):
        "Transfer from the dialog to the object" 
        self.obj.FinType = str(self.form.finTypesCombo.currentText())
        self.obj.FinCrossSection = str(self.form.finCrossSectionsCombo.currentText())
        self.obj.RootChord = _toFloat(self.form.rootChordInput.text())
        self.obj.TipChord = _toFloat(self.form.tipChordInput.text())
        self.obj.Height = _toFloat(self.form.heightInput.text())
        self.obj.SweepLength = _toFloat(self.form.sweepLengthInput.text())
        self.obj.SweepAngle = _toFloat(self.form.sweepAngleInput.text())
        self.obj.Thickness = _toFloat(self.form.thicknessInput.text())
    
    def transferFrom(self):
        "Transfer from the object to the dialog"
        self.form.finTypesCombo.setCurrentText(self.obj.FinType)
        self.form.finCrossSectionsCombo.setCurrentText(self.obj.FinCrossSection)
        self.form.rootChordInput.setText("%f" % self.obj.RootChord)
        self.form.tipChordInput.setText("%f" % self.obj.TipChord)
        self.form.heightInput.setText("%f" % self.obj.Height)
        self.form.sweepLengthInput.setText("%f" % self.obj.SweepLength)
        self.form.sweepAngleInput.setText("%f" % self.obj.SweepAngle)
        self.form.thicknessInput.setText("%f" % self.obj.Thickness)
        
    def onFinTypes(self, value):
        self.obj.FinType = value
        self.obj.Proxy.execute(self.obj)
        
    def onFinCrossSection(self, value):
        self.obj.FinCrossSection = value
        self.obj.Proxy.execute(self.obj)
        
    def onRootChord(self, value):
        self.obj.RootChord = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onTipChord(self, value):
        self.obj.TipChord = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onHeight(self, value):
        self._sweepAngleFromLength()
        self.obj.Thickness = _toFloat(value)
        self.obj.Proxy.execute(self.obj)

    def _sweepLengthFromAngle(self):
        theta = _toFloat(self.form.sweepAngleInput.text())
        if theta <= -90.0 or theta >= 90.0:
            _err("Sweep angle must be greater than -90 and less than +90")
            return
        theta = math.radians(-1.0 * (theta + 90.0))
        length = _toFloat(self.form.heightInput.text()) / math.tan(theta)
        self.form.sweepLengthInput.setText("%f" % length)
        self.obj.SweepLength = length
 
    def _sweepAngleFromLength(self):
        theta = 90.0 - math.degrees(math.atan2(_toFloat(self.form.heightInput.text()), _toFloat(self.form.sweepLengthInput.text())))
        self.form.sweepAngleInput.setText("%f" % theta)
        self.obj.SweepAngle = theta
        
    def onSweepLength(self, value):
        self._sweepAngleFromLength()
        self.obj.SweepLength = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onSweepAngle(self, value):
        self._sweepLengthFromAngle()
        self.obj.SweepAngle = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onThickness(self, value):
        self.obj.Thickness = _toFloat(value)
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
        FreeCADGui.ActiveDocument.resetEdit()
        FreeCAD.ActiveDocument.abortTransaction()
        FreeCAD.ActiveDocument.recompute() #??? Should the object not be created?
