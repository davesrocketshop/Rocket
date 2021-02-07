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

from PySide import QtGui, QtCore
from PySide2.QtWidgets import QDialog, QGridLayout

from App.Utilities import _toFloat

class _BodyTubeDialog(QDialog):

    def __init__(self, parent=None):
        super(_BodyTubeDialog, self).__init__(parent)


        # define our window
        self.setGeometry(250, 250, 400, 350)
        self.setWindowTitle("Body Tube Parameter")

        # Get the body tube parameters: length, ID, etc...
        self.idLabel = QtGui.QLabel("Inner Diameter", self)

        self.idValidator = QtGui.QDoubleValidator(self)
        self.idValidator.setBottom(0.0)

        self.idInput = QtGui.QLineEdit(self)
        self.idInput.setFixedWidth(100)
        self.idInput.setValidator(self.idValidator)

        self.odLabel = QtGui.QLabel("Outer Diameter", self)

        self.odValidator = QtGui.QDoubleValidator(self)
        self.odValidator.setBottom(0.0)

        self.odInput = QtGui.QLineEdit(self)
        self.odInput.setFixedWidth(100)
        self.odInput.setValidator(self.odValidator)

        self.lengthLabel = QtGui.QLabel("Length", self)

        self.lengthValidator = QtGui.QDoubleValidator(self)
        self.lengthValidator.setBottom(0.0)

        self.lengthInput = QtGui.QLineEdit(self)
        self.lengthInput.setFixedWidth(100)
        self.lengthInput.setValidator(self.lengthValidator)

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
        self.obj = obj
        
        self.form = _BodyTubeDialog()
        self.form.setWindowIcon(QtGui.QIcon(":/icons/Rocket_BodyTube.svg"))
        
        self.form.idInput.textEdited.connect(self.onIdChanged)
        self.form.odInput.textEdited.connect(self.onOdChanged)
        self.form.lengthInput.textEdited.connect(self.onLengthChanged)
        
        self.update()
        
        if mode == 0: # fresh created
            self.obj.Proxy.execute(self.obj)  # calculate once 
            FreeCAD.Gui.SendMsgToActiveView("ViewFit")
        
    def transferTo(self):
        "Transfer from the dialog to the object" 
        self.obj.InnerDiameter = _toFloat(self.form.idInput.text())
        self.obj.OuterDiameter = _toFloat(self.form.odInput.text())
        self.obj.Length = _toFloat(self.form.lengthInput.text())
    
    def transferFrom(self):
        "Transfer from the object to the dialog"
        self.form.idInput.setText("%f" % self.obj.InnerDiameter)
        self.form.odInput.setText("%f" % self.obj.OuterDiameter)
        self.form.lengthInput.setText("%f" % self.obj.Length)
        
    def onIdChanged(self, value):
        self.obj.InnerDiameter = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onOdChanged(self, value):
        self.obj.OuterDiameter = _toFloat(value)
        self.obj.Proxy.execute(self.obj)
        
    def onLengthChanged(self, value):
        self.obj.Length = _toFloat(value)
        self.obj.Proxy.execute(self.obj)

        
    def getStandardButtons(self):
        return int(QtGui.QDialogButtonBox.Ok) | int(QtGui.QDialogButtonBox.Cancel)| int(QtGui.QDialogButtonBox.Apply)
    
    def clicked(self,button):
        if button == QtGui.QDialogButtonBox.Apply:
            #print "Apply"
            self.transferTo()
            self.obj.Proxy.execute(self.obj) 
        
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
