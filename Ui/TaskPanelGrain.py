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

from App.Constants import GRAIN_INHIBITED_NEITHER, GRAIN_INHIBITED_TOP, GRAIN_INHIBITED_BOTTOM, GRAIN_INHIBITED_BOTH
from App.Constants import GRAIN_GEOMETRY_BATES, GRAIN_GEOMETRY_C, GRAIN_GEOMETRY_CONICAL, GRAIN_GEOMETRY_CUSTOM, GRAIN_GEOMETRY_D, \
        GRAIN_GEOMETRY_END, GRAIN_GEOMETRY_FINOCYL, GRAIN_GEOMETRY_MOONBURNER, GRAIN_GEOMETRY_RODTUBE, GRAIN_GEOMETRY_STAR, GRAIN_GEOMETRY_XCORE

from DraftTools import translate

from App.Utilities import _err, _toFloat

class _GrainDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        ui = FreeCADGui.UiLoader()

        # define our window
        self.setGeometry(250, 250, 400, 350)
        self.setWindowTitle(translate('Rocket', "Nozzle Parameter"))

        # Get the nozzle parameters: length, ID, etc...
        self.geometryNameLabel = QtGui.QLabel(translate('Rocket', "Geometry"), self)

        self.geometryNames = (GRAIN_GEOMETRY_BATES, GRAIN_GEOMETRY_C, GRAIN_GEOMETRY_CONICAL, GRAIN_GEOMETRY_CUSTOM, GRAIN_GEOMETRY_D,
            GRAIN_GEOMETRY_END, GRAIN_GEOMETRY_FINOCYL, GRAIN_GEOMETRY_MOONBURNER, GRAIN_GEOMETRY_RODTUBE, GRAIN_GEOMETRY_STAR, GRAIN_GEOMETRY_XCORE)
        self.geometryNameCombo = QtGui.QComboBox(self)
        self.geometryNameCombo.addItems(self.geometryNames)

        self.diameterLabel = QtGui.QLabel(translate('Rocket', "Diameter"), self)

        self.diameterInput = ui.createWidget("Gui::InputField")
        self.diameterInput.unit = 'mm'
        self.diameterInput.setMinimumWidth(100)

        self.lengthLabel = QtGui.QLabel(translate('Rocket', "Length"), self)

        self.lengthInput = ui.createWidget("Gui::InputField")
        self.lengthInput.unit = 'mm'
        self.lengthInput.setMinimumWidth(100)

        self.inhibitedEndsLabel = QtGui.QLabel(translate('Rocket', "Inhibited Ends"), self)

        self.inhibitedEnds = (GRAIN_INHIBITED_NEITHER, GRAIN_INHIBITED_TOP, GRAIN_INHIBITED_BOTTOM, GRAIN_INHIBITED_BOTH)
        self.inhibitedEndsCombo = QtGui.QComboBox(self)
        self.inhibitedEndsCombo.addItems(self.inhibitedEnds)

        self.coreDiameterLabel = QtGui.QLabel(translate('Rocket', "Core Diameter"), self)

        self.coreDiameterInput = ui.createWidget("Gui::InputField")
        self.coreDiameterInput.unit = 'mm'
        self.coreDiameterInput.setMinimumWidth(100)

        # self.convAngleLabel = QtGui.QLabel(translate('Rocket', "Convergence Half Angle"), self)

        # self.convAngleInput = ui.createWidget("Gui::InputField")
        # self.convAngleInput.unit = 'deg'
        # self.convAngleInput.setMinimumWidth(100)

        # self.throatLengthLabel = QtGui.QLabel(translate('Rocket', "Throat Length"), self)

        # self.throatLengthInput = ui.createWidget("Gui::InputField")
        # self.throatLengthInput.unit = 'mm'
        # self.throatLengthInput.setMinimumWidth(100)

        # self.slagCoeffLabel = QtGui.QLabel(translate('Rocket', "Slag Buildup Coefficient"), self)

        # self.slagCoeffInput = ui.createWidget("Gui::InputField")
        # self.slagCoeffInput.setMinimumWidth(100)

        # self.erosionCoeffLabel = QtGui.QLabel(translate('Rocket', "Throat Erosion Coefficient"), self)

        # self.erosionCoeffInput = ui.createWidget("Gui::InputField")
        # self.erosionCoeffInput.setMinimumWidth(100)

        # self.expansionRatioLabel = QtGui.QLabel(translate('Rocket', "Expansion Ratio"), self)
        # self.expansionRatio = QtGui.QLabel(translate('Rocket', "-"), self)

        layout = QGridLayout()

        row = 0
        layout.addWidget(self.geometryNameLabel, row, 0, 1, 2)
        layout.addWidget(self.geometryNameCombo, row, 1)
        row += 1

        layout.addWidget(self.diameterLabel, row, 0)
        layout.addWidget(self.diameterInput, row, 1)
        row += 1

        layout.addWidget(self.lengthLabel, row, 0)
        layout.addWidget(self.lengthInput, row, 1)
        row += 1

        layout.addWidget(self.inhibitedEndsLabel, row, 0)
        layout.addWidget(self.inhibitedEndsCombo, row, 1)
        row += 1

        layout.addWidget(self.coreDiameterLabel, row, 0)
        layout.addWidget(self.coreDiameterInput, row, 1)
        row += 1

        # layout.addWidget(self.throatLengthLabel, row, 0)
        # layout.addWidget(self.throatLengthInput, row, 1)
        # row += 1

        # layout.addWidget(self.slagCoeffLabel, row, 0)
        # layout.addWidget(self.slagCoeffInput, row, 1)
        # row += 1

        # layout.addWidget(self.erosionCoeffLabel, row, 0)
        # layout.addWidget(self.erosionCoeffInput, row, 1)
        # row += 1

        # layout.addWidget(self.expansionRatioLabel, row, 0)
        # layout.addWidget(self.expansionRatio, row, 1)
        # row += 1

        self.setLayout(layout)

class TaskPanelGrain(QObject):

    def __init__(self,obj,mode):
        super().__init__()

        self._obj = obj
        
        self._form = _GrainDialog()

        self.form = [self._form]

        self._form.geometryNameCombo.currentTextChanged.connect(self.onGeometryName)
        self._form.diameterInput.textEdited.connect(self.onDiameter)
        self._form.lengthInput.textEdited.connect(self.onLength)
        self._form.inhibitedEndsCombo.currentTextChanged.connect(self.onInhibitedEnds)
        self._form.coreDiameterInput.textEdited.connect(self.onCoreDiameter)

        self.update()

        
    def transferTo(self):
        "Transfer from the dialog to the object" 
        self._obj.GeometryName = str(self._form.geometryNameCombo.currentText())
        self._obj.Diameter = self._form.diameterInput.text()
        self._obj.Length = self._form.lengthInput.text()
        self._obj.InhibitedEnds = str(self._form.inhibitedEndsCombo.currentText())
        self._obj.CoreDiameter = self._form.coreDiameterInput.text()

    def transferFrom(self):
        "Transfer from the object to the dialog"
        self._form.geometryNameCombo.setCurrentText(self._obj.GeometryName)
        self._form.diameterInput.setText(self._obj.Diameter.UserString)
        self._form.lengthInput.setText(self._obj.Length.UserString)
        self._form.inhibitedEndsCombo.setCurrentText(self._obj.InhibitedEnds)
        self._form.coreDiameterInput.setText(self._obj.CoreDiameter.UserString)

        # self.updateExpansion()

    # def updateExpansion(self):
    #     ratio = self._obj.Proxy.calcExpansion()
    #     self._form.expansionRatio.setText(str(ratio))

    def onGeometryName(self, value):
        self._obj.GeometryName = value
        
    def onDiameter(self, value):
        try:
            self._obj.Diameter = FreeCAD.Units.Quantity(value).Value
        except ValueError:
            pass
        
    def onLength(self, value):
        try:
            self._obj.Length = FreeCAD.Units.Quantity(value).Value
        except ValueError:
            pass

    def onInhibitedEnds(self, value):
        self._obj.InhibitedEnds = value
        
    def onCoreDiameter(self, value):
        try:
            self._obj.CoreDiameter = FreeCAD.Units.Quantity(value).Value
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
