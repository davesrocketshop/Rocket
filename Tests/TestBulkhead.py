# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

################################################################################
#                                                                              #
#   © 2022 David Carter <dcarter@davidcarter.ca>                               #
#                                                                              #
#   This addon is free software: you can redistribute it and/or modify         #
#   it under the terms of the GNU Lesser General Public License as             #
#   published by the Free Software Foundation, either version 2.1              #
#   of the License, or (at your option) any later version.                     #
#                                                                              #
#   This addon is distributed in the hope that it will be useful,              #
#   but WITHOUT ANY WARRANTY; without even the implied warranty                #
#   of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                    #
#   See the GNU Lesser General Public License for more details.                #
#                                                                              #
#   You should have received a copy of the GNU Lesser General Public           #
#   License along with this addon. If not, see https://www.gnu.org/licenses    #
#                                                                              #
################################################################################


"""Class for testing bulkheads"""

__title__ = "FreeCAD Bulkhead Tests"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import unittest

from Ui.Commands.CmdBulkhead import makeBulkhead

class BulkheadTests(unittest.TestCase):

    def setUp(self):
        self.Doc = FreeCAD.newDocument("BulkheadTest")

    def tearDown(self):
        FreeCAD.closeDocument(self.Doc.Name)

    def _checkShape(self, feature, message):
        self.assertTrue(feature._obj.Shape.isValid(), message)
        self.assertIsNone(feature._obj.Shape.check(True), message)

    def testBasic(self):
        feature = makeBulkhead('Bulkhead')
        self.Doc.recompute()

        self._checkShape(feature, "Basic")

    def testStep(self):
        feature = makeBulkhead('Bulkhead')
        feature._obj.Step = True
        self.Doc.recompute()

        self._checkShape(feature, "Step")

    def testHoles(self):
        feature = makeBulkhead('Bulkhead')
        feature._obj.Holes = True
        feature._obj.HoleCount = 4
        self.Doc.recompute()

        self._checkShape(feature, "Holes")
