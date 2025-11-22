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
"""Class for database lookups"""

__title__ = "FreeCAD Database Lookup"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import sqlite3
import os

import FreeCAD
import FreeCADGui

from PySide import QtGui, QtCore
from PySide.QtGui import QStandardItemModel, QStandardItem
from PySide.QtWidgets import QVBoxLayout, QHBoxLayout

from Rocket.Constants import COMPONENT_TYPE_BODYTUBE, COMPONENT_TYPE_BULKHEAD, COMPONENT_TYPE_CENTERINGRING, \
    COMPONENT_TYPE_COUPLER, COMPONENT_TYPE_ENGINEBLOCK, COMPONENT_TYPE_LAUNCHLUG, COMPONENT_TYPE_NOSECONE, \
    COMPONENT_TYPE_PARACHUTE, COMPONENT_TYPE_STREAMER, COMPONENT_TYPE_TRANSITION, COMPONENT_TYPE_RAILBUTTON, \
    COMPONENT_TYPE_ANY
from Rocket.Utilities import _valueWithUnits, _err

from Rocket.Parts.BodyTube import listBodyTubes, listBodyTubesBySize, getBodyTube
from Rocket.Parts.NoseCone import listNoseCones, listNoseConesBySize, getNoseCone
from Rocket.Parts.Transition import listTransitions, listTransitionsBySize, getTransition
from Rocket.Parts.RailButton import listRailButton, getRailButton

from Rocket.Parts.Exceptions import MultipleEntryError, NotFoundError

translate = FreeCAD.Qt.translate

from Ui.UIPaths import getUIPath
from Ui.DialogUtilities import saveDialog, restoreDialog, getParams
from Ui.Widgets.WaitCursor import WaitCursor

# Constant definitions
userCancelled   = "Cancelled"
userOK          = "OK"

# Compatible component lookup types
_compatible = {
    COMPONENT_TYPE_BODYTUBE : (COMPONENT_TYPE_ANY, COMPONENT_TYPE_BODYTUBE, COMPONENT_TYPE_COUPLER, COMPONENT_TYPE_ENGINEBLOCK, COMPONENT_TYPE_LAUNCHLUG,),
    COMPONENT_TYPE_BULKHEAD : (COMPONENT_TYPE_BULKHEAD,),
    COMPONENT_TYPE_CENTERINGRING : (COMPONENT_TYPE_CENTERINGRING,),
    COMPONENT_TYPE_COUPLER : (COMPONENT_TYPE_ANY, COMPONENT_TYPE_BODYTUBE, COMPONENT_TYPE_COUPLER, COMPONENT_TYPE_ENGINEBLOCK, COMPONENT_TYPE_LAUNCHLUG,),
    COMPONENT_TYPE_ENGINEBLOCK : (COMPONENT_TYPE_ANY, COMPONENT_TYPE_BODYTUBE, COMPONENT_TYPE_COUPLER, COMPONENT_TYPE_ENGINEBLOCK, COMPONENT_TYPE_LAUNCHLUG,),
    COMPONENT_TYPE_LAUNCHLUG : (COMPONENT_TYPE_ANY, COMPONENT_TYPE_BODYTUBE, COMPONENT_TYPE_COUPLER, COMPONENT_TYPE_ENGINEBLOCK, COMPONENT_TYPE_LAUNCHLUG,),
    COMPONENT_TYPE_NOSECONE : (COMPONENT_TYPE_NOSECONE,),
    COMPONENT_TYPE_PARACHUTE : (COMPONENT_TYPE_PARACHUTE, COMPONENT_TYPE_STREAMER,),
    COMPONENT_TYPE_STREAMER : (COMPONENT_TYPE_PARACHUTE, COMPONENT_TYPE_STREAMER,),
    COMPONENT_TYPE_TRANSITION : (COMPONENT_TYPE_TRANSITION,),
    COMPONENT_TYPE_RAILBUTTON : (COMPONENT_TYPE_RAILBUTTON,)
}
_translated = {
    COMPONENT_TYPE_BODYTUBE : translate('Rocket', COMPONENT_TYPE_BODYTUBE),
    COMPONENT_TYPE_BULKHEAD : translate('Rocket', COMPONENT_TYPE_BULKHEAD),
    COMPONENT_TYPE_CENTERINGRING : translate('Rocket', COMPONENT_TYPE_CENTERINGRING),
    COMPONENT_TYPE_COUPLER : translate('Rocket', COMPONENT_TYPE_COUPLER),
    COMPONENT_TYPE_ENGINEBLOCK : translate('Rocket', COMPONENT_TYPE_ENGINEBLOCK),
    COMPONENT_TYPE_LAUNCHLUG : translate('Rocket', COMPONENT_TYPE_LAUNCHLUG),
    COMPONENT_TYPE_NOSECONE : translate('Rocket', COMPONENT_TYPE_NOSECONE),
    COMPONENT_TYPE_PARACHUTE : translate('Rocket', COMPONENT_TYPE_PARACHUTE),
    COMPONENT_TYPE_STREAMER : translate('Rocket', COMPONENT_TYPE_STREAMER),
    COMPONENT_TYPE_TRANSITION : translate('Rocket', COMPONENT_TYPE_TRANSITION),
    COMPONENT_TYPE_RAILBUTTON : translate('Rocket', COMPONENT_TYPE_RAILBUTTON),
    COMPONENT_TYPE_ANY : translate('Rocket', COMPONENT_TYPE_ANY)
}


class DialogLookup: #(QtGui.QDialog):
    def __init__(self, lookup, component = None):
        super().__init__()

        self._lookup = lookup
        self._component = component
        self._model = QStandardItemModel() # (4, 4)
        self._form = FreeCADGui.PySideUic.loadUi(os.path.join(getUIPath(), 'Ui', "DialogLookup.ui"))

        # Default result is an empty dict
        self.result = {}
        self.match = False

        # self.initSortColumns(lookup)
        self.initUI()
        self.initDB()

    def initUI(self):
        global _compatible

        self.result = userCancelled
        param = getParams("DialogLookup")

        # create our window
        restoreDialog(self._form, "DialogLookup", 640, 480)

        self._form.setWindowTitle(translate('Rocket', "Component lookup..."))
        self._form.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        # searchLabel = QtGui.QLabel(translate('Rocket', "Search"), self)

        # self._form.searchInput = QtGui.QLineEdit(self)
        # self._form.searchInput.setMinimumWidth(80)
        self._form.searchInput.textEdited.connect(self.onSearch)
        self._form.matchCheckbox.clicked.connect(self.onMatchComponent)
        self._form.matchSpinbox.valueChanged.connect(self.onMatchTolerance)
        self._form.matchDiameterCheckbox.setChecked(param.GetBool("MatchDiameter", True))
        self._form.matchAftDiameterCheckbox.setChecked(param.GetBool("MatchAftDiameter", True))
        self._form.matchLengthCheckbox.setChecked(param.GetBool("MatchLengthDiameter", True))
        self._form.matchDiameterCheckbox.clicked.connect(self.onMatchDiameter)
        self._form.matchAftDiameterCheckbox.clicked.connect(self.onMatchAftDiameter)
        self._form.matchLengthCheckbox.clicked.connect(self.onMatchLength)

        # lookupTypeLabel = QtGui.QLabel(translate('Rocket', "Component"), self)

        # self._form.lookupTypeCombo = QtGui.QComboBox(self)
        for item in _compatible[self._lookup]:
            self._form.lookupTypeCombo.addItem(_translated[item], item)
        self._form.lookupTypeCombo.setCurrentText(_translated[self._lookup])
        self._form.lookupTypeCombo.currentTextChanged.connect(self.onLookupType)

        # self._form.dbTable = QtGui.QTableView(self)
        self._form.dbTable.setModel(self._model)

        self._form.dbTable.setSelectionBehavior(QtGui.QTableView.SelectRows)
        self._form.dbTable.setSelectionMode(QtGui.QTableView.SingleSelection)
        self._form.dbTable.setSortingEnabled(True)
        self._form.dbTable.doubleClicked.connect(self.onTableDoubleClick)

        self._form.buttonBox.accepted.connect(self.onOk)
        self._form.buttonBox.rejected.connect(self.onCancel)

        self._form.matchSpinbox.setValue(param.GetInt("Tolerance", 5))

        if not self._component or self._lookup == COMPONENT_TYPE_RAILBUTTON:
            self._form.matchCheckbox.setVisible(False)
            self._form.matchSpinbox.setVisible(False)
            self._form.toleranceLabel.setVisible(False)
            self._form.matchDiameterCheckbox.setVisible(False)
            self._form.matchAftDiameterCheckbox.setVisible(False)
            self._form.matchLengthCheckbox.setVisible(False)
        else:
            self._form.matchCheckbox.setChecked(True)
            self._setMatchState()

        # now make the window visible
        self._form.show()

    def initDB(self):
        self._connection = sqlite3.connect("file:" + FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/parts/Parts.db?mode=ro", uri=True)
        self._connection.row_factory = sqlite3.Row
        self._updateModel()

    def _setMatchState(self):
        if self._component:
            query = self._getQueryType()
            if query in [COMPONENT_TYPE_BODYTUBE, COMPONENT_TYPE_COUPLER, COMPONENT_TYPE_ENGINEBLOCK,
                    COMPONENT_TYPE_LAUNCHLUG, COMPONENT_TYPE_CENTERINGRING, COMPONENT_TYPE_BULKHEAD]:
                self._form.matchDiameterCheckbox.setText(translate("Rocket", "Diameter"))
                self._form.matchAftDiameterCheckbox.setVisible(False)
                self._form.matchLengthCheckbox.setVisible(False)
            elif query == COMPONENT_TYPE_TRANSITION:
                self._form.matchDiameterCheckbox.setText(translate("Rocket", "Fore Diameter"))
                self._form.matchAftDiameterCheckbox.setVisible(True)
                self._form.matchLengthCheckbox.setVisible(True)
            elif query == COMPONENT_TYPE_RAILBUTTON:
                self._form.matchDiameterCheckbox.setVisible(False)
                self._form.matchAftDiameterCheckbox.setVisible(False)
                self._form.matchLengthCheckbox.setVisible(False)
            else:
                self._form.matchDiameterCheckbox.setText(translate("Rocket", "Diameter"))
                self._form.matchAftDiameterCheckbox.setVisible(False)
                self._form.matchLengthCheckbox.setVisible(True)

    def exec(self):
        self._form.exec()

    def onClose(self):
        saveDialog(self._form, "DialogLookup")
        param = getParams("DialogLookup")
        param.SetInt("Tolerance", self._form.matchSpinbox.value())
        param.SetBool("MatchDiameter", self._form.matchDiameterCheckbox.isChecked())
        param.SetBool("MatchAftDiameter", self._form.matchAftDiameterCheckbox.isChecked())
        param.SetBool("MatchLengthDiameter", self._form.matchLengthCheckbox.isChecked())
        self._form.close()

    def onLookupType(self, value):
        with WaitCursor():
            self._setMatchState()
            self._updateModel()

    def onMatchComponent(self, value):
        with WaitCursor():
            self._updateModel()

    def onMatchTolerance(self, value):
        with WaitCursor():
            self._updateModel()

    def onMatchDiameter(self, value):
        with WaitCursor():
            self._updateModel()

    def onMatchAftDiameter(self, value):
        with WaitCursor():
            self._updateModel()

    def onMatchLength(self, value):
        with WaitCursor():
            self._updateModel()

    def onSearch(self, value):
        with WaitCursor():
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
                        self._form.dbTable.showRow(row)
                    else:
                        self._form.dbTable.hideRow(row)
            else:
                for row in range(self._model.rowCount()):
                    self._form.dbTable.showRow(row)

    def onTableDoubleClick(self, selected):
        self.result = self._getSelected(selected.row())
        self.onClose()

    def onCancel(self):
        self.result = {}
        self.onClose()

    def onOk(self):
        selected = self._form.dbTable.selectedIndexes()
        if len(selected) > 0:
            row = selected[0].row()
            self.result = self._getSelected(row)
        else:
            self.result = {}
        self.onClose()

    def _getItemFromRow(self, row):
        item = self._model.item(row, 0)
        return item

    def _getSelectedBodyTube(self, row):
        try:
            index = int(self._getItemFromRow(row).text())
            tube = getBodyTube(self._connection, index)
            return tube
        except NotFoundError:
            _err(translate('Rocket', "Body tube not found"))
        except MultipleEntryError:
            _err(translate('Rocket', "Multiple identical entries found"))
        return {}

    def _getSelectedNose(self, row):
        try:
            index = int(self._getItemFromRow(row).text())
            cone = getNoseCone(self._connection, index)
            return cone
        except NotFoundError:
            _err(translate('Rocket', "Nose cone not found"))
        except MultipleEntryError:
            _err(translate('Rocket', "Multiple identical entries found"))
        return {}

    def _getSelectedTransition(self, row):
        try:
            index = int(self._getItemFromRow(row).text())
            tran = getTransition(self._connection, index)
            return tran
        except NotFoundError:
            _err(translate('Rocket', "Transition not found"))
        except MultipleEntryError:
            _err(translate('Rocket', "Multiple identical entries found"))
        return {}

    def _getSelectedRailButton(self, row):
        try:
            index = int(self._getItemFromRow(row).text())
            button = getRailButton(self._connection, index)
            return button
        except NotFoundError:
            _err(translate('Rocket', "Rail button not found"))
        except MultipleEntryError:
            _err(translate('Rocket', "Multiple identical entries found"))
        return {}
    
    def _getQueryType(self):
        queryType = str(self._form.lookupTypeCombo.currentData())
        if queryType == COMPONENT_TYPE_ANY:
            return self._lookup
        return queryType

    def _getSelected(self, row):
        query = self._getQueryType()

        if query in [COMPONENT_TYPE_BODYTUBE, COMPONENT_TYPE_COUPLER, COMPONENT_TYPE_ENGINEBLOCK,
                COMPONENT_TYPE_LAUNCHLUG, COMPONENT_TYPE_CENTERINGRING, COMPONENT_TYPE_BULKHEAD]:
            return self._getSelectedBodyTube(row)
        elif query == COMPONENT_TYPE_NOSECONE:
            return self._getSelectedNose(row)
        elif query == COMPONENT_TYPE_TRANSITION:
            return self._getSelectedTransition(row)
        elif query == COMPONENT_TYPE_RAILBUTTON:
            return self._getSelectedRailButton(row)
        # elif query == COMPONENT_TYPE_PARACHUTE:
        #     pass
        # elif query == COMPONENT_TYPE_STREAMER:
        #     pass
        return {}

    def _itemWithDimension(self, value, dim):
        return self._newItem(_valueWithUnits(value, dim))

    def _newItem(self, text):
        item = QStandardItem(text)
        item.setEditable(False)
        return item

    def _queryBodyTube(self, queryType):
        if self._component and self._form.matchCheckbox.isChecked():
            if self._form.matchDiameterCheckbox.isChecked():
                tolerance = self._form.matchSpinbox.value()
                minimum = self._component.Proxy.getOuterDiameter(0)
                maximum = minimum
                minimum -= minimum * (tolerance / 100.0)
                maximum += maximum * (tolerance / 100.0)
            else:
                minimum = None
                maximum = None
            rows = listBodyTubesBySize(self._connection, minimum, maximum, queryType)
            self.match = True
        else:
            rows = listBodyTubes(self._connection, queryType)
            self.match = False

        self._model.setRowCount(len(rows))
        if queryType == COMPONENT_TYPE_BULKHEAD:
            self._model.setColumnCount(7)
        else:
            self._model.setColumnCount(8)
        self._form.rowsEdit.setText(f"{len(rows)}")
        self._form.dbTable.hideColumn(0) # This holds index for lookups
        self._form.dbTable.setVerticalHeader(None)

        # Add the column headers
        self._model.setHorizontalHeaderItem(1, self._newItem(translate('Rocket', "Type")))
        self._model.setHorizontalHeaderItem(2, self._newItem(translate('Rocket', "Manufacturer")))
        self._model.setHorizontalHeaderItem(3, self._newItem(translate('Rocket', "Part Number")))
        self._model.setHorizontalHeaderItem(4, self._newItem(translate('Rocket', "Description")))
        self._model.setHorizontalHeaderItem(5, self._newItem(translate('Rocket', "Outer Diameter")))
        if queryType == COMPONENT_TYPE_BULKHEAD:
            self._model.setHorizontalHeaderItem(6, self._newItem(translate('Rocket', "Length")))
        else:
            self._model.setHorizontalHeaderItem(6, self._newItem(translate('Rocket', "Inner Diameter")))
            self._model.setHorizontalHeaderItem(7, self._newItem(translate('Rocket', "Length")))

        rowCount = 0
        for row in rows:
            self._model.setItem(rowCount, 0, self._newItem(str(row["body_tube_index"])))
            self._model.setItem(rowCount, 1, self._newItem(str(row["type"])))
            self._model.setItem(rowCount, 2, self._newItem(str(row["manufacturer"])))
            self._model.setItem(rowCount, 3, self._newItem(str(row["part_number"])))
            self._model.setItem(rowCount, 4, self._newItem(str(row["description"])))
            self._model.setItem(rowCount, 5, self._newItem(self._itemWithDimension(row["outer_diameter"], row["outer_diameter_units"])))
            if queryType == COMPONENT_TYPE_BULKHEAD:
                self._model.setItem(rowCount, 6, self._newItem(self._itemWithDimension(row["length"], row["length_units"])))
            else:
                self._model.setItem(rowCount, 6, self._newItem(self._itemWithDimension(row["inner_diameter"], row["inner_diameter_units"])))
                self._model.setItem(rowCount, 7, self._newItem(self._itemWithDimension(row["length"], row["length_units"])))

            rowCount += 1

    def _queryNoseCone(self):
        if self._component and self._form.matchCheckbox.isChecked():
            tolerance = self._form.matchSpinbox.value()
            if self._form.matchDiameterCheckbox.isChecked():
                minDiameter = self._component.Proxy.getAftDiameter()
                maxDiameter = minDiameter
                minDiameter -= minDiameter * (tolerance / 100.0)
                maxDiameter += maxDiameter * (tolerance / 100.0)
            else:
                minDiameter = None
                maxDiameter = None
            if self._form.matchLengthCheckbox.isChecked():
                minLength = self._component.Proxy.getLength()
                maxLength = minLength
                minLength -= minLength * (tolerance / 100.0)
                maxLength += maxLength * (tolerance / 100.0)
            else:
                minLength = None
                maxLength = None
            rows = listNoseConesBySize(self._connection, minDiameter, maxDiameter, minLength, maxLength)
            self.match = True
        else:
            rows = listNoseCones(self._connection)
            self.match = False

        self._model.setRowCount(len(rows))
        self._model.setColumnCount(9)
        self._form.rowsEdit.setText(f"{len(rows)}")
        self._form.dbTable.hideColumn(0) # This holds index for lookups
        self._form.dbTable.setVerticalHeader(None)

        # Add the column headers
        self._model.setHorizontalHeaderItem(1, self._newItem(translate('Rocket', "Manufacturer")))
        self._model.setHorizontalHeaderItem(2, self._newItem(translate('Rocket', "Part Number")))
        self._model.setHorizontalHeaderItem(3, self._newItem(translate('Rocket', "Description")))
        self._model.setHorizontalHeaderItem(4, self._newItem(translate('Rocket', "Shape")))
        self._model.setHorizontalHeaderItem(5, self._newItem(translate('Rocket', "Diameter")))
        self._model.setHorizontalHeaderItem(6, self._newItem(translate('Rocket', "Length")))
        self._model.setHorizontalHeaderItem(7, self._newItem(translate('Rocket', "Shoulder Diameter")))
        self._model.setHorizontalHeaderItem(8, self._newItem(translate('Rocket', "Shoulder Length")))

        rowCount = 0
        for row in rows:
            self._model.setItem(rowCount, 0, self._newItem(str(row["nose_index"])))
            self._model.setItem(rowCount, 1, self._newItem(str(row["manufacturer"])))
            self._model.setItem(rowCount, 2, self._newItem(str(row["part_number"])))
            self._model.setItem(rowCount, 3, self._newItem(str(row["description"])))
            self._model.setItem(rowCount, 4, self._newItem(str(row["shape"])))
            self._model.setItem(rowCount, 5, self._newItem(self._itemWithDimension(row["diameter"], row["diameter_units"])))
            self._model.setItem(rowCount, 6, self._newItem(self._itemWithDimension(row["length"], row["length_units"])))
            self._model.setItem(rowCount, 7, self._newItem(self._itemWithDimension(row["shoulder_diameter"], row["shoulder_diameter_units"])))
            self._model.setItem(rowCount, 8, self._newItem(self._itemWithDimension(row["shoulder_length"], row["shoulder_length_units"])))

            rowCount += 1

    def _queryTransition(self):
        if self._component and self._form.matchCheckbox.isChecked():
            tolerance = self._form.matchSpinbox.value()
            if self._form.matchDiameterCheckbox.isChecked():
                minForeDiameter = self._component.Proxy.getForeDiameter()
                maxForeDiameter = minForeDiameter
                minForeDiameter -= minForeDiameter * (tolerance / 100.0)
                maxForeDiameter += maxForeDiameter * (tolerance / 100.0)
            else:
                minForeDiameter = None
                maxForeDiameter = None
            if self._form.matchAftDiameterCheckbox.isChecked():
                minAftDiameter = self._component.Proxy.getAftDiameter()
                maxAftDiameter = minAftDiameter
                minAftDiameter -= minAftDiameter * (tolerance / 100.0)
                maxAftDiameter += maxAftDiameter * (tolerance / 100.0)
            else:
                minAftDiameter = None
                maxAftDiameter = None
            if self._form.matchLengthCheckbox.isChecked():
                minLength = self._component.Proxy.getLength()
                maxLength = minLength
                minLength -= minLength * (tolerance / 100.0)
                maxLength += maxLength * (tolerance / 100.0)
            else:
                minLength = None
                maxLength = None
            rows = listTransitionsBySize(self._connection, minForeDiameter, maxForeDiameter, minAftDiameter, maxAftDiameter, minLength, maxLength)
            self.match = True
        else:
            rows = listTransitions(self._connection)
            self.match = False

        self._model.setRowCount(len(rows))
        self._model.setColumnCount(12)
        self._form.rowsEdit.setText(f"{len(rows)}")
        self._form.dbTable.hideColumn(0) # This holds index for lookups
        self._form.dbTable.setVerticalHeader(None)

        # Add the column headers
        self._model.setHorizontalHeaderItem(1, self._newItem(translate('Rocket', "Manufacturer")))
        self._model.setHorizontalHeaderItem(2, self._newItem(translate('Rocket', "Part Number")))
        self._model.setHorizontalHeaderItem(3, self._newItem(translate('Rocket', "Description")))
        self._model.setHorizontalHeaderItem(4, self._newItem(translate('Rocket', "Shape")))
        self._model.setHorizontalHeaderItem(5, self._newItem(translate('Rocket', "Fore Diameter")))
        self._model.setHorizontalHeaderItem(6, self._newItem(translate('Rocket', "Aft Diameter")))
        self._model.setHorizontalHeaderItem(7, self._newItem(translate('Rocket', "Length")))
        self._model.setHorizontalHeaderItem(8, self._newItem(translate('Rocket', "Fore Shoulder Diameter")))
        self._model.setHorizontalHeaderItem(9, self._newItem(translate('Rocket', "Fore Shoulder Length")))
        self._model.setHorizontalHeaderItem(10, self._newItem(translate('Rocket', "Aft Shoulder Diameter")))
        self._model.setHorizontalHeaderItem(11, self._newItem(translate('Rocket', "Aft Shoulder Length")))

        rowCount = 0
        for row in rows:
            self._model.setItem(rowCount, 0, self._newItem(str(row["transition_index"])))
            self._model.setItem(rowCount, 1, self._newItem(str(row["manufacturer"])))
            self._model.setItem(rowCount, 2, self._newItem(str(row["part_number"])))
            self._model.setItem(rowCount, 3, self._newItem(str(row["description"])))
            self._model.setItem(rowCount, 4, self._newItem(str(row["shape"])))
            self._model.setItem(rowCount, 5, self._newItem(self._itemWithDimension(row["fore_outside_diameter"], row["fore_outside_diameter_units"])))
            self._model.setItem(rowCount, 6, self._newItem(self._itemWithDimension(row["aft_outside_diameter"], row["aft_outside_diameter_units"])))
            self._model.setItem(rowCount, 7, self._newItem(self._itemWithDimension(row["length"], row["length_units"])))
            self._model.setItem(rowCount, 8, self._newItem(self._itemWithDimension(row["fore_shoulder_diameter"], row["fore_shoulder_diameter_units"])))
            self._model.setItem(rowCount, 9, self._newItem(self._itemWithDimension(row["fore_shoulder_length"], row["fore_shoulder_length_units"])))
            self._model.setItem(rowCount, 10, self._newItem(self._itemWithDimension(row["aft_shoulder_diameter"], row["aft_shoulder_diameter_units"])))
            self._model.setItem(rowCount, 11, self._newItem(self._itemWithDimension(row["aft_shoulder_length"], row["aft_shoulder_length_units"])))

            rowCount += 1

    def _queryRailButton(self):
        rows = listRailButton(self._connection)

        self._model.setRowCount(len(rows))
        self._model.setColumnCount(11)
        self._form.rowsEdit.setText(f"{len(rows)}")
        self._form.dbTable.hideColumn(0) # This holds index for lookups
        self._form.dbTable.setVerticalHeader(None)

        # Add the column headers
        self._model.setHorizontalHeaderItem(1, self._newItem(translate('Rocket', "Manufacturer")))
        self._model.setHorizontalHeaderItem(2, self._newItem(translate('Rocket', "Part Number")))
        self._model.setHorizontalHeaderItem(3, self._newItem(translate('Rocket', "Description")))
        self._model.setHorizontalHeaderItem(4, self._newItem(translate('Rocket', "Finish")))
        self._model.setHorizontalHeaderItem(5, self._newItem(translate('Rocket', "Outer Diameter")))
        self._model.setHorizontalHeaderItem(6, self._newItem(translate('Rocket', "Inner Diameter")))
        self._model.setHorizontalHeaderItem(7, self._newItem(translate('Rocket', "Height")))
        self._model.setHorizontalHeaderItem(8, self._newItem(translate('Rocket', "Base Height")))
        self._model.setHorizontalHeaderItem(9, self._newItem(translate('Rocket', "Flange Height")))
        self._model.setHorizontalHeaderItem(10, self._newItem(translate('Rocket', "Screw Height")))
        # self._model.setHorizontalHeaderItem(11, self._newItem(translate('Rocket', "Drag Coeeficient")))
        # self._model.setHorizontalHeaderItem(12, self._newItem(translate('Rocket', "Screw Mass")))
        # self._model.setHorizontalHeaderItem(13, self._newItem(translate('Rocket', "Nut Mass")))

        rowCount = 0
        for row in rows:
            self._model.setItem(rowCount, 0, self._newItem(str(row["rail_button_index"])))
            self._model.setItem(rowCount, 1, self._newItem(str(row["manufacturer"])))
            self._model.setItem(rowCount, 2, self._newItem(str(row["part_number"])))
            self._model.setItem(rowCount, 3, self._newItem(str(row["description"])))
            self._model.setItem(rowCount, 4, self._newItem(str(row["finish"])))
            self._model.setItem(rowCount, 5, self._newItem(self._itemWithDimension(row["outer_diameter"], row["outer_diameter_units"])))
            self._model.setItem(rowCount, 6, self._newItem(self._itemWithDimension(row["inner_diameter"], row["inner_diameter_units"])))
            self._model.setItem(rowCount, 7, self._newItem(self._itemWithDimension(row["height"], row["height_units"])))
            self._model.setItem(rowCount, 8, self._newItem(self._itemWithDimension(row["base_height"], row["base_height_units"])))
            self._model.setItem(rowCount, 9, self._newItem(self._itemWithDimension(row["flange_height"], row["flange_height_units"])))
            self._model.setItem(rowCount, 10, self._newItem(self._itemWithDimension(row["screw_height"], row["screw_height_units"])))

            rowCount += 1

    def _updateModel(self):
        queryType = str(self._form.lookupTypeCombo.currentData())
        if queryType == COMPONENT_TYPE_ANY:
            query = self._lookup
        else:
            query = queryType

        if query in [COMPONENT_TYPE_BODYTUBE, COMPONENT_TYPE_COUPLER, COMPONENT_TYPE_ENGINEBLOCK,
                COMPONENT_TYPE_LAUNCHLUG, COMPONENT_TYPE_CENTERINGRING, COMPONENT_TYPE_BULKHEAD]:
            self._queryBodyTube(queryType)
        elif query == COMPONENT_TYPE_NOSECONE:
            self._queryNoseCone()
        elif query == COMPONENT_TYPE_TRANSITION:
            self._queryTransition()
        elif query == COMPONENT_TYPE_RAILBUTTON:
            self._queryRailButton()
        # elif query == COMPONENT_TYPE_PARACHUTE:
        #     pass
        # elif query == COMPONENT_TYPE_STREAMER:
        #     pass

    def update(self):
        # Update the SQL query
        pass
