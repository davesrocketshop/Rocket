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
"""Class for drawing body tubes"""

__title__ = "FreeCAD Body Tubes"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from typing import Any

import FreeCAD
import FreeCADGui
import Materials

from Rocket.Utilities import translate

from PySide import QtGui, QtCore
from PySide.QtWidgets import QDialog, QGridLayout, QVBoxLayout, QSizePolicy

from Ui.TaskPanelDatabase import TaskPanelDatabase
from Ui.TaskPanelLocation import TaskPanelLocation
from Rocket.Constants import COMPONENT_TYPE_BODYTUBE, COMPONENT_TYPE_LAUNCHLUG, COMPONENT_TYPE_COUPLER, COMPONENT_TYPE_ENGINEBLOCK

from Rocket.Constants import FEATURE_INNER_TUBE, FEATURE_LAUNCH_LUG, FEATURE_TUBE_COUPLER, FEATURE_ENGINE_BLOCK

from Ui.Widgets.MaterialTab import MaterialTab
from Ui.Widgets.CommentTab import CommentTab
from Ui.Widgets.ScalingTab import ScalingTabBodyTube

from Rocket.Utilities import _valueOnly, _err

class _BodyTubeDialog(QDialog):

    def __init__(self, obj: Any, parent : Any = None) -> None:
        super().__init__(parent)

        self.tabWidget = QtGui.QTabWidget()
        self.tabGeneral = QtGui.QWidget()
        self.tabMaterial = MaterialTab()
        self.tabComment = CommentTab()
        self.tabScaling = None
        if not obj.Proxy.Type in [FEATURE_INNER_TUBE, FEATURE_LAUNCH_LUG, FEATURE_TUBE_COUPLER, FEATURE_ENGINE_BLOCK]:
            self.tabScaling = ScalingTabBodyTube(obj)

        self.tabWidget.addTab(self.tabGeneral, translate('Rocket', "General"))
        if self.tabScaling:
            self.tabWidget.addTab(self.tabScaling.widget(), translate('Rocket', "Scaling"))
        self.tabWidget.addTab(self.tabMaterial, translate('Rocket', "Material"))
        self.tabWidget.addTab(self.tabComment, translate('Rocket', "Comment"))

        layout = QVBoxLayout()
        layout.addWidget(self.tabWidget)
        self.setLayout(layout)

        self.setTabGeneral()

    def setTabGeneral(self):

        ui = FreeCADGui.UiLoader()

        # define our window
        self.setGeometry(250, 250, 400, 350)
        self.setWindowTitle(translate('Rocket', "Body Tube Parameter"))

        # Get the body tube parameters: length, ID, etc...
        self.idLabel = QtGui.QLabel(translate('Rocket', "Inner Diameter"), self)

        self.idInput = ui.createWidget("Gui::InputField")
        self.idInput.unit = FreeCAD.Units.Length
        self.idInput.setMinimumWidth(100)

        self.odLabel = QtGui.QLabel(translate('Rocket', "Outer Diameter"), self)

        self.odInput = ui.createWidget("Gui::InputField")
        self.odInput.unit = FreeCAD.Units.Length
        self.odInput.setMinimumWidth(100)

        self.autoDiameterCheckbox = QtGui.QCheckBox(translate('Rocket', "auto"), self)
        self.autoDiameterCheckbox.setCheckState(QtCore.Qt.Unchecked)

        self.thicknessLabel = QtGui.QLabel(translate('Rocket', "Wall Thickness"), self)

        self.thicknessInput = ui.createWidget("Gui::InputField")
        self.thicknessInput.unit = FreeCAD.Units.Length
        self.thicknessInput.setMinimumWidth(80)

        self.lengthLabel = QtGui.QLabel(translate('Rocket', "Length"), self)

        self.lengthInput = ui.createWidget("Gui::InputField")
        self.lengthInput.unit = FreeCAD.Units.Length
        self.lengthInput.setMinimumWidth(100)

        self.motorGroup = QtGui.QGroupBox(translate('Rocket', "Motor Mount"), self)
        self.motorGroup.setCheckable(True)

        self.overhangLabel = QtGui.QLabel(translate('Rocket', "Overhang"), self)

        self.overhangInput = ui.createWidget("Gui::InputField")
        self.overhangInput.unit = FreeCAD.Units.Length
        self.overhangInput.setMinimumWidth(80)

        # Motor group
        row = 0
        grid = QGridLayout()

        grid.addWidget(self.overhangLabel, row, 0)
        grid.addWidget(self.overhangInput, row, 1)

        self.motorGroup.setLayout(grid)

        # General parameters
        row = 0
        grid = QGridLayout()

        grid.addWidget(self.odLabel, row, 0)
        grid.addWidget(self.odInput, row, 1)
        grid.addWidget(self.autoDiameterCheckbox, row, 2)
        row += 1

        grid.addWidget(self.idLabel, row, 0)
        grid.addWidget(self.idInput, row, 1)
        row += 1

        grid.addWidget(self.thicknessLabel, row, 0)
        grid.addWidget(self.thicknessInput, row, 1)
        row += 1

        grid.addWidget(self.lengthLabel, row, 0)
        grid.addWidget(self.lengthInput, row, 1)

        layout = QVBoxLayout()
        layout.addItem(grid)
        layout.addWidget(self.motorGroup)
        layout.addItem(QtGui.QSpacerItem(0,0, QSizePolicy.Expanding, QSizePolicy.Expanding))

        self.tabGeneral.setLayout(layout)

class TaskPanelBodyTube:

    def __init__(self, obj : Any, mode : int) -> None:
        self._obj = obj
        self._isAssembly = self._obj.Proxy.isRocketAssembly()
        self._motorMount = hasattr(self._obj, "MotorMount")

        self._btForm = _BodyTubeDialog(obj)
        if self._obj.Proxy.Type == FEATURE_LAUNCH_LUG:
            self._db = TaskPanelDatabase(obj, COMPONENT_TYPE_LAUNCHLUG)
        elif self._obj.Proxy.Type == FEATURE_TUBE_COUPLER:
            self._db = TaskPanelDatabase(obj, COMPONENT_TYPE_COUPLER)
        elif self._obj.Proxy.Type == FEATURE_ENGINE_BLOCK:
            self._db = TaskPanelDatabase(obj, COMPONENT_TYPE_ENGINEBLOCK)
        else:
            self._db = TaskPanelDatabase(obj, COMPONENT_TYPE_BODYTUBE)
        self._dbForm = self._db.getForm()

        self._location = TaskPanelLocation(obj)
        self._locationForm = self._location.getForm()

        self.form = [self._btForm, self._locationForm, self._dbForm]
        self._btForm.setWindowIcon(QtGui.QIcon(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_BodyTube.svg"))

        self._btForm.odInput.textEdited.connect(self.onOd)
        self._btForm.autoDiameterCheckbox.stateChanged.connect(self.onAutoDiameter)
        self._btForm.idInput.textEdited.connect(self.onId)
        self._btForm.thicknessInput.textEdited.connect(self.onThickness)
        self._btForm.lengthInput.textEdited.connect(self.onLength)

        if self._motorMount:
            self._btForm.motorGroup.toggled.connect(self.onMotor)
            self._btForm.overhangInput.textEdited.connect(self.onOverhang)

        if self._btForm.tabScaling:
            self._btForm.tabScaling.scaled.connect(self.onScale)
            self._btForm.tabScaling.updated.connect(self.onUpdated)

        self._db.dbLoad.connect(self.onLookup)
        self._location.locationChange.connect(self.onLocation)

        self.update()

        if mode == 0: # fresh created
            self._obj.Proxy.execute(self._obj)  # calculate once
            FreeCAD.Gui.SendMsgToActiveView("ViewFit")

    def transferTo(self):
        "Transfer from the dialog to the object"
        self._obj.Proxy.setOuterDiameter(FreeCAD.Units.Quantity(self._btForm.odInput.text()).Value)
        self._obj.Proxy.setOuterDiameterAutomatic(self._btForm.autoDiameterCheckbox.isChecked())
        self._obj.Proxy.setThickness(FreeCAD.Units.Quantity(self._btForm.thicknessInput.text()).Value)
        self._obj.Proxy.setLength(FreeCAD.Units.Quantity(self._btForm.lengthInput.text()).Value)
        if self._motorMount:
            self._obj.MotorMount = self._btForm.motorGroup.isChecked()
            self._obj.Overhang = self._btForm.overhangInput.text()

        if self._btForm.tabScaling:
            self._btForm.tabScaling.transferTo(self._obj)
        self._btForm.tabMaterial.transferTo(self._obj)
        self._btForm.tabComment.transferTo(self._obj)

    def transferFrom(self):
        "Transfer from the object to the dialog"
        self._btForm.odInput.setText(self._obj.Diameter.UserString)
        self._btForm.autoDiameterCheckbox.setChecked(self._obj.AutoDiameter)
        self._btForm.idInput.setText("0.0")
        self._btForm.thicknessInput.setText(self._obj.Thickness.UserString)
        self._btForm.lengthInput.setText(self._obj.Length.UserString)
        if self._motorMount:
            self._btForm.motorGroup.setChecked(self._obj.MotorMount)
            self._btForm.overhangInput.setText(self._obj.Overhang.UserString)

        if self._btForm.tabScaling:
            self._btForm.tabScaling.transferFrom(self._obj)
        self._btForm.tabMaterial.transferFrom(self._obj)
        self._btForm.tabComment.transferFrom(self._obj)

        self._setAutoDiameterState()
        self._setIdFromThickness()
        self._setMotorState()

    def setEdited(self):
        try:
            self._obj.Proxy.setEdited()
        except ReferenceError:
            # Object may be deleted
            pass

    def onScale(self) -> None:
        # Update the scale values
        if self._btForm.tabScaling:
            scale = self._btForm.tabScaling.getScale()
            length = self._obj.Length / scale
            diameter = self._obj.Diameter / scale
            if scale < 1.0:
                self._btForm.tabScaling._form.scaleRadio.setText(translate('Rocket', "Upscale"))
                self._btForm.tabScaling._form.scaledInput.setText(f"{1.0/scale}")
            else:
                self._btForm.tabScaling._form.scaleRadio.setText(translate('Rocket', "Scale"))
                self._btForm.tabScaling._form.scaledInput.setText(f"{scale}")
            self._btForm.tabScaling._form.scaledLengthInput.setText(length.UserString)
            self._btForm.tabScaling._form.scaledDiameterInput.setText(diameter.UserString)

    def onUpdated(self) -> None:
        self.transferFrom()

    def onOd(self, value):
        try:
            # self._obj.Diameter = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.setOuterDiameter(FreeCAD.Units.Quantity(value).Value)
            self._setIdFromThickness()
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def _setAutoDiameterState(self):
        if self._isAssembly:
            self._btForm.odInput.setEnabled(not self._obj.AutoDiameter)
            self._btForm.autoDiameterCheckbox.setChecked(self._obj.AutoDiameter)
            self._btForm.autoDiameterCheckbox.setEnabled(True)
        else:
            self._btForm.odInput.setEnabled(True)
            self._obj.AutoDiameter = False
            self._btForm.autoDiameterCheckbox.setChecked(self._obj.AutoDiameter)
            self._btForm.autoDiameterCheckbox.setEnabled(False)

        if self._obj.AutoDiameter:
            self._obj.Diameter = self._obj.Proxy.getOuterDiameter(0)
            self._btForm.odInput.setText(self._obj.Diameter.UserString)
            self._setIdFromThickness()

        # Set the scale state
        self.onScale()

    def onAutoDiameter(self, value):
        self._obj.Proxy.setOuterDiameterAutomatic(value)
        self._setAutoDiameterState()

        self._obj.Proxy.execute(self._obj)
        self.setEdited()

    def _setThicknessFromId(self, value):
        od = float(self._obj.Diameter.Value)
        if od > 0.0:
            id = FreeCAD.Units.Quantity(value).Value
            thickness = (od - id) / 2.0
            # self._obj.Thickness = FreeCAD.Units.Quantity(thickness).Value
            self._obj.Proxy.setThickness(FreeCAD.Units.Quantity(thickness).Value)
        else:
            # self._obj.Thickness = FreeCAD.Units.Quantity(0.0).Value
            self._obj.Proxy.setThickness(FreeCAD.Units.Quantity(0.0).Value)
        self._btForm.thicknessInput.setText(self._obj.Thickness.UserString)

    def onId(self, value):
        try:
            self._setThicknessFromId(value)
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def _setIdFromThickness(self):
        od = float(self._obj.Diameter.Value)
        if od > 0.0:
            id = od - 2.0 * float(self._obj.Thickness)
            self._btForm.idInput.setText(FreeCAD.Units.Quantity(id, FreeCAD.Units.Length).UserString)
        else:
            self._btForm.idInput.setText(FreeCAD.Units.Quantity(0.0, FreeCAD.Units.Length).UserString)

    def onThickness(self, value):
        try:
            self._obj.Proxy.setThickness(FreeCAD.Units.Quantity(value).Value)
            self._setIdFromThickness()
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def onLength(self, value):
        try:
            self._obj.Proxy.setLength(FreeCAD.Units.Quantity(value).Value)
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def _setMotorState(self):
        if not self._motorMount: #self._obj.Proxy.Type == FEATURE_LAUNCH_LUG:
            self._btForm.overhangInput.setHidden(True)
            self._btForm.motorGroup.setHidden(True)
        else:
            if self._isAssembly:
                self._btForm.motorGroup.setEnabled(True)
                self._btForm.overhangInput.setEnabled(self._obj.MotorMount)
                self._btForm.motorGroup.setChecked(self._obj.MotorMount)
            else:
                self._obj.MotorMount = False
                self._btForm.motorGroup.setEnabled(False)
                self._btForm.overhangInput.setEnabled(self._obj.MotorMount)
                self._btForm.motorGroup.setChecked(self._obj.MotorMount)

    def onMotor(self, value):
        self._obj.MotorMount = value
        self._setMotorState()

        self._obj.Proxy.execute(self._obj)
        self.setEdited()

    def onOverhang(self, value):
        try:
            self._obj.Overhang = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def onLookup(self):
        result = self._db.getLookupResult()

        diameter = _valueOnly(result["inner_diameter"], result["inner_diameter_units"])
        self._obj.Proxy.setOuterDiameter(_valueOnly(result["outer_diameter"], result["outer_diameter_units"]))
        self._obj.Proxy.setThickness((self._obj.Diameter.Value - diameter) / 2.0)
        if not self._db.getLookupMatch():
            self._obj.Proxy.setLength(_valueOnly(result["length"], result["length_units"]))
        try:
            self._obj.ShapeMaterial = Materials.MaterialManager().getMaterial(result["uuid"])
        except LookupError:
            # Use the default
            _err(translate('Rocket', "Unable to find material '{}'").format(result["uuid"]))

        self.update()
        self._obj.Proxy.execute(self._obj)
        self.setEdited()

    def onLocation(self):
        self._obj.Proxy.updateChildren()
        self._obj.Proxy.execute(self._obj)
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
        FreeCAD.ActiveDocument.commitTransaction()
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.resetEdit()


    def reject(self):
        FreeCAD.ActiveDocument.abortTransaction()
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.resetEdit()
        self.setEdited()
        FreeCAD.ActiveDocument.recompute()
