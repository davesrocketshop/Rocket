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

__title__ = "FreeCAD Motor Analyzer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import FreeCADGui

from DraftTools import translate

from PySide import QtGui

from Ui.DialogFinFlutter import DialogFinFlutter
from Ui.ViewMotor import ViewProviderMotor, ViewProviderMotorConfig, ViewProviderPropellant, ViewProviderPropellantTab, \
    ViewProviderNozzle, ViewProviderGrains, ViewProviderGrain

from App.motor.Motor import Motor
from App.motor.MotorConfig import MotorConfig
from App.motor.Grain import Grains, Grain
from App.motor.Nozzle import Nozzle
from App.motor.Propellant import Propellant, PropellantTab

def makeMotorConfig(name="MotorConfig"):

    config = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    MotorConfig(config)

    if FreeCAD.GuiUp:
        ViewProviderMotorConfig(config.ViewObject)

    return config

def makePropellant(name="Propellant"):

    propellant = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    Propellant(propellant)

    if FreeCAD.GuiUp:
        ViewProviderPropellant(propellant.ViewObject)

    return propellant

def makePropellantTab(name="PropellantTab"):

    tab = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    PropellantTab(tab)

    if FreeCAD.GuiUp:
        ViewProviderPropellantTab(tab.ViewObject)

    return tab

def makeNozzle(name="Nozzle"):

    nozzle = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    Nozzle(nozzle)

    if FreeCAD.GuiUp:
        ViewProviderNozzle(nozzle.ViewObject)

    return nozzle

def makeGrains(name="Grains"):

    grains = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    Grains(grains)

    if FreeCAD.GuiUp:
        ViewProviderGrains(grains.ViewObject)

    return grains

def makeGrain(type, name="Grain"):

    grain = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    Grain(grain)
    grain.GeometryName = type

    if FreeCAD.GuiUp:
        ViewProviderGrain(grain.ViewObject)

    return grain

def makeMotor(name="Motor"):
    motor = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    Motor(motor)

    if FreeCAD.GuiUp:
        ViewProviderMotor(motor.ViewObject)

    config = makeMotorConfig()
    motor.addObject(config)

    propellant = makePropellant()
    motor.addObject(propellant)

    nozzle = makeNozzle()
    motor.addObject(nozzle)

    grains = makeGrains()
    motor.addObject(grains)

    return motor

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
        FreeCADGui.doCommand("Ui.CmdOpenMotor.makeMotor('Motor')")
        FreeCADGui.doCommand("FreeCAD.ActiveDocument.recompute()")
        FreeCADGui.doCommand("FreeCADGui.activeDocument().setEdit(FreeCAD.ActiveDocument.ActiveObject.Name,0)")

    def IsActive(self):
        # Available with active document
        try:
            import skfmm # Not part of the standard FreeCAD install
            if FreeCAD.ActiveDocument:
                return True
        except ModuleNotFoundError:
            pass

        return False
        
    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Open Motor Analysis'),
                'ToolTip': translate("Rocket", 'Open Motor Analysis'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_OpenMotor.svg"}
