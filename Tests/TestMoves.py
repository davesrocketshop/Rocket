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


"""Class for testing component moves"""

__title__ = "FreeCAD Move Command Tests"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui
import unittest
import RocketGui

from PySide import QtGui

from Ui.Commands.CmdBodyTube import makeBodyTube
from Ui.Commands.CmdRocket import makeRocket
from Ui.Commands.CmdStage import makeStage, addToStage
from Ui.Commands.CmdNoseCone import makeNoseCone

from Tests.util.TestRockets import TestRockets

class MoveTests(unittest.TestCase):

    def setUp(self):
        self.Doc = FreeCAD.newDocument("BodyTest")

    def tearDown(self):
        FreeCAD.closeDocument(self.Doc.Name)

    def makeAlpha(self):
        rocket = makeRocket("Rocket", False)
        stage1 = makeStage('Stage')
        rocket.addChild(stage1._obj)
        FreeCADGui.Selection.clearSelection()
        FreeCADGui.Selection.addSelection(stage1._obj)

        nose1 = makeNoseCone('NoseCone')
        addToStage(nose1)
        tube1 = makeBodyTube('BodyTube')
        addToStage(tube1)
        self.Doc.recompute()

    def toggleAll(self, tree, item, collapse):
        if collapse == False:
            tree.expandItem(item)
            # print("Expand {0}".format(item))
        elif collapse == True:
            tree.collapseItem(item)

        for i in range(item.childCount()):
            self.toggleAll(tree, item.child(i), collapse)

    def expandTree(self):
        mw = FreeCADGui.getMainWindow()
        trees = mw.findChildren(QtGui.QTreeWidget)

        for tree in trees:
            items = tree.selectedItems()
            for item in items:
                self.toggleAll(tree, item, False)

    def getTree(self):
        mw = FreeCADGui.getMainWindow()
        trees = mw.findChildren(QtGui.QTreeWidget)
        tree = trees[0]
        return tree

    def getCurrentItem(self, tree):
        # item = tree.currentItem()
        items = tree.selectedItems()
        item = items[0]
        return item

    def getItemAbove(self, tree, item):
        itemAbove = tree.itemAbove(item)
        return itemAbove

    def getItemBelow(self, tree, item):
        itemBelow = tree.itemBelow(item)
        return itemBelow

    # def _checkShape(self, feature, message):
    #     self.assertTrue(feature._obj.Shape.isValid(), message)
    #     self.assertIsNone(feature._obj.Shape.check(True), message)
    def showPositions(self):
        objs = FreeCADGui.Selection.getSelection()
        for obj in objs:
            print(obj.Label)
        #     if hasattr(obj, "Proxy"):
        #         if hasattr(obj.Proxy, "getType"):
        #             if obj.Proxy.getType() == FEATURE_ROCKET:
        #                 return obj.Proxy

        # return None

    # def testNoTree(self):
    #     tube1 = makeBodyTube('BodyTube')
    #     tube2 = makeBodyTube('BodyTube')
    #     self.Doc.recompute()

    #     FreeCADGui.Selection.clearSelection()
    #     FreeCADGui.Selection.addSelection(tube1._obj)

    #     tree = self.getTree()
    #     tree.selectAll()
    #     item = self.getCurrentItem(tree)
    #     self.assertIsNone(self.getItemAbove(tree, item))
    #     self.assertIsNotNone(self.getItemBelow(tree, item))

    #     FreeCADGui.runCommand('Rocket_MoveDown')

    #     self.assertIsNotNone(self.getItemAbove(tree, item))
    #     self.assertIsNone(self.getItemBelow(tree, item))

    # def testOutsideTree(self):
    #     tube1 = makeBodyTube('BodyTube')
    #     rocket = makeRocket("Rocket", True)
    #     tube2 = makeBodyTube('BodyTube')
    #     self.Doc.recompute()

    #     self.assertIsNone(tube1.getParent())

    #     FreeCADGui.Selection.clearSelection()
    #     FreeCADGui.Selection.addSelection(tube1._obj)
    #     FreeCADGui.runCommand('Rocket_MoveDown')
    #     self.assertIsNotNone(tube1.getParent())

    #     FreeCADGui.Selection.clearSelection()
    #     FreeCADGui.Selection.addSelection(tube1._obj)
    #     FreeCADGui.runCommand('Rocket_MoveDown')
    #     self.assertIsNone(tube1.getParent())

    #     FreeCADGui.Selection.clearSelection()
    #     FreeCADGui.Selection.addSelection(tube1._obj)
    #     FreeCADGui.runCommand('Rocket_MoveUp')
    #     self.assertIsNotNone(tube1.getParent())

    #     FreeCADGui.Selection.clearSelection()
    #     FreeCADGui.Selection.addSelection(tube1._obj)
    #     FreeCADGui.runCommand('Rocket_MoveUp')
    #     self.assertIsNone(tube1.getParent())

    # def testMoveIntoTree(self):
    #     tube1 = makeBodyTube('BodyTube')
    #     rocket = makeRocket("Rocket", True)
    #     tube2 = makeBodyTube('BodyTube')
    #     self.Doc.recompute()
    #     self.showPositions()

    # def testMoveOutOfTree(self):
    #     tube1 = makeBodyTube('BodyTube')
    #     rocket = makeRocket("Rocket", True)
    #     tube2 = makeBodyTube('BodyTube')
    #     self.Doc.recompute()
    #     self.showPositions()

    def testCrossStages(self):
        # self.makeAlpha()
        rocket = TestRockets.makeEstesAlphaIII()
        # tube1 = makeBodyTube('BodyTube')
        # rocket = makeRocket("Rocket", True)
        # tube2 = makeBodyTube('BodyTube')
        self.Doc.recompute()
        # self.showPositions()

