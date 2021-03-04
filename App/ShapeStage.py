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
"""Class for rocket assemblies"""

__title__ = "FreeCAD Rocket Assembly"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

class ShapeStage:

    def __init__(self, obj):
        if not hasattr(obj,"Group"):
            obj.addExtension("App::GroupExtensionPython")

        obj.Proxy=self
        self.version = '1.0'

    def __getstate__(self):
        return self.version

    def position(obj):
        # Dynamic placements
        length = 0.0
        i = len(obj.Group) - 1
        while i >= 0:
            child = obj.Group[i]
            child.Proxy.setAxialPosition(length)

            length += float(child.Proxy.getAxialLength())
            i -= 1

    def execute(self,obj):
        """Method run when the object is recomputed.

        If the site has no Shape or Terrain property assigned, do nothing.

        Perform additions and subtractions on terrain, and assign to the site's
        Shape.

            see Mod/Arch/ArchSite.py for more information
        """

        if not hasattr(obj,'Shape'): # old-style Site
            return

