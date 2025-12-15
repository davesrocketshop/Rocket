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
        current = self._quantityFromText(text)
        formatted = self._formatQuantity(current)
        if text != formatted:
            self._setText(formatted)
            self.quantity = current

    # Override the base function to ensure the quantity is set
    def setText(self, text : str) -> None:
        self._quantity = self._quantityFromText(text)
        formatted = self._formatQuantity(self._quantity)
        self._setText(formatted)

    def _setText(self, text : str) -> None:
        super().setText(text)

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
        return self._quantity

    @quantity.setter
    def quantity(self, value: FreeCAD.Units.Quantity) -> None:
        value = self._quantityWithUnits(value)
        if self._quantity == value:
            return

        self._quantity = value
        self._update()
        self.quantityChanged.emit(self._quantity)

    def _update(self) -> None:
        text = self.text()
        formatted = self._formatQuantity(self._quantity)
        if text != formatted:
            self._setText(formatted)

    def _formatQuantity(self, quantity : FreeCAD.Units.Quantity) -> str:
        try:
            return self._format.format(float(quantity.getValueAs(FreeCAD.Units.Quantity(self._units)))) + ' ' + self._units
        except ValueError as ex:
            pass
        return self._format.format(quantity.Value)

    def _quantityWithUnits(self, value : FreeCAD.Units.Quantity) -> FreeCAD.Units.Quantity:
        if self._units and not self._hasUnits(value):
            value = FreeCAD.Units.Quantity(f"{value.Value} {self._units}")
        return value

    def _quantityFromText(self, text : str) -> FreeCAD.Units.Quantity:
        quantity = FreeCAD.Units.Quantity(text)
        return self._quantityWithUnits(quantity)

    def _hasUnits(self, quantity : FreeCAD.Units.Quantity) -> bool:
        """
        Checks if a FreeCAD Base.Quantity object has any units specified.
        """
        try:
            if FreeCAD.Units.Unit(quantity) != FreeCAD.Units.Unit(FreeCAD.Units.Quantity()):
                return True

        except ValueError:
            # If the input isn't a valid Quantity object or unit parsing fails
            return False
        except Exception as e:
            # Handle other potential errors
            print(f"An error occurred: {e}")
            return False
        return False


