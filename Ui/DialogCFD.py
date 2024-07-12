# ***************************************************************************
# *   Copyright (c) 2024 David Carter <dcarter@davidcarter.ca>              *
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
"""Class for CFD Analyzer"""

__title__ = "FreeCAD CFD Analyzer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import FreeCADGui
import os

from DraftTools import translate

from PySide import QtGui, QtCore
from PySide2.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGridLayout

from Ui.UIPaths import getUIPath

class DialogCFD:
    def __init__(self):
        # super().__init__()

        self._form = FreeCADGui.PySideUic.loadUi(os.path.join(getUIPath(), 'Ui', 'Resources', 'ui', "DialogCFD.ui"))
        if self._form is None:
            print("Form is empty")
        self._studies = (translate("Rocket", "Example"),)
        self._form.comboStudy.addItems(self._studies)
        # self._form.show()

    def update(self):
        'fills the widgets'
        # self.transferFrom()
        pass
                
    def accept(self):
        # self.transferTo()
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.resetEdit()
        FreeCADGui.Control.closeDialog()

    # def unsetEdit(self, vobj, mode):
    #     if self.taskd:
    #         self.taskd.closing()
    #         self.taskd = None
    #     FreeCADGui.Control.closeDialog()
  
    def reject(self):
        FreeCAD.ActiveDocument.abortTransaction()
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.resetEdit()
        # self.setEdited()
        FreeCADGui.Control.closeDialog()
