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
"""Provides support for importing XML files."""

__title__ = "FreeCAD XML SAX Element"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from abc import abstractmethod

from PySide import QtGui

import FreeCAD

translate = FreeCAD.Qt.translate

from Rocket.Utilities import _msg, _err

class Element:

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        self._tag = tag
        self._parent = parent
        self._filename = filename
        self._line = line

        self._validChildren = {}
        self._knownTags = []
        self._componentTags = []

        self._parentObj = parentObj
        self._feature = None

        self.makeObject()

    @abstractmethod
    def makeObject(self):
        pass

    def end(self):
        return self._parent

    def isChildElement(self, tag):
        return str(tag).lower().strip() in self._validChildren

    def testCreateChild(self, tag):
        return True

    def isTag(self, tag):
        return str(tag).lower() == self._tag.lower()

    def handleTag(self, tag, attributes):
        _tag = tag.lower().strip()
        if _tag in self._knownTags:
            return
        elif not _tag in self._componentTags:
            _msg('\tUnknown tag %s in %s' % (tag, self._tag))

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag in self._knownTags:
            return
        elif not _tag in self._componentTags:
            _msg('\tUnknown tag /%s in %s' % (tag, self._tag))

    def createChild(self, tag, attributes, filename, line):
        _tag = tag.lower().strip()
        if not _tag in self._validChildren:
            _err("Invalid element %s" % tag)
            return None
        obj = self._feature
        if obj is None:
            obj = self._parentObj
        # if obj:
        #     if hasattr(obj, '_obj'):
        #         obj = obj._obj
        return self._validChildren[_tag](self, tag, attributes, obj, filename, line)

    def isAuto(self, content):
        return str(content).lower().startswith("auto")

class NullElement(Element):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._validChildren = { tag : NullElement }

    def handleTag(self, tag, attributes):
        # Ignore unknown tags
        return

    def handleEndTag(self, tag, content):
        # Ignore unknown tags
        return

class UnsupportedElement(NullElement):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        # QtGui.QMessageBox.information(None,
        #                               translate("Rocket", "Unsupported Feature"),
        #                               translate("Rocket", "Unsupported feature {}").format(tag))
