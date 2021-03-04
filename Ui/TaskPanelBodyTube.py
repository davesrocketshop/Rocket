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
"""Class for drawing nose cones"""

__title__ = "FreeCAD Nose Cones"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    

import FreeCAD
import FreeCADGui

from DraftTools import translate

from PySide import QtGui
from PySide2.QtWidgets import QDialog, QGridLayout

from Ui.TaskPanelDatabase import TaskPanelDatabase
from App.Constants import COMPONENT_TYPE_BODYTUBE

from App.Utilities import _valueWithUnits

class _BodyTubeDialog(QDialog):

    def __init__(self, parent=None):
        super(_BodyTubeDialog, self).__init__(parent)

        ui = FreeCADGui.UiLoader()

        # define our window
        self.setGeometry(250, 250, 400, 350)
        self.setWindowTitle(translate('Rocket', "Body Tube Parameter"))

        # Get the body tube parameters: length, ID, etc...
        self.idLabel = QtGui.QLabel(translate('Rocket', "Inner Diameter"), self)

        self.idInput = ui.createWidget("Gui::InputField")
        self.idInput.unit = 'mm'
        self.idInput.setFixedWidth(100)

        self.odLabel = QtGui.QLabel(translate('Rocket', "Outer Diameter"), self)

        self.odInput = ui.createWidget("Gui::InputField")
        self.odInput.unit = 'mm'
        self.odInput.setFixedWidth(100)

        self.lengthLabel = QtGui.QLabel(translate('Rocket', "Length"), self)

        self.lengthInput = ui.createWidget("Gui::InputField")
        self.lengthInput.unit = 'mm'
        self.lengthInput.setFixedWidth(100)

        layout = QGridLayout()

        layout.addWidget(self.idLabel, 0, 0, 1, 2)
        layout.addWidget(self.idInput, 0, 1)

        layout.addWidget(self.odLabel, 1, 0)
        layout.addWidget(self.odInput, 1, 1)

        layout.addWidget(self.lengthLabel, 2, 0)
        layout.addWidget(self.lengthInput, 2, 1)

        self.setLayout(layout)

class TaskPanelBodyTube:

    def __init__(self,obj,mode):
        self._obj = obj
        
        self._btForm = _BodyTubeDialog()
        self._db = TaskPanelDatabase(obj, COMPONENT_TYPE_BODYTUBE)
        self._dbForm = self._db.getForm()

        self.form = [self._btForm, self._dbForm]
        self._btForm.setWindowIcon(QtGui.QIcon(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_BodyTube.svg"))
        
        self._btForm.idInput.textEdited.connect(self.onIdChanged)
        self._btForm.odInput.textEdited.connect(self.onOdChanged)
        self._btForm.lengthInput.textEdited.connect(self.onLengthChanged)

        self._db.dbLoad.connect(self.onLookup)
        
        self.update()
        
        if mode == 0: # fresh created
            self._obj.Proxy.execute(self._obj)  # calculate once 
            FreeCAD.Gui.SendMsgToActiveView("ViewFit")
        
    def transferTo(self):
        "Transfer from the dialog to the object" 
        self._obj.InnerDiameter = self._btForm.idInput.text()
        self._obj.OuterDiameter = self._btForm.odInput.text()
        self._obj.Length = self._btForm.lengthInput.text()

    def transferFrom(self):
        "Transfer from the object to the dialog"
        self._btForm.idInput.setText(self._obj.InnerDiameter.UserString)
        self._btForm.odInput.setText(self._obj.OuterDiameter.UserString)
        self._btForm.lengthInput.setText(self._obj.Length.UserString)
        
    def onIdChanged(self, value):
        try:
            self._obj.InnerDiameter = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        
    def onOdChanged(self, value):
        try:
            self._obj.OuterDiameter = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        
    def onLengthChanged(self, value):
        try:
            self._obj.Length = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        
    def onLookup(self):
        result = self._db.getLookupResult()

        self._obj.InnerDiameter = _valueWithUnits(result["inner_diameter"], result["inner_diameter_units"])
        self._obj.OuterDiameter = _valueWithUnits(result["outer_diameter"], result["outer_diameter_units"])
        self._obj.Length = _valueWithUnits(result["length"], result["length_units"])

        self.update()
        self._obj.Proxy.execute(self._obj) 
        
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
