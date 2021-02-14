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

from PySide import QtGui, QtCore
from PySide2.QtWidgets import QDialog, QGridLayout

from App.Utilities import _toFloat
from App.Constants import COMPONENT_TYPE_BODYTUBE, COMPONENT_TYPE_BULKHEAD, COMPONENT_TYPE_CENTERINGRING, COMPONENT_TYPE_COUPLER, \
    COMPONENT_TYPE_ENGINEBLOCK, COMPONENT_TYPE_LAUNCHLUG, COMPONENT_TYPE_NOSECONE, COMPONENT_TYPE_PARACHUTE, COMPONENT_TYPE_STREAMER, COMPONENT_TYPE_TRANSITION

from App.Parts.PartDatabase import PartDatabase

class _databaseLookupDialog(QDialog):

    def __init__(self, lookup, parent=None):
        super().__init__(parent)

        self._database = PartDatabase(FreeCAD.getUserAppDataDir() + "Mod/Rocket/")

        # define our window
        self.setGeometry(250, 250, 400, 350)
        self.setWindowTitle(translate('Rocket', "Component Database"))

        # Select the type of component
        self.componentTypeLabel = QtGui.QLabel(translate('Rocket', "Component type"), self)

        self.componentTypes = (
                                COMPONENT_TYPE_BODYTUBE,
                                COMPONENT_TYPE_BULKHEAD,
                                COMPONENT_TYPE_CENTERINGRING,
                                COMPONENT_TYPE_COUPLER,
                                COMPONENT_TYPE_ENGINEBLOCK,
                                COMPONENT_TYPE_LAUNCHLUG,
                                COMPONENT_TYPE_NOSECONE,
                                COMPONENT_TYPE_PARACHUTE,
                                COMPONENT_TYPE_STREAMER,
                                COMPONENT_TYPE_TRANSITION
                            )
        self.componentTypesCombo = QtGui.QComboBox(self)
        self.componentTypesCombo.addItems(self.componentTypes)
        self.componentTypesCombo.setCurrentText(lookup)

        self.manufacturerTypeLabel = QtGui.QLabel(translate('Rocket', "Manufacturer"), self)

        self.manufacturerTypes = ["All"] + self._database.getManufacturers()
        self.manufacturerTypesCombo = QtGui.QComboBox(self)
        self.manufacturerTypesCombo.addItems(self.manufacturerTypes)

        layout = QGridLayout()

        n = 0
        layout.addWidget(self.componentTypeLabel, n, 0, 1, 2)
        layout.addWidget(self.componentTypesCombo, n, 1)
        n += 1

        layout.addWidget(self.manufacturerTypeLabel, n, 0)
        layout.addWidget(self.manufacturerTypesCombo, n, 1)
        n += 1

        self.setLayout(layout)

class TaskPanelDatabase:

    def __init__(self, form):
        self._form = form
        # self._form.setWindowIcon(QtGui.QIcon(":/icons/Rocket_BodyTube.svg"))
        
        # self._form.idInput.textEdited.connect(self.onIdChanged)
        # self._form.odInput.textEdited.connect(self.onOdChanged)
        # self._form.lengthInput.textEdited.connect(self.onLengthChanged)
        
        self.update()

    def getForm(lookup, parent=None):
        return _databaseLookupDialog(lookup, parent)
        
    def transferTo(self):
        "Transfer from the dialog to the object" 
        # self.obj.InnerDiameter = _toFloat(self._form.idInput.text())
        # self.obj.OuterDiameter = _toFloat(self._form.odInput.text())
        # self.obj.Length = _toFloat(self._form.lengthInput.text())
        pass

    def transferFrom(self):
        "Transfer from the object to the dialog"
        # self._form.idInput.setText("%f" % self.obj.InnerDiameter)
        # self._form.odInput.setText("%f" % self.obj.OuterDiameter)
        # self._form.lengthInput.setText("%f" % self.obj.Length)
        pass
        
    def onIdChanged(self, value):
        # self.obj.InnerDiameter = _toFloat(value)
        # self.obj.Proxy.execute(self.obj)
        pass
        
    def onOdChanged(self, value):
        # self.obj.OuterDiameter = _toFloat(value)
        # self.obj.Proxy.execute(self.obj)
        pass
        
    def onLengthChanged(self, value):
        # self.obj.Length = _toFloat(value)
        # self.obj.Proxy.execute(self.obj)
        pass

        
    # def getStandardButtons(self):
    #     return int(QtGui.QDialogButtonBox.Ok) | int(QtGui.QDialogButtonBox.Cancel)| int(QtGui.QDialogButtonBox.Apply)

    # def clicked(self,button):
    #     if button == QtGui.QDialogButtonBox.Apply:
    #         #print "Apply"
    #         self.transferTo()
    #         self.obj.Proxy.execute(self.obj) 
        
    def update(self):
        'fills the widgets'
        self.transferFrom()
                
    # def accept(self):
    #     self.transferTo()
    #     FreeCAD.ActiveDocument.recompute()
    #     FreeCADGui.ActiveDocument.resetEdit()
        
                    
    # def reject(self):
    #     FreeCAD.ActiveDocument.abortTransaction()
    #     FreeCAD.ActiveDocument.recompute()
    #     FreeCADGui.ActiveDocument.resetEdit()
