# -*- coding: utf-8 -*-
# Rocket gui init module
# (c) 2001 Juergen Riegel
# License LGPL

class RocketWorkbench ( Workbench ):
    "Rocket workbench object"
    Icon = FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/RocketWorkbench.svg"
    MenuText = "Rocket"
    ToolTip = "Rocket workbench"
    
    def Initialize(self):
        # load the module
        import RocketGui
        self.appendToolbar('Rocket',['Rocket_HelloWorld'])
        self.appendMenu('Rocket',['Rocket_HelloWorld'])
    
    def GetClassName(self):
        return "Gui::PythonWorkbench"

Gui.addWorkbench(RocketWorkbench())
