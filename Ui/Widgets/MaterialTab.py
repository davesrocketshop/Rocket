# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2023 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for drawing material tab"""

__title__ = "FreeCAD Material Tab"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"


import FreeCAD
import FreeCADGui

translate = FreeCAD.Qt.translate

import Materials
import MatGui

from PySide import QtGui
from PySide.QtWidgets import QGridLayout, QVBoxLayout, QSizePolicy

# from Rocket.Material import Material

class MaterialTab(QtGui.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTabMaterial()

    def setTabMaterial(self):
        self.materialManager = Materials.MaterialManager()

        ui = FreeCADGui.UiLoader()

        self.materialTreeWidget = ui.createWidget("MatGui::MaterialTreeWidget")
        self.materialTreePy = MatGui.MaterialTreeWidget(self.materialTreeWidget)
        self.materialTreeWidget.onMaterial.connect(self.onMaterial)

        row = 0
        grid = QGridLayout()

        grid.addWidget(self.materialTreeWidget, row, 0)
        row += 1

        layout = QVBoxLayout()
        layout.addItem(grid)
        layout.addItem(QtGui.QSpacerItem(0,0, QSizePolicy.Expanding, QSizePolicy.Expanding))

        self.setLayout(layout)

    def transferTo(self, obj):
        "Transfer from the dialog to the object"
        obj.ShapeMaterial = self.materialManager.getMaterial(self.uuid)

    def transferFrom(self, obj):
        "Transfer from the object to the dialog"
        self.uuid = obj.ShapeMaterial.UUID
        self.materialTreePy.UUID = self.uuid

    def onMaterial(self, uuid):
        self.uuid = uuid
