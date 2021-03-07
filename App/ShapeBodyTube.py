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
"""Class for drawing body tubes"""

__title__ = "FreeCAD Body Tubes"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from PySide import QtCore
    
from App.ShapeComponent import ShapeLocation
from App.Constants import FEATURE_BODY_TUBE, FEATURE_BULKHEAD, FEATURE_BODY_TUBE, FEATURE_CENTERING_RING, FEATURE_FIN

from App.BodyTubeShapeHandler import BodyTubeShapeHandler

from DraftTools import translate

class ShapeBodyTube(ShapeLocation):

    def __init__(self, obj):
        super().__init__(obj)
        self.Type = FEATURE_BODY_TUBE

        # Default set to a BT-50
        if not hasattr(obj,"InnerDiameter"):
            obj.addProperty('App::PropertyLength', 'InnerDiameter', 'BodyTube', translate('App::Property', 'Diameter of the inside of the body tube')).InnerDiameter = 24.13
        if not hasattr(obj,"OuterDiameter"):
            obj.addProperty('App::PropertyLength', 'OuterDiameter', 'BodyTube', translate('App::Property', 'Diameter of the outside of the body tube')).OuterDiameter = 24.79
        if not hasattr(obj,"Length"):
            obj.addProperty('App::PropertyLength', 'Length', 'BodyTube', translate('App::Property', 'Length of the body tube')).Length = 457.0

        if not hasattr(obj,"InnerDiameter"):
            obj.addProperty('App::PropertyLength', 'InnerDiameter', 'BodyTube', translate('App::Property', 'Diameter of the inside of the body tube')).InnerDiameter = 24.1
        if not hasattr(obj,"OuterDiameter"):
            obj.addProperty('App::PropertyLength', 'OuterDiameter', 'BodyTube', translate('App::Property', 'Diameter of the outside of the body tube')).OuterDiameter = 24.8
        if not hasattr(obj,"Length"):
            obj.addProperty('App::PropertyLength', 'Length', 'BodyTube', QT_TRANSLATtranslateE_NOOP('App::Property', 'Length of the body tube')).Length = 457.0

        if not hasattr(obj,"Shape"):
            obj.addProperty('Part::PropertyPartShape', 'Shape', 'BodyTube', translate('App::Property', 'Shape of the body tube'))

        if not hasattr(obj,"Group"):
            obj.addExtension("App::GroupExtensionPython")

    def getAxialLength(self):
        # Return the length of this component along the central axis
        return self._obj.Length

    def getRadius(self):
        # For placing objects on the outer part of the parent
        return self._obj.OuterDiameter / 2.0

    def execute(self, obj):
        shape = BodyTubeShapeHandler(obj)
        if shape is not None:
            shape.draw()

    def eligibleChild(self, childType):
        return childType in [FEATURE_BULKHEAD, FEATURE_BODY_TUBE, FEATURE_CENTERING_RING, FEATURE_FIN]

    def onChildEdited(self):
        print("%s: onChildEdited()" % (self.__class__.__name__))
        self._obj.Proxy.setEdited()

def hookChildren(obj, group, oldGroup):
    print("hookChildren()")
    changed = False
    for child in group:
        if child not in oldGroup:
            print("%s: hookChildren added" % (child.__class__.__name__))
            child.Proxy.resetPlacement()
            child.Proxy.edited.connect(obj.Proxy.onChildEdited, QtCore.Qt.QueuedConnection)
            changed = True

    for child in oldGroup:
        if child not in group:
            print("%s: hookChildren removed" % (child.__class__.__name__))
            child.Proxy.edited.connect(None)
            changed = True

    if changed:
        obj.Proxy.setEdited()

