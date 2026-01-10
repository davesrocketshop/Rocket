# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for part import exceptions"""

__title__ = "FreeCAD Rocket Import Exceptions"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

class UnsupportedVersion(Exception):

    def __init__(self, message="Unknown manufacturer"):
        self._message = message


class UnsupportedConfiguration(Exception):

    def __init__(self, message="Unsupported configuration"):
        self._message = message

class UnsupportedFeature(Exception):

    def __init__(self, message="Unsupported feature"):
        self._message = message

class ObjectNotFound(Exception):

    def __init__(self, message="Object not found"):
        self._message = message

