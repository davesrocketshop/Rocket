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
"""Class for CFD Analysis"""

__title__ = "FreeCAD CFD Analysis"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import FreeCADGui
import os

from DraftTools import translate

from PySide import QtGui

from CfdOF import CfdTools

from Ui.Commands.Command import Command
from Ui.DialogFinFlutter import DialogFinFlutter

def calcFinFlutter():

    # See if we have a fin selected
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

class CmdCFDAnalysis(Command):
    def Activated(self):
        FreeCADGui.addModule("Ui.Commands.CmdFlutterAnalysis")
        FreeCADGui.doCommand("Ui.Commands.CmdFlutterAnalysis.calcFinFlutter()")

    def IsActive(self):
        # Available when a part is selected
        # return self.partFinSelected()
        return True
        
    def GetResources(self):
        icon_path = os.path.join(CfdTools.getModulePath(), "Gui", "Icons", "cfd.svg")
        return {'MenuText': translate("Rocket", 'CFD Analysis'),
                'ToolTip': translate("Rocket", 'Perform a CFD Analysis'),
                'Pixmap': icon_path}
