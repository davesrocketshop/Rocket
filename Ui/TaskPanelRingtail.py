# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

################################################################################
#                                                                              #
#   © 2021 David Carter <dcarter@davidcarter.ca>                               #
#                                                                              #
#   This addon is free software: you can redistribute it and/or modify         #
#   it under the terms of the GNU Lesser General Public License as             #
#   published by the Free Software Foundation, either version 2.1              #
#   of the License, or (at your option) any later version.                     #
#                                                                              #
#   This addon is distributed in the hope that it will be useful,              #
#   but WITHOUT ANY WARRANTY; without even the implied warranty                #
#   of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                    #
#   See the GNU Lesser General Public License for more details.                #
#                                                                              #
#   You should have received a copy of the GNU Lesser General Public           #
#   License along with this addon. If not, see https://www.gnu.org/licenses    #
#                                                                              #
################################################################################


"""Class for drawing ring tails"""

__title__ = "FreeCAD Ring Tails"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from typing import Any

import FreeCAD
import FreeCADGui
import Materials

translate = FreeCAD.Qt.translate

from PySide import QtGui, QtCore
from PySide.QtWidgets import QDialog, QGridLayout, QVBoxLayout, QSizePolicy

from Ui.TaskPanelDatabase import TaskPanelDatabase
from Ui.TaskPanelLocation import TaskPanelLocation
from Rocket.Constants import COMPONENT_TYPE_BODYTUBE

from Ui.Widgets.MaterialTab import MaterialTab
from Ui.Widgets.CommentTab import CommentTab
from Ui.Widgets.ScalingTab import ScalingTabBodyTube

from Rocket.Utilities import _valueOnly, _err

class _RingtailDialog(QDialog):

    def __init__(self, obj: Any, parent : Any = None) -> None:
        super().__init__(parent)

        self.tabWidget = QtGui.QTabWidget()
        self.tabGeneral = QtGui.QWidget()
        self.tabScaling = ScalingTabBodyTube(obj)
        self.tabMaterial = MaterialTab()
        self.tabComment = CommentTab()
        self.tabWidget.addTab(self.tabGeneral, translate('Rocket', "General"))
        self.tabWidget.addTab(self.tabScaling.widget(), translate('Rocket', "Scaling"))
        self.tabWidget.addTab(self.tabMaterial, translate('Rocket', "Material"))
        self.tabWidget.addTab(self.tabComment, translate('Rocket', "Comment"))

        layout = QVBoxLayout()
        layout.addWidget(self.tabWidget)
        self.setLayout(layout)

        self.setTabGeneral()

    def setTabGeneral(self) -> None:

        ui = FreeCADGui.UiLoader()

        # define our window
        self.setGeometry(250, 250, 400, 350)
        self.setWindowTitle(translate('Rocket', "Ring tail Parameter"))

        # Get the ring tail parameters: length, ID, etc...
        self.idLabel = QtGui.QLabel(translate('Rocket', "Inner diameter"), self)

        self.idInput = ui.createWidget("Gui::InputField")
        self.idInput.unit = FreeCAD.Units.Length
        self.idInput.setMinimumWidth(100)

        self.odLabel = QtGui.QLabel(translate('Rocket', "Outer diameter"), self)

        self.odInput = ui.createWidget("Gui::InputField")
        self.odInput.unit = FreeCAD.Units.Length
        self.odInput.setMinimumWidth(100)

        self.autoDiameterCheckbox = QtGui.QCheckBox(translate('Rocket', "auto"), self)
        self.autoDiameterCheckbox.setCheckState(QtCore.Qt.Unchecked)

        self.thicknessLabel = QtGui.QLabel(translate('Rocket', "Wall thickness"), self)

        self.thicknessInput = ui.createWidget("Gui::InputField")
        self.thicknessInput.unit = FreeCAD.Units.Length
        self.thicknessInput.setMinimumWidth(80)

        self.lengthLabel = QtGui.QLabel(translate('Rocket', "Length"), self)

        self.lengthInput = ui.createWidget("Gui::InputField")
        self.lengthInput.unit = FreeCAD.Units.Length
        self.lengthInput.setMinimumWidth(100)

        self.autoLengthCheckbox = QtGui.QCheckBox(translate('Rocket', "auto"), self)
        self.autoLengthCheckbox.setCheckState(QtCore.Qt.Unchecked)

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
        grid.addWidget(self.autoLengthCheckbox, row, 2)

        layout = QVBoxLayout()
        layout.addItem(grid)
        layout.addItem(QtGui.QSpacerItem(0,0, QSizePolicy.Expanding, QSizePolicy.Expanding))

        self.tabGeneral.setLayout(layout)

class TaskPanelRingtail:

    def __init__(self, obj : Any, mode : int) -> None:
        self._obj = obj
        self._isAssembly = self._obj.Proxy.isRocketAssembly()

        self._btForm = _RingtailDialog(obj)
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
        self._btForm.autoLengthCheckbox.stateChanged.connect(self.onAutoLength)

        self._btForm.tabScaling.scaled.connect(self.onScale)

        self._db.dbLoad.connect(self.onLookup)
        self._location.locationChange.connect(self.onLocation)

        self.update()

        if mode == 0: # fresh created
            self._obj.Proxy.execute(self._obj)  # calculate once
            FreeCAD.Gui.SendMsgToActiveView("ViewFit")

    def transferTo(self) -> None:
        "Transfer from the dialog to the object"
        self._obj.Proxy.setOuterDiameter(FreeCAD.Units.Quantity(self._btForm.odInput.text()).Value)
        self._obj.Proxy.setOuterDiameterAutomatic(self._btForm.autoDiameterCheckbox.isChecked())
        self._obj.Proxy.setThickness(FreeCAD.Units.Quantity(self._btForm.thicknessInput.text()).Value)
        self._obj.Proxy.setLength(FreeCAD.Units.Quantity(self._btForm.lengthInput.text()).Value)
        self._obj.Proxy.setLengthAutomatic(self._btForm.autoLengthCheckbox.isChecked())

        self._btForm.tabScaling.transferTo(self._obj)
        self._btForm.tabMaterial.transferTo(self._obj)
        self._btForm.tabComment.transferTo(self._obj)

    def transferFrom(self) -> None:
        "Transfer from the object to the dialog"
        self._btForm.odInput.setText(self._obj.Diameter.UserString)
        self._btForm.autoDiameterCheckbox.setChecked(self._obj.AutoDiameter)
        self._btForm.idInput.setText("0.0")
        self._btForm.thicknessInput.setText(self._obj.Thickness.UserString)
        self._btForm.lengthInput.setText(self._obj.Length.UserString)
        self._btForm.autoLengthCheckbox.setChecked(self._obj.AutoLength)

        self._btForm.tabScaling.transferFrom(self._obj)
        self._btForm.tabMaterial.transferFrom(self._obj)
        self._btForm.tabComment.transferFrom(self._obj)

        self._setAutoDiameterState()
        self._setAutoLengthState()
        self._setIdFromThickness()

    def setEdited(self) -> None:
        try:
            self._obj.Proxy.setEdited()
        except ReferenceError:
            # Object may be deleted
            pass

    def onScale(self) -> None:
        # Update the scale values
        scale = self._btForm.tabScaling.getScale()
        length = self._obj.Length / scale
        diameter = self._obj.Diameter / scale
        if scale < 1.0:
            self._btForm.tabScaling._form.scaledLabel.setText(translate('Rocket', "Upscale"))
            self._btForm.tabScaling._form.scaledInput.setText(f"{1.0/scale}")
        else:
            self._btForm.tabScaling._form.scaledLabel.setText(translate('Rocket', "Scale"))
            self._btForm.tabScaling._form.scaledInput.setText(f"{scale}")
        self._btForm.tabScaling._form.scaledLengthInput.setText(length.UserString)
        self._btForm.tabScaling._form.scaledDiameterInput.setText(diameter.UserString)

    def onOd(self, value : str) -> None:
        try:
            # self._obj.Diameter = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.setOuterDiameter(FreeCAD.Units.Quantity(value).Value)
            self._setIdFromThickness()
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def _setAutoDiameterState(self) -> None:
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

    def _setAutoLengthState(self) -> None:
        if self._isAssembly:
            self._btForm.lengthInput.setEnabled(not self._obj.AutoLength)
            self._btForm.autoLengthCheckbox.setChecked(self._obj.AutoLength)
            self._btForm.autoLengthCheckbox.setEnabled(True)
        else:
            self._btForm.lengthInput.setEnabled(True)
            self._obj.AutoLength = False
            self._btForm.autoLengthCheckbox.setChecked(self._obj.AutoLength)
            self._btForm.autoLengthCheckbox.setEnabled(False)

        if self._obj.AutoLength:
            self._obj.Length = self._obj.Proxy.getLength()
            self._btForm.lengthInput.setText(self._obj.Length.UserString)

    def onAutoDiameter(self, value : bool) -> None:
        self._obj.Proxy.setOuterDiameterAutomatic(value)
        self._setAutoDiameterState()

        self._obj.Proxy.execute(self._obj)
        self.setEdited()

    def onAutoLength(self, value : str) -> None:
        self._obj.Proxy.setLengthAutomatic(value)
        self._setAutoLengthState()

        self._obj.Proxy.execute(self._obj)
        self.setEdited()

    def _setThicknessFromId(self, value : str) -> None:
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

    def onId(self, value : str) -> None:
        try:
            self._setThicknessFromId(value)
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def _setIdFromThickness(self) -> None:
        od = float(self._obj.Diameter.Value)
        if od > 0.0:
            id = od - 2.0 * float(self._obj.Thickness)
            self._btForm.idInput.setText(FreeCAD.Units.Quantity(id).UserString)
        else:
            self._btForm.idInput.setText(FreeCAD.Units.Quantity(0.0).UserString)

    def onThickness(self, value : str) -> None:
        try:
            self._obj.Proxy.setThickness(FreeCAD.Units.Quantity(value).Value)
            self._setIdFromThickness()
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def onLength(self, value : str) -> None:
        try:
            self._obj.Proxy.setLength(FreeCAD.Units.Quantity(value).Value)
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def onLookup(self) -> None:
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

    def onLocation(self) -> None:
        self._obj.Proxy.updateChildren()
        self._obj.Proxy.execute(self._obj)
        self.setEdited()

    def getStandardButtons(self) -> Any:
        return QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Apply

    def clicked(self,button) -> None:
        if button == QtGui.QDialogButtonBox.Apply:
            self.transferTo()
            self._obj.Proxy.execute(self._obj)

    def update(self) -> None:
        'fills the widgets'
        self.transferFrom()

    def accept(self) -> None:
        self.transferTo()
        FreeCAD.ActiveDocument.commitTransaction()
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.resetEdit()


    def reject(self) -> None:
        FreeCAD.ActiveDocument.abortTransaction()
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.resetEdit()
        self.setEdited()
        FreeCAD.ActiveDocument.recompute()
