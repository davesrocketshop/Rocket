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

        self.coreOffsetLabel = QtGui.QLabel(translate('Rocket', "Core Offset"), self)

        self.coreOffsetInput = ui.createWidget("Gui::InputField")
        self.coreOffsetInput.unit = 'mm'
        self.coreOffsetInput.setMinimumWidth(100)

        self.coreDiameterLabel = QtGui.QLabel(translate('Rocket', "Core Diameter"), self)

        self.coreDiameterInput = ui.createWidget("Gui::InputField")
        self.coreDiameterInput.unit = 'mm'
        self.coreDiameterInput.setMinimumWidth(100)

        self.forewardCoreDiameterLabel = QtGui.QLabel(translate('Rocket', "Foreward Core Diameter"), self)

        self.forewardCoreDiameterInput = ui.createWidget("Gui::InputField")
        self.forewardCoreDiameterInput.unit = 'mm'
        self.forewardCoreDiameterInput.setMinimumWidth(100)

        self.aftCoreDiameterLabel = QtGui.QLabel(translate('Rocket', "Aft Core Diameter"), self)

        self.aftCoreDiameterInput = ui.createWidget("Gui::InputField")
        self.aftCoreDiameterInput.unit = 'mm'
        self.aftCoreDiameterInput.setMinimumWidth(100)

        self.slotWidthLabel = QtGui.QLabel(translate('Rocket', "Slot Width"), self)

        self.slotWidthInput = ui.createWidget("Gui::InputField")
        self.slotWidthInput.unit = 'mm'
        self.slotWidthInput.setMinimumWidth(100)

        self.slotOffsetLabel = QtGui.QLabel(translate('Rocket', "Slot Offset"), self)

        self.slotOffsetInput = ui.createWidget("Gui::InputField")
        self.slotOffsetInput.unit = 'mm'
        self.slotOffsetInput.setMinimumWidth(100)

        self.slotLengthLabel = QtGui.QLabel(translate('Rocket', "Slot Length"), self)

        self.slotLengthInput = ui.createWidget("Gui::InputField")
        self.slotLengthInput.unit = 'mm'
        self.slotLengthInput.setMinimumWidth(100)

        self.numFinsLabel = QtGui.QLabel(translate('Rocket', "Number of Fins"), self)

        self.numFinsSpinBox = QtGui.QSpinBox(self)
        self.numFinsSpinBox.setMinimumWidth(100)
        self.numFinsSpinBox.setMinimum(1)
        self.numFinsSpinBox.setMaximum(10000)

        self.finWidthLabel = QtGui.QLabel(translate('Rocket', "Fin Width"), self)

        self.finWidthInput = ui.createWidget("Gui::InputField")
        self.finWidthInput.unit = 'mm'
        self.finWidthInput.setMinimumWidth(100)

        self.finLengthLabel = QtGui.QLabel(translate('Rocket', "Fin Length"), self)

        self.finLengthInput = ui.createWidget("Gui::InputField")
        self.finLengthInput.unit = 'mm'
        self.finLengthInput.setMinimumWidth(100)

        self.rodDiameterLabel = QtGui.QLabel(translate('Rocket', "Rod Diameter"), self)

        self.rodDiameterInput = ui.createWidget("Gui::InputField")
        self.rodDiameterInput.unit = 'mm'
        self.rodDiameterInput.setMinimumWidth(100)

        self.supportDiameterLabel = QtGui.QLabel(translate('Rocket', "Support Diameter"), self)

        self.supportDiameterInput = ui.createWidget("Gui::InputField")
        self.supportDiameterInput.unit = 'mm'
        self.supportDiameterInput.setMinimumWidth(100)

        self.numPointsLabel = QtGui.QLabel(translate('Rocket', "Number of Points"), self)

        self.numPointsSpinBox = QtGui.QSpinBox(self)
        self.numPointsSpinBox.setMinimumWidth(100)
        self.numPointsSpinBox.setMinimum(1)
        self.numPointsSpinBox.setMaximum(10000)

        self.pointLengthLabel = QtGui.QLabel(translate('Rocket', "Point Length"), self)

        self.pointLengthInput = ui.createWidget("Gui::InputField")
        self.pointLengthInput.unit = 'mm'
        self.pointLengthInput.setMinimumWidth(100)

        self.pointWidthLabel = QtGui.QLabel(translate('Rocket', "Point Base Width"), self)

        self.pointWidthInput = ui.createWidget("Gui::InputField")
        self.pointWidthInput.unit = 'mm'
        self.pointWidthInput.setMinimumWidth(100)

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

        layout.addWidget(self.forewardCoreDiameterLabel, row, 0)
        layout.addWidget(self.forewardCoreDiameterInput, row, 1)
        row += 1

        layout.addWidget(self.aftCoreDiameterLabel, row, 0)
        layout.addWidget(self.aftCoreDiameterInput, row, 1)
        row += 1

        layout.addWidget(self.inhibitedEndsLabel, row, 0)
        layout.addWidget(self.inhibitedEndsCombo, row, 1)
        row += 1

        layout.addWidget(self.numFinsLabel, row, 0)
        layout.addWidget(self.numFinsSpinBox, row, 1)
        row += 1

        layout.addWidget(self.finWidthLabel, row, 0)
        layout.addWidget(self.finWidthInput, row, 1)
        row += 1

        layout.addWidget(self.finLengthLabel, row, 0)
        layout.addWidget(self.finLengthInput, row, 1)
        row += 1

        layout.addWidget(self.coreOffsetLabel, row, 0)
        layout.addWidget(self.coreOffsetInput, row, 1)
        row += 1

        layout.addWidget(self.coreDiameterLabel, row, 0)
        layout.addWidget(self.coreDiameterInput, row, 1)
        row += 1

        layout.addWidget(self.slotWidthLabel, row, 0)
        layout.addWidget(self.slotWidthInput, row, 1)
        row += 1

        layout.addWidget(self.slotOffsetLabel, row, 0)
        layout.addWidget(self.slotOffsetInput, row, 1)
        row += 1

        layout.addWidget(self.slotLengthLabel, row, 0)
        layout.addWidget(self.slotLengthInput, row, 1)
        row += 1

        layout.addWidget(self.rodDiameterLabel, row, 0)
        layout.addWidget(self.rodDiameterInput, row, 1)
        row += 1

        layout.addWidget(self.supportDiameterLabel, row, 0)
        layout.addWidget(self.supportDiameterInput, row, 1)
        row += 1

        layout.addWidget(self.numPointsLabel, row, 0)
        layout.addWidget(self.numPointsSpinBox, row, 1)
        row += 1

        layout.addWidget(self.pointLengthLabel, row, 0)
        layout.addWidget(self.pointLengthInput, row, 1)
        row += 1

        layout.addWidget(self.pointWidthLabel, row, 0)
        layout.addWidget(self.pointWidthInput, row, 1)
        row += 1

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
        self._form.coreOffsetInput.textEdited.connect(self.onCoreOffset)
        self._form.coreDiameterInput.textEdited.connect(self.onCoreDiameter)
        self._form.forewardCoreDiameterInput.textEdited.connect(self.onForewardCoreDiameter)
        self._form.aftCoreDiameterInput.textEdited.connect(self.onAftCoreDiameter)
        self._form.slotWidthInput.textEdited.connect(self.onSlotWidth)
        self._form.slotOffsetInput.textEdited.connect(self.onSlotOffset)
        self._form.slotLengthInput.textEdited.connect(self.onSlotLength)
        self._form.numFinsSpinBox.valueChanged.connect(self.onNumFins)
        self._form.finWidthInput.textEdited.connect(self.onFinWidth)
        self._form.finLengthInput.textEdited.connect(self.onFinLength)
        self._form.rodDiameterInput.textEdited.connect(self.onRodDiameter)
        self._form.supportDiameterInput.textEdited.connect(self.onSupportDiameter)
        self._form.numPointsSpinBox.valueChanged.connect(self.onNumPoints)
        self._form.pointLengthInput.textEdited.connect(self.onPointLength)
        self._form.pointWidthInput.textEdited.connect(self.onPointWidth)

        self.update()
        
    def transferTo(self):
        "Transfer from the dialog to the object" 
        self._obj.GeometryName = str(self._form.geometryNameCombo.currentText())
        self._obj.Diameter = self._form.diameterInput.text()
        self._obj.Length = self._form.lengthInput.text()
        self._obj.InhibitedEnds = str(self._form.inhibitedEndsCombo.currentText())
        self._obj.CoreOffset = self._form.coreOffsetInput.text()
        self._obj.CoreDiameter = self._form.coreDiameterInput.text()
        self._obj.ForwardCoreDiameter = self._form.forewardCoreDiameterInput.text()
        self._obj.AftCoreDiameter = self._form.aftCoreDiameterInput.text()
        self._obj.SlotWidth = self._form.slotWidthInput.text()
        self._obj.SlotOffset = self._form.slotOffsetInput.text()
        self._obj.SlotLength = self._form.slotLengthInput.text()
        self._obj.NumFins = self._form.numFinsSpinBox.value()
        self._obj.FinWidth = self._form.finWidthInput.text()
        self._obj.FinLength = self._form.finLengthInput.text()
        self._obj.RodDiameter = self._form.rodDiameterInput.text()
        self._obj.SupportDiameter = self._form.supportDiameterInput.text()
        self._obj.NumPoints = self._form.numPointsSpinBox.value()
        self._obj.PointLength = self._form.pointLengthInput.text()
        self._obj.PointWidth = self._form.pointWidthInput.text()

    def transferFrom(self):
        "Transfer from the object to the dialog"
        self._form.geometryNameCombo.setCurrentText(self._obj.GeometryName)
        self._form.diameterInput.setText(self._obj.Diameter.UserString)
        self._form.lengthInput.setText(self._obj.Length.UserString)
        self._form.inhibitedEndsCombo.setCurrentText(self._obj.InhibitedEnds)
        self._form.coreOffsetInput.setText(self._obj.CoreOffset.UserString)
        self._form.coreDiameterInput.setText(self._obj.CoreDiameter.UserString)
        self._form.forewardCoreDiameterInput.setText(self._obj.ForwardCoreDiameter.UserString)
        self._form.aftCoreDiameterInput.setText(self._obj.AftCoreDiameter.UserString)
        self._form.slotWidthInput.setText(self._obj.SlotWidth.UserString)
        self._form.slotOffsetInput.setText(self._obj.SlotOffset.UserString)
        self._form.slotLengthInput.setText(self._obj.SlotLength.UserString)
        self._form.numFinsSpinBox.setValue(self._obj.NumFins)
        self._form.finWidthInput.setText(self._obj.FinWidth.UserString)
        self._form.finLengthInput.setText(self._obj.FinLength.UserString)
        self._form.rodDiameterInput.setText(self._obj.RodDiameter.UserString)
        self._form.supportDiameterInput.setText(self._obj.SupportDiameter.UserString)
        self._form.numPointsSpinBox.setValue(self._obj.NumPoints)
        self._form.pointLengthInput.setText(self._obj.PointLength.UserString)
        self._form.pointWidthInput.setText(self._obj.PointWidth.UserString)

        self.updateGeometry()

    def updateGeometry(self):
        name = str(self._form.geometryNameCombo.currentText())
        if name == GRAIN_GEOMETRY_BATES:
            self.setGeometryBates()
        elif name == GRAIN_GEOMETRY_C:
            self.setGeometryCGrain()
        elif name == GRAIN_GEOMETRY_CONICAL:
            self.setGeometryConical()
        # elif name == GRAIN_GEOMETRY_CUSTOM:
        #     self.setGeometryCustom()
        elif name == GRAIN_GEOMETRY_D:
            self.setGeometryDGrain()
        elif name == GRAIN_GEOMETRY_END:
            self.setGeometryEndBurner()
        elif name == GRAIN_GEOMETRY_FINOCYL:
            self.setGeometryFinocyl()
        elif name == GRAIN_GEOMETRY_MOONBURNER:
            self.setGeometryMoonBurner()
        elif name == GRAIN_GEOMETRY_RODTUBE:
            self.setGeometryRodTube()
        elif name == GRAIN_GEOMETRY_STAR:
            self.setGeometryStar()
        elif name == GRAIN_GEOMETRY_XCORE:
            self.setGeometryXCore()

    def setGeometryBates(self):
        self._form.diameterLabel.setHidden(False)
        self._form.diameterInput.setHidden(False)
        self._form.lengthLabel.setHidden(False)
        self._form.lengthInput.setHidden(False)
        self._form.inhibitedEndsLabel.setHidden(False)
        self._form.inhibitedEndsCombo.setHidden(False)
        self._form.coreDiameterLabel.setHidden(False)
        self._form.coreDiameterInput.setHidden(False)
        self._form.slotWidthLabel.setHidden(True)
        self._form.slotWidthInput.setHidden(True)
        self._form.slotOffsetLabel.setHidden(True)
        self._form.slotOffsetInput.setHidden(True)
        self._form.forewardCoreDiameterLabel.setHidden(True)
        self._form.forewardCoreDiameterInput.setHidden(True)
        self._form.aftCoreDiameterLabel.setHidden(True)
        self._form.aftCoreDiameterInput.setHidden(True)
        self._form.numFinsLabel.setHidden(True)
        self._form.numFinsSpinBox.setHidden(True)
        self._form.finWidthLabel.setHidden(True)
        self._form.finWidthInput.setHidden(True)
        self._form.finLengthLabel.setHidden(True)
        self._form.finLengthInput.setHidden(True)
        self._form.coreOffsetLabel.setHidden(True)
        self._form.coreOffsetInput.setHidden(True)
        self._form.rodDiameterLabel.setHidden(True)
        self._form.rodDiameterInput.setHidden(True)
        self._form.supportDiameterLabel.setHidden(True)
        self._form.supportDiameterInput.setHidden(True)
        self._form.numPointsLabel.setHidden(True)
        self._form.numPointsSpinBox.setHidden(True)
        self._form.pointLengthLabel.setHidden(True)
        self._form.pointLengthInput.setHidden(True)
        self._form.pointWidthLabel.setHidden(True)
        self._form.pointWidthInput.setHidden(True)
        self._form.slotLengthLabel.setHidden(True)
        self._form.slotLengthInput.setHidden(True)

    def setGeometryCGrain(self):
        self._form.diameterLabel.setHidden(False)
        self._form.diameterInput.setHidden(False)
        self._form.lengthLabel.setHidden(False)
        self._form.lengthInput.setHidden(False)
        self._form.inhibitedEndsLabel.setHidden(False)
        self._form.inhibitedEndsCombo.setHidden(False)
        self._form.coreDiameterLabel.setHidden(True)
        self._form.coreDiameterInput.setHidden(True)
        self._form.slotWidthLabel.setHidden(False)
        self._form.slotWidthInput.setHidden(False)
        self._form.slotOffsetLabel.setHidden(False)
        self._form.slotOffsetInput.setHidden(False)
        self._form.forewardCoreDiameterLabel.setHidden(True)
        self._form.forewardCoreDiameterInput.setHidden(True)
        self._form.aftCoreDiameterLabel.setHidden(True)
        self._form.aftCoreDiameterInput.setHidden(True)
        self._form.numFinsLabel.setHidden(True)
        self._form.numFinsSpinBox.setHidden(True)
        self._form.finWidthLabel.setHidden(True)
        self._form.finWidthInput.setHidden(True)
        self._form.finLengthLabel.setHidden(True)
        self._form.finLengthInput.setHidden(True)
        self._form.coreOffsetLabel.setHidden(True)
        self._form.coreOffsetInput.setHidden(True)
        self._form.rodDiameterLabel.setHidden(True)
        self._form.rodDiameterInput.setHidden(True)
        self._form.supportDiameterLabel.setHidden(True)
        self._form.supportDiameterInput.setHidden(True)
        self._form.numPointsLabel.setHidden(True)
        self._form.numPointsSpinBox.setHidden(True)
        self._form.pointLengthLabel.setHidden(True)
        self._form.pointLengthInput.setHidden(True)
        self._form.pointWidthLabel.setHidden(True)
        self._form.pointWidthInput.setHidden(True)
        self._form.slotLengthLabel.setHidden(True)
        self._form.slotLengthInput.setHidden(True)

    def setGeometryConical(self):
        self._form.diameterLabel.setHidden(False)
        self._form.diameterInput.setHidden(False)
        self._form.lengthLabel.setHidden(False)
        self._form.lengthInput.setHidden(False)
        self._form.inhibitedEndsLabel.setHidden(False)
        self._form.inhibitedEndsCombo.setHidden(False)
        self._form.coreDiameterLabel.setHidden(True)
        self._form.coreDiameterInput.setHidden(True)
        self._form.slotWidthLabel.setHidden(True)
        self._form.slotWidthInput.setHidden(True)
        self._form.slotOffsetLabel.setHidden(True)
        self._form.slotOffsetInput.setHidden(True)
        self._form.forewardCoreDiameterLabel.setHidden(False)
        self._form.forewardCoreDiameterInput.setHidden(False)
        self._form.aftCoreDiameterLabel.setHidden(False)
        self._form.aftCoreDiameterInput.setHidden(False)
        self._form.numFinsLabel.setHidden(True)
        self._form.numFinsSpinBox.setHidden(True)
        self._form.finWidthLabel.setHidden(True)
        self._form.finWidthInput.setHidden(True)
        self._form.finLengthLabel.setHidden(True)
        self._form.finLengthInput.setHidden(True)
        self._form.coreOffsetLabel.setHidden(True)
        self._form.coreOffsetInput.setHidden(True)
        self._form.rodDiameterLabel.setHidden(True)
        self._form.rodDiameterInput.setHidden(True)
        self._form.supportDiameterLabel.setHidden(True)
        self._form.supportDiameterInput.setHidden(True)
        self._form.numPointsLabel.setHidden(True)
        self._form.numPointsSpinBox.setHidden(True)
        self._form.pointLengthLabel.setHidden(True)
        self._form.pointLengthInput.setHidden(True)
        self._form.pointWidthLabel.setHidden(True)
        self._form.pointWidthInput.setHidden(True)
        self._form.slotLengthLabel.setHidden(True)
        self._form.slotLengthInput.setHidden(True)

    def setGeometryDGrain(self):
        self._form.diameterLabel.setHidden(False)
        self._form.diameterInput.setHidden(False)
        self._form.lengthLabel.setHidden(False)
        self._form.lengthInput.setHidden(False)
        self._form.inhibitedEndsLabel.setHidden(False)
        self._form.inhibitedEndsCombo.setHidden(False)
        self._form.coreDiameterLabel.setHidden(True)
        self._form.coreDiameterInput.setHidden(True)
        self._form.slotWidthLabel.setHidden(True)
        self._form.slotWidthInput.setHidden(True)
        self._form.slotOffsetLabel.setHidden(False)
        self._form.slotOffsetInput.setHidden(False)
        self._form.forewardCoreDiameterLabel.setHidden(True)
        self._form.forewardCoreDiameterInput.setHidden(True)
        self._form.aftCoreDiameterLabel.setHidden(True)
        self._form.aftCoreDiameterInput.setHidden(True)
        self._form.numFinsLabel.setHidden(True)
        self._form.numFinsSpinBox.setHidden(True)
        self._form.finWidthLabel.setHidden(True)
        self._form.finWidthInput.setHidden(True)
        self._form.finLengthLabel.setHidden(True)
        self._form.finLengthInput.setHidden(True)
        self._form.coreOffsetLabel.setHidden(True)
        self._form.coreOffsetInput.setHidden(True)
        self._form.rodDiameterLabel.setHidden(True)
        self._form.rodDiameterInput.setHidden(True)
        self._form.supportDiameterLabel.setHidden(True)
        self._form.supportDiameterInput.setHidden(True)
        self._form.numPointsLabel.setHidden(True)
        self._form.numPointsSpinBox.setHidden(True)
        self._form.pointLengthLabel.setHidden(True)
        self._form.pointLengthInput.setHidden(True)
        self._form.pointWidthLabel.setHidden(True)
        self._form.pointWidthInput.setHidden(True)
        self._form.slotLengthLabel.setHidden(True)
        self._form.slotLengthInput.setHidden(True)

    def setGeometryEndBurner(self):
        self._form.diameterLabel.setHidden(False)
        self._form.diameterInput.setHidden(False)
        self._form.lengthLabel.setHidden(False)
        self._form.lengthInput.setHidden(False)
        self._form.inhibitedEndsLabel.setHidden(True)
        self._form.inhibitedEndsCombo.setHidden(True)
        self._form.coreDiameterLabel.setHidden(True)
        self._form.coreDiameterInput.setHidden(True)
        self._form.slotWidthLabel.setHidden(True)
        self._form.slotWidthInput.setHidden(True)
        self._form.slotOffsetLabel.setHidden(True)
        self._form.slotOffsetInput.setHidden(True)
        self._form.forewardCoreDiameterLabel.setHidden(True)
        self._form.forewardCoreDiameterInput.setHidden(True)
        self._form.aftCoreDiameterLabel.setHidden(True)
        self._form.aftCoreDiameterInput.setHidden(True)
        self._form.numFinsLabel.setHidden(True)
        self._form.numFinsSpinBox.setHidden(True)
        self._form.finWidthLabel.setHidden(True)
        self._form.finWidthInput.setHidden(True)
        self._form.finLengthLabel.setHidden(True)
        self._form.finLengthInput.setHidden(True)
        self._form.coreOffsetLabel.setHidden(True)
        self._form.coreOffsetInput.setHidden(True)
        self._form.rodDiameterLabel.setHidden(True)
        self._form.rodDiameterInput.setHidden(True)
        self._form.supportDiameterLabel.setHidden(True)
        self._form.supportDiameterInput.setHidden(True)
        self._form.numPointsLabel.setHidden(True)
        self._form.numPointsSpinBox.setHidden(True)
        self._form.pointLengthLabel.setHidden(True)
        self._form.pointLengthInput.setHidden(True)
        self._form.pointWidthLabel.setHidden(True)
        self._form.pointWidthInput.setHidden(True)
        self._form.slotLengthLabel.setHidden(True)
        self._form.slotLengthInput.setHidden(True)

    def setGeometryFinocyl(self):
        self._form.diameterLabel.setHidden(False)
        self._form.diameterInput.setHidden(False)
        self._form.lengthLabel.setHidden(False)
        self._form.lengthInput.setHidden(False)
        self._form.inhibitedEndsLabel.setHidden(False)
        self._form.inhibitedEndsCombo.setHidden(False)
        self._form.coreDiameterLabel.setHidden(False)
        self._form.coreDiameterInput.setHidden(False)
        self._form.slotWidthLabel.setHidden(True)
        self._form.slotWidthInput.setHidden(True)
        self._form.slotOffsetLabel.setHidden(True)
        self._form.slotOffsetInput.setHidden(True)
        self._form.forewardCoreDiameterLabel.setHidden(True)
        self._form.forewardCoreDiameterInput.setHidden(True)
        self._form.aftCoreDiameterLabel.setHidden(True)
        self._form.aftCoreDiameterInput.setHidden(True)
        self._form.numFinsLabel.setHidden(False)
        self._form.numFinsSpinBox.setHidden(False)
        self._form.finWidthLabel.setHidden(False)
        self._form.finWidthInput.setHidden(False)
        self._form.finLengthLabel.setHidden(False)
        self._form.finLengthInput.setHidden(False)
        self._form.coreOffsetLabel.setHidden(True)
        self._form.coreOffsetInput.setHidden(True)
        self._form.rodDiameterLabel.setHidden(True)
        self._form.rodDiameterInput.setHidden(True)
        self._form.supportDiameterLabel.setHidden(True)
        self._form.supportDiameterInput.setHidden(True)
        self._form.numPointsLabel.setHidden(True)
        self._form.numPointsSpinBox.setHidden(True)
        self._form.pointLengthLabel.setHidden(True)
        self._form.pointLengthInput.setHidden(True)
        self._form.pointWidthLabel.setHidden(True)
        self._form.pointWidthInput.setHidden(True)
        self._form.slotLengthLabel.setHidden(True)
        self._form.slotLengthInput.setHidden(True)

    def setGeometryMoonBurner(self):
        self._form.diameterLabel.setHidden(False)
        self._form.diameterInput.setHidden(False)
        self._form.lengthLabel.setHidden(False)
        self._form.lengthInput.setHidden(False)
        self._form.inhibitedEndsLabel.setHidden(False)
        self._form.inhibitedEndsCombo.setHidden(False)
        self._form.coreDiameterLabel.setHidden(False)
        self._form.coreDiameterInput.setHidden(False)
        self._form.slotWidthLabel.setHidden(True)
        self._form.slotWidthInput.setHidden(True)
        self._form.slotOffsetLabel.setHidden(True)
        self._form.slotOffsetInput.setHidden(True)
        self._form.forewardCoreDiameterLabel.setHidden(True)
        self._form.forewardCoreDiameterInput.setHidden(True)
        self._form.aftCoreDiameterLabel.setHidden(True)
        self._form.aftCoreDiameterInput.setHidden(True)
        self._form.numFinsLabel.setHidden(True)
        self._form.numFinsSpinBox.setHidden(True)
        self._form.finWidthLabel.setHidden(True)
        self._form.finWidthInput.setHidden(True)
        self._form.finLengthLabel.setHidden(True)
        self._form.finLengthInput.setHidden(True)
        self._form.coreOffsetLabel.setHidden(False)
        self._form.coreOffsetInput.setHidden(False)
        self._form.rodDiameterLabel.setHidden(True)
        self._form.rodDiameterInput.setHidden(True)
        self._form.supportDiameterLabel.setHidden(True)
        self._form.supportDiameterInput.setHidden(True)
        self._form.numPointsLabel.setHidden(True)
        self._form.numPointsSpinBox.setHidden(True)
        self._form.pointLengthLabel.setHidden(True)
        self._form.pointLengthInput.setHidden(True)
        self._form.pointWidthLabel.setHidden(True)
        self._form.pointWidthInput.setHidden(True)
        self._form.slotLengthLabel.setHidden(True)
        self._form.slotLengthInput.setHidden(True)

    def setGeometryRodTube(self):
        self._form.diameterLabel.setHidden(False)
        self._form.diameterInput.setHidden(False)
        self._form.lengthLabel.setHidden(False)
        self._form.lengthInput.setHidden(False)
        self._form.inhibitedEndsLabel.setHidden(False)
        self._form.inhibitedEndsCombo.setHidden(False)
        self._form.coreDiameterLabel.setHidden(False)
        self._form.coreDiameterInput.setHidden(False)
        self._form.slotWidthLabel.setHidden(True)
        self._form.slotWidthInput.setHidden(True)
        self._form.slotOffsetLabel.setHidden(True)
        self._form.slotOffsetInput.setHidden(True)
        self._form.forewardCoreDiameterLabel.setHidden(True)
        self._form.forewardCoreDiameterInput.setHidden(True)
        self._form.aftCoreDiameterLabel.setHidden(True)
        self._form.aftCoreDiameterInput.setHidden(True)
        self._form.numFinsLabel.setHidden(True)
        self._form.numFinsSpinBox.setHidden(True)
        self._form.finWidthLabel.setHidden(True)
        self._form.finWidthInput.setHidden(True)
        self._form.finLengthLabel.setHidden(True)
        self._form.finLengthInput.setHidden(True)
        self._form.coreOffsetLabel.setHidden(True)
        self._form.coreOffsetInput.setHidden(True)
        self._form.rodDiameterLabel.setHidden(False)
        self._form.rodDiameterInput.setHidden(False)
        self._form.supportDiameterLabel.setHidden(False)
        self._form.supportDiameterInput.setHidden(False)
        self._form.numPointsLabel.setHidden(True)
        self._form.numPointsSpinBox.setHidden(True)
        self._form.pointLengthLabel.setHidden(True)
        self._form.pointLengthInput.setHidden(True)
        self._form.pointWidthLabel.setHidden(True)
        self._form.pointWidthInput.setHidden(True)
        self._form.slotLengthLabel.setHidden(True)
        self._form.slotLengthInput.setHidden(True)

    def setGeometryStar(self):
        self._form.diameterLabel.setHidden(False)
        self._form.diameterInput.setHidden(False)
        self._form.lengthLabel.setHidden(False)
        self._form.lengthInput.setHidden(False)
        self._form.inhibitedEndsLabel.setHidden(False)
        self._form.inhibitedEndsCombo.setHidden(False)
        self._form.coreDiameterLabel.setHidden(True)
        self._form.coreDiameterInput.setHidden(True)
        self._form.slotWidthLabel.setHidden(True)
        self._form.slotWidthInput.setHidden(True)
        self._form.slotOffsetLabel.setHidden(True)
        self._form.slotOffsetInput.setHidden(True)
        self._form.forewardCoreDiameterLabel.setHidden(True)
        self._form.forewardCoreDiameterInput.setHidden(True)
        self._form.aftCoreDiameterLabel.setHidden(True)
        self._form.aftCoreDiameterInput.setHidden(True)
        self._form.numFinsLabel.setHidden(True)
        self._form.numFinsSpinBox.setHidden(True)
        self._form.finWidthLabel.setHidden(True)
        self._form.finWidthInput.setHidden(True)
        self._form.finLengthLabel.setHidden(True)
        self._form.finLengthInput.setHidden(True)
        self._form.coreOffsetLabel.setHidden(True)
        self._form.coreOffsetInput.setHidden(True)
        self._form.rodDiameterLabel.setHidden(True)
        self._form.rodDiameterInput.setHidden(True)
        self._form.supportDiameterLabel.setHidden(True)
        self._form.supportDiameterInput.setHidden(True)
        self._form.numPointsLabel.setHidden(False)
        self._form.numPointsSpinBox.setHidden(False)
        self._form.pointLengthLabel.setHidden(False)
        self._form.pointLengthInput.setHidden(False)
        self._form.pointWidthLabel.setHidden(False)
        self._form.pointWidthInput.setHidden(False)
        self._form.slotLengthLabel.setHidden(True)
        self._form.slotLengthInput.setHidden(True)

    def setGeometryXCore(self):
        self._form.diameterLabel.setHidden(False)
        self._form.diameterInput.setHidden(False)
        self._form.lengthLabel.setHidden(False)
        self._form.lengthInput.setHidden(False)
        self._form.inhibitedEndsLabel.setHidden(False)
        self._form.inhibitedEndsCombo.setHidden(False)
        self._form.coreDiameterLabel.setHidden(True)
        self._form.coreDiameterInput.setHidden(True)
        self._form.slotWidthLabel.setHidden(False)
        self._form.slotWidthInput.setHidden(False)
        self._form.slotOffsetLabel.setHidden(True)
        self._form.slotOffsetInput.setHidden(True)
        self._form.forewardCoreDiameterLabel.setHidden(True)
        self._form.forewardCoreDiameterInput.setHidden(True)
        self._form.aftCoreDiameterLabel.setHidden(True)
        self._form.aftCoreDiameterInput.setHidden(True)
        self._form.numFinsLabel.setHidden(True)
        self._form.numFinsSpinBox.setHidden(True)
        self._form.finWidthLabel.setHidden(True)
        self._form.finWidthInput.setHidden(True)
        self._form.finLengthLabel.setHidden(True)
        self._form.finLengthInput.setHidden(True)
        self._form.coreOffsetLabel.setHidden(True)
        self._form.coreOffsetInput.setHidden(True)
        self._form.rodDiameterLabel.setHidden(True)
        self._form.rodDiameterInput.setHidden(True)
        self._form.supportDiameterLabel.setHidden(True)
        self._form.supportDiameterInput.setHidden(True)
        self._form.numPointsLabel.setHidden(True)
        self._form.numPointsSpinBox.setHidden(True)
        self._form.pointLengthLabel.setHidden(True)
        self._form.pointLengthInput.setHidden(True)
        self._form.pointWidthLabel.setHidden(True)
        self._form.pointWidthInput.setHidden(True)
        self._form.slotLengthLabel.setHidden(False)
        self._form.slotLengthInput.setHidden(False)

    def onGeometryName(self, value):
        self._obj.GeometryName = value
        self.updateGeometry()
        
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
        
    def onCoreOffset(self, value):
        try:
            self._obj.CoreOffset = FreeCAD.Units.Quantity(value).Value
        except ValueError:
            pass
        
    def onCoreDiameter(self, value):
        try:
            self._obj.CoreDiameter = FreeCAD.Units.Quantity(value).Value
        except ValueError:
            pass
        
    def onForewardCoreDiameter(self, value):
        try:
            self._obj.ForewardCoreDiameter = FreeCAD.Units.Quantity(value).Value
        except ValueError:
            pass
        
    def onAftCoreDiameter(self, value):
        try:
            self._obj.AftCoreDiameter = FreeCAD.Units.Quantity(value).Value
        except ValueError:
            pass
        
    def onSlotWidth(self, value):
        try:
            self._obj.SlotWidth = FreeCAD.Units.Quantity(value).Value
        except ValueError:
            pass
        
    def onSlotOffset(self, value):
        try:
            self._obj.SlotOffset = FreeCAD.Units.Quantity(value).Value
        except ValueError:
            pass
        
    def onSlotLength(self, value):
        try:
            self._obj.SlotLength = FreeCAD.Units.Quantity(value).Value
        except ValueError:
            pass
       
    def onNumFins(self, value):
        self._obj.NumFins = value
        
    def onFinWidth(self, value):
        try:
            self._obj.FinWidth = FreeCAD.Units.Quantity(value).Value
        except ValueError:
            pass
        
    def onFinLength(self, value):
        try:
            self._obj.FinLength = FreeCAD.Units.Quantity(value).Value
        except ValueError:
            pass
        
    def onRodDiameter(self, value):
        try:
            self._obj.RodDiameter = FreeCAD.Units.Quantity(value).Value
        except ValueError:
            pass
        
    def onSupportDiameter(self, value):
        try:
            self._obj.SupportDiameter = FreeCAD.Units.Quantity(value).Value
        except ValueError:
            pass
        
    def onNumPoints(self, value):
        self._obj.NumPoints = value
        
    def onPointLength(self, value):
        try:
            self._obj.PointLength = FreeCAD.Units.Quantity(value).Value
        except ValueError:
            pass
        
    def onPointWidth(self, value):
        try:
            self._obj.PointWidth = FreeCAD.Units.Quantity(value).Value
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
