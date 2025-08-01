# ***************************************************************************
# *   Copyright (c) 2021-2025 David Carter <dcarter@davidcarter.ca>         *
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
"""Class for drawing bulkheads"""

__title__ = "FreeCAD Bulkheads"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"


import FreeCAD
import FreeCADGui
import Materials

from PySide import QtGui, QtCore
from PySide.QtWidgets import QDialog, QGridLayout, QVBoxLayout

from DraftTools import translate

from Ui.TaskPanelDatabase import TaskPanelDatabase
from Ui.TaskPanelLocation import TaskPanelLocation
from Ui.Widgets.MaterialTab import MaterialTab
from Ui.Widgets.CommentTab import CommentTab

from Rocket.Constants import COMPONENT_TYPE_BULKHEAD, COMPONENT_TYPE_CENTERINGRING

from Rocket.Utilities import _valueWithUnits, _err

class _BulkheadDialog(QDialog):

    def __init__(self, crPanel, parent=None):
        super(_BulkheadDialog, self).__init__(parent)

        self.tabWidget = QtGui.QTabWidget()
        self.tabGeneral = QtGui.QWidget()
        self.tabMaterial = MaterialTab()
        self.tabComment = CommentTab()
        self.tabWidget.addTab(self.tabGeneral, translate('Rocket', "General"))
        self.tabWidget.addTab(self.tabMaterial, translate('Rocket', "Material"))
        self.tabWidget.addTab(self.tabComment, translate('Rocket', "Comment"))

        layout = QVBoxLayout()
        layout.addWidget(self.tabWidget)
        self.setLayout(layout)

        self.setTabGeneral(crPanel)

    def setTabGeneral(self, crPanel):

        ui = FreeCADGui.UiLoader()

        # define our window
        self.setGeometry(250, 250, 400, 350)
        if crPanel:
            self.setWindowTitle(translate('Rocket', "Centering Ring Parameter"))
        else:
            self.setWindowTitle(translate('Rocket', "Bulkhead Parameter"))

        # Get the body tube parameters: length, ID, etc...
        self.diameterLabel = QtGui.QLabel(translate('Rocket', "Outer Diameter"), self)

        self.diameterInput = ui.createWidget("Gui::InputField")
        self.diameterInput.unit = FreeCAD.Units.Length
        self.diameterInput.setMinimumWidth(80)

        self.autoDiameterCheckbox = QtGui.QCheckBox(translate('Rocket', "auto"), self)
        self.autoDiameterCheckbox.setCheckState(QtCore.Qt.Unchecked)

        self.thicknessLabel = QtGui.QLabel(translate('Rocket', "Thickness"), self)

        self.thicknessInput = ui.createWidget("Gui::InputField")
        self.thicknessInput.unit = FreeCAD.Units.Length
        self.thicknessInput.setMinimumWidth(80)

        if crPanel:
            self.centerDiameterLabel = QtGui.QLabel(translate('Rocket', "Inner Diameter"), self)

            self.centerDiameterInput = ui.createWidget("Gui::InputField")
            self.centerDiameterInput.unit = FreeCAD.Units.Length
            self.centerDiameterInput.setMinimumWidth(80)

            self.autoCenterDiameterCheckbox = QtGui.QCheckBox(translate('Rocket', "auto"), self)
            self.autoCenterDiameterCheckbox.setCheckState(QtCore.Qt.Unchecked)

            self.notchGroup = QtGui.QGroupBox(translate('Rocket', "Notched"), self)
            self.notchGroup.setCheckable(True)

            self.notchWidthLabel = QtGui.QLabel(translate('Rocket', "Width"), self)

            self.notchWidthInput = ui.createWidget("Gui::InputField")
            self.notchWidthInput.unit = FreeCAD.Units.Length
            self.notchWidthInput.setMinimumWidth(80)

            self.notchHeightLabel = QtGui.QLabel(translate('Rocket', "Height"), self)

            self.notchHeightInput = ui.createWidget("Gui::InputField")
            self.notchHeightInput.unit = FreeCAD.Units.Length
            self.notchHeightInput.setMinimumWidth(80)

        self.stepGroup = QtGui.QGroupBox(translate('Rocket', "Step"), self)
        self.stepGroup.setCheckable(True)

        self.stepDiameterLabel = QtGui.QLabel(translate('Rocket', "Diameter"), self)

        self.stepDiameterInput = ui.createWidget("Gui::InputField")
        self.stepDiameterInput.unit = FreeCAD.Units.Length
        self.stepDiameterInput.setMinimumWidth(80)

        self.stepThicknessLabel = QtGui.QLabel(translate('Rocket', "Thickness"), self)

        self.stepThicknessInput = ui.createWidget("Gui::InputField")
        self.stepThicknessInput.unit = FreeCAD.Units.Length
        self.stepThicknessInput.setMinimumWidth(80)

        self.stepReverseCheckbox = QtGui.QCheckBox(translate('Rocket', "reverse"), self)
        self.stepReverseCheckbox.setCheckState(QtCore.Qt.Unchecked)

        self.holeGroup = QtGui.QGroupBox(translate('Rocket', "Holes"), self)
        self.holeGroup.setCheckable(True)

        self.holeDiameterLabel = QtGui.QLabel(translate('Rocket', "Diameter"), self)

        self.holeDiameterInput = ui.createWidget("Gui::InputField")
        self.holeDiameterInput.unit = FreeCAD.Units.Length
        self.holeDiameterInput.setMinimumWidth(80)

        self.holeCenterLabel = QtGui.QLabel(translate('Rocket', "Center"), self)

        self.holeCenterInput = ui.createWidget("Gui::InputField")
        self.holeCenterInput.unit = FreeCAD.Units.Length
        self.holeCenterInput.setMinimumWidth(80)

        self.holeCountLabel = QtGui.QLabel(translate('Rocket', "Count"), self)

        self.holeCountSpinBox = QtGui.QSpinBox(self)
        self.holeCountSpinBox.setMinimumWidth(80)
        self.holeCountSpinBox.setMinimum(1)
        self.holeCountSpinBox.setMaximum(10000)

        self.holeOffsetLabel = QtGui.QLabel(translate('Rocket', "Offset"), self)

        # Offsets can be positive or negative so no validator required
        self.holeOffsetInput = ui.createWidget("Gui::InputField")
        self.holeOffsetInput.unit = FreeCAD.Units.Angle
        self.holeOffsetInput.setMinimumWidth(80)

        # Notch group
        if crPanel:
            row = 0
            layout = QGridLayout()

            layout.addWidget(self.notchWidthLabel, row, 0)
            layout.addWidget(self.notchWidthInput, row, 1)
            row += 1

            layout.addWidget(self.notchHeightLabel, row, 0)
            layout.addWidget(self.notchHeightInput, row, 1)

            self.notchGroup.setLayout(layout)

        # Multiple instances
        self.instanceGroup = QtGui.QGroupBox(translate('Rocket', "Instances"), self)
        self.instanceGroup.setCheckable(False)

        self.instanceCountLabel = QtGui.QLabel(translate('Rocket', "Instance Count"), self)

        self.instanceCountSpinBox = QtGui.QSpinBox(self)
        self.instanceCountSpinBox.setMinimumWidth(100)
        self.instanceCountSpinBox.setMinimum(1)
        self.instanceCountSpinBox.setMaximum(10000)
        self.instanceCountSpinBox.setValue(1)

        self.instanceSeparationLabel = QtGui.QLabel(translate('Rocket', "Instance Separation"), self)

        self.instanceSeparationInput = ui.createWidget("Gui::InputField")
        self.instanceSeparationInput.unit = FreeCAD.Units.Length
        self.instanceSeparationInput.setMinimumWidth(100)

        # Step group
        row = 0
        layout = QGridLayout()

        layout.addWidget(self.stepDiameterLabel, row, 0)
        layout.addWidget(self.stepDiameterInput, row, 1)
        row += 1

        layout.addWidget(self.stepThicknessLabel, row, 0)
        layout.addWidget(self.stepThicknessInput, row, 1)
        row += 1

        layout.addWidget(self.stepReverseCheckbox, row, 1)

        self.stepGroup.setLayout(layout)

        # Hole group
        row = 0
        layout = QGridLayout()

        layout.addWidget(self.holeDiameterLabel, row, 0)
        layout.addWidget(self.holeDiameterInput, row, 1)
        row += 1

        layout.addWidget(self.holeCenterLabel, row, 0)
        layout.addWidget(self.holeCenterInput, row, 1)
        row += 1

        layout.addWidget(self.holeCountLabel, row, 0)
        layout.addWidget(self.holeCountSpinBox, row, 1)
        row += 1

        layout.addWidget(self.holeOffsetLabel, row, 0)
        layout.addWidget(self.holeOffsetInput, row, 1)

        self.holeGroup.setLayout(layout)

        # Instance group
        row = 0
        grid = QGridLayout()

        grid.addWidget(self.instanceCountLabel, row, 0)
        grid.addWidget(self.instanceCountSpinBox, row, 1)
        row += 1

        grid.addWidget(self.instanceSeparationLabel, row, 0)
        grid.addWidget(self.instanceSeparationInput, row, 1)
        row += 1

        self.instanceGroup.setLayout(grid)

        # Main items
        row = 0
        grid = QGridLayout()

        grid.addWidget(self.diameterLabel, row, 0)
        grid.addWidget(self.diameterInput, row, 1)
        grid.addWidget(self.autoDiameterCheckbox, row, 2)
        row += 1

        if crPanel:
            grid.addWidget(self.centerDiameterLabel, row, 0)
            grid.addWidget(self.centerDiameterInput, row, 1)
            grid.addWidget(self.autoCenterDiameterCheckbox, row, 2)
            row += 1

        grid.addWidget(self.thicknessLabel, row, 0)
        grid.addWidget(self.thicknessInput, row, 1)

        # Final layout
        layout = QVBoxLayout()
        layout.addItem(grid)
        if crPanel:
            layout.addWidget(self.notchGroup)

        layout.addWidget(self.stepGroup)
        layout.addWidget(self.holeGroup)
        layout.addWidget(self.instanceGroup)

        self.tabGeneral.setLayout(layout)

class TaskPanelBulkhead:

    def __init__(self, obj, crPanel, mode):
        self._obj = obj
        self._crPanel = crPanel
        self._isAssembly = self._obj.Proxy.isRocketAssembly()

        self._bulkForm = _BulkheadDialog(self._crPanel)
        if crPanel:
            self._db = TaskPanelDatabase(obj, COMPONENT_TYPE_CENTERINGRING)
        else:
            self._db = TaskPanelDatabase(obj, COMPONENT_TYPE_BULKHEAD)
        self._dbForm = self._db.getForm()

        self._location = TaskPanelLocation(obj)
        self._locationForm = self._location.getForm()

        self.form = [self._bulkForm, self._locationForm, self._dbForm]
        if self._crPanel:
            self._bulkForm.setWindowIcon(QtGui.QIcon(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_CenterinRing.svg"))
        else:
            self._bulkForm.setWindowIcon(QtGui.QIcon(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Bulkhead.svg"))

        self._bulkForm.diameterInput.textEdited.connect(self.onDiameter)
        self._bulkForm.autoDiameterCheckbox.stateChanged.connect(self.onAutoDiameter)
        self._bulkForm.thicknessInput.textEdited.connect(self.onThickness)

        self._bulkForm.stepGroup.toggled.connect(self.onStep)
        self._bulkForm.stepDiameterInput.textEdited.connect(self.onStepDiameter)
        self._bulkForm.stepThicknessInput.textEdited.connect(self.onStepThickness)
        self._bulkForm.stepReverseCheckbox.toggled.connect(self.onStepReverse)

        self._bulkForm.holeGroup.toggled.connect(self.onHole)
        self._bulkForm.holeDiameterInput.textEdited.connect(self.onHoleDiameter)
        self._bulkForm.holeCenterInput.textEdited.connect(self.onHoleCenter)
        self._bulkForm.holeCountSpinBox.valueChanged.connect(self.onHoleCount)
        self._bulkForm.holeOffsetInput.textEdited.connect(self.onHoleOffset)

        if self._crPanel:
            self._bulkForm.centerDiameterInput.textEdited.connect(self.onCenterDiameter)
            self._bulkForm.autoCenterDiameterCheckbox.stateChanged.connect(self.onAutoCenterDiameter)

            self._bulkForm.notchGroup.toggled.connect(self.onNotched)
            self._bulkForm.notchWidthInput.textEdited.connect(self.onNotchWidth)
            self._bulkForm.notchHeightInput.textEdited.connect(self.onNotchHeight)

        self._bulkForm.instanceCountSpinBox.valueChanged.connect(self.onInstanceCount)
        self._bulkForm.instanceSeparationInput.textEdited.connect(self.onInstanceSeparation)

        self._db.dbLoad.connect(self.onLookup)
        self._location.locationChange.connect(self.onLocation)

        self.update()

        if mode == 0: # fresh created
            self._obj.Proxy.execute(self._obj)  # calculate once
            FreeCAD.Gui.SendMsgToActiveView("ViewFit")

    def transferTo(self):
        "Transfer from the dialog to the object"
        self._obj.Diameter = self._bulkForm.diameterInput.text()
        self._obj.AutoDiameter = self._bulkForm.autoDiameterCheckbox.isChecked()
        self._obj.Thickness = self._bulkForm.thicknessInput.text()

        self._obj.Step = self._bulkForm.stepGroup.isChecked()
        self._obj.StepDiameter = self._bulkForm.stepDiameterInput.text()
        self._obj.StepThickness = self._bulkForm.stepThicknessInput.text()
        self._obj.StepReverse = self._bulkForm.stepReverseCheckbox.isChecked()

        self._obj.Holes = self._bulkForm.holeGroup.isChecked()
        self._obj.HoleDiameter = self._bulkForm.holeDiameterInput.text()
        self._obj.HoleCenter = self._bulkForm.holeCenterInput.text()
        self._obj.HoleCount = self._bulkForm.holeCountSpinBox.value()
        self._obj.HoleOffset = self._bulkForm.holeOffsetInput.text()

        if self._crPanel:
            self._obj.CenterDiameter = self._bulkForm.centerDiameterInput.text()
            self._obj.CenterAutoDiameter = self._bulkForm.autoCenterDiameterCheckbox.isChecked()

            self._obj.Notched = self._bulkForm.notchGroup.isChecked()
            self._obj.NotchWidth = self._bulkForm.notchWidthInput.text()
            self._obj.NotchHeight = self._bulkForm.notchHeightInput.text()

        self._obj.InstanceCount = self._bulkForm.instanceCountSpinBox.value()
        self._obj.InstanceSeparation = self._bulkForm.instanceSeparationInput.text()

        self._bulkForm.tabMaterial.transferTo(self._obj)
        self._bulkForm.tabComment.transferTo(self._obj)

    def transferFrom(self):
        "Transfer from the object to the dialog"
        self._bulkForm.diameterInput.setText(self._obj.Diameter.UserString)
        self._bulkForm.autoDiameterCheckbox.setChecked(self._obj.AutoDiameter)
        self._bulkForm.thicknessInput.setText(self._obj.Thickness.UserString)

        self._bulkForm.stepGroup.setChecked(self._obj.Step)
        self._bulkForm.stepDiameterInput.setText(self._obj.StepDiameter.UserString)
        self._bulkForm.stepThicknessInput.setText(self._obj.StepThickness.UserString)
        self._bulkForm.stepReverseCheckbox.setChecked(self._obj.StepReverse)

        self._bulkForm.holeGroup.setChecked(self._obj.Holes)
        self._bulkForm.holeDiameterInput.setText(self._obj.HoleDiameter.UserString)
        self._bulkForm.holeCenterInput.setText(self._obj.HoleCenter.UserString)
        self._bulkForm.holeCountSpinBox.setValue(self._obj.HoleCount)
        self._bulkForm.holeOffsetInput.setText(self._obj.HoleOffset.UserString)

        if self._crPanel:
            self._bulkForm.centerDiameterInput.setText(self._obj.CenterDiameter.UserString)
            self._bulkForm.autoCenterDiameterCheckbox.setChecked(self._obj.CenterAutoDiameter)

            self._bulkForm.notchGroup.setChecked(self._obj.Notched)
            self._bulkForm.notchWidthInput.setText(self._obj.NotchWidth.UserString)
            self._bulkForm.notchHeightInput.setText(self._obj.NotchHeight.UserString)
            self._setNotchedState()
            self._setAutoCenterDiameterState()

        self._bulkForm.instanceCountSpinBox.setValue(self._obj.InstanceCount)
        self._bulkForm.instanceSeparationInput.setText(self._obj.InstanceSeparation.UserString)

        self._bulkForm.tabMaterial.transferFrom(self._obj)
        self._bulkForm.tabComment.transferFrom(self._obj)

        self._setAutoDiameterState()
        self._setHoleState()

    def setEdited(self):
        try:
            self._obj.Proxy.setEdited()
        except ReferenceError:
            # Object may be deleted
            pass

    def onDiameter(self, value):
        try:
            self._obj.Diameter = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def _setAutoDiameterState(self):
        if self._isAssembly:
            self._bulkForm.diameterInput.setEnabled(not self._obj.AutoDiameter)
            self._bulkForm.autoDiameterCheckbox.setChecked(self._obj.AutoDiameter)
        else:
            self._obj.AutoDiameter = False
            self._bulkForm.diameterInput.setEnabled(not self._obj.AutoDiameter)
            self._bulkForm.autoDiameterCheckbox.setChecked(self._obj.AutoDiameter)
            self._bulkForm.autoDiameterCheckbox.setEnabled(self._obj.AutoDiameter)

        if self._obj.AutoDiameter:
            if self._obj.Proxy.hasParent():
                parent = self._obj.Proxy.getParent()
                self._obj.Diameter = 2.0 * parent.getInnerRadius(0)
                self._bulkForm.diameterInput.setText(self._obj.Diameter.UserString)

    def onAutoDiameter(self, value):
        self._obj.AutoDiameter = value
        self._setAutoDiameterState()

        self._obj.Proxy.execute(self._obj)
        self.setEdited()

    def onThickness(self, value):
        try:
            self._obj.Thickness = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def onCenterDiameter(self, value):
        try:
            self._obj.CenterDiameter = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def _setAutoCenterDiameterState(self):
        if self._isAssembly:
            self._bulkForm.centerDiameterInput.setEnabled(not self._obj.CenterAutoDiameter)
            self._bulkForm.autoCenterDiameterCheckbox.setChecked(self._obj.CenterAutoDiameter)
        else:
            self._obj.CenterAutoDiameter = False
            self._bulkForm.centerDiameterInput.setEnabled(not self._obj.CenterAutoDiameter)
            self._bulkForm.autoCenterDiameterCheckbox.setChecked(self._obj.CenterAutoDiameter)
            self._bulkForm.autoCenterDiameterCheckbox.setEnabled(self._obj.CenterAutoDiameter)

        if self._obj.CenterAutoDiameter:
            self._obj.CenterDiameter = 2.0 * self._obj.Proxy.getRadius(0)
            self._bulkForm.centerDiameterInput.setText(self._obj.CenterDiameter.UserString)

    def onAutoCenterDiameter(self, value):
        self._obj.CenterAutoDiameter = value
        self._setAutoCenterDiameterState()

        self._obj.Proxy.execute(self._obj)
        self.setEdited()

    def onStep(self, value):
        self._obj.Step = self._bulkForm.stepGroup.isChecked()

        self._obj.Proxy.execute(self._obj)
        self.setEdited()

    def onStepDiameter(self, value):
        try:
            self._obj.StepDiameter = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def onStepThickness(self, value):
        try:
            self._obj.StepThickness = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def onStepReverse(self, value):
        self._obj.StepReverse = self._bulkForm.stepReverseCheckbox.isChecked()

        self._obj.Proxy.execute(self._obj)

    def _setHoleState(self):
        self._bulkForm.holeDiameterInput.setEnabled(self._obj.Holes)
        self._bulkForm.holeCenterInput.setEnabled(self._obj.Holes)
        self._bulkForm.holeCountSpinBox.setEnabled(self._obj.Holes)
        self._bulkForm.holeOffsetInput.setEnabled(self._obj.Holes)

    def onHole(self, value):
        self._obj.Holes = self._bulkForm.holeGroup.isChecked()
        self._setHoleState()

        self._obj.Proxy.execute(self._obj)
        self.setEdited()

    def onHoleDiameter(self, value):
        try:
            self._obj.HoleDiameter = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def onHoleCenter(self, value):
        try:
            self._obj.HoleCenter = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def onHoleCount(self, value):
        self._obj.HoleCount = int(value)
        self._obj.Proxy.execute(self._obj)
        self.setEdited()

    def onHoleOffset(self, value):
        try:
            self._obj.HoleOffset = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def _setNotchedState(self):
        self._bulkForm.notchWidthInput.setEnabled(self._obj.Notched)
        self._bulkForm.notchHeightInput.setEnabled(self._obj.Notched)

    def onNotched(self, value):
        self._obj.Notched = self._bulkForm.notchGroup.isChecked()
        self._setNotchedState()

        self._obj.Proxy.execute(self._obj)
        self.setEdited()

    def onNotchWidth(self, value):
        try:
            self._obj.NotchWidth = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def onNotchHeight(self, value):
        try:
            self._obj.NotchHeight = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def onLookup(self):
        result = self._db.getLookupResult()

        self._obj.Diameter = _valueWithUnits(result["outer_diameter"], result["outer_diameter_units"])
        self._obj.Thickness =_valueWithUnits(result["length"], result["length_units"])
        try:
            self._obj.ShapeMaterial = Materials.MaterialManager().getMaterial(result["uuid"])
        except LookupError:
            # Use the default
            _err(translate('Rocket', "Unable to find material '{}'").format(result["uuid"]))

        self._obj.Step = False
        self._obj.StepDiameter = 0.0
        self._obj.StepThickness = 0.0

        self._obj.Holes = False
        self._obj.HoleDiameter = 0.0
        self._obj.HoleCenter = 0.0
        self._obj.HoleCount = 1
        self._obj.HoleOffset = 0.0

        if self._crPanel:
            self._obj.CenterDiameter = _valueWithUnits(result["inner_diameter"], result["inner_diameter_units"])

            self._obj.Notched = False
            self._obj.NotchWidth = 0.0
            self._obj.NotchHeight = 0.0

        self.update()
        self._obj.Proxy.execute(self._obj)
        self.setEdited()

    def onLocation(self):
        self._obj.Proxy.updateChildren()
        self._obj.Proxy.execute(self._obj)
        self.setEdited()

    def onInstanceCount(self, value):
        try:
            self._obj.InstanceCount = value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def onInstanceSeparation(self, value):
        try:
            self._obj.InstanceSeparation = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def getStandardButtons(self):
        return QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Apply

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
