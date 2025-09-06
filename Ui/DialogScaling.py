# ***************************************************************************
# *   Copyright (c) 2025 David Carter <dcarter@davidcarter.ca>              *
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
"""Class for Scaling Dialog"""

__title__ = "FreeCAD Scaling Dialog"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import os
import sqlite3
import threading
import csv

import FreeCAD
import FreeCADGui
import Materials

from Rocket.Utilities import translate

from PySide import QtGui, QtCore, QtWidgets
# from PySide.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGridLayout
from PySide.QtGui import QStandardItemModel, QStandardItem

from Rocket.Constants import COMPONENT_TYPE_BODYTUBE

from Rocket.Parts.BodyTube import searchBodyTube, listBodyTubesBySize, getBodyTube
from Rocket.Utilities import _valueWithUnits, _valueOnly, _err

from Rocket.Parts.Exceptions import MultipleEntryError, NotFoundError

from Ui.UIPaths import getUIPath
from Ui.Commands.CmdBodyTube import makeBodyTube
from Ui.Commands.CmdStage import addToStage

from Ui.DialogUtilities import saveDialog, restoreDialog

class DialogScaling(QtCore.QObject):
    progressUpdate = QtCore.Signal(object)
    threadComplete = QtCore.Signal(object)

    def worker(self):
        connection = self.initDB()
        ref1 = FreeCAD.Units.Quantity(self.form.reference1Input.text()).Value
        scale = self.form.scaleValueSpinbox.value()
        tolerance = self.form.toleranceSpinbox.value()

        if ref1 > 0 and scale > 0 and tolerance > 0:
            target = ref1 / scale
            min_diameter = target - (target * (tolerance / 100.0))
            max_diameter = target + (target * (tolerance / 100.0))
            scaled = searchBodyTube(connection, min_diameter, max_diameter, COMPONENT_TYPE_BODYTUBE)

            steps = len(scaled)
            step = 1
            if len(scaled) > 0:
                for tube in scaled:
                    error = (float(tube['normalized_diameter']) - target) * 100.0 / target
                    newScale = ref1 / _valueOnly(tube['outer_diameter'], tube["outer_diameter_units"])
                    self.progressUpdate.emit(([
                            self._newItem(str(tube["body_tube_index"])),
                            self._newItem(str(tube["manufacturer"])),
                            self._newItem(str(tube["part_number"])),
                            self._newItem(str(tube["description"])),
                            self._itemWithDimension(tube["outer_diameter"], tube["outer_diameter_units"]),
                            self._newItem(f"{newScale:.2f}"),
                            self._newItem(f"{error:.2f}")
                        ], int(step * 100.0 /steps)))
                    step = step + 1
            else:
                self.progressUpdate.emit((None, 100))

        self.threadComplete.emit(None)

    def __init__(self):
        super().__init__()

        self._model = QStandardItemModel()

        self.initUI()
        # self.initDB()

        self._materialManager = Materials.MaterialManager()

    def initDB(self):
        connection = sqlite3.connect("file:" + FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/parts/Parts.db?mode=ro", uri=True)
        connection.row_factory = sqlite3.Row

        return connection

    def initUI(self):

        self.form = FreeCADGui.PySideUic.loadUi(os.path.join(getUIPath(), 'Resources', 'ui', "DialogBodyScale.ui"))

        self.form.resultsTable.setModel(self._model)
        self.form.progressBar.setHidden(True)

        self.customizeUI()
        restoreDialog(self.form, self.getDialogName(), 400, 307)

        self.progressUpdate.connect(self.onProgress)
        self.threadComplete.connect(self.onThreadComplete)

        self.form.resultsTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.form.resultsTable.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        selectionModel = self.form.resultsTable.selectionModel()
        selectionModel.selectionChanged.connect(self.onSelection)

        self.form.minimumCheckbox.stateChanged.connect(self.onMinimum)
        self.form.maximumCheckbox.stateChanged.connect(self.onMaximum)
        self.form.searchButton.clicked.connect(self.onSearch)
        self.form.addToDocumentButton.clicked.connect(self.onAddToDocument)
        self.form.exportCSVButton.clicked.connect(self.onExportCSV)
        self.form.accepted.connect(self.saveWindow)
        self.form.rejected.connect(self.saveWindow)

        # Not enabled until we have some search results
        self.form.exportCSVButton.setEnabled(False)
        self.form.addToDocumentButton.setEnabled(False)

        self.restoreParameters()

    def customizeUI(self):
        self.form.setWindowTitle(translate('Rocket', "Body Scaler"))
        self.form.reference1Label.setText(translate('Rocket', "Reference Diameter"))
        self.form.reference2Label.setHidden(True)
        self.form.reference2Input.setHidden(True)

        self.form.minimumCheckbox.setHidden(True)
        self.form.maximumCheckbox.setHidden(True)
        self.form.minimumInput.setHidden(True)
        self.form.maximumInput.setHidden(True)

    def _newItem(self, text):
        item = QStandardItem(text)
        item.setEditable(False)
        return item

    def _itemWithDimension(self, value, dim):
        return self._newItem(_valueWithUnits(value, dim))

    def enableButtons(self, enabled):
        self.form.searchButton.setEnabled(enabled)
        self.form.exportCSVButton.setEnabled(enabled)

    def onSearch(self, checked):
        self.enableButtons(False)
        self.form.addToDocumentButton.setEnabled(False)

        # Do search
        self._model.clear()
        self.setColumnHeaders()

        self.form.progressBar.setHidden(False)
        self.form.progressBar.setValue(0)

        thread = threading.Thread(target=self.worker)
        thread.start()

    def setColumnHeaders(self):
        # Add the column headers
        headers = [
            translate('Rocket', "Index"),
            translate('Rocket', "Manufacturer"),
            translate('Rocket', "Part Number"),
            translate('Rocket', "Description"),
            translate('Rocket', "Outer Diameter"),
            translate('Rocket', "Scale"),
            translate('Rocket', "Error (%)")
        ]
        self._model.setHorizontalHeaderLabels(headers)
        self.form.resultsTable.hideColumn(0) # This holds index for lookups

    def onThreadComplete(self, value):
        self.form.progressBar.setHidden(True)
        self.enableButtons(True)

    def onExportCSV(self, checked):
        columns = self._model.columnCount()
        rows = self._model.rowCount()
        if rows > 0:
            filename = QtGui.QFileDialog.getSaveFileName(QtGui.QApplication.activeWindow(), translate("Rocket","Export CSV File"), None, "CSV file (*.csv)")
            if filename:
                with open(filename[0].encode("utf8"), "w") as csvfile:
                    csvfile = csv.writer(csvfile,delimiter="\t")
                    header = []
                    for column in range(columns):
                        item = self._model.horizontalHeaderItem(column)
                        header.append(item.text())
                    csvfile.writerow(header)
                    for i in range(rows):
                        row = []
                        for column in range(columns):
                            item = self._model.item(i, column)
                            row.append(item.text())
                        csvfile.writerow(row)
                print("successfully exported ",filename[0])

    def onProgress(self, progress):
        items = progress[0]
        value = progress[1]
        if items:
            self._model.appendRow(items)
        self.form.progressBar.setValue(value)

    def onMinimum(self, state):
        self.form.minimumInput.setEnabled(self.form.minimumCheckbox.checkState() == QtCore.Qt.Checked)

    def onMaximum(self, state):
        self.form.maximumInput.setEnabled(self.form.maximumCheckbox.checkState() == QtCore.Qt.Checked)

    def onSelection(self, selected, deselected):
        if FreeCAD.ActiveDocument:
            self.form.addToDocumentButton.setEnabled(True)
        else:
            self.form.addToDocumentButton.setEnabled(False)

    def onAddToDocument(self):
        selectionModel = self.form.resultsTable.selectionModel()
        for row in selectionModel.selectedRows():
            self.addBodyTubes(row.row())

    def addBodyTubes(self, row):
        connection = self.initDB()
        try:
            item = self._model.item(row, 0)
            index = int(item.text())
            tube = getBodyTube(connection, index)
            self.addTubeToDocument(tube)
        except NotFoundError:
            _err(translate('Rocket', "Body tube not found"))
        except MultipleEntryError:
            _err(translate('Rocket', "Multiple identical entries found"))

    def addTubeToDocument(self, tube):
        bodyTube = makeBodyTube()
        bodyTube._obj.Manufacturer = tube["manufacturer"]
        bodyTube._obj.PartNumber = tube["part_number"]
        bodyTube._obj.Description = tube["description"]

        try:
            bodyTube._obj.ShapeMaterial = self._materialManager.getMaterial(tube["uuid"])
        except Exception:
            _err(translate("Rocket", "Material '{}' not found - using default material").format(tube["uuid"]))

        diameter = _valueOnly(tube["inner_diameter"], tube["inner_diameter_units"])
        bodyTube.setOuterDiameter(_valueOnly(tube["outer_diameter"], tube["outer_diameter_units"]))
        bodyTube.setThickness((bodyTube._obj.Diameter.Value - diameter) / 2.0)
        bodyTube.setLength(_valueOnly(tube["length"], tube["length_units"]))

        bodyTube.execute(bodyTube._obj)
        bodyTube.setEdited()

        addToStage(bodyTube)
        FreeCAD.ActiveDocument.recompute()

    def exec_(self):
        self.form.exec_()

    def getParam(self):
        name = self.getDialogName()
        return FreeCAD.ParamGet(f"User parameter:BaseApp/Preferences/Mod/Material/Resources/Modules/Rocket/Dialog/{name}")

    def getDialogName(self) -> str:
        return "DialogScaling"

    def saveWindow(self):
        saveDialog(self.form, self.getDialogName())
        self.saveParameters()

    def saveParameters(self):
        param = self.getParam()
        param.SetString("ReferenceDiameter1", self.form.reference1Input.text())
        param.SetString("ReferenceDiameter2", self.form.reference2Input.text())
        param.SetFloat("Scale", self.form.scaleValueSpinbox.value())
        param.SetFloat("Tolerance", self.form.toleranceSpinbox.value())
        param.SetBool("HasMinimumDiameter", self.form.minimumCheckbox.checkState() == QtCore.Qt.Checked)
        param.SetBool("HasMaximumDiameter", self.form.maximumCheckbox.checkState() == QtCore.Qt.Checked)
        param.SetString("MinimumDiameter", self.form.minimumInput.text())
        param.SetString("MaximumDiameter", self.form.maximumInput.text())

    def restoreParameters(self):
        param = self.getParam()
        value = param.GetString("ReferenceDiameter1", "0.0 mm")
        self.form.reference1Input.setText(value)
        value = param.GetString("ReferenceDiameter2", "0.0 mm")
        self.form.reference2Input.setText(value)
        value = param.GetFloat("Scale", 1.0)
        self.form.scaleValueSpinbox.setValue(value)
        value = param.GetFloat("Tolerance", 5.0)
        self.form.toleranceSpinbox.setValue(value)
        value = param.GetBool("HasMinimumDiameter", False)
        if value:
            self.form.minimumCheckbox.setCheckState(QtCore.Qt.Checked)
        else:
            self.form.minimumCheckbox.setCheckState(QtCore.Qt.Unchecked)
        value = param.GetBool("HasMaximumDiameter", False)
        if value:
            self.form.maximumCheckbox.setCheckState(QtCore.Qt.Checked)
        else:
            self.form.maximumCheckbox.setCheckState(QtCore.Qt.Unchecked)
        value = param.GetString("MinimumDiameter", "0.0 mm")
        self.form.minimumInput.setText(value)
        value = param.GetString("MaximumDiameter", "0.0 mm")
        self.form.maximumInput.setText(value)

class DialogScalingPairs(DialogScaling):

    def worker(self):
        connection = self.initDB()
        ref1 = FreeCAD.Units.Quantity(self.form.reference1Input.text()).Value
        ref2 = FreeCAD.Units.Quantity(self.form.reference2Input.text()).Value
        tolerance = self.form.toleranceSpinbox.value()
        minimumOD = None
        if self.form.minimumCheckbox.checkState() == QtCore.Qt.Checked:
            minimumOD = FreeCAD.Units.Quantity(self.form.minimumInput.text()).Value
        maximumOD = None
        if self.form.maximumCheckbox.checkState() == QtCore.Qt.Checked:
            maximumOD = FreeCAD.Units.Quantity(self.form.maximumInput.text()).Value

        if ref1 > 0 and ref2 > 0 and tolerance > 0:
            if ref1 > ref2:
                temp = ref1
                ref1 = ref2
                ref2 = temp

            scale = ref2 / ref1
            tubes = listBodyTubesBySize(connection, minimumOD, maximumOD, orderByOD=True)

            steps = len(tubes)
            step = 1
            for tube in tubes:
                od = float(tube["normalized_diameter"])
                target = od * scale
                if maximumOD is None or target < maximumOD:
                    min_diameter = target - (target * (tolerance / 100.0))
                    max_diameter = target + (target * (tolerance / 100.0))
                    if maximumOD:
                        max_diameter = min(max_diameter, maximumOD)
                    scaled = searchBodyTube(connection, min_diameter, max_diameter, COMPONENT_TYPE_BODYTUBE)
                    if len(scaled) > 0:
                        for tube2 in scaled:
                            error = (float(tube2['normalized_diameter']) - target) * 100.0 / target
                            newScale = ref1 / _valueOnly(tube['outer_diameter'], tube["outer_diameter_units"])
                            self.progressUpdate.emit(([
                                    self._newItem(str(tube["body_tube_index"])),
                                    self._newItem(str(tube["manufacturer"])),
                                    self._newItem(str(tube["part_number"])),
                                    self._newItem(str(tube["description"])),
                                    self._itemWithDimension(tube["outer_diameter"], tube["outer_diameter_units"]),
                                    self._newItem(str(tube2["body_tube_index"])),
                                    self._newItem(str(tube2["manufacturer"])),
                                    self._newItem(str(tube2["part_number"])),
                                    self._newItem(str(tube2["description"])),
                                    self._itemWithDimension(tube2["outer_diameter"], tube2["outer_diameter_units"]),
                                    self._newItem(f"{newScale:.2f}"),
                                    self._newItem(f"{error:.2f}")
                                ], int(step * 100.0 /steps)))
                    else:
                        self.progressUpdate.emit((None, int(step * 100.0 /steps)))
                step = step + 1

        self.threadComplete.emit(None)

    def __init__(self):
        super().__init__()

    def customizeUI(self):
        self.form.scaleValueRadio.setHidden(True)
        self.form.scaleValueSpinbox.setHidden(True)

    def setColumnHeaders(self):
        # Add the column headers
        headers = [
            translate('Rocket', "Index"),
            translate('Rocket', "Manufacturer"),
            translate('Rocket', "Part Number"),
            translate('Rocket', "Description"),
            translate('Rocket', "Outer Diameter"),
            translate('Rocket', "Index"),
            translate('Rocket', "Manufacturer"),
            translate('Rocket', "Part Number"),
            translate('Rocket', "Description"),
            translate('Rocket', "Outer Diameter"),
            translate('Rocket', "Scale"),
            translate('Rocket', "Error (%)")
        ]
        self._model.setHorizontalHeaderLabels(headers)
        self.form.resultsTable.hideColumn(0) # This holds index for lookups
        self.form.resultsTable.hideColumn(5)

    def getDialogName(self) -> str:
        return "DialogScalingPairs"

    def addBodyTubes(self, row):
        connection = self.initDB()
        try:
            # There are two tubes to add
            item = self._model.item(row, 0)
            index = int(item.text())
            tube = getBodyTube(connection, index)
            self.addTubeToDocument(tube)

            item = self._model.item(row, 5)
            index = int(item.text())
            tube = getBodyTube(connection, index)
            self.addTubeToDocument(tube)
        except NotFoundError:
            _err(translate('Rocket', "Body tube not found"))
        except MultipleEntryError:
            _err(translate('Rocket', "Multiple identical entries found"))
