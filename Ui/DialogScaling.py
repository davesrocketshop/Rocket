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

import FreeCAD
import FreeCADGui

from DraftTools import translate

from PySide import QtGui, QtCore
# from PySide.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGridLayout
from PySide.QtGui import QStandardItemModel, QStandardItem

from Rocket.Constants import COMPONENT_TYPE_BODYTUBE

from Rocket.Parts.BodyTube import searchBodyTube, listBodyTubes
from Rocket.Utilities import _valueWithUnits, _valueOnly

from Ui.UIPaths import getUIPath

class DialogScaling(QtCore.QObject):
    progressUpdate = QtCore.Signal(object)
    threadComplete = QtCore.Signal(object)

    def worker(self):
        connection = self.initDB()
        ref1 = FreeCAD.Units.Quantity(self.form.inputReference1.text()).Value
        ref2 = FreeCAD.Units.Quantity(self.form.inputReference2.text()).Value
        tolerance = self.form.spinTolerance.value()

        if ref1 > 0 and ref2 > 0 and tolerance > 0:
            if ref1 > ref2:
                temp = ref1
                ref1 = ref2
                ref2 = temp

            scale = ref2 / ref1
            tubes = listBodyTubes(connection, COMPONENT_TYPE_BODYTUBE, orderByOD=True)

            steps = len(tubes)
            step = 1
            for tube in tubes:
                od = float(tube["outer_diameter"])
                target = od * scale
                min_diameter = target - (target * (tolerance / 100.0))
                max_diameter = target + (target * (tolerance / 100.0))
                scaled = searchBodyTube(connection, min_diameter, max_diameter, COMPONENT_TYPE_BODYTUBE)
                if len(scaled) > 0:
                    for tube2 in scaled:
                        error = (float(tube2['outer_diameter']) - target) * 100.0 / target
                        # dia = _valueOnly(tube['outer_diameter'], tube["outer_diameter_units"])
                        # print(f"scale: {ref1} - {dia}")
                        newScale = ref1 / _valueOnly(tube['outer_diameter'], tube["outer_diameter_units"])
                        self.progressUpdate.emit(([
                                self._newItem(str(tube["manufacturer"])),
                                self._newItem(str(tube["part_number"])),
                                self._newItem(str(tube["description"])),
                                self._itemWithDimension(tube["outer_diameter"], tube["outer_diameter_units"]),
                                self._newItem(str(tube2["manufacturer"])),
                                self._newItem(str(tube2["part_number"])),
                                self._newItem(str(tube2["description"])),
                                self._itemWithDimension(tube2["outer_diameter"], tube2["outer_diameter_units"]),
                                self._newItem(f"1:{newScale:.2f}"),
                                self._newItem(f"{error:.2f}")
                            ], int(step * 100.0 /steps)))
                else:
                    self.progressUpdate.emit((None, int(step * 100.0 /steps)))
                step = step + 1

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

        self.progressUpdate.connect(self.onProgress)
        self.threadComplete.connect(self.onThreadComplete)

        self.form.buttonSearch.clicked.connect(self.onSearch)
        self.form.buttonCSV.clicked.connect(self.onExportCSV)

        # Not enabled until we have some search results
        self.form.buttonCSV.setEnabled(False)

    def _newItem(self, text):
        item = QStandardItem(text)
        item.setEditable(False)
        return item

    def _itemWithDimension(self, value, dim):
        return self._newItem(_valueWithUnits(value, dim))

    def enableButtons(self, enabled):
        self.form.buttonSearch.setEnabled(enabled)
        self.form.buttonCSV.setEnabled(enabled)

    def _searchRelative(self):
        connection = self.initDB()
        ref1 = FreeCAD.Units.Quantity(self.form.inputReference1.text()).Value
        ref2 = FreeCAD.Units.Quantity(self.form.inputReference2.text()).Value
        tolerance = self.form.spinTolerance.value()

        if ref1 > 0 and ref2 > 0 and tolerance > 0:
            if ref1 > ref2:
                temp = ref1
                ref1 = ref2
                ref2 = temp

            scale = ref2 / ref1
            tubes = listBodyTubes(connection, COMPONENT_TYPE_BODYTUBE, orderByOD=True)
            self.form.progressBar.setHidden(False)
            self.form.progressBar.setMaximum(len(tubes))

            step = 0
            for tube in tubes:
                od = float(tube["outer_diameter"])
                target = od * scale
                min_diameter = target - (target * (tolerance / 100.0))
                max_diameter = target + (target * (tolerance / 100.0))
                # print(f"Tube {tube['part_number']} min {min_diameter} max {max_diameter}")
                scaled = searchBodyTube(connection, min_diameter, max_diameter, COMPONENT_TYPE_BODYTUBE)
                if len(scaled) > 0:
                    for tube2 in scaled:
                        error = (float(tube2['outer_diameter']) - target) * 100.0 / target
                        newScale = ref1 / _valueOnly(tube['outer_diameter'], tube["outer_diameter_units"])
                        # print(f"\tTube {tube2['part_number']} error {error:.2f}")
                        self._model.appendRow([
                            self._newItem(str(tube["manufacturer"])),
                            self._newItem(str(tube["part_number"])),
                            self._newItem(str(tube["description"])),
                            self._itemWithDimension(tube["outer_diameter"], tube["outer_diameter_units"]),
                            self._newItem(str(tube2["manufacturer"])),
                            self._newItem(str(tube2["part_number"])),
                            self._newItem(str(tube2["description"])),
                            self._itemWithDimension(tube2["outer_diameter"], tube2["outer_diameter_units"]),
                            self._newItem(f"1:{newScale:.2f}"),
                            self._newItem(f"{error:.2f}")
                        ])
                step = step + 1
                self.form.progressBar.setValue(step)
            self.form.progressBar.setHidden(True)

    def onSearch(self, checked):
        self.enableButtons(False)

        # Do search
        self._model.clear()

        # Add the column headers
        self._model.setHorizontalHeaderItem(0, self._newItem(translate('Rocket', "Manufacturer")))
        self._model.setHorizontalHeaderItem(1, self._newItem(translate('Rocket', "Part Number")))
        self._model.setHorizontalHeaderItem(2, self._newItem(translate('Rocket', "Description")))
        self._model.setHorizontalHeaderItem(3, self._newItem(translate('Rocket', "Outer Diameter")))
        self._model.setHorizontalHeaderItem(4, self._newItem(translate('Rocket', "Manufacturer")))
        self._model.setHorizontalHeaderItem(5, self._newItem(translate('Rocket', "Part Number")))
        self._model.setHorizontalHeaderItem(6, self._newItem(translate('Rocket', "Description")))
        self._model.setHorizontalHeaderItem(7, self._newItem(translate('Rocket', "Outer Diameter")))
        self._model.setHorizontalHeaderItem(8, self._newItem(translate('Rocket', "Scale")))
        self._model.setHorizontalHeaderItem(9, self._newItem(translate('Rocket', "Error (%)")))

        self.form.progressBar.setHidden(False)
        self.form.progressBar.setValue(0)

        thread = threading.Thread(target=self.worker)
        thread.start()
        # self._searchRelative()

        # thread.join()

    def onThreadComplete(self, value):
        self.form.progressBar.setHidden(True)
        self.enableButtons(True)

    def onExportCSV(self, checked):
        pass

    def onProgress(self, progress):
        items = progress[0]
        value = progress[1]
        if items is not None:
            self._model.appendRow(items)
        self.form.progressBar.setValue(value)
        # print(f'setValue({value})')

    def exec_(self):
        self.form.exec_()
