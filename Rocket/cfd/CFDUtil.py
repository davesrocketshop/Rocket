# ***************************************************************************
# *   Copyright (c) 2024-2025 David Carter <dcarter@davidcarter.ca>         *
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
"""Class for creating a solid rocket model"""

__title__ = "FreeCAD Create Solid"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import Part

from CfdOF.Mesh.CfdMesh import CfdMesh

from Rocket.cfd.FeatureCFDRocket import FeatureCFDRocket
from Rocket.cfd.FeatureMultiCFDAnalysis import FeatureMultiCFDAnalysis
from Rocket.cfd.FeatureWindTunnel import FeatureWindTunnel
from Rocket.cfd.ViewProviders.ViewProviderCFDMesh import ViewProviderCFDMesh
from Rocket.cfd.ViewProviders.ViewProviderCFDRocket import ViewProviderCFDRocket
from Rocket.cfd.ViewProviders.ViewProviderMultiCFDAnalysis import ViewProviderMutliCFDAnalysis
from Rocket.cfd.ViewProviders.ViewProviderWindTunnel import ViewProviderWindTunnel

def getProxy(obj):
    if hasattr(obj, "Proxy"):
        return obj.Proxy
    return obj

def createSolid(obj):
    ''' Generates a solid compound object '''
    shape = None
    for current in getProxy(obj).getChildren():
        if hasattr(current, "Shape"):
            solid = getProxy(current).getSolidShape(current)
            if solid is not None and solid.isValid():
                if shape == None:
                    shape = solid
                else:
                    shape = Part.makeCompound([shape, solid])
        child = createSolid(current)
        if child is not None and child.isValid():
            if shape == None:
                shape = child
            else:
                shape = Part.makeCompound([shape, child])

    return shape

def caliber(obj):
    ''' Get the caliber of the component '''
    diameter = 0.0
    for current in getProxy(obj).getChildren():
        proxy = getProxy(current)
        if hasattr(proxy, "getMaxRadius"):
            radius = FreeCAD.Units.Quantity(proxy.getMaxRadius()).Value
            diameter = max(diameter, 2.0 * radius)
        child = caliber(current)
        diameter = max(diameter, child)

    return diameter

def finThickness(obj):
    ''' Get the caliber of the component '''
    thickness = 0.0
    for current in getProxy(obj).getChildren():
        # print(current)
        proxy = getProxy(current)
        if hasattr(proxy, "getFinThickness"):
            fin = FreeCAD.Units.Quantity(proxy.getFinThickness()).Value
            if thickness <= 0.0:
                thickness = fin
            elif fin > 0.0:
                thickness = min(thickness, fin)
        child = finThickness(current)
        if thickness <= 0.0:
            thickness = child
        elif child > 0.0:
            thickness = min(thickness, child)

    return thickness

def makeCFDRocket(name='CFDRocket'):
    '''makeCFDRocket(name): makes a CFD Rocket'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureCFDRocket(obj)
    # obj.Proxy.setDefaults()
    if FreeCAD.GuiUp:
        ViewProviderCFDRocket(obj.ViewObject)
        # obj.ViewObject.ShapeAppearance[0].Transparency = 0
        obj.ViewObject.Transparency = 0

    return obj.Proxy

def makeWindTunnel(name='WindTunnel', diameter=10.0, length=20.0, offset=0.0):
    '''makeWindTunnel(name): makes a Wind Tunnel'''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    FeatureWindTunnel(obj)
    obj.Diameter = diameter
    obj.Length = length
    obj.Placement.Base.x = -offset
    # obj.Proxy.setDefaults()
    if FreeCAD.GuiUp:
        ViewProviderWindTunnel(obj.ViewObject)
        # obj.ViewObject.ShapeAppearance[0].Transparency = 70
        obj.ViewObject.Transparency = 70

    return obj.Proxy

def makeMultiCFDAnalysis(name):
    """ Create a Cfd Analysis group object """
    obj = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroupPython", name)
    FeatureMultiCFDAnalysis(obj)

    if FreeCAD.GuiUp:
        ViewProviderMutliCFDAnalysis(obj.ViewObject)
    return obj

def makeCfdMesh(name="CFDMesh"):
    obj = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroupPython", name)
    CfdMesh(obj)
    if FreeCAD.GuiUp:
        ViewProviderCFDMesh(obj.ViewObject)
    return obj
