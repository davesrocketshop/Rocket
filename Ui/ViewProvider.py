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
"""Superclass for view providers"""

__title__ = "FreeCAD View Provider"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

translate = FreeCAD.Qt.translate

from Ui.Widgets.WaitCursor import WaitCursor

class ViewProvider:

    def __init__(self, vobj):
        vobj.Proxy = self
        self._addExtension(vobj)

    def _addExtension(self, vobj):
        vobj.addExtension("Gui::ViewProviderGroupExtensionPython")

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object

    def canDropObject(self, obj):
        if not self.Object.Proxy.isRocketAssembly():
            return False
        return self.Object.Proxy.eligibleChild(obj.Proxy.Type)

    def setupContextMenu(self, viewObject, menu):
        action = menu.addAction(translate('Rocket', 'Edit %1').replace('%1', viewObject.Object.Label))
        action.triggered.connect(lambda: self.startDefaultEditMode(viewObject))
        return False

    def startDefaultEditMode(self, viewObject):
        self.startTransaction(viewObject)
        viewObject.Document.setEdit(viewObject.Object, 0)

    def claimChildren(self):
        """Define which objects will appear as children in the tree view.

        Returns
        -------
        list of <App::DocumentObject>s:
            The objects claimed as children.
        """
        objs = []
        if hasattr(self,"Object"):
            objs = self.Object.Group
            for obj in objs:
                if hasattr(obj, "Proxy"):
                    obj.Proxy.setParent(self.Object)
            if hasattr(self.Object, "Profile"):
                objs.append(self.Object.Profile)

        return objs

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None

    def setAppearance(self, appearance):
        self.ViewObject.ShapeAppearance = (
            appearance
        )
        self.ViewObject.LineColor = appearance.DiffuseColor

    def startTransaction(self, vobj):
        document = vobj.Document.Document
        if not document.HasPendingTransaction:
            text = translate('Rocket', 'Edit %1').replace('%1', vobj.Object.Label)
            document.openTransaction(text)

    def getDialog(self, obj, mode):
        return None

    def setEdit(self, vobj, mode):
        if mode == 0:
            with WaitCursor():
                self.startTransaction(vobj)
                taskd = self.getDialog(self.Object,mode)
                taskd.obj = vobj.Object
                taskd.update()
                FreeCADGui.Control.showDialog(taskd)
                return True

    def unsetEdit(self, vobj, mode):
        if mode == 0:
            with WaitCursor():
                FreeCADGui.Control.closeDialog()
                return
