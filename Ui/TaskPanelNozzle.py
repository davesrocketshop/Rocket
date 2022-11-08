# ***************************************************************************
# *   Copyright (c) 2022 David Carter <dcarter@davidcarter.ca>              *
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
"""Class for simulating nozzles"""

__title__ = "FreeCAD Nozzles"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    

import FreeCAD
import FreeCADGui

from PySide import QtGui, QtCore
from PySide.QtCore import QObject, Signal
from PySide2.QtWidgets import QDialog, QGridLayout, QVBoxLayout, QSizePolicy
import math

from DraftTools import translate

from App.Constants import FIN_TYPE_TRAPEZOID, FIN_TYPE_ELLIPSE, FIN_TYPE_SKETCH
from App.Constants import FIN_CROSS_SAME, FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, \
    FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE

from App.Utilities import _err, _toFloat

class _NozzleDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        ui = FreeCADGui.UiLoader()

        # define our window
        self.setGeometry(250, 250, 400, 350)
        self.setWindowTitle(translate('Rocket', "Nozzle Parameter"))

        # Get the nozzle parameters: length, ID, etc...
        self.throatLabel = QtGui.QLabel(translate('Rocket', "Throat Diameter"), self)

        self.throatInput = ui.createWidget("Gui::InputField")
        self.throatInput.unit = 'mm'
        self.throatInput.setMinimumWidth(100)

        self.exitLabel = QtGui.QLabel(translate('Rocket', "Exit Diameter"), self)

        self.exitInput = ui.createWidget("Gui::InputField")
        self.exitInput.unit = 'mm'
        self.exitInput.setMinimumWidth(100)

        self.efficiencyLabel = QtGui.QLabel(translate('Rocket', "Efficiency"), self)

        self.efficiencyInput = ui.createWidget("Gui::InputField")
        self.efficiencyInput.setMinimumWidth(100)

        self.divAngleLabel = QtGui.QLabel(translate('Rocket', "Divergence Half Angle"), self)

        self.divAngleInput = ui.createWidget("Gui::InputField")
        self.divAngleInput.unit = 'deg'
        self.divAngleInput.setMinimumWidth(100)

        self.convAngleLabel = QtGui.QLabel(translate('Rocket', "Convergence Half Angle"), self)

        self.convAngleInput = ui.createWidget("Gui::InputField")
        self.convAngleInput.unit = 'deg'
        self.convAngleInput.setMinimumWidth(100)

        self.throatLengthLabel = QtGui.QLabel(translate('Rocket', "Throat Length"), self)

        self.throatLengthInput = ui.createWidget("Gui::InputField")
        self.throatLengthInput.unit = 'mm'
        self.throatLengthInput.setMinimumWidth(100)

        self.slagCoeffLabel = QtGui.QLabel(translate('Rocket', "Slag Buildup Coefficient"), self)

        self.slagCoeffInput = ui.createWidget("Gui::InputField")
        self.slagCoeffInput.setMinimumWidth(100)

        self.erosionCoeffLabel = QtGui.QLabel(translate('Rocket', "Throat Erosion Coefficient"), self)

        self.erosionCoeffInput = ui.createWidget("Gui::InputField")
        self.erosionCoeffInput.setMinimumWidth(100)

        self.expansionRatioLabel = QtGui.QLabel(translate('Rocket', "Expansion Ratio"), self)
        self.expansionRatio = QtGui.QLabel(translate('Rocket', "-"), self)

        layout = QGridLayout()

        row = 0
        layout.addWidget(self.throatLabel, row, 0, 1, 2)
        layout.addWidget(self.throatInput, row, 1)
        row += 1

        layout.addWidget(self.exitLabel, row, 0)
        layout.addWidget(self.exitInput, row, 1)
        row += 1

        layout.addWidget(self.efficiencyLabel, row, 0)
        layout.addWidget(self.efficiencyInput, row, 1)
        row += 1

        layout.addWidget(self.divAngleLabel, row, 0)
        layout.addWidget(self.divAngleInput, row, 1)
        row += 1

        layout.addWidget(self.convAngleLabel, row, 0)
        layout.addWidget(self.convAngleInput, row, 1)
        row += 1

        layout.addWidget(self.throatLengthLabel, row, 0)
        layout.addWidget(self.throatLengthInput, row, 1)
        row += 1

        layout.addWidget(self.slagCoeffLabel, row, 0)
        layout.addWidget(self.slagCoeffInput, row, 1)
        row += 1

        layout.addWidget(self.erosionCoeffLabel, row, 0)
        layout.addWidget(self.erosionCoeffInput, row, 1)
        row += 1

        layout.addWidget(self.expansionRatioLabel, row, 0)
        layout.addWidget(self.expansionRatio, row, 1)
        row += 1

        self.setLayout(layout)

class TaskPanelNozzle(QObject):

    def __init__(self,obj,mode):
        super().__init__()

        self._obj = obj
        
        self._form = _NozzleDialog()

        self.form = [self._form]

        self._form.throatInput.textEdited.connect(self.onThroat)
        self._form.exitInput.textEdited.connect(self.onExit)

        self.update()

        
    def transferTo(self):
        "Transfer from the dialog to the object" 
        self._obj.Throat = self._form.throatInput.text()
        self._obj.Exit = self._form.exitInput.text()
        self._obj.Efficiency = float(self._form.efficiencyInput.text())
        self._obj.DivAngle = self._form.divAngleInput.text()
        self._obj.ConvAngle = self._form.convAngleInput.text()
        self._obj.ThroatLength = self._form.throatLengthInput.text()
        self._obj.SlagCoeff = float(self._form.slagCoeffInput.text())
        self._obj.ErosionCoeff = float(self._form.erosionCoeffInput.text())

    def transferFrom(self):
        "Transfer from the object to the dialog"
        self._form.throatInput.setText(self._obj.Throat.UserString)
        self._form.exitInput.setText(self._obj.Exit.UserString)
        self._form.efficiencyInput.setText(str(self._obj.Efficiency))
        self._form.divAngleInput.setText(self._obj.DivAngle.UserString)
        self._form.convAngleInput.setText(self._obj.ConvAngle.UserString)
        self._form.throatLengthInput.setText(self._obj.ThroatLength.UserString)
        # self._form.slagCoeffInput.setText(self._obj.SlagCoeff.UserString)
        # self._form.erosionCoeffInput.setText(self._obj.ErosionCoeff.UserString)
        self._form.slagCoeffInput.setText(str(self._obj.SlagCoeff))
        self._form.erosionCoeffInput.setText(str(self._obj.ErosionCoeff))

        self.updateExpansion()

    def updateExpansion(self):
        ratio = self._obj.Proxy.calcExpansion()
        self._form.expansionRatio.setText(str(ratio))
        
    def onThroat(self, value):
        try:
            self._obj.Throat = FreeCAD.Units.Quantity(value).Value
            self.updateExpansion()
        except ValueError:
            pass
        
    def onExit(self, value):
        try:
            self._obj.Exit = FreeCAD.Units.Quantity(value).Value
            self.updateExpansion()
        except ValueError:
            pass
        
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
