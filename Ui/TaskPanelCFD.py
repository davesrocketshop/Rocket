# ***************************************************************************
# *   Copyright (c) 2024 David Carter <dcarter@davidcarter.ca>              *
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
"""Class for CFD Analyzer"""

__title__ = "FreeCAD CFD Analyzer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui
import os
import math

from DraftTools import translate

from PySide import QtGui, QtCore
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGridLayout

from Rocket.cfd.CFDUtil import caliber, createSolid, makeCFDRocket, makeWindTunnel

from Ui.UIPaths import getUIPath

class _DialogCFD(QDialog):
    def __init__(self, rocket):
        # super().__init__()

        self._rocket = rocket
        path = os.path.join(getUIPath(), 'Ui', 'Resources', 'ui', "DialogCFD.ui")
        print(path)
        self._form = FreeCADGui.PySideUic.loadUi(os.path.join(getUIPath(), 'Ui', 'Resources', 'ui', "DialogCFD.ui"))
        if self._form is None:
            print("Form is empty")
        self._studies = (translate("Rocket", "Example"),)
        self._form.comboStudy.addItems(self._studies)
        self._form.show()

    def update(self):
        'fills the widgets'
        # self.transferFrom()
        pass

    def accept(self):
        # self.transferTo()
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.resetEdit()
        FreeCADGui.Control.closeDialog()

    # def unsetEdit(self, vobj, mode):
    #     if self.taskd:
    #         self.taskd.closing()
    #         self.taskd = None
    #     FreeCADGui.Control.closeDialog()

    def reject(self):
        FreeCAD.ActiveDocument.abortTransaction()
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.resetEdit()
        # self.setEdited()
        FreeCADGui.Control.closeDialog()

class TaskPanelCFD(QtCore.QObject):

    def __init__(self, rocket):
        super().__init__()

        self._rocket = rocket

        self.form = FreeCADGui.PySideUic.loadUi(os.path.join(getUIPath(), 'Resources', 'ui', "DialogCFD.ui"))
        # self.form = FreeCADGui.PySideUic.loadUi(':/ui/DialogCFD.ui')

        self._studies = (translate("Rocket", "Coarse"),translate("Rocket", "Fine"),)
        self.form.comboStudy.addItems(self._studies)

        self.form.buttonCreate.clicked.connect(self.onCreate)

        FreeCAD.setActiveTransaction("Create Rocket CFD Study")
        self.update()

    def update(self):
        # Set Nproc to the number of available threads
        if hasattr(os, "sched_getaffinity"):
            self.form.spinNproc.setValue(len(os.sched_getaffinity(0)))
        else:
            self.form.spinNproc.setValue(os.cpu_count())

        self._solid = createSolid(self._rocket)
        diameter = caliber(self._rocket)
        box = self._solid.BoundBox
        length = box.XLength

        self.form.inputLength.setText(str(length))
        self.form.inputDiameter.setText(str(diameter))

    def transferTo(self):
        "Transfer from the dialog to the object"
        # self._obj.Proxy.setOuterDiameter(FreeCAD.Units.Quantity(self._btForm.odInput.text()).Value)
        # self._obj.Proxy.setOuterDiameterAutomatic(self._btForm.autoDiameterCheckbox.isChecked())
        # self._obj.Proxy.setThickness(FreeCAD.Units.Quantity(self._btForm.thicknessInput.text()).Value)
        # self._obj.Proxy.setLength(FreeCAD.Units.Quantity(self._btForm.lengthInput.text()).Value)
        # if self._motorMount:
        #     self._obj.MotorMount = self._btForm.motorGroup.isChecked()
        #     self._obj.Overhang = self._btForm.overhangInput.text()

        # self._btForm.tabMaterial.transferTo(self._obj)
        # self._btForm.tabComment.transferTo(self._obj)
        pass

    def transferFrom(self):
        "Transfer from the object to the dialog"
        # self._btForm.odInput.setText(self._obj.Diameter.UserString)
        # self._btForm.autoDiameterCheckbox.setChecked(self._obj.AutoDiameter)
        # self._btForm.idInput.setText("0.0")
        # self._btForm.thicknessInput.setText(self._obj.Thickness.UserString)
        # self._btForm.lengthInput.setText(self._obj.Length.UserString)
        # if self._motorMount:
        #     self._btForm.motorGroup.setChecked(self._obj.MotorMount)
        #     self._btForm.overhangInput.setText(self._obj.Overhang.UserString)

        # self._btForm.tabMaterial.transferFrom(self._obj)
        # self._btForm.tabComment.transferFrom(self._obj)

        # self._setAutoDiameterState()
        # self._setIdFromThickness()
        # self._setMotorState()
        pass

    def onCreate(self):
        CFDrocket = makeCFDRocket()
        CFDrocket._obj.Shape = self._solid
        diameter = FreeCAD.Units.Quantity(self.form.inputDiameter.text()).Value
        length = FreeCAD.Units.Quantity(self.form.inputLength.text()).Value

        # Get a blockage ratio of 0.1%
        area = (diameter * diameter) / 0.001
        tunnelDiameter = math.sqrt(area)
        FreeCADGui.doCommand("Ui.Commands.CmdCFDAnalysis.makeWindTunnel('WindTunnel',{},{},{})".format(tunnelDiameter, 10.0 * length, 2.0 * length))
        FreeCADGui.doCommand("Ui.Commands.CmdCFDAnalysis.makeWindTunnel('Refinement',{},{},{})".format(tunnelDiameter * 0.25, 3.5 * length, 0.5 * length))
        FreeCADGui.doCommand("Ui.Commands.CmdCFDAnalysis.makeWindTunnel('Refinement',{},{},{})".format(tunnelDiameter * 0.5, 9.0 * length, 1.0 * length))
        FreeCADGui.doCommand("Ui.Commands.CmdCFDAnalysis.makeWindTunnel('Refinement',{},{},{})".format(tunnelDiameter * 0.75, 9.5 * length, 1.5 * length))
        FreeCAD.ActiveDocument.recompute()

        # self.deactivate()
        # FreeCAD.closeActiveTransaction()
        self.form.buttonCreate.setEnabled(False)

    def accept(self):
        self.deactivate()
        FreeCAD.closeActiveTransaction()
        return True

    def reject(self):
        self.deactivate()
        FreeCAD.closeActiveTransaction(True)
        return True

    def deactivate(self):
        # pref = Preferences.preferences()
        # pref.SetBool("BOMOnlyParts", self.form.CheckBox_onlyParts.isChecked())
        # pref.SetBool("BOMDetailParts", self.form.CheckBox_detailParts.isChecked())
        # pref.SetBool("BOMDetailSubAssemblies", self.form.CheckBox_detailSubAssemblies.isChecked())

        if FreeCADGui.Control.activeDialog():
            FreeCADGui.Control.closeDialog()
