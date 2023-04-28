# ***************************************************************************
# *   Copyright (c) 2021-2023 David Carter <dcarter@davidcarter.ca>         *
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
"""Class for drawing stages"""

__title__ = "FreeCAD Parallel Stage View Provider"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import FreeCADGui

from PySide import QtCore,QtGui
from pivy import coin

from DraftTools import translate

from Ui.ViewProvider import ViewProvider

from Ui.TaskPanelParallelStage import TaskPanelParallelStage

class ViewProviderParallelStage(ViewProvider):

    def __init__(self, vobj):
        super().__init__(vobj)
        
    def getIcon(self):
        return FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_ParallelStage.svg"

    def attach(self, vobj):
        super().attach(vobj)

        self.sep = coin.SoSeparator()
        vobj.addDisplayMode(self.sep, "Default")

    def getDisplayModes(self,vobj):
        return ["Default"]

    def getDefaultDisplayMode(self):
        return "Default"

    def setDisplayMode(self,mode):
        return mode

    def setupContextMenu(self, vobj, menu):
        """Add the component specific options to the context menu."""
        action1 = QtGui.QAction(translate("Rocket","Toggle active stage"),menu)
        QtCore.QObject.connect(action1,QtCore.SIGNAL("triggered()"),self.toggleParallelStage)
        menu.addAction(action1)

        action = menu.addAction(translate('Rocket', 'Edit %1').replace('%1', vobj.Object.Label))
        action.triggered.connect(lambda: self.startDefaultEditMode(vobj))
        return False

    def startDefaultEditMode(self, vobj):
        document = vobj.Document.Document
        if not document.HasPendingTransaction:
            text = translate('Rocket', 'Edit %1').replace('%1', vobj.Object.Label)
            document.openTransaction(text)
        vobj.Document.setEdit(vobj.Object, 0)


    def toggleParallelStage(self):
        FreeCADGui.runCommand("Rocket_ToggleParallelStage")

    def setEdit(self, vobj, mode):
        if True: #mode == 0:
            taskd = TaskPanelParallelStage(self.Object, mode)
            taskd.obj = vobj.Object
            taskd.update()
            FreeCADGui.Control.showDialog(taskd)
            return True

    def unsetEdit(self, vobj, mode):
        if mode == 0:
            FreeCADGui.Control.closeDialog()
            return
