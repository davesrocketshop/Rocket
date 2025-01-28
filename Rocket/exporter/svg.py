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

import FreeCAD
import Draft
import Part
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

        svg.write(get_svg(ob, override=False))
        _label_enc = str(ob.Label.encode('utf8'))
        _label = _label_enc.replace('<', '&lt;').replace('>', '&gt;')
        # replace('"', "&quot;")
        svg.write('<title>%s</title>\n' % _label)
        svg.write('</g>\n')

    # Close the file
    svg.write('</svg>')
    svg.close()

def get_svg(obj,
            scale=1, linewidth=0.35, fontsize=12,
            fillstyle="shape color", direction=None, linestyle=None,
            color=None, linespacing=None, techdraw=False, rotation=0,
            fillspaces=False, override=True):
    """Return a string containing an SVG representation of the object.

    Paramaeters
    -----------
    scale: float, optional
        It defaults to 1.
        It allows scaling line widths down, so they are resolution-independent.

    linewidth: float, optional
        It defaults to 0.35.

    fontsize: float, optional
        It defaults to 12, which is interpreted as `pt` unit (points).
        It is used if the given object contains any text.

    fillstyle: str, optional
        It defaults to 'shape color'.

    direction: Base::Vector3, optional
        It defaults to `None`.
        It is an arbitrary projection vector or a `WorkingPlane.PlaneBase`
        instance.

    linestyle: optional
        It defaults to `None`.

    color: optional
        It defaults to `None`.

    linespacing: float, optional
        It defaults to `None`.

    techdraw: bool, optional
        It defaults to `False`.
        If it is `True`, it sets some options for generating SVG strings
        for displaying inside TechDraw.

    rotation: float, optional
        It defaults to 0.

    fillspaces: bool, optional
        It defaults to `False`.

    override: bool, optional
        It defaults to `True`.
    """
    # If this is a group, recursively call this function to gather
    # all the SVG strings from the contents of the group
    if hasattr(obj, "isDerivedFrom"):
        if (obj.isDerivedFrom("App::DocumentObjectGroup")
                or obj.isDerivedFrom("App::LinkGroup")
                or (obj.isDerivedFrom("App::Link")
                        and obj.LinkedObject.isDerivedFrom("App::DocumentObjectGroup"))):

            hidden_doc = None

            if (obj.isDerivedFrom("App::LinkGroup")
                    or (obj.isDerivedFrom("App::Link")
                            and obj.LinkedObject.isDerivedFrom("App::DocumentObjectGroup"))):
                if obj.Placement.isIdentity():
                    if obj.isDerivedFrom("App::LinkGroup"):
                        group = obj.ElementList
                    else:
                        group = obj.Group
                else:
                    # Using a hidden doc hack to handle placements.
                    hidden_doc = FreeCAD.newDocument(name="hidden", hidden=True, temp=True)
                    new = hidden_doc.copyObject(obj, True)
                    pla = new.Placement
                    new.Placement = FreeCAD.Placement()
                    if new.isDerivedFrom("App::LinkGroup"):
                        group = new.ElementList
                    else:
                        group = new.Group
                    for child in group:
                        child.Placement = pla * child.Placement
            else:
                group = obj.Group

            svg = ""
            for child in group:
                svg += get_svg(child,
                               scale, linewidth, fontsize,
                               fillstyle, direction, linestyle,
                               color, linespacing, techdraw,
                               rotation, fillspaces, override)

            if hidden_doc is not None:
                try:
                    FreeCAD.closeDocument(hidden_doc.Name)
                except:
                    pass

            return svg

    vobj = Draft._get_view_object(obj)

    pathdata = []
    svg = ""
    linewidth = float(linewidth)/scale
    if not override:
        if vobj is not None and hasattr(vobj, "LineWidth"):
            if hasattr(vobj.LineWidth, "Value"):
                lw = vobj.LineWidth.Value
            else:
                lw = vobj.LineWidth
            linewidth = lw * linewidth

    fontsize = (float(fontsize)/scale)/2
    if linespacing:
        linespacing = float(linespacing)/scale
    else:
        linespacing = 0.5

    # print(obj.Label, "line spacing", linespacing, "scale", scale)

    # The number of times the dots are smaller than the arrow size
    pointratio = 0.75
    plane = None

    if direction:
        if isinstance(direction, FreeCAD.Vector):
            if direction != FreeCAD.Vector(0, 0, 0):
                plane = Draft.WorkingPlane.PlaneBase()
                plane.align_to_point_and_axis_svg(FreeCAD.Vector(0, 0, 0),
                                                  direction.negative().negative(),
                                                  0)
            else:
                raise ValueError("'direction' cannot be: Vector(0, 0, 0)")
        elif isinstance(direction, Draft.WorkingPlane.PlaneBase):
            plane = direction

    stroke = "#000000"
    tstroke = stroke
    if color and override:
        if "#" in color:
            stroke = color
        else:
            stroke = Draft.utils.get_rgb(color)
        tstroke = stroke
    elif FreeCAD.GuiUp:
        # find print color
        pc = Draft.get_print_color(obj)
        if pc:
            stroke = Draft.utils.get_rgb(pc)
        # get line color
        elif vobj is not None:
            if hasattr(vobj, "LineColor"):
                stroke = Draft.utils.get_rgb(vobj.LineColor)
            elif hasattr(vobj, "TextColor"):
                stroke = Draft.utils.get_rgb(vobj.TextColor)
            if hasattr(vobj, "TextColor"):
                tstroke = Draft.utils.get_rgb(vobj.TextColor)

    lstyle = "none"
    if override:
        lstyle = Draft.get_line_style(linestyle, scale)
    else:
        if vobj is not None and hasattr(vobj, "DrawStyle"):
            lstyle = Draft.get_line_style(vobj.DrawStyle, scale)

    if not obj:
        pass

    elif isinstance(obj, Part.Shape):
        svg = Draft._svg_shape(svg, obj, plane,
                         fillstyle, pathdata, stroke, linewidth, lstyle)

    elif hasattr(obj, 'Shape'):
        # In the past we tested for a Part Feature
        # elif obj.isDerivedFrom('Part::Feature'):
        #
        # however, this doesn't work for App::Links; instead we
        # test for a 'Shape'. All Part::Features should have a Shape,
        # and App::Links can have one as well.
        if obj.Shape.isNull():
            return ''

        fill_opacity = 1
        # setting fill
        if obj.Shape.Faces:
            if FreeCAD.GuiUp:
                try:
                    m = vobj.DisplayMode
                except AttributeError:
                    m = None

                if m != "Wireframe":
                    if (fillstyle == "shape color") and hasattr(vobj,"ShapeColor"):
                        fill = Draft.utils.get_rgb(vobj.ShapeColor,
                                             testbw=False)
                        fill_opacity = 1 - vobj.Transparency / 100.0
                    elif fillstyle in ("none",None):
                        fill = "none"
                    else:
                        fill = 'url(#'+fillstyle+')'
                        svg += Draft.get_pattern(fillstyle)
                else:
                    fill = "none"
            else:
                fill = "#888888"
        else:
            fill = 'none'

        if len(obj.Shape.Vertexes) > 1:
            wiredEdges = []
            if obj.Shape.Faces:
                for i, f in enumerate(obj.Shape.Faces):
                    # place outer wire first
                    wires = [f.OuterWire]
                    wires.extend([w for w in f.Wires if w.hashCode() != f.OuterWire.hashCode()])
                    svg += Draft.get_path(obj, plane,
                                    fill, pathdata, stroke, linewidth, lstyle,
                                    fill_opacity=fill_opacity,
                                    wires=f.Wires,
                                    pathname='%s_f%04d' % (obj.Name, i))
                    wiredEdges.extend(f.Edges)
            else:
                for i, w in enumerate(obj.Shape.Wires):
                    svg += Draft.get_path(obj, plane,
                                    fill, pathdata, stroke, linewidth, lstyle,
                                    fill_opacity=fill_opacity,
                                    edges=w.Edges,
                                    pathname='%s_w%04d' % (obj.Name, i))
                    wiredEdges.extend(w.Edges)
            if len(wiredEdges) != len(obj.Shape.Edges):
                fill = 'none' # Required if obj has a face. Edges processed here have no face.
                for i, e in enumerate(obj.Shape.Edges):
                    if Draft.DraftGeomUtils.findEdge(e, wiredEdges) is None:
                        svg += Draft.get_path(obj, plane,
                                        fill, pathdata, stroke, linewidth,
                                        lstyle, fill_opacity=fill_opacity,
                                        edges=[e],
                                        pathname='%s_nwe%04d' % (obj.Name, i))
        else:
            # closed circle or spline
            if obj.Shape.Edges:
                if isinstance(obj.Shape.Edges[0].Curve, Part.Circle):
                    svg = Draft.get_circle(plane,
                                     fill, stroke, linewidth, lstyle,
                                     obj.Shape.Edges[0])
                else:
                    svg = Draft.get_path(obj, plane,
                                   fill, pathdata, stroke, linewidth, lstyle,
                                   fill_opacity=fill_opacity,
                                   edges=obj.Shape.Edges)

    return svg
