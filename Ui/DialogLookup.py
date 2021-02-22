# ***************************************************************************
# *   Copyright (c) 2021 David Carter <dcarter@davidcarter.ca>              *
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
import FreeCADGui

from DraftTools import translate

from PySide import QtGui, QtCore
from PySide.QtGui import QStandardItemModel, QStandardItem
from PySide.QtCore import QModelIndex
from PySide2.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTableView

from App.Constants import COMPONENT_TYPE_BODYTUBE, COMPONENT_TYPE_BULKHEAD, COMPONENT_TYPE_CENTERINGRING, \
    COMPONENT_TYPE_COUPLER, COMPONENT_TYPE_ENGINEBLOCK, COMPONENT_TYPE_LAUNCHLUG, COMPONENT_TYPE_NOSECONE, \
    COMPONENT_TYPE_PARACHUTE, COMPONENT_TYPE_STREAMER, COMPONENT_TYPE_TRANSITION

from App.Parts.NoseCone import NoseCone


# Constant definitions
userCancelled   = "Cancelled"
userOK          = "OK"

# Compatible component lookup types
_compatible = {
    COMPONENT_TYPE_BODYTUBE : (COMPONENT_TYPE_BODYTUBE, COMPONENT_TYPE_COUPLER, COMPONENT_TYPE_ENGINEBLOCK, COMPONENT_TYPE_LAUNCHLUG,),
    COMPONENT_TYPE_BULKHEAD : (COMPONENT_TYPE_BULKHEAD,),
    COMPONENT_TYPE_CENTERINGRING : (COMPONENT_TYPE_CENTERINGRING,),
    COMPONENT_TYPE_COUPLER : (COMPONENT_TYPE_BODYTUBE, COMPONENT_TYPE_COUPLER, COMPONENT_TYPE_ENGINEBLOCK, COMPONENT_TYPE_LAUNCHLUG,),
    COMPONENT_TYPE_ENGINEBLOCK : (COMPONENT_TYPE_BODYTUBE, COMPONENT_TYPE_COUPLER, COMPONENT_TYPE_ENGINEBLOCK, COMPONENT_TYPE_LAUNCHLUG,),
    COMPONENT_TYPE_LAUNCHLUG : (COMPONENT_TYPE_BODYTUBE, COMPONENT_TYPE_COUPLER, COMPONENT_TYPE_ENGINEBLOCK, COMPONENT_TYPE_LAUNCHLUG,),
    COMPONENT_TYPE_NOSECONE : (COMPONENT_TYPE_NOSECONE,),
    COMPONENT_TYPE_PARACHUTE : (COMPONENT_TYPE_PARACHUTE, COMPONENT_TYPE_STREAMER,),
    COMPONENT_TYPE_STREAMER : (COMPONENT_TYPE_PARACHUTE, COMPONENT_TYPE_STREAMER,),
    COMPONENT_TYPE_TRANSITION : (COMPONENT_TYPE_TRANSITION,)
}

class DialogLookup(QtGui.QDialog):
    """"""
    def __init__(self, lookup):
        super().__init__()

        self._lookup = lookup
        self._model = QStandardItemModel() # (4, 4)

        self.initUI()
        self.initDB()

    def initUI(self):
        global _compatible

        self.result = userCancelled

        # create our window
        # define window		xLoc,yLoc,xDim,yDim
        self.setGeometry(	250, 250, 400, 350)
        self.setWindowTitle(translate('Rocket', "Component lookup..."))
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        searchLabel = QtGui.QLabel(translate('Rocket', "Search"), self)

        self._searchInput = QtGui.QLineEdit(self)
        self._searchInput.setFixedWidth(80)

        lookupTypeLabel = QtGui.QLabel(translate('Rocket', "Component"), self)

        self._lookupTypeCombo = QtGui.QComboBox(self)
        self._lookupTypeCombo.addItems(_compatible[self._lookup])
        self._lookupTypeCombo.setCurrentText(self._lookup)
        self._lookupTypeCombo.currentTextChanged.connect(self.onLookupType)

        self._dbTable = QtGui.QTableView(self)
        self._dbTable.setModel(self._model)
        self._dbTable.setSelectionBehavior(QtGui.QTableView.SelectRows)
        self._dbTable.setSelectionMode(QtGui.QTableView.SingleSelection)
        self._dbTable.setSortingEnabled(True)
        self._dbTable.doubleClicked.connect(self.onTableDoubleClick)

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
        line.addWidget(lookupTypeLabel)
        line.addWidget(self._lookupTypeCombo)
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

    def onLookupType(self, value):
        self._updateModel()

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

    def _getSelected(self, row):
        try:
            index = int(self._model.item(row, 0).text())
            cone = NoseCone.getNoseCone(self._connection, index)
            return cone
        except NotFoundError:
            _err(translate('Rocket', "Nose cone not found"))
        except MultipleEntryError:
            _err(translate('Rocket', "Multiple identical entries found"))
        return {}

    def _itemWithDimension(self, value, dim):
        return self._newItem("%f %s" % (value, dim))

    def _newItem(self, text):
        item = QStandardItem(text)
        item.setEditable(False)
        return item

    def _queryNoseCone(self):
        rows = NoseCone.listNoseCones(self._connection)

        self._model.setRowCount(len(rows))
        self._model.setColumnCount(9)
        self._dbTable.hideColumn(0) # This holds index for lookups
        self._dbTable.setVerticalHeader(None)

        # Add the column headers
        self._model.setHorizontalHeaderItem(1, self._newItem(translate('Rocket', "Manufacturer")))
        self._model.setHorizontalHeaderItem(2, self._newItem(translate('Rocket', "Part Number")))
        self._model.setHorizontalHeaderItem(3, self._newItem(translate('Rocket', "Description")))
        self._model.setHorizontalHeaderItem(4, self._newItem(translate('Rocket', "Diameter")))
        self._model.setHorizontalHeaderItem(5, self._newItem(translate('Rocket', "Length")))
        self._model.setHorizontalHeaderItem(6, self._newItem(translate('Rocket', "Shoulder Diameter")))
        self._model.setHorizontalHeaderItem(7, self._newItem(translate('Rocket', "Shoulder Length")))
        self._model.setHorizontalHeaderItem(8, self._newItem(translate('Rocket', "Shape")))

        rowCount = 0
        for row in rows:
            self._model.setItem(rowCount, 0, self._newItem(str(row["nose_index"])))
            self._model.setItem(rowCount, 1, self._newItem(str(row["manufacturer"])))
            self._model.setItem(rowCount, 2, self._newItem(str(row["part_number"])))
            self._model.setItem(rowCount, 3, self._newItem(str(row["description"])))
            self._model.setItem(rowCount, 4, self._newItem(self._itemWithDimension(row["diameter"], row["diameter_units"])))
            self._model.setItem(rowCount, 5, self._newItem(self._itemWithDimension(row["length"], row["length_units"])))
            self._model.setItem(rowCount, 6, self._newItem(self._itemWithDimension(row["shoulder_diameter"], row["shoulder_diameter_units"])))
            self._model.setItem(rowCount, 7, self._newItem(self._itemWithDimension(row["shoulder_length"], row["shoulder_length_units"])))
            self._model.setItem(rowCount, 8, self._newItem(str(row["shape"])))

            rowCount += 1

    def _updateModel(self):
        queryType = str(self._lookupTypeCombo.currentText())
        if queryType == COMPONENT_TYPE_BODYTUBE:
            pass
        elif queryType == COMPONENT_TYPE_BULKHEAD:
            pass
        elif queryType == COMPONENT_TYPE_CENTERINGRING:
            pass
        elif queryType == COMPONENT_TYPE_COUPLER:
            pass
        elif queryType == COMPONENT_TYPE_ENGINEBLOCK:
            pass
        elif queryType == COMPONENT_TYPE_LAUNCHLUG:
            pass
        elif queryType == COMPONENT_TYPE_NOSECONE:
            self._queryNoseCone()
        elif queryType == COMPONENT_TYPE_PARACHUTE:
            pass
        elif queryType == COMPONENT_TYPE_STREAMER:
            pass
        elif queryType == COMPONENT_TYPE_TRANSITION:
            pass

    def update():
        # Update the SQL query
        pass
