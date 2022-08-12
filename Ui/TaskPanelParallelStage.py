# ***************************************************************************
# *   Copyright (c) 2021 David Carter <dcarter@davidcarter.ca>              *
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
"""Class for drawing parallel stage"""

__title__ = "FreeCAD Nose Cones"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    

import FreeCAD
import FreeCADGui

from DraftTools import translate

from PySide import QtGui, QtCore
from PySide2.QtWidgets import QDialog, QGridLayout, QVBoxLayout

from Ui.TaskPanelLocation import TaskPanelLocation
from App.Constants import COMPONENT_TYPE_BODYTUBE, COMPONENT_TYPE_LAUNCHLUG
from App.Constants import FEATURE_LAUNCH_LUG

from App.Utilities import _valueWithUnits, _valueOnly

class _ParallelStageDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        ui = FreeCADGui.UiLoader()

        # define our window
        self.setGeometry(250, 250, 400, 350)
        self.setWindowTitle(translate('Rocket', "Parallel Stage Parameter"))

        # Get the body tube parameters: length, ID, etc...
        
        self.stageCountLabel = QtGui.QLabel(translate('Rocket', "Stage Count"), self)

        self.stageCountSpinBox = QtGui.QSpinBox(self)
        self.stageCountSpinBox.setMinimumWidth(80)
        self.stageCountSpinBox.setMinimum(1)
        self.stageCountSpinBox.setMaximum(10000)

        self.stageSpacingLabel = QtGui.QLabel(translate('Rocket', "Stage Spacing"), self)

        self.stageSpacingInput = ui.createWidget("Gui::InputField")
        self.stageSpacingInput.unit = 'deg'
        self.stageSpacingInput.setMinimumWidth(80)

        # General parameters
        row = 0
        grid = QGridLayout()

        grid.addWidget(self.stageCountLabel, row, 0)
        grid.addWidget(self.stageCountSpinBox, row, 1)
        row += 1

        grid.addWidget(self.stageSpacingLabel, row, 0)
        grid.addWidget(self.stageSpacingInput, row, 1)
        row += 1

        layout = QVBoxLayout()
        layout.addItem(grid)

        self.setLayout(layout)

class TaskPanelParallelStage:

    def __init__(self,obj,mode):
        self._obj = obj
        
        self._btForm = _ParallelStageDialog()

        self._location = TaskPanelLocation(obj, radial=True)
        self._locationForm = self._location.getForm()

        self.form = [self._btForm, self._locationForm]
        self._btForm.setWindowIcon(QtGui.QIcon(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_ParallelStage.svg"))
        
        self._btForm.stageCountSpinBox.valueChanged.connect(self.onCount)
        self._btForm.stageSpacingInput.textEdited.connect(self.onSpacing)

        self._location.locationChange.connect(self.onLocation)
        
        self.update()
        
        if mode == 0: # fresh created
            self._obj.Proxy.execute(self._obj)  # calculate once 
            FreeCAD.Gui.SendMsgToActiveView("ViewFit")
        
    def transferTo(self):
        "Transfer from the dialog to the object" 
        self._obj.StageCount = self._btForm.stageCountSpinBox.value()
        self._obj.StageSpacing = self._btForm.stageSpacingInput.text()

    def transferFrom(self):
        "Transfer from the object to the dialog"
        self._btForm.stageCountSpinBox.setValue(self._obj.StageCount)
        self._btForm.stageSpacingInput.setText(self._obj.StageSpacing.UserString)

    def setEdited(self):
        try:
            self._obj.Proxy.setEdited()
        except ReferenceError:
            # Object may be deleted
            pass

    def redraw(self):
        self._obj.Proxy.execute(self._obj)
        
    def onCount(self, value):
        self._obj.StageCount = value
        self._obj.StageSpacing = 360.0 / float(value)
        self._btForm.stageSpacingInput.setText(self._obj.StageSpacing.UserString)
        self.redraw()
        self.setEdited()
        
    def onSpacing(self, value):
        self._obj.StageSpacing = value
        self.redraw()
        self.setEdited()

    def onLocation(self):
        self._obj.Proxy.execute(self._obj) 
        self.setEdited()
        
    def getStandardButtons(self):
        return int(QtGui.QDialogButtonBox.Ok) | int(QtGui.QDialogButtonBox.Cancel)| int(QtGui.QDialogButtonBox.Apply)

    def clicked(self,button):
        if button == QtGui.QDialogButtonBox.Apply:
            #print "Apply"
            self.transferTo()
            self._obj.Proxy.execute(self._obj) 
        
    def update(self):
        'fills the widgets'
        self.transferFrom()
                
    def accept(self):
        self.transferTo()
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.resetEdit()
        
                    
    def reject(self):
        FreeCAD.ActiveDocument.abortTransaction()
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.resetEdit()
        self.setEdited()
