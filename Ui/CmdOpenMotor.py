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
"""Class for Motor Analysis"""

__title__ = "FreeCAD Black Powder Calculator"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import FreeCADGui

from DraftTools import translate

from PySide import QtGui

from Ui.DialogFinFlutter import DialogFinFlutter

def calcOpenMotor():

    # See if we have a fin selected. If so, this is a custom fin
    for fin in FreeCADGui.Selection.getSelection():
        if fin.isDerivedFrom('Part::FeaturePython'):
            if hasattr(fin,"FinType"):
                try:
                    form = DialogFinFlutter(fin)
                    form.exec_()
                except TypeError as ex:
                    QtGui.QMessageBox.information(None, "", str(ex))
                return

    QtGui.QMessageBox.information(None, "", translate('Rocket', "Please select a fin first"))

class CmdOpenMotor:
    def Activated(self):
        FreeCADGui.addModule("Ui.CmdOpenMotor")
        FreeCADGui.doCommand("Ui.CmdOpenMotor.calcOpenMotor()")

    def IsActive(self):
        # Always available, even without active document
        return True
        
    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Open Motor Analysis'),
                'ToolTip': translate("Rocket", 'Open Motor Analysis'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_OpenMotor.svg"}
