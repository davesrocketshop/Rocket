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
"""Class for drawing rockets"""

__title__ = "FreeCAD Rocket View Provider"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import FreeCADGui

from PySide import QtCore,QtGui

from DraftTools import translate

from App.Utilities import _msg
from App.ShapeRocket import hookChildren

class ViewProviderRocket:

    def __init__(self, vobj):
        vobj.addExtension("Gui::ViewProviderGroupExtensionPython")
        vobj.Proxy = self
        self._oldChildren = []
        
    def getIcon(self):
        return FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Rocket.svg"

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object

    def canDropObject(self, obj):
        return self.Object.Proxy.eligibleChild(obj.Proxy.Type)

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

        hookChildren(self.Object, objs, self._oldChildren)
        self._oldChildren = objs

        return objs

    def setupContextMenu(self, vobj, menu):
        """Add the component specific options to the context menu."""
        action1 = QtGui.QAction(translate("Rocket","Toggle active rocket"),menu)
        QtCore.QObject.connect(action1,QtCore.SIGNAL("triggered()"),self.toggleRocket)
        menu.addAction(action1)

    def toggleRocket(self):
        FreeCADGui.runCommand("Rocket_ToggleRocket")
        FreeCADGui.runCommand("Rocket_ToggleStage")

    def setEdit(self,vobj,mode):
        # No editor associated with this object
        return False

    def unsetEdit(self,vobj,mode):
        return False

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None
