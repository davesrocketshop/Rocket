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
"""Class for drawing shapes"""

__title__ = "FreeCAD Base Shape Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import Part

class ShapeHandlerBase():
    
    def _drawPods(self, base):
        podInfo = self.getPodInfo()
        parentInfo = self.getParentPodInfo()

        shapes = []
        for i in range(podInfo.podCount):
            shape = Part.Shape(base) # Create a copy
            offset = podInfo.offsets[i]
            if parentInfo is not None: # and self._obj.AngleOffset > 0:
                offset.Y = float(offset.Y) + float(parentInfo.offsets[i].Y)
                offset.Z = float(offset.Y) + float(parentInfo.offsets[i].Z)

            #     parentOffset = podInfo.offsets[i]
            #     angle = float(self._obj.AngleOffset) + i * float(podInfo.podSpacing)
            #     shape.rotate(FreeCAD.Vector(0, parentOffset.Y, parentOffset.Z), FreeCAD.Vector(1,0,0), angle)

            #     circle = Part.makeCircle(1, FreeCAD.Vector(0, parentOffset.Y, parentOffset.Z), FreeCAD.Vector(1,0,0))
            #     Part.show(circle)
            #     circle = Part.makeCircle(1, FreeCAD.Vector(0, offset.Y, offset.Z), FreeCAD.Vector(1,0,0))
            #     Part.show(circle)
                
            # shape.rotate(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(1,0,0), i * float(podInfo.podSpacing))
            shape.translate(FreeCAD.Vector(0, offset.Y, offset.Z))
            shapes.append(shape)

        return Part.makeCompound(shapes)
    
    def getPodInfo(self):
        return self._obj.PodInfo
    
    def getParentPodInfo(self):
        parent = self._obj.Proxy.getParent()
        if parent is not None:
            if hasattr(parent._obj, "PodInfo"):
                return parent._obj.PodInfo
        return None
