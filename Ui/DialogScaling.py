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

from DraftTools import translate

from PySide import QtGui, QtCore, QtWidgets
# from PySide.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGridLayout
from PySide.QtGui import QStandardItemModel, QStandardItem

from Rocket.Constants import COMPONENT_TYPE_BODYTUBE

from Rocket.Parts.BodyTube import searchBodyTube, listBodyTubesBySize
from Rocket.Utilities import _valueWithUnits, _valueOnly

from Ui.UIPaths import getUIPath

def saveDialog(dialog, dialogName):
    param = FreeCAD.ParamGet(f"User parameter:BaseApp/Preferences/Mod/Material/Resources/Modules/Rocket/Dialog/{dialogName}")

    geom = dialog.geometry()
    param.SetInt("Width", geom.width())
    param.SetInt("Height", geom.height())
    param.SetInt("x", geom.x())
    param.SetInt("y", geom.y())

def restoreDialog(dialog, dialogName, defaultWidth, defaultHeight):
    param = FreeCAD.ParamGet(f"User parameter:BaseApp/Preferences/Mod/Material/Resources/Modules/Rocket/Dialog/{dialogName}")
    width = param.GetInt("Width", defaultWidth)
    height = param.GetInt("Height", defaultHeight)
    x = param.GetInt("x", 100)
    y = param.GetInt("y", 100)

    dialog.move(x, y)
    dialog.resize(width, height)

class DialogScaling(QtCore.QObject):
    progressUpdate = QtCore.Signal(object)
    threadComplete = QtCore.Signal(object)

    def worker(self):
        connection = self.initDB()
        ref1 = FreeCAD.Units.Quantity(self.form.inputReference1.text()).Value
        scale = FreeCAD.Units.Quantity(self.form.spinScale.text()).Value
        tolerance = self.form.spinTolerance.value()

        if ref1 > 0 and scale > 0 and tolerance > 0:
            target = ref1 / scale
            min_diameter = target - (target * (tolerance / 100.0))
            max_diameter = target + (target * (tolerance / 100.0))
            scaled = searchBodyTube(connection, min_diameter, max_diameter, COMPONENT_TYPE_BODYTUBE)

            steps = len(scaled)
            step = 1
            if len(scaled) > 0:
                for tube in scaled:
                    error = (float(tube['outer_diameter']) - target) * 100.0 / target
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

    def initDB(self):
        connection = sqlite3.connect("file:" + FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/parts/Parts.db?mode=ro", uri=True)
        connection.row_factory = sqlite3.Row

        return connection

    def initUI(self):

        self.form = FreeCADGui.PySideUic.loadUi(os.path.join(getUIPath(), 'Resources', 'ui', "DialogBodyScale.ui"))

        self.form.tableResults.setModel(self._model)
        self.form.progressBar.setHidden(True)

        self.customizeUI()
        restoreDialog(self.form, self.getDialogName(), 400, 307)

        self.progressUpdate.connect(self.onProgress)
        self.threadComplete.connect(self.onThreadComplete)

        self.form.tableResults.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.form.tableResults.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        selectionModel = self.form.tableResults.selectionModel()
        selectionModel.selectionChanged.connect(self.onSelection)

        self.form.checkMinimum.stateChanged.connect(self.onMinimum)
        self.form.checkMaximum.stateChanged.connect(self.onMaximum)
        self.form.buttonSearch.clicked.connect(self.onSearch)
        self.form.buttonCSV.clicked.connect(self.onExportCSV)
        self.form.accepted.connect(self.saveWindow)
        self.form.rejected.connect(self.saveWindow)

        # Not enabled until we have some search results
        self.form.buttonCSV.setEnabled(False)
        self.form.buttonAddToDocument.setEnabled(False)

    def customizeUI(self):
        self.form.setWindowTitle(translate('Rocket', "Body Scaler"))
        self.form.labelReference1.setText(translate('Rocket', "Reference Diameter"))
        self.form.labelReference2.setHidden(True)
        self.form.inputReference2.setHidden(True)

        self.form.checkMinimum.setHidden(True)
        self.form.checkMaximum.setHidden(True)
        self.form.inputMinimum.setHidden(True)
        self.form.inputMaximum.setHidden(True)

    def _newItem(self, text):
        item = QStandardItem(text)
        item.setEditable(False)
        return item

    def _itemWithDimension(self, value, dim):
        return self._newItem(_valueWithUnits(value, dim))

    def enableButtons(self, enabled):
        self.form.buttonSearch.setEnabled(enabled)
        self.form.buttonCSV.setEnabled(enabled)
        if FreeCAD.ActiveDocument:
            self.form.buttonAddToDocument.setEnabled(enabled)
        else:
            self.form.buttonAddToDocument.setEnabled(False)

    def onSearch(self, checked):
        self.enableButtons(False)

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
        self.form.tableResults.hideColumn(0) # This holds index for lookups

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
        if items is not None:
            self._model.appendRow(items)
        self.form.progressBar.setValue(value)

    def onMinimum(self, state):
        self.form.inputMinimum.setEnabled(self.form.checkMinimum.checkState() == QtCore.Qt.Checked)

    def onMaximum(self, state):
        self.form.inputMaximum.setEnabled(self.form.checkMaximum.checkState() == QtCore.Qt.Checked)

    def onSelection(self, selected, deselected):
        print("onSelection()")

    def exec_(self):
        self.form.exec_()

    def getParam(self):
        name = self.getDialogName()
        return FreeCAD.ParamGet(f"User parameter:BaseApp/Preferences/Mod/Material/Resources/Modules/Rocket/Dialog/{name}")
    
    def getDialogName(self) -> str:
        return "DialogScaling"

    def saveWindow(self):
        saveDialog(self.form, self.getDialogName())

class DialogScalingPairs(DialogScaling):

    def worker(self):
        connection = self.initDB()
        ref1 = FreeCAD.Units.Quantity(self.form.inputReference1.text()).Value
        ref2 = FreeCAD.Units.Quantity(self.form.inputReference2.text()).Value
        tolerance = self.form.spinTolerance.value()
        minimumOD = None
        if self.form.checkMinimum.checkState() == QtCore.Qt.Checked:
            minimumOD = FreeCAD.Units.Quantity(self.form.inputMinimum.text()).Value
        maximumOD = None
        if self.form.checkMaximum.checkState() == QtCore.Qt.Checked:
            maximumOD = FreeCAD.Units.Quantity(self.form.inputMaximum.text()).Value

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
                od = float(tube["outer_diameter"])
                target = od * scale
                if maximumOD is None or target < maximumOD:
                    min_diameter = target - (target * (tolerance / 100.0))
                    max_diameter = target + (target * (tolerance / 100.0))
                    if maximumOD is not None:
                        max_diameter = min(max_diameter, maximumOD)
                    scaled = searchBodyTube(connection, min_diameter, max_diameter, COMPONENT_TYPE_BODYTUBE)
                    if len(scaled) > 0:
                        for tube2 in scaled:
                            error = (float(tube2['outer_diameter']) - target) * 100.0 / target
                            # dia = _valueOnly(tube['outer_diameter'], tube["outer_diameter_units"])
                            # print(f"scale: {ref1} - {dia}")
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
        self.form.labelScale.setHidden(True)
        self.form.spinScale.setHidden(True)

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
        self.form.tableResults.hideColumn(0) # This holds index for lookups
        self.form.tableResults.hideColumn(5)

    def getDialogName(self) -> str:
        return "DialogScalingPairs"
