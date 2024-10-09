# ***************************************************************************
# *   Copyright (c) 2021-2024 David Carter <dcarter@davidcarter.ca>         *
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
"""Class for database lookups"""

__title__ = "FreeCAD Database Lookup"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import sqlite3

import FreeCAD

from DraftTools import translate

from PySide import QtGui, QtCore
from PySide.QtGui import QStandardItemModel, QStandardItem
from PySide.QtWidgets import QVBoxLayout, QHBoxLayout

from Rocket.Utilities import _valueWithUnits

from Rocket.Parts.Material import listMaterials

# Constant definitions
userCancelled   = "Cancelled"
userOK          = "OK"

class DialogMaterialMapping(QtGui.QDialog):

    def __init__(self):
        super().__init__()

        self._model = QStandardItemModel() # (4, 4)

        # self.initSortColumns(lookup)
        self.initUI()
        self.initDB()

        # Default result is an empty dict
        self.result = {}

    def initUI(self):
        global _compatible

        self.result = userCancelled

        # create our window
        # define window		xLoc,yLoc,xDim,yDim
        self.setGeometry(	250, 250, 640, 480)
        self.setWindowTitle(translate('Rocket', "Component lookup..."))
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        searchLabel = QtGui.QLabel(translate('Rocket', "Search"), self)

        self._searchInput = QtGui.QLineEdit(self)
        self._searchInput.setMinimumWidth(80)
        self._searchInput.textEdited.connect(self.onSearch)

        self._dbTable = QtGui.QTableView(self)
        self._dbTable.setModel(self._model)

        self._dbTable.setSelectionBehavior(QtGui.QTableView.SelectRows)
        self._dbTable.setSelectionMode(QtGui.QTableView.SingleSelection)
        self._dbTable.setSortingEnabled(True)
        # self._dbTable.doubleClicked.connect(self.onTableDoubleClick)

        # cancel button
        cancelButton = QtGui.QPushButton('Cancel', self)
        cancelButton.clicked.connect(self.onCancel)
        cancelButton.setAutoDefault(True)

        # OK button
        okButton = QtGui.QPushButton('OK', self)
        okButton.setDefault(True)
        okButton.clicked.connect(self.onOk)

        layout = QVBoxLayout()
        line = QHBoxLayout()
        line.addWidget(searchLabel)
        line.addWidget(self._searchInput)
        line.addStretch()
        layout.addLayout(line)

        layout.addWidget(self._dbTable)

        line = QHBoxLayout()
        line.addStretch()
        line.addWidget(okButton)
        line.addWidget(cancelButton)
        layout.addLayout(line)

        self.setLayout(layout)

        # now make the window visible
        self.show()

    def initDB(self):
        self._connection = sqlite3.connect("file:" + FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/parts/Parts.db?mode=ro", uri=True)
        self._connection.row_factory = sqlite3.Row
        self._updateModel()

    # def onLookupType(self, value):
    #     self._updateModel()

    def onSearch(self, value):
        rows = []
        value = str(value).strip()
        if len(value) > 0:
            for column in range(self._model.columnCount()):
                items = self._model.findItems(value, QtCore.Qt.MatchContains, column)
                for item in items:
                    row = item.row()
                    if not row in rows:
                        rows.append(row)

            for row in range(self._model.rowCount()):
                if row in rows:
                    self._dbTable.showRow(row)
                else:
                    self._dbTable.hideRow(row)
        else:
            for row in range(self._model.rowCount()):
                self._dbTable.showRow(row)

    def onTableDoubleClick(self, selected):
        self.result = self._getSelected(selected.row())
        self.close()

    def onCancel(self):
        self.result = {}
        self.close()

    def onOk(self):
        selected = self._dbTable.selectedIndexes()
        if len(selected) > 0:
            row = selected[0].row()
            self.result = self._getSelected(row)
        else:
            self.result = {}
        self.close()

    def _getItemFromRow(self, row):
        item = self._model.item(row, 0)
        return item

    def _getSelected(self, row):
        return {}

    def _itemWithDimension(self, value, dim):
        return self._newItem(_valueWithUnits(value, dim))

    def _newItem(self, text):
        item = QStandardItem(text)
        item.setEditable(False)
        return item

    def _queryMaterial(self):
        rows = listMaterials(self._connection)

        self._model.setRowCount(len(rows))
        self._model.setColumnCount(5)
        self._dbTable.hideColumn(0) # This holds index for lookups
        self._dbTable.setVerticalHeader(None)

        # Add the column headers
        self._model.setHorizontalHeaderItem(1, self._newItem(translate('Rocket', "Manufacturer")))
        self._model.setHorizontalHeaderItem(2, self._newItem(translate('Rocket', "Material Name")))
        self._model.setHorizontalHeaderItem(3, self._newItem(translate('Rocket', "Type")))
        self._model.setHorizontalHeaderItem(4, self._newItem(translate('Rocket', "Density")))

        for rowCount, row in enumerate(rows):
            self._model.setItem(rowCount, 0, self._newItem(str(row["material_index"])))
            self._model.setItem(rowCount, 1, self._newItem(str(row["manufacturer"])))
            self._model.setItem(rowCount, 2, self._newItem(str(row["material_name"])))
            self._model.setItem(rowCount, 3, self._newItem(str(row["type"])))
            self._model.setItem(rowCount, 4, self._newItem(self._itemWithDimension(row["density"], row["units"])))
            # self._model.setItem(rowCount, 4, self._newItem(str(row["density"]) + " " + str(row["units"])))

    def _updateModel(self):
        self._queryMaterial()

    def update(self):
        # Update the SQL query
        pass
