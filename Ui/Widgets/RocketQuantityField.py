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
"""Class for a quantity field"""

__title__ = "Rocket Quantity Field"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD

from PySide.QtGui import QFocusEvent
from PySide.QtWidgets import QLineEdit
from PySide.QtCore import Signal, Property

FORMAT_ALTITUDE = "{0:.2f}"
FORMAT_PRESSURE = "{0:.4f}"
FORMAT_VELOCITY = "{0:.2f}"

class RocketQuantityField(QLineEdit):

    # Signals
    unitsChanged = Signal(str)
    formatChanged = Signal(str)
    quantityChanged = Signal(FreeCAD.Units.Quantity)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self._units = "m"
        self._format = "{0:.2f}"
        self._quantity = FreeCAD.Units.Quantity()

    # def focusInEvent(self, event : QFocusEvent) -> None:
    #     print(f"focusInEvent({self.objectName()})")
        
    def focusOutEvent(self, event : QFocusEvent) -> None:
        text = self.text()
        try:
            current = FreeCAD.Units.Quantity(text) #.getValueAs(FreeCAD.Units.Quantity(self._units))
        except ValueError:
            current = FreeCAD.Units.Quantity(text + " " + self._units)
        formatted = self._formatQuantity(current)
        if text != formatted:
            self.setText(formatted)
            self.quantity = current
        # print(f"focusOut text {text} -> {current}")

    #
    # Property : unit
    #
    # @Property(str, notify=unitsChanged, doc="The current value property.")
    @Property(str, notify=unitsChanged)
    def unit(self) -> str:
        return self._units

    @unit.setter
    def unit(self, newUnits: str) -> None:
        if self._units == newUnits:
            return
        
        self._units = newUnits
        self._update()
        self.unitsChanged.emit(self._units)

    #
    # Property : format
    #
    @Property(str, notify=formatChanged)
    def format(self) -> str:
        return self._format

    @format.setter
    def format(self, newFormat: str) -> None:
        if self._format == newFormat:
            return
        
        self._format = newFormat
        self._update()
        self.formatChanged.emit(self._format)

    #
    # Property : quantity
    #
    @Property(FreeCAD.Units.Quantity, notify=quantityChanged)
    def quantity(self) -> FreeCAD.Units.Quantity:
        # print(f"get quantity {type(self._quantity)}")
        return self._quantity

    @quantity.setter
    def quantity(self, value: FreeCAD.Units.Quantity) -> None:
        if self._quantity == value:
            return
        
        # print(f"set quantity {type(self._quantity)}")
        self._quantity = value
        self._update()
        self.quantityChanged.emit(self._quantity)

    def _update(self) -> None:
        text = self.text()
        formatted = self._formatQuantity(self._quantity)
        if text != formatted:
            self.setText(formatted)
        # print(f"_update text {text} -> {formatted}")

    def _formatQuantity(self, quantity : FreeCAD.Units.Quantity) -> str:
        try:
            return self._format.format(float(quantity.getValueAs(FreeCAD.Units.Quantity(self._units)))) + ' ' + self._units
        except ValueError:
            pass
        return self._format.format(quantity.Value)

