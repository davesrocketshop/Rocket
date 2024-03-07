# ***************************************************************************
# *   Copyright (c) 2023-2024 David Carter <dcarter@davidcarter.ca>         *
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
"""Class for drawing material tab"""

__title__ = "FreeCAD Material Tab"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    

from DraftTools import translate

from PySide import QtGui
from PySide2.QtWidgets import QGridLayout, QVBoxLayout, QSizePolicy

from Rocket.Material import Material
from Rocket.Utilities import oldMaterials, newMaterials

if newMaterials():
    import MatGui

class MaterialTab(QtGui.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        if oldMaterials():
            self.setTabMaterialV21()
        else:
            self.setTabMaterialV22()

    def setTabMaterialV21(self):

        self.materialLabel = QtGui.QLabel(translate('Rocket', "Material"), self)

        self.materialPresetCombo = QtGui.QComboBox(self)
        row = 0
        grid = QGridLayout()

        grid.addWidget(self.materialLabel, row, 0)
        grid.addWidget(self.materialPresetCombo, row, 1)
        row += 1

        layout = QVBoxLayout()
        layout.addItem(grid)
        layout.addItem(QtGui.QSpacerItem(0,0, QSizePolicy.Expanding, QSizePolicy.Expanding))

        self.setLayout(layout)

    def setTabMaterialV22(self):

        self.materialTree = MatGui.MaterialTreeWidget(self)
        row = 0
        grid = QGridLayout()

        grid.addWidget(self.materialTree, row, 0)
        row += 1

        layout = QVBoxLayout()
        layout.addItem(grid)
        layout.addItem(QtGui.QSpacerItem(0,0, QSizePolicy.Expanding, QSizePolicy.Expanding))

        self.setLayout(layout)
        
    def transferTo(self, obj):
        "Transfer from the dialog to the object"
        if oldMaterials():
            obj.Material = str(self.materialPresetCombo.currentText())

    def transferFrom(self, obj):
        "Transfer from the object to the dialog"
        if oldMaterials():
            self.updateMaterials()
            self.materialPresetCombo.setCurrentText(obj.Material)
    
    def updateMaterials(self):
        "fills the combo with the existing FCMat cards"
        self.materialPresetCombo.addItem('')
        cards = Material.materialDictionary()
        if cards:
            for k in sorted(cards.keys()):
                self.materialPresetCombo.addItem(k)
