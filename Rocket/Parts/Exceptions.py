# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for part import exceptions"""

__title__ = "FreeCAD Rocket Import Exceptions"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

class InvalidError(Exception):

    def __init__(self, manufacturer, partNo, message):
        self._manufacturer = manufacturer
        self._name = partNo
        self._message = message

class MultipleEntryError(Exception):

    def __init__(self, message="Multiple entries found"):
        self._message = message

class UnknownManufacturerError(Exception):

    def __init__(self, message="Unknown manufacturer"):
        self._message = message

class MaterialNotFoundError(Exception):

    def __init__(self, message="Unknown material"):
        self._message = message

class NotFoundError(Exception):

    def __init__(self, message="Unknown material"):
        self._message = message
