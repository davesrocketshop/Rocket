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
"""Class for drawing wind tunnels"""

__title__ = "FreeCAD Wind Tunnels"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"


import FreeCAD
import FreeCADGui
import Materials

from DraftTools import translate

from PySide import QtGui, QtCore
from PySide.QtWidgets import QDialog, QGridLayout, QVBoxLayout, QSizePolicy

from Ui.TaskPanelDatabase import TaskPanelDatabase
from Ui.TaskPanelLocation import TaskPanelLocation
from Rocket.Constants import COMPONENT_TYPE_BODYTUBE, COMPONENT_TYPE_LAUNCHLUG, COMPONENT_TYPE_COUPLER, COMPONENT_TYPE_ENGINEBLOCK

from Rocket.Constants import FEATURE_LAUNCH_LUG, FEATURE_TUBE_COUPLER, FEATURE_ENGINE_BLOCK

from Ui.Widgets.MaterialTab import MaterialTab
from Ui.Widgets.CommentTab import CommentTab

from Rocket.Utilities import _valueOnly

class _WindTunnelDialog(QDialog):

    def __init__(self, parent=None):
        super(_WindTunnelDialog, self).__init__(parent)

        ui = FreeCADGui.UiLoader()

        # define our window
        self.setGeometry(250, 250, 400, 350)
        self.setWindowTitle(translate('Rocket', "Wind Tunnel Parameter"))

        # Get the body tube parameters: length, ID, etc...
        self.diameterLabel = QtGui.QLabel(translate('Rocket', "Diameter"), self)

        self.diameterInput = ui.createWidget("Gui::InputField")
        self.diameterInput.unit = 'mm'
        self.diameterInput.setMinimumWidth(100)

        self.lengthLabel = QtGui.QLabel(translate('Rocket', "Length"), self)

        self.lengthInput = ui.createWidget("Gui::InputField")
        self.lengthInput.unit = 'mm'
        self.lengthInput.setMinimumWidth(100)

        # General parameters
        row = 0
        grid = QGridLayout()

        grid.addWidget(self.diameterLabel, row, 0)
        grid.addWidget(self.diameterInput, row, 1)
        row += 1

        grid.addWidget(self.lengthLabel, row, 0)
        grid.addWidget(self.lengthInput, row, 1)

        layout = QVBoxLayout()
        layout.addItem(grid)
        layout.addItem(QtGui.QSpacerItem(0,0, QSizePolicy.Expanding, QSizePolicy.Expanding))

        self.setLayout(layout)

class TaskPanelWindTunnel:

    def __init__(self,obj,mode):
        self._obj = obj

        self.form = _WindTunnelDialog()
        self.form.setWindowIcon(QtGui.QIcon(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_BodyTube.svg"))

        self.form.diameterInput.textEdited.connect(self.onDiameter)
        self.form.lengthInput.textEdited.connect(self.onLength)

        self.update()

    def transferTo(self):
        "Transfer from the dialog to the object"
        self._obj.Diameter = FreeCAD.Units.Quantity(self.form.diameterInput.text()).Value
        self._obj.Length = FreeCAD.Units.Quantity(self.form.lengthInput.text()).Value

    def transferFrom(self):
        "Transfer from the object to the dialog"
        self.form.diameterInput.setText(self._obj.Diameter.UserString)
        self.form.lengthInput.setText(self._obj.Length.UserString)

    def setEdited(self):
        # try:
        #     self._obj.Proxy.setEdited()
        # except ReferenceError:
        #     # Object may be deleted
        #     pass
        pass

    def onDiameter(self, value):
        try:
            self._obj.Diameter = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def onLength(self, value):
        try:
            self._obj.Length = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        self.setEdited()

    def getStandardButtons(self):
        return QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Apply

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
