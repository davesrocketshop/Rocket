# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2022 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for testing body tubes"""

__title__ = "FreeCAD Body Tube Tests"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import unittest

from Ui.Commands.CmdBodyTube import makeBodyTube

class BodyTubeTests(unittest.TestCase):

    def setUp(self):
        self.Doc = FreeCAD.newDocument("BodyTest")

    def tearDown(self):
        FreeCAD.closeDocument(self.Doc.Name)

    def _checkShape(self, feature, message):
        self.assertTrue(feature._obj.Shape.isValid(), message)
        self.assertIsNone(feature._obj.Shape.check(True), message)

    def testBasic(self):
        feature = makeBodyTube('BodyTube')
        self.Doc.recompute()

        self._checkShape(feature, "Basic")
