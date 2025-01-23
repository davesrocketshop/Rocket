# ***************************************************************************
# *   Copyright (c) 2009 Yorik van Havre <yorik@uncreated.net>              *
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
"""Provides support for importing and exporting SVG files.

It enables importing/exporting objects directly to/from the 3D document
but doesn't handle the SVG output from the TechDraw module.

Currently it only reads the following entities:
* paths, lines, circular arcs, rects, circles, ellipses, polygons, polylines.

Currently unsupported:
* use, image.
"""
## @package importSVG
#  \ingroup DRAFT
#  \brief SVG file importer and exporter

# Check code with
# flake8 --ignore=E226,E266,E401,W503

__title__ = "FreeCAD Draft Workbench - SVG importer/exporter"
__author__ = "Yorik van Havre, Sebastian Hoogen"
__url__ = "https://www.freecad.org"

# TODO:
# ignoring CDATA
# handle image element (external references and inline base64)
# debug Problem with 'Sans' font from Inkscape
# debug Problem with fill color
# implement inheriting fill style from group
# handle relative units

# import math
# import os
# import re
# import xml.sax

import FreeCAD
import Draft
from DraftTools import translate
from Rocket.Utilities import _err, _msg, _wrn
from builtins import open as pyopen

def export(exportList, filename):
    """Export the SVG file with a given list of objects.

    The objects must be derived from Part::Feature, in order to be processed
    and exported.

    Parameters
    ----------
    exportList : list
        List of document objects to export.
    filename : str
        Path to the new file.

    Returns
    -------
    None
        If `exportList` doesn't have shapes to export.
    """
    # svg_export_style = params.get_param("svg_export_style")
    # if svg_export_style != 0 and svg_export_style != 1:
    #     _msg(translate("ImportSVG",
    #                    "Unknown SVG export style, switching to Translated"))
    #    svg_export_style = 0
    svg_export_style = 0

    # Determine the size of the page by adding the bounding boxes
    # of all shapes
    bb = FreeCAD.BoundBox()
    for obj in exportList:
        if (hasattr(obj, "Shape")
                and obj.Shape
                and obj.Shape.BoundBox.isValid()):
            bb.add(obj.Shape.BoundBox)
        else:
            # if Draft.get_type(obj) in ("Text", "LinearDimension", ...)
            _wrn("'{}': no Shape, "
                 "calculate manual bounding box".format(obj.Label))
            bb.add(Draft.get_bbox(obj))

    if not bb.isValid():
        _err(translate("ImportSVG",
                       "The export list contains no object "
                       "with a valid bounding box"))
        return

    minx = bb.XMin
    maxx = bb.XMax
    miny = bb.YMin
    maxy = bb.YMax

    if svg_export_style == 0:
        # translated-style exports get a bit of a margin
        margin = (maxx - minx) * 0.01
    else:
        # raw-style exports get no margin
        margin = 0

    minx -= margin
    maxx += margin
    miny -= margin
    maxy += margin
    sizex = maxx - minx
    sizey = maxy - miny
    miny += margin

    # Use the native Python open which was saved as `pyopen`
    svg = pyopen(filename, 'w')

    # Write header.
    # We specify the SVG width and height in FreeCAD's physical units (mm),
    # and specify the viewBox so that user units maps one-to-one to mm.
    svg.write('<?xml version="1.0"?>\n')
    svg.write('<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"')
    svg.write(' "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n')
    svg.write('<svg')
    svg.write(' width="' + str(sizex) + 'mm" height="' + str(sizey) + 'mm"')
    if svg_export_style == 0:
        # translated-style exports have the viewbox starting at X=0, Y=0
        svg.write(' viewBox="0 0 ' + str(sizex) + ' ' + str(sizey) + '"')
    else:
        # Raw-style exports have the viewbox starting at X=xmin, Y=-ymax
        # We need the negative Y here because SVG is upside down, and we
        # flip the sketch right-way up with a scale later
        svg.write(' viewBox="%f %f %f %f"' % (minx, -maxy, sizex, sizey))

    svg.write(' xmlns="http://www.w3.org/2000/svg" version="1.1"')
    svg.write('>\n')

    # Write paths
    for ob in exportList:
        if svg_export_style == 0:
            # translated-style exports have the entire sketch translated
            # to fit in the X>0, Y>0 quadrant
            # svg.write('<g transform="translate('
            #           + str(-minx) + ',' + str(-miny + 2*margin)
            #           + ') scale(1,-1)">\n')
            svg.write('<g id="%s" transform="translate(%f,%f) '
                      'scale(1,-1)">\n' % (ob.Name, -minx, maxy))
        else:
            # raw-style exports do not translate the sketch
            svg.write('<g id="%s" transform="scale(1,-1)">\n' % ob.Name)

        svg.write(Draft.get_svg(ob, override=False))
        _label_enc = str(ob.Label.encode('utf8'))
        _label = _label_enc.replace('<', '&lt;').replace('>', '&gt;')
        # replace('"', "&quot;")
        svg.write('<title>%s</title>\n' % _label)
        svg.write('</g>\n')

    # Close the file
    svg.write('</svg>')
    svg.close()
