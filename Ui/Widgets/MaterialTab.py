# ***************************************************************************
# *   Copyright (c) 2023 David Carter <dcarter@davidcarter.ca>              *
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
    
import FreeCAD

from DraftTools import translate

from PySide import QtGui
from PySide2.QtWidgets import QGridLayout, QVBoxLayout, QSizePolicy

from Rocket.Material import Material

class MaterialTab(QtGui.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTabMaterial()

    def setTabMaterial(self):

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
        
    def transferTo(self, obj):
        "Transfer from the dialog to the object" 
        obj.Material = str(self.materialPresetCombo.currentText())

    def transferFrom(self, obj):
        "Transfer from the object to the dialog"
        self.updateMaterials()
        self.materialPresetCombo.setCurrentText(obj.Material)
    
    def updateMaterials(self):
        "fills the combo with the existing FCMat cards"

        prefs = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Material/Cards")
        sortByResources = prefs.GetBool("SortByResources", False)

        materials, cards, icons = Material.materialDictionary()
        if cards:
            names = []
            if sortByResources:
                for path in sorted(materials.keys()):
                    names.append([icons[path], cards[path]])
            else:
                nameMap = {}
                for path, name in cards.items():
                    nameMap[name] = path
                for name in sorted(nameMap.keys()):
                    path = nameMap[name]
                    names.append([icons[path], name])

        names.insert(0, [None, ""])
        for mat in names:
            self.materialPresetCombo.addItem(QtGui.QIcon(mat[0]), mat[1])
