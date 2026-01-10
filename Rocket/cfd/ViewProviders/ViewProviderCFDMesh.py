# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2025 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Class for CFD Meshes"""

__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import os

from CfdOF import CfdTools

class ViewProviderCFDMesh:
    """ A View Provider for the CfdMesh object """
    def __init__(self, vobj):
        vobj.Proxy = self
        # self.taskd = None
        # self.num_refinement_objs = 0
        # self.num_dyn_refinement_objs = 0

    def getIcon(self):
        icon_path = os.path.join(CfdTools.getModulePath(), "Gui", "Icons", "mesh.svg")
        return icon_path

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object

    def setEdit(self, vobj, mode):
        # for obj in FreeCAD.ActiveDocument.Objects:
        #     if hasattr(obj, 'Proxy') and isinstance(obj.Proxy, CfdMesh):
        #         obj.ViewObject.show()

        # if self.Object.Part is None:
        #     FreeCAD.Console.PrintError("Meshed part no longer exists")
        #     return False

        # from CfdOF.Mesh import TaskPanelCfdMesh
        # import importlib
        # importlib.reload(TaskPanelCfdMesh)
        # self.taskd = TaskPanelCfdMesh.TaskPanelCfdMesh(self.Object)
        # self.taskd.obj = vobj.Object
        # FreeCADGui.Control.showDialog(self.taskd)
        return True

    def unsetEdit(self, vobj, mode):
        # if self.taskd:
        #     self.taskd.closed()
        #     self.taskd = None
        # FreeCADGui.Control.closeDialog()
        pass

    # def doubleClicked(self, vobj):
    #     if FreeCADGui.activeWorkbench().name() != 'CfdOFWorkbench':
    #         FreeCADGui.activateWorkbench("CfdOFWorkbench")
    #     gui_doc = FreeCADGui.getDocument(vobj.Object.Document)
    #     if not gui_doc.getInEdit():
    #         gui_doc.setEdit(vobj.Object.Name)
    #     else:
    #         FreeCAD.Console.PrintError('Task dialog already open\n')
    #         FreeCADGui.Control.showTaskView()
    #     return True

    # def onDelete(self, feature, subelements):
    #     try:
    #         for obj in self.Object.Group:
    #             obj.ViewObject.show()
    #     except Exception as err:
    #         FreeCAD.Console.PrintError("Error in onDelete: " + str(err))
    #     return True

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None

    # dumps and loads replace __getstate__ and __setstate__ post v. 0.21.2
    def dumps(self):
        return None

    def loads(self, state):
        return None
