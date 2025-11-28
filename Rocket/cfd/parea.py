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
# *   This code is heavily inspired by the parea Python module, customized  *
# *   to work with FreeCAD meshes instead of STL files                      *
# *                                                                         *
# *   https://github.com/nathanrooy/p-area                                  *
# *                                                                         *
# ***************************************************************************


from shapely.geometry import Polygon
from shapely.ops import unary_union

#--- constants ----------------------------------------------------------------+

x, y = [0, 1]

#--- functions ----------------------------------------------------------------+


def _area2(a, b, c):
    '''Calculate twice the area of a 2D triangle
    
    Parameters
    ----------
    a, b, c : tuple
        vertex tuples containing two floats (x, y)
    
    Returns
    -------
    float
        twice the triangle area

    References
    ----------
    [1] Computational Geometry in C by Joseph O'Rourke    
    '''
    return (
        (b[x] - a[x]) * (c[y] - a[y]) -
        (c[x] - a[x]) * (b[y] - a[y]))


def _mungeTriangle(v1, v2, v3, min_area=0):
    '''MUNGE TRIANGLE
    
    For every new triangle that gets added, it  needs to pass some basic 
    quality controls and if need be, fixed.
    
    1) Triangles with zero area are automatically rejected.
    
    2) Triangles must have three unique vertices.
    
    3) All triangles will be returned with a CCW winding regardless of the 
    winding upon input.
    
    4) Final output is a list of three edges, consisting of vertex master list 
    indices.
    
    Inputs
    ------
    v1, v2, v3 : tuples
    
    Returns
    -------
    t : a list consisting of three edge tuples
    '''
    
    # first check if the triangle has three unique vertices
    if v1==v2 or v2==v3 or v3==v1: return []

    a2 = _area2(v1, v2, v3)
    
    # if the triangle has cw winding, reverse the winding order 
    if a2 < 0:
        t_verts = [v1, v3, v2]
    
    # the winding order is correct, leave vertices alone
    if a2 > 0:
        t_verts = [v1, v2, v3]
        
    # minimum triangle area check
    if abs(a2 * 0.5)<=min_area:
        return []
        
    return t_verts

def _projectTriangleToXYPlane(tri_3d):
    return [(v[1], v[2], 0.0) for v in tri_3d]

def _projectTriangleToXZPlane(tri_3d):
    return [(v[0], v[2]) for v in tri_3d]

def _meshTriangleGenerator(mesh):
    # initialize
    triangle = []

    # cycle through stl line by line
    for i, facet in enumerate(mesh.Facets):
        if len(facet.Points) != 3:
            print("Points = {}".format(facet.Points))
        else:
            for point in facet.Points:
                # print(type(point[0]))
                # print(dir(point[0]))
                x, y, z = float(point[0]), float(point[1]), float(point[2])
                triangle.append([x, y, z])
            yield triangle
            triangle = []

def _loadMesh(mesh, plane):
    '''LOAD STL

    Parameters
    ----------
    mesh : existing mesh

    Returns
    -------
    list of shapely polygon objects
    '''

    # assemble stl
    triangles = []
    for i, t in enumerate(_meshTriangleGenerator(mesh)):
        if plane == 'XZ':
            v1, v2, v3 = _projectTriangleToXZPlane(t)
        else:
            v1, v2, v3 = _projectTriangleToXYPlane(t)
        verts = _mungeTriangle(v1, v2, v3)
        if len(verts) == 3:
            triangles.append(Polygon(verts))

    return triangles

def calculateProjectedArea(mesh, plane='XY'):
    '''CALCULATE PROJECTED AREA

    Parameters
    ----------
    mesh : existing mesh

    Returns
    -------
    float
    '''

    # bulk load all triangles from stl
    triangles = _loadMesh(mesh, plane)

    # merge triangles into single polygon
    sub_polys = unary_union(triangles)

    return unary_union(sub_polys).area
