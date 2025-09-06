# ***************************************************************************
# *   Copyright (c) 2021-2025 David Carter <dcarter@davidcarter.ca>         *
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
"""Class for drawing bulkheads"""

__title__ = "FreeCAD Bulkhead View Provider"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

from Ui.TaskPanelBulkhead import TaskPanelBulkhead
from Ui.ViewProvider import ViewProvider
from Ui.Widgets.WaitCursor import WaitCursor

class ViewProviderBulkhead(ViewProvider):

    def __init__(self, vobj):
        super().__init__(vobj)

    def getIcon(self):
        return FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Bulkhead.svg"

    def setEdit(self, vobj, mode):
        if mode == 0:
            with WaitCursor():
                self.startTransaction(vobj)
                taskd = TaskPanelBulkhead(self.Object, False, mode)
                taskd.obj = vobj.Object
                taskd.update()
                FreeCADGui.Control.showDialog(taskd)
                return True

    def unsetEdit(self, vobj, mode):
        if mode == 0:
            with WaitCursor():
                FreeCADGui.Control.closeDialog()
                return
