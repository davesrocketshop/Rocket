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
"""Superclass for view providers"""

__title__ = "FreeCAD View Provider"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from pivy import coin
    
from DraftTools import translate

class ViewProvider:

    def __init__(self, vobj):
        vobj.Proxy = self
        vobj.addExtension("Gui::ViewProviderGroupExtensionPython")

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object

    def canDropObject(self, obj):
        return self.Object.Proxy.eligibleChild(obj.Proxy.Type)

    def setupContextMenu(self, viewObject, menu):
        action = menu.addAction(translate('Rocket', 'Edit %1').replace('%1', viewObject.Object.Label))
        action.triggered.connect(lambda: self.startDefaultEditMode(viewObject))
        return False

    def startDefaultEditMode(self, viewObject):
        document = viewObject.Document.Document
        if not document.HasPendingTransaction:
            text = translate('Rocket', 'Edit %1').replace('%1', viewObject.Object.Label)
            document.openTransaction(text)
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

    def composite(self, color, alpha):
        # Simplified assuming base color is 1 and base alpha is 1
        # https://en.wikipedia.org/wiki/Alpha_compositing
        color0 = (color * alpha) + 1 - alpha
        return color0

    def setColor(self, red, green, blue, alpha):
        # RGBA composited with (1,1,1,1)
        red0 = self.composite(red / 255.0, alpha / 255.0)
        green0 = self.composite(green / 255.0, alpha / 255.0)
        blue0 = self.composite(blue / 255.0, alpha / 255.0)
        color = (red0, green0, blue0)
        self.ViewObject.ShapeColor = color
        self.ViewObject.LineColor = color

    def setShininess(self, shininess):
        self.ViewObject.ShapeMaterial.Shininess = shininess
