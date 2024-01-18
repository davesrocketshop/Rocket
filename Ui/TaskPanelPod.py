# ***************************************************************************
# *   Copyright (c) 2021-2024 David Carter <dcarter@davidcarter.ca>         *
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
"""Class for drawing pods"""

__title__ = "FreeCAD Pods"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    

import FreeCAD
import FreeCADGui

from DraftTools import translate

from PySide import QtGui, QtCore
from PySide2.QtWidgets import QDialog, QGridLayout, QVBoxLayout, QSizePolicy

from Ui.TaskPanelLocation import TaskPanelLocation
from Ui.Widgets.CommentTab import CommentTab

class _PodDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.tabWidget = QtGui.QTabWidget()
        self.tabGeneral = QtGui.QWidget()
        self.tabComment = CommentTab()
        self.tabWidget.addTab(self.tabGeneral, translate('Rocket', "General"))
        self.tabWidget.addTab(self.tabComment, translate('Rocket', "Comment"))

        layout = QVBoxLayout()
        layout.addWidget(self.tabWidget)
        self.setLayout(layout)

        self.setTabGeneral()

    def setTabGeneral(self):

        ui = FreeCADGui.UiLoader()

        # define our window
        self.setGeometry(250, 250, 400, 350)
        self.setWindowTitle(translate('Rocket', "Pod Parameter"))

        # Get the body tube parameters: length, ID, etc...
        
        self.podCountLabel = QtGui.QLabel(translate('Rocket', "Pod Count"), self)

        self.podCountSpinBox = QtGui.QSpinBox(self)
        self.podCountSpinBox.setMinimumWidth(80)
        self.podCountSpinBox.setMinimum(1)
        self.podCountSpinBox.setMaximum(10000)

        self.podSpacingLabel = QtGui.QLabel(translate('Rocket', "Pod Spacing"), self)

        self.podSpacingInput = ui.createWidget("Gui::InputField")
        self.podSpacingInput.unit = 'deg'
        self.podSpacingInput.setMinimumWidth(80)

        # General parameters
        row = 0
        grid = QGridLayout()

        grid.addWidget(self.podCountLabel, row, 0)
        grid.addWidget(self.podCountSpinBox, row, 1)
        row += 1

        grid.addWidget(self.podSpacingLabel, row, 0)
        grid.addWidget(self.podSpacingInput, row, 1)
        row += 1

        layout = QVBoxLayout()
        layout.addItem(grid)
        layout.addItem(QtGui.QSpacerItem(0,0, QSizePolicy.Expanding, QSizePolicy.Expanding))

        self.tabGeneral.setLayout(layout)

class TaskPanelPod:

    def __init__(self,obj,mode):
        self._obj = obj
        
        self._btForm = _PodDialog()

        self._location = TaskPanelLocation(obj, radial=True)
        self._locationForm = self._location.getForm()

        self.form = [self._btForm, self._locationForm]
        self._btForm.setWindowIcon(QtGui.QIcon(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Pod.svg"))
        
        self._btForm.podCountSpinBox.valueChanged.connect(self.onCount)
        self._btForm.podSpacingInput.textEdited.connect(self.onSpacing)

        self._location.locationChange.connect(self.onLocation)
        
        self.update()
        
        if mode == 0: # fresh created
            self._obj.Proxy.execute(self._obj)  # calculate once 
            FreeCAD.Gui.SendMsgToActiveView("ViewFit")
        
    def transferTo(self):
        "Transfer from the dialog to the object" 
        self._obj.PodCount = self._btForm.podCountSpinBox.value()
        self._obj.PodSpacing = self._btForm.podSpacingInput.text()

        self._btForm.tabComment.transferTo(self._obj)

    def transferFrom(self):
        "Transfer from the object to the dialog"
        self._btForm.podCountSpinBox.setValue(self._obj.PodCount)
        self._btForm.podSpacingInput.setText(self._obj.PodSpacing.UserString)

        self._btForm.tabComment.transferFrom(self._obj)

    def setEdited(self):
        try:
            self._obj.Proxy.setEdited()
        except ReferenceError:
            # Object may be deleted
            pass

    def redraw(self):
        self._obj.Proxy.execute(self._obj)
        
    def onCount(self, value):
        self._obj.PodCount = value
        self._obj.PodSpacing = 360.0 / float(value)
        self._btForm.podSpacingInput.setText(self._obj.PodSpacing.UserString)
        self.redraw()
        self.setEdited()
        
    def onSpacing(self, value):
        self._obj.PodSpacing = value
        self.redraw()
        self.setEdited()

    def onLocation(self):
        self._obj.Proxy.updateChildren()
        self._obj.Proxy.execute(self._obj) 
        self.setEdited()
        
    def getStandardButtons(self):
        return int(QtGui.QDialogButtonBox.Ok) | int(QtGui.QDialogButtonBox.Cancel)| int(QtGui.QDialogButtonBox.Apply)

    def clicked(self,button):
        if button == QtGui.QDialogButtonBox.Apply:
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
