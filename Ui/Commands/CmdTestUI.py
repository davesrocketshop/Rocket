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
"""Class for calculating fin flutter"""

__title__ = "FreeCAD Fin Flutter Calculator"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

translate = FreeCAD.Qt.translate

from PySide import QtGui

from Ui.Commands.Command import Command
from Ui.DialogFinFlutter import DialogFinFlutter
from Ui.DialogTestUI import DialogTestUI

def testUI():
    try:
        form = DialogTestUI()
        form.exec()
    except TypeError as ex:
        QtGui.QMessageBox.information(None, "", str(ex))

class CmdTestUI(Command):
    def Activated(self):
        FreeCADGui.addModule("Ui.Commands.CmdTestUI")
        FreeCADGui.doCommand("Ui.Commands.CmdTestUI.testUI()")

    def IsActive(self):
        # Available when a part is selected
        return True

    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Test UI'),
                'ToolTip': translate("Rocket", 'Test framework for UI loading'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_TestUI.svg"}
