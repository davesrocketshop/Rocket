# ***************************************************************************
# *   Copyright (c) 2022 David Carter <dcarter@davidcarter.ca>              *
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
"""Class for motor view providers"""

__title__ = "FreeCAD View Provider"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

from PySide import QtGui

from Ui.ViewProvider import ViewProvider, ViewProviderGroup
from Ui.MainPanelMotor import MainPanelDialog
from Ui.TaskPanelGrain import TaskPanelGrain
from Ui.TaskPanelNozzle import TaskPanelNozzle

def addMotorView(view):
    "addMotorView(view): adds the given motor view to the FreeCAD MDI area"
    if FreeCAD.GuiUp:
        mw = FreeCADGui.getMainWindow()
        mdi = mw.findChild(QtGui.QMdiArea)
        sw = mdi.addSubWindow(view)
        sw.setWindowIcon(QtGui.QIcon(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_OpenMotor.svg"))
        sw.show()
        mdi.setActiveSubWindow(sw)
        # view.show()

class ViewProviderMotor(ViewProviderGroup):

    def __init__(self, vobj):
        super().__init__(vobj)

    def getIcon(self):
        return FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_OpenMotor.svg"

    def setEdit(self,vobj,mode=0):
        if hasattr(self,"editor"):
            pass
        else:
            self.editor = MainPanelDialog(vobj.Object, mode)
            addMotorView(self.editor)
        return True

    def unsetEdit(self,vobj,mode):
        return False

class ViewProviderMotorConfig(ViewProvider):

    def __init__(self, vobj):
        super().__init__(vobj)

    def getIcon(self):
        return FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_OpenMotor.svg"

    def setEdit(self,vobj,mode):
        # No editor associated with this object
        return False

    def unsetEdit(self,vobj,mode):
        return False

class ViewProviderPropellant(ViewProviderGroup):

    def __init__(self, vobj):
        super().__init__(vobj)

    def getIcon(self):
        return FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_OpenMotor.svg"

    def setEdit(self,vobj,mode):
        # No editor associated with this object
        return False

    def unsetEdit(self,vobj,mode):
        return False

class ViewProviderPropellantTab(ViewProvider):

    def __init__(self, vobj):
        super().__init__(vobj)

    def getIcon(self):
        return FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_OpenMotor.svg"

    def setEdit(self,vobj,mode):
        # No editor associated with this object
        return False

    def unsetEdit(self,vobj,mode):
        return False

class ViewProviderNozzle(ViewProvider):

    def __init__(self, vobj):
        super().__init__(vobj)

    def getIcon(self):
        return FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_OpenMotor.svg"

    def setEdit(self, vobj, mode):
        if mode == 0:
            taskd = TaskPanelNozzle(self.Object, mode)
            taskd.obj = vobj.Object
            taskd.update()
            FreeCADGui.Control.showDialog(taskd)
            return True

    def unsetEdit(self, vobj, mode):
        if mode == 0:
            FreeCADGui.Control.closeDialog()
            return

class ViewProviderGrains(ViewProviderGroup):

    def __init__(self, vobj):
        super().__init__(vobj)

    def getIcon(self):
        return FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_OpenMotor.svg"

    def setEdit(self,vobj,mode):
        # No editor associated with this object
        return False

    def unsetEdit(self,vobj,mode):
        return False

class ViewProviderGrain(ViewProvider):

    def __init__(self, vobj):
        super().__init__(vobj)

    def getIcon(self):
        return FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_OpenMotor.svg"

    def setEdit(self, vobj, mode):
        if mode == 0:
            taskd = TaskPanelGrain(self.Object, mode)
            taskd.obj = vobj.Object
            taskd.update()
            FreeCADGui.Control.showDialog(taskd)
            return True

    def unsetEdit(self, vobj, mode):
        if mode == 0:
            FreeCADGui.Control.closeDialog()
            return
