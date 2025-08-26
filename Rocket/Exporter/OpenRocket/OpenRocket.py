# ***************************************************************************
# *   Copyright (c) 2025 David Carter <dcarter@davidcarter.ca>              *
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
"""Provides support for exporting Open Rocket files."""

__title__ = "FreeCAD Open Rocket Exporter"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import io
import uuid
from typing import Any

import FreeCAD

from Rocket.RocketComponentShapeless import RocketComponentShapeless
from Rocket.FeatureStage import FeatureStage

from Rocket.Constants import FEATURE_ROCKET, FEATURE_STAGE, FEATURE_PARALLEL_STAGE, FEATURE_BULKHEAD, FEATURE_POD, \
    FEATURE_BODY_TUBE, FEATURE_INNER_TUBE, FEATURE_TUBE_COUPLER, FEATURE_ENGINE_BLOCK, FEATURE_CENTERING_RING, \
    FEATURE_FIN, FEATURE_FINCAN, FEATURE_NOSE_CONE, FEATURE_TRANSITION, FEATURE_LAUNCH_LUG, FEATURE_RAIL_BUTTON, \
    FEATURE_RAIL_GUIDE, FEATURE_OFFSET, FEATURE_RINGTAIL
from Rocket.Constants import TYPE_CONE, TYPE_BLUNTED_CONE, TYPE_SPHERICAL, TYPE_ELLIPTICAL, TYPE_OGIVE, \
    TYPE_BLUNTED_OGIVE, TYPE_SECANT_OGIVE, TYPE_PARABOLA, TYPE_VON_KARMAN, TYPE_PARABOLIC, TYPE_POWER, TYPE_HAACK, \
    TYPE_NIKE_SMOKE, TYPE_PROXY
from Rocket.Constants import STYLE_SOLID, STYLE_HOLLOW, STYLE_SOLID_CORE
from Rocket.Constants import LOCATION_PARENT_TOP, LOCATION_PARENT_MIDDLE, LOCATION_PARENT_BOTTOM, LOCATION_BASE, \
    LOCATION_AFTER, LOCATION_SURFACE, LOCATION_CENTER
from Rocket.Constants import FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_ELLIPSE, FIN_CROSS_BICONVEX, \
    FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE
from Rocket.Constants import FIN_TYPE_TRAPEZOID, FIN_TYPE_TRIANGLE, FIN_TYPE_ELLIPSE, FIN_TYPE_TUBE, FIN_TYPE_SKETCH
from Rocket.Constants import FINCAN_STYLE_SLEEVE


class OpenRocketExporter:

    def __init__(self, exportList: list[FreeCAD.DocumentObject], filename: str) -> None:
        self._exportList = exportList
        self._filename = filename

        self._feature = {
            FEATURE_ROCKET : self.writeNull,
            FEATURE_STAGE : self.writeNull,
            FEATURE_PARALLEL_STAGE : self.writeNull,
            FEATURE_BULKHEAD : self.writeBulkhead,
            FEATURE_POD : self.writeNull,
            FEATURE_BODY_TUBE : self.writeBodytube,
            FEATURE_INNER_TUBE : self.writeInnerTube,
            FEATURE_TUBE_COUPLER : self.writeTubeCoupler,
            FEATURE_ENGINE_BLOCK : self.writeEngineBlock,
            FEATURE_CENTERING_RING : self.writeCenteringRing,
            FEATURE_FIN : self.writeFin,
            FEATURE_FINCAN : self.writeFinCan,
            FEATURE_NOSE_CONE : self.writeNosecone,
            FEATURE_TRANSITION : self.writeTransition,
            FEATURE_LAUNCH_LUG : self.writeLaunchLug,
            FEATURE_RAIL_BUTTON : self.writeRailButton,
            FEATURE_RAIL_GUIDE : self.writeNull,
            FEATURE_OFFSET : self.writeNull,
            FEATURE_RINGTAIL : self.writeNull,
        }

        self._noseTypes = {
            TYPE_CONE : self.writeNoseTypeCone,
            TYPE_BLUNTED_CONE : self.writeNoseTypeCone,
            TYPE_SPHERICAL : self.writeNoseTypeEllipsoid,
            TYPE_ELLIPTICAL : self.writeNoseTypeEllipsoid,
            TYPE_OGIVE : self.writeNoseTypeOgive,
            TYPE_BLUNTED_OGIVE : self.writeNoseTypeOgive,
            TYPE_SECANT_OGIVE : self.writeNoseTypeOgive,
            TYPE_PARABOLA : self.writeNoseTypePower, # Actually a power series
            TYPE_VON_KARMAN : self.writeNoseTypeHaack,
            TYPE_PARABOLIC : self.writeNoseTypeParabolic,
            TYPE_POWER : self.writeNoseTypePower,
            TYPE_HAACK : self.writeNoseTypeHaack,
            TYPE_NIKE_SMOKE : self.writeNoseTypeCone,
            TYPE_PROXY : self.writeNoseTypeOgive,
        }

        self._transitionTypes = {
            TYPE_CONE : self.writeTransitionTypeCone,
            TYPE_BLUNTED_CONE : self.writeTransitionTypeCone,
            TYPE_SPHERICAL : self.writeTransitionTypeEllipsoid,
            TYPE_ELLIPTICAL : self.writeTransitionTypeEllipsoid,
            TYPE_OGIVE : self.writeTransitionTypeOgive,
            TYPE_BLUNTED_OGIVE : self.writeTransitionTypeOgive,
            TYPE_SECANT_OGIVE : self.writeTransitionTypeOgive,
            TYPE_PARABOLA : self.writeTransitionTypePower, # Actually a power series
            TYPE_VON_KARMAN : self.writeTransitionTypeHaack,
            TYPE_PARABOLIC : self.writeTransitionTypeParabolic,
            TYPE_POWER : self.writeTransitionTypePower,
            TYPE_HAACK : self.writeTransitionTypeHaack,
            TYPE_NIKE_SMOKE : self.writeTransitionTypeCone,
            TYPE_PROXY : self.writeTransitionTypeOgive,
        }

        self._locations = {
            LOCATION_PARENT_TOP : "top",
            LOCATION_PARENT_MIDDLE : "middle",
            LOCATION_PARENT_BOTTOM : "bottom",
            LOCATION_BASE : "base",
            LOCATION_AFTER : "after",
            LOCATION_SURFACE : "surface",
            LOCATION_CENTER : "center"
        }

        self._finCrossSection = {
            FIN_CROSS_SQUARE : "square",
            FIN_CROSS_ROUND : "rounded",
            FIN_CROSS_ELLIPSE : "rounded",
            FIN_CROSS_BICONVEX : "square",
            FIN_CROSS_AIRFOIL : "airfoil",
            FIN_CROSS_WEDGE : "square",
            FIN_CROSS_DIAMOND : "square",
            FIN_CROSS_TAPER_LE : "square",
            FIN_CROSS_TAPER_TE : "square",
            FIN_CROSS_TAPER_LETE : "square",
        }

    def export(self):
        entry = self._exportList[0]
        # print(dir(entry.Document))
        name=entry.Document.Name
        with open(self._filename, "w", encoding='utf-8') as file:
            file.write(f"""<?xml version='1.0' encoding='utf-8'?>
<openrocket version="1.10" creator="Rocket Workbench">
  <rocket>
    <name>{name}</name>
    <id>{uuid.uuid4()}</id>
    <axialoffset method="absolute">0.0</axialoffset>
    <position type="absolute">0.0</position>
    <designtype>original</designtype>
    <referencetype>maximum</referencetype>

    <subcomponents>
""")
            self.writeStages(file, entry)
            file.write("""    </subcomponents>
  </rocket>

  <simulations>
  </simulations>
  <photostudio>
  </photostudio>
  <docprefs>
  </docprefs>
</openrocket>
""")

    def writeStages(self, file : io.TextIOBase, obj : FreeCAD.DocumentObject) -> None:
        proxy = self.getProxy(obj)
        for child in proxy.getChildren():
            childProxy = self.getProxy(child)
            if isinstance(childProxy, FeatureStage):
                self.writeStage(file, childProxy)

    def writeStage(self, file : io.TextIOBase, feature : RocketComponentShapeless):
        stageName = feature.getName()
        file.write(f"""      <stage>
        <name>{stageName}</name>
        <id>{uuid.uuid4()}</id>\n""")
        indent = 8
        self.writeSubcomponents(file, feature, indent)
        file.write("      </stage>\n")

    def getProxy(self, obj : Any) -> RocketComponentShapeless:
        if hasattr(obj, "Proxy"):
            return obj.Proxy
        return obj

    def toMeters(self, mm : float) -> float:
        return mm / 1000.0

    def writeSubcomponents(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int, extra : RocketComponentShapeless | None = None) -> None:
        if feature.hasChildren() or extra:
            file.write(f"{' ' * indent}<subcomponents>\n")
            if extra:
                type = extra.getType()
                if type == FEATURE_FINCAN:
                    type = FEATURE_FIN # Avoid recursion
                    if type in self._feature:
                        self._feature[type](file, extra, indent + 2, "fin")
                    if extra._obj.LaunchLug:
                        type = FEATURE_LAUNCH_LUG
                    if type in self._feature:
                        self._feature[type](file, extra, indent + 2, "lug")
            for child in feature.getChildren():
                childProxy = self.getProxy(child)
                type = childProxy.getType()
                if type in self._feature:
                    self._feature[type](file, childProxy, indent + 2)
                else:
                    print(f"Unknown feature {type}")
            file.write(f"{' ' * indent}</subcomponents>\n")

    def writeNull(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        pass

    def writeNosecone(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        file.write(f"{' ' * indent}<nosecone>\n")
        file.write(f"{' ' * (indent + 2)}<name>{feature.getName()}</name>\n")
        file.write(f"{' ' * (indent + 2)}<id>{uuid.uuid4()}</id>\n")
        if len(feature._obj.Comment) > 0:
            file.write(f"{' ' * (indent + 2)}<comment>{feature._obj.Comment}</comment>\n")
        noseType = feature._obj.NoseType
        if noseType in self._noseTypes:
            self._noseTypes[noseType](file, feature, indent + 2)
        else:
            print(f"Unknown nose type {noseType}")
        file.write(f"{' ' * indent}</nosecone>\n\n")

    def writeNoseTypeCone(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        self.writeNoseParameters(file, feature, indent, "conical")

    def writeNoseTypeOgive(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        self.writeNoseParameters(file, feature, indent, "ogive")

    def writeNoseTypeEllipsoid(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        self.writeNoseParameters(file, feature, indent, "ellipsoid")

    def writeNoseTypePower(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        self.writeNoseParameters(file, feature, indent, "power")

    def writeNoseTypeParabolic(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        self.writeNoseParameters(file, feature, indent, "parabolic")

    def writeNoseTypeHaack(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        self.writeNoseParameters(file, feature, indent, "haack")

    def writeNoseParameters(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int, shape : str) -> None:
        file.write(f"{' ' * (indent)}<length>{self.toMeters(float(feature.getLength()))}</length>\n")
        if feature._obj.NoseStyle == STYLE_SOLID:
            file.write(f"{' ' * (indent)}<thickness>filled</thickness>\n")
        else:
            file.write(f"{' ' * (indent)}<thickness>{self.toMeters(feature._obj.Thickness.Value)}</thickness>\n")
        if feature._obj.NoseType in [TYPE_SECANT_OGIVE, TYPE_POWER, TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_HAACK, TYPE_VON_KARMAN]:
            file.write(f"{' ' * (indent)}<shapeparameter>{feature._obj.Coefficient}</shapeparameter>\n")
        else:
            file.write(f"{' ' * (indent)}<shapeparameter>1.0</shapeparameter>\n")
        file.write(f"{' ' * (indent)}<shape>{shape}</shape>\n")
        # <shapeclipped>false</shapeclipped>
        file.write(f"{' ' * (indent)}<aftradius>{self.toMeters(float(feature.getAftRadius()))}</aftradius>\n")
        self.writeNoseShoulder(file, feature, indent)
        file.write(f"{' ' * (indent)}<isflipped>false</isflipped>\n")

    def writeNoseShoulder(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        if feature._obj.Shoulder:
            file.write(f"{' ' * (indent)}<aftshoulderradius>{self.toMeters(float(feature.getAftShoulderRadius()))}</aftshoulderradius>\n")
            file.write(f"{' ' * (indent)}<aftshoulderlength>{self.toMeters(feature._obj.ShoulderLength.Value)}</aftshoulderlength>\n")
            file.write(f"{' ' * (indent)}<aftshoulderthickness>{self.toMeters(feature._obj.ShoulderThickness.Value)}</aftshoulderthickness>\n")
            if feature._obj.NoseStyle != STYLE_HOLLOW:
                file.write(f"{' ' * (indent)}<aftshouldercapped>true</aftshouldercapped>\n")
            else:
                file.write(f"{' ' * (indent)}<aftshouldercapped>false</aftshouldercapped>\n")

    def writeTransition(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        file.write(f"{' ' * indent}<transition>\n")
        file.write(f"{' ' * (indent + 2)}<name>{feature.getName()}</name>\n")
        file.write(f"{' ' * (indent + 2)}<id>{uuid.uuid4()}</id>\n")
        if len(feature._obj.Comment) > 0:
            file.write(f"{' ' * (indent + 2)}<comment>{feature._obj.Comment}</comment>\n")
        transitionType = feature._obj.TransitionType
        if transitionType in self._transitionTypes:
            self._transitionTypes[transitionType](file, feature, indent + 2)
        else:
            print(f"Unknown nose type {transitionType}")
        file.write(f"{' ' * indent}</transition>\n\n")

    def writeTransitionTypeCone(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        self.writeTransitionParameters(file, feature, indent, "conical")

    def writeTransitionTypeOgive(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        self.writeTransitionParameters(file, feature, indent, "ogive")

    def writeTransitionTypeEllipsoid(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        self.writeTransitionParameters(file, feature, indent, "ellipsoid")

    def writeTransitionTypePower(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        self.writeTransitionParameters(file, feature, indent, "power")

    def writeTransitionTypeParabolic(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        self.writeTransitionParameters(file, feature, indent, "parabolic")

    def writeTransitionTypeHaack(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        self.writeTransitionParameters(file, feature, indent, "haack")

    def writeTransitionParameters(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int, shape : str) -> None:
        file.write(f"{' ' * (indent)}<length>{self.toMeters(float(feature.getLength()))}</length>\n")
        if feature._obj.TransitionStyle == STYLE_SOLID:
            file.write(f"{' ' * (indent)}<thickness>filled</thickness>\n")
        else:
            file.write(f"{' ' * (indent)}<thickness>{self.toMeters(feature._obj.Thickness.Value)}</thickness>\n")
        file.write(f"{' ' * (indent)}<shape>{shape}</shape>\n")
        if feature._obj.TransitionType in [TYPE_ELLIPTICAL, TYPE_POWER, TYPE_PARABOLA, TYPE_HAACK, TYPE_VON_KARMAN]:
            if feature._obj.Clipped:
                file.write(f"{' ' * (indent)}<shapeclipped>true</shapeclipped>\n")
            else:
                file.write(f"{' ' * (indent)}<shapeclipped>false</shapeclipped>\n")
        if feature._obj.TransitionType in [TYPE_SECANT_OGIVE, TYPE_POWER, TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_HAACK, TYPE_VON_KARMAN]:
            file.write(f"{' ' * (indent)}<shapeparameter>{feature._obj.Coefficient}</shapeparameter>\n")
        elif feature._obj.TransitionType in [TYPE_OGIVE, TYPE_BLUNTED_OGIVE]:
            file.write(f"{' ' * (indent)}<shapeparameter>1.0</shapeparameter>\n")
        if feature.isForeRadiusAutomatic():
            file.write(f"{' ' * (indent)}<foreradius>auto {self.toMeters(float(feature.getForeRadius()))}</foreradius>\n")
        else:
            file.write(f"{' ' * (indent)}<foreradius>{self.toMeters(float(feature.getForeRadius()))}</foreradius>\n")
        if feature.isAftRadiusAutomatic():
            file.write(f"{' ' * (indent)}<aftradius>auto {self.toMeters(float(feature.getAftRadius()))}</aftradius>\n")
        else:
            file.write(f"{' ' * (indent)}<aftradius>{self.toMeters(float(feature.getAftRadius()))}</aftradius>\n")
        self.writeTransitionForeShoulder(file, feature, indent)
        self.writeTransitionAftShoulder(file, feature, indent)

    def writeTransitionForeShoulder(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        if feature._obj.ForeShoulder:
            file.write(f"{' ' * (indent)}<foreshoulderradius>{self.toMeters(feature.getForeShoulderRadius())}</foreshoulderradius>\n")
            file.write(f"{' ' * (indent)}<foreshoulderlength>{self.toMeters(feature._obj.ForeShoulderLength.Value)}</foreshoulderlength>\n")
            file.write(f"{' ' * (indent)}<foreshoulderthickness>{self.toMeters(feature._obj.ForeShoulderThickness.Value)}</foreshoulderthickness>\n")
            if feature._obj.TransitionStyle not in [STYLE_HOLLOW, STYLE_SOLID_CORE]:
                file.write(f"{' ' * (indent)}<foreshouldercapped>true</foreshouldercapped>\n")
            else:
                file.write(f"{' ' * (indent)}<foreshouldercapped>false</foreshouldercapped>\n")
        else:
            file.write(f"{' ' * (indent)}<foreshoulderradius>0.0</foreshoulderradius>\n")
            file.write(f"{' ' * (indent)}<foreshoulderlength>0.0</foreshoulderlength>\n")
            file.write(f"{' ' * (indent)}<foreshoulderthickness>0.0</foreshoulderthickness>\n")
            file.write(f"{' ' * (indent)}<foreshouldercapped>false</foreshouldercapped>\n")

    def writeTransitionAftShoulder(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        if feature._obj.AftShoulder:
            file.write(f"{' ' * (indent)}<aftshoulderradius>{self.toMeters(float(feature.getAftShoulderRadius()))}</aftshoulderradius>\n")
            file.write(f"{' ' * (indent)}<aftshoulderlength>{self.toMeters(feature._obj.AftShoulderLength.Value)}</aftshoulderlength>\n")
            file.write(f"{' ' * (indent)}<aftshoulderthickness>{self.toMeters(feature._obj.AftShoulderThickness.Value)}</aftshoulderthickness>\n")
            if feature._obj.TransitionStyle not in [STYLE_HOLLOW, STYLE_SOLID_CORE]:
                file.write(f"{' ' * (indent)}<aftshouldercapped>true</aftshouldercapped>\n")
            else:
                file.write(f"{' ' * (indent)}<aftshouldercapped>false</aftshouldercapped>\n")
        else:
            file.write(f"{' ' * (indent)}<aftshoulderradius>0.0</aftshoulderradius>\n")
            file.write(f"{' ' * (indent)}<aftshoulderlength>0.0</aftshoulderlength>\n")
            file.write(f"{' ' * (indent)}<aftshoulderthickness>0.0</aftshoulderthickness>\n")
            file.write(f"{' ' * (indent)}<aftshouldercapped>false</aftshouldercapped>\n")

    def writeBodytube(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int, finCan : RocketComponentShapeless | None = None) -> None:
        file.write(f"{' ' * indent}<bodytube>\n")
        file.write(f"{' ' * (indent + 2)}<name>{feature.getName()}</name>\n")
        file.write(f"{' ' * (indent + 2)}<id>{uuid.uuid4()}</id>\n")
        file.write(f"{' ' * (indent + 2)}<length>{self.toMeters(float(feature.getLength()))}</length>\n")
        file.write(f"{' ' * (indent + 2)}<thickness>{self.toMeters(feature._obj.Thickness.Value)}</thickness>\n")
        if hasattr(feature, "isOuterRadiusAutomatic") and feature.isOuterRadiusAutomatic():
            file.write(f"{' ' * (indent + 2)}<radius>auto {self.toMeters(float(feature.getForeRadius()))}</radius>\n")
        else:
            file.write(f"{' ' * (indent + 2)}<radius>{self.toMeters(float(feature.getForeRadius()))}</radius>\n")
        self.writeMotorMount(file, feature, indent + 2)
        # if finCan:
        #     # Fincans aren't directly supported by OpenRocket. This is a kludge
        #     self.writeFin(file, finCan, indent + 2)
        self.writeSubcomponents(file, feature, indent + 2, finCan)
        file.write(f"{' ' * indent}</bodytube>\n\n")

    def writeTubeCoupler(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        file.write(f"{' ' * indent}<tubecoupler>\n")
        file.write(f"{' ' * (indent + 2)}<name>{feature.getName()}</name>\n")
        file.write(f"{' ' * (indent + 2)}<id>{uuid.uuid4()}</id>\n")
        file.write(f"{' ' * (indent + 2)}<axialoffset method=\"{self.getAxialMethod(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</axialoffset>\n")
        file.write(f"{' ' * (indent + 2)}<position type=\"{self.getPositionType(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</position>\n")
        file.write(f"{' ' * (indent + 2)}<length>{self.toMeters(float(feature.getLength()))}</length>\n")
        # <radialposition>0.0</radialposition>
        # <radialdirection>0.0</radialdirection>
        if feature.isOuterRadiusAutomatic():
            file.write(f"{' ' * (indent + 2)}<outerradius>auto {self.toMeters(float(feature.getOuterRadius(0)))}</outerradius>\n")
        else:
            file.write(f"{' ' * (indent + 2)}<outerradius>{self.toMeters(float(feature.getOuterRadius(0)))}</outerradius>\n")
        file.write(f"{' ' * (indent + 2)}<thickness>{self.toMeters(feature._obj.Thickness.Value)}</thickness>\n")
        self.writeSubcomponents(file, feature, indent + 2)
        file.write(f"{' ' * indent}</tubecoupler>\n\n")

    def writeInnerTube(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        file.write(f"{' ' * indent}<innertube>\n")
        file.write(f"{' ' * (indent + 2)}<name>{feature.getName()}</name>\n")
        file.write(f"{' ' * (indent + 2)}<id>{uuid.uuid4()}</id>\n")
        file.write(f"{' ' * (indent + 2)}<axialoffset method=\"{self.getAxialMethod(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</axialoffset>\n")
        file.write(f"{' ' * (indent + 2)}<position type=\"{self.getPositionType(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</position>\n")
        file.write(f"{' ' * (indent + 2)}<length>{self.toMeters(float(feature.getLength()))}</length>\n")
        # <radialposition>0.0</radialposition>
        # <radialdirection>0.0</radialdirection>
        if feature.isOuterRadiusAutomatic():
            file.write(f"{' ' * (indent + 2)}<outerradius>auto {self.toMeters(float(feature.getOuterRadius(0)))}</outerradius>\n")
        else:
            file.write(f"{' ' * (indent + 2)}<outerradius>{self.toMeters(float(feature.getOuterRadius(0)))}</outerradius>\n")
        file.write(f"{' ' * (indent + 2)}<thickness>{self.toMeters(feature._obj.Thickness.Value)}</thickness>\n")
        self.writeMotorMount(file, feature, indent + 2)
        self.writeSubcomponents(file, feature, indent + 2)
        file.write(f"{' ' * indent}</innertube>\n\n")

    def writeMotorMount(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        if feature.isMotorMount():
            file.write(f"{' ' * indent}<motormount>\n")
            file.write(f"{' ' * (indent + 2)}<overhang>{self.toMeters(feature._obj.Overhang.Value)}</overhang>\n")
            self.writeSubcomponents(file, feature, indent + 2)
            file.write(f"{' ' * indent}</motormount>\n\n")

    def writeBulkhead(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        file.write(f"{' ' * indent}<bulkhead>\n")
        file.write(f"{' ' * (indent + 2)}<name>{feature.getName()}</name>\n")
        file.write(f"{' ' * (indent + 2)}<id>{uuid.uuid4()}</id>\n")
        file.write(f"{' ' * (indent + 2)}<instancecount>1</instancecount>\n")
        file.write(f"{' ' * (indent + 2)}<instanceseparation>0</instanceseparation>\n")
        file.write(f"{' ' * (indent + 2)}<axialoffset method=\"{self.getAxialMethod(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</axialoffset>\n")
        file.write(f"{' ' * (indent + 2)}<position type=\"{self.getPositionType(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</position>\n")
        file.write(f"{' ' * (indent + 2)}<length>{self.toMeters(float(feature.getLength()))}</length>\n")
        # <radialposition>0.0</radialposition>
        # <radialdirection>0.0</radialdirection>
        if feature.isOuterRadiusAutomatic():
            file.write(f"{' ' * (indent + 2)}<outerradius>auto {self.toMeters(float(feature.getOuterRadius(0)))}</outerradius>\n")
        else:
            file.write(f"{' ' * (indent + 2)}<outerradius>{self.toMeters(float(feature.getOuterRadius(0)))}</outerradius>\n")
        file.write(f"{' ' * indent}</bulkhead>\n\n")

    def writeCenteringRing(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        file.write(f"{' ' * indent}<centeringring>\n")
        file.write(f"{' ' * (indent + 2)}<name>{feature.getName()}</name>\n")
        file.write(f"{' ' * (indent + 2)}<id>{uuid.uuid4()}</id>\n")
        file.write(f"{' ' * (indent + 2)}<instancecount>1</instancecount>\n")
        file.write(f"{' ' * (indent + 2)}<instanceseparation>0</instanceseparation>\n")
        file.write(f"{' ' * (indent + 2)}<axialoffset method=\"{self.getAxialMethod(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</axialoffset>\n")
        file.write(f"{' ' * (indent + 2)}<position type=\"{self.getPositionType(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</position>\n")
        file.write(f"{' ' * (indent + 2)}<length>{self.toMeters(float(feature.getLength()))}</length>\n")
        # <radialposition>0.0</radialposition>
        # <radialdirection>0.0</radialdirection>
        if feature.isOuterRadiusAutomatic():
            file.write(f"{' ' * (indent + 2)}<outerradius>auto {self.toMeters(float(feature.getOuterRadius(0)))}</outerradius>\n")
        else:
            file.write(f"{' ' * (indent + 2)}<outerradius>{self.toMeters(float(feature.getOuterRadius(0)))}</outerradius>\n")
        if feature.isInnerRadiusAutomatic():
            file.write(f"{' ' * (indent + 2)}<innerradius>auto</innerradius>\n")
        else:
            file.write(f"{' ' * (indent + 2)}<innerradius>{self.toMeters(float(feature.getInnerRadius(0)))}</innerradius>\n")
        file.write(f"{' ' * indent}</centeringring>\n\n")

    def writeEngineBlock(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        file.write(f"{' ' * indent}<engineblock>\n")
        file.write(f"{' ' * (indent + 2)}<name>{feature.getName()}</name>\n")
        file.write(f"{' ' * (indent + 2)}<id>{uuid.uuid4()}</id>\n")
        file.write(f"{' ' * (indent + 2)}<axialoffset method=\"{self.getAxialMethod(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</axialoffset>\n")
        file.write(f"{' ' * (indent + 2)}<position type=\"{self.getPositionType(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</position>\n")
        file.write(f"{' ' * (indent + 2)}<length>{self.toMeters(float(feature.getLength()))}</length>\n")
        if feature.isOuterRadiusAutomatic():
            file.write(f"{' ' * (indent + 2)}<outerradius>auto {self.toMeters(float(feature.getOuterRadius(0)))}</outerradius>\n")
        else:
            file.write(f"{' ' * (indent + 2)}<outerradius>{self.toMeters(float(feature.getOuterRadius(0)))}</outerradius>\n")
        file.write(f"{' ' * (indent + 2)}<thickness>{self.toMeters(float(feature.getThickness()))}</thickness>\n")
        file.write(f"{' ' * indent}</engineblock>\n\n")

    def writeLaunchLug(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int, suffix : str | None = None) -> None:
        file.write(f"{' ' * indent}<launchlug>\n")
        if suffix:
            file.write(f"{' ' * (indent + 2)}<name>{feature.getName()}-{suffix}</name>\n")
        else:
            file.write(f"{' ' * (indent + 2)}<name>{feature.getName()}</name>\n")
        file.write(f"{' ' * (indent + 2)}<id>{uuid.uuid4()}</id>\n")
        if hasattr(feature, "getInstanceCount"):
            file.write(f"{' ' * (indent + 2)}<instancecount>{feature.getInstanceCount()}</instancecount>\n")
            file.write(f"{' ' * (indent + 2)}<instanceseparation>{feature.getInstanceSeparation()}</instanceseparation>\n")
        if feature.getType() == FEATURE_FINCAN:
            offset = float(feature._obj.FinSpacing) / 2.0
            file.write(f"{' ' * (indent + 2)}<angleoffset method=\"relative\">{-offset}</angleoffset>\n")
            file.write(f"{' ' * (indent + 2)}<radialdirection>{-offset}</radialdirection>\n")
            file.write(f"{' ' * (indent + 2)}<axialoffset method=\"{self.getAxialMethod(feature)}\">{self.toMeters(feature._obj.LugLeadingEdgeOffset.Value)}</axialoffset>\n")
            file.write(f"{' ' * (indent + 2)}<position type=\"top\">{self.toMeters(feature._obj.LugLeadingEdgeOffset.Value)}</position>\n")
            file.write(f"{' ' * (indent + 2)}<radius>{self.toMeters(float(feature._obj.LugInnerDiameter) / 2.0 + float(feature._obj.LugThickness))}</radius>\n")
            file.write(f"{' ' * (indent + 2)}<length>{self.toMeters(float(feature._obj.LugLength))}</length>\n")
            file.write(f"{' ' * (indent + 2)}<thickness>{self.toMeters(float(feature._obj.LugThickness))}</thickness>\n")
        else:
            file.write(f"{' ' * (indent + 2)}<angleoffset method=\"relative\">{feature._obj.AngleOffset.Value}</angleoffset>\n")
            file.write(f"{' ' * (indent + 2)}<radialdirection>{feature._obj.AngleOffset.Value}</radialdirection>\n")
            file.write(f"{' ' * (indent + 2)}<axialoffset method=\"{self.getAxialMethod(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</axialoffset>\n")
            file.write(f"{' ' * (indent + 2)}<position type=\"{self.getPositionType(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</position>\n")
            file.write(f"{' ' * (indent + 2)}<radius>{self.toMeters(float(feature.getOuterRadius(0)))}</radius>\n")
            file.write(f"{' ' * (indent + 2)}<length>{self.toMeters(float(feature.getLength()))}</length>\n")
            file.write(f"{' ' * (indent + 2)}<thickness>{self.toMeters(feature._obj.Thickness.Value)}</thickness>\n")
        file.write(f"{' ' * indent}</launchlug>\n\n")

    def writeRailButton(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        file.write(f"{' ' * indent}<railbutton>\n")
        file.write(f"{' ' * (indent + 2)}<name>{feature.getName()}</name>\n")
        file.write(f"{' ' * (indent + 2)}<id>{uuid.uuid4()}</id>\n")
        file.write(f"{' ' * (indent + 2)}<instancecount>{feature.getInstanceCount()}</instancecount>\n")
        file.write(f"{' ' * (indent + 2)}<instanceseparation>{feature.getInstanceSeparation()}</instanceseparation>\n")
        file.write(f"{' ' * (indent + 2)}<angleoffset method=\"relative\">{feature._obj.AngleOffset.Value}</angleoffset>\n")
        file.write(f"{' ' * (indent + 2)}<axialoffset method=\"{self.getAxialMethod(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</axialoffset>\n")
        file.write(f"{' ' * (indent + 2)}<position type=\"{self.getPositionType(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</position>\n")
        file.write(f"{' ' * (indent + 2)}<outerdiameter>{self.toMeters(feature._obj.Diameter.Value)}</outerdiameter>\n")
        file.write(f"{' ' * (indent + 2)}<innerdiameter>{self.toMeters(feature._obj.InnerDiameter.Value)}</innerdiameter>\n")
        file.write(f"{' ' * (indent + 2)}<height>{self.toMeters(feature._obj.Height.Value)}</height>\n")
        file.write(f"{' ' * (indent + 2)}<baseheight>{self.toMeters(feature._obj.BaseHeight.Value)}</baseheight>\n")
        file.write(f"{' ' * (indent + 2)}<flangeheight>{self.toMeters(feature._obj.FlangeHeight.Value)}</flangeheight>\n")
        file.write(f"{' ' * (indent + 2)}<screwheight>0.0</screwheight>\n")
        file.write(f"{' ' * indent}</railbutton>\n\n")

    def writeFin(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int, suffix : str | None = None) -> None:
        if feature._obj.FinType == FIN_TYPE_TRAPEZOID:
            self.writeFinTrapezoid(file, feature, indent, suffix)
        elif feature._obj.FinType == FIN_TYPE_TRIANGLE:
            self.writeFinTrapezoid(file, feature, indent, suffix)
        elif feature._obj.FinType == FIN_TYPE_ELLIPSE:
            self.writeFinEllipse(file, feature, indent, suffix)
        elif feature._obj.FinType == FIN_TYPE_TUBE:
            self.writeFinTube(file, feature, indent, suffix)
        elif feature._obj.FinType == FIN_TYPE_SKETCH:
            self.writeFinSketch(file, feature, indent, suffix)
        else:
            print("Unknown fin type")

    def writeFinCan(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        if feature._obj.FinCanStyle == FINCAN_STYLE_SLEEVE:
            self.writeInnerTube(file, feature, indent)
            ...
        else:
            self.writeBodytube(file, feature, indent, feature)
        # self.writeFin(file, feature, indent)

    def writeFinTrapezoid(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int, suffix : str | None = None) -> None:
        file.write(f"{' ' * indent}<trapezoidfinset>\n")
        if suffix:
            file.write(f"{' ' * (indent + 2)}<name>{feature.getName()}-{suffix}</name>\n")
        else:
            file.write(f"{' ' * (indent + 2)}<name>{feature.getName()}</name>\n")
        file.write(f"{' ' * (indent + 2)}<id>{uuid.uuid4()}</id>\n")
        if feature.isFinSet():
            fins = feature.getFinCount()
        else:
            fins = 1
        file.write(f"{' ' * (indent + 2)}<instancecount>{fins}</instancecount>\n")
        file.write(f"{' ' * (indent + 2)}<fincount>{fins}</fincount>\n")
        file.write(f"{' ' * (indent + 2)}<radiusoffset method=\"{self.getRadialMethod(feature)}\">{self.toMeters(feature._obj.RadialOffset.Value)}</radiusoffset>\n")
        file.write(f"{' ' * (indent + 2)}<angleoffset method=\"relative\">{feature._obj.AngleOffset.Value}</angleoffset>\n")
        file.write(f"{' ' * (indent + 2)}<rotation>{feature._obj.AngleOffset.Value}</rotation>\n")
        file.write(f"{' ' * (indent + 2)}<axialoffset method=\"{self.getAxialMethod(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</axialoffset>\n")
        file.write(f"{' ' * (indent + 2)}<position type=\"{self.getPositionType(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</position>\n")
        # file.write(f"{' ' * (indent + 2)}<length>{self.toMeters(float(feature.getLength()))}</length>\n")
        file.write(f"{' ' * (indent + 2)}<thickness>{self.toMeters(feature.getRootThickness())}</thickness>\n")
        file.write(f"{' ' * (indent + 2)}<crosssection>{self.getCrossSection(feature)}</crosssection>\n")
        file.write(f"{' ' * (indent + 2)}<cant>{feature._obj.Cant.Value}</cant>\n")
        self.writeFinTab(file, feature, indent + 2)
        if feature._obj.Fillets:
            file.write(f"{' ' * (indent + 2)}<filletradius>{self.toMeters(feature._obj.FilletRadius.Value)}</filletradius>\n")
        else:
            file.write(f"{' ' * (indent + 2)}<filletradius>0.0</filletradius>\n")
        file.write(f"{' ' * (indent + 2)}<rootchord>{self.toMeters(feature.getRootChord())}</rootchord>\n")
        if feature._obj.FinType == FIN_TYPE_TRIANGLE:
            file.write(f"{' ' * (indent + 2)}<tipchord>0.0</tipchord>\n")
        else:
            file.write(f"{' ' * (indent + 2)}<tipchord>{self.toMeters(feature.getTipChord())}</tipchord>\n")
        file.write(f"{' ' * (indent + 2)}<sweeplength>{self.toMeters(feature.getSweepLength())}</sweeplength>\n")
        file.write(f"{' ' * (indent + 2)}<height>{self.toMeters(feature.getHeight())}</height>\n")
        self.writeSubcomponents(file, feature, indent + 2)
        file.write(f"{' ' * indent}</trapezoidfinset>\n\n")

    def writeFinEllipse(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int, suffix : str | None = None) -> None:
        file.write(f"{' ' * indent}<ellipticalfinset>\n")
        if suffix:
            file.write(f"{' ' * (indent + 2)}<name>{feature.getName()}-{suffix}</name>\n")
        else:
            file.write(f"{' ' * (indent + 2)}<name>{feature.getName()}</name>\n")
        file.write(f"{' ' * (indent + 2)}<id>{uuid.uuid4()}</id>\n")
        if feature.isFinSet():
            fins = feature.getFinCount()
        else:
            fins = 1
        file.write(f"{' ' * (indent + 2)}<instancecount>{fins}</instancecount>\n")
        file.write(f"{' ' * (indent + 2)}<fincount>{fins}</fincount>\n")
        file.write(f"{' ' * (indent + 2)}<radiusoffset method=\"{self.getRadialMethod(feature)}\">{self.toMeters(feature._obj.RadialOffset.Value)}</radiusoffset>\n")
        file.write(f"{' ' * (indent + 2)}<angleoffset method=\"relative\">{feature._obj.AngleOffset.Value}</angleoffset>\n")
        file.write(f"{' ' * (indent + 2)}<rotation>{feature._obj.AngleOffset.Value}</rotation>\n")
        file.write(f"{' ' * (indent + 2)}<axialoffset method=\"{self.getAxialMethod(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</axialoffset>\n")
        file.write(f"{' ' * (indent + 2)}<position type=\"{self.getPositionType(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</position>\n")
        # file.write(f"{' ' * (indent + 2)}<length>{self.toMeters(float(feature.getLength()))}</length>\n")
        file.write(f"{' ' * (indent + 2)}<thickness>{self.toMeters(feature.getRootThickness())}</thickness>\n")
        file.write(f"{' ' * (indent + 2)}<crosssection>{self.getCrossSection(feature)}</crosssection>\n")
        file.write(f"{' ' * (indent + 2)}<cant>{feature._obj.Cant.Value}</cant>\n")
        self.writeFinTab(file, feature, indent + 2)
        if feature._obj.Fillets:
            file.write(f"{' ' * (indent + 2)}<filletradius>{self.toMeters(feature._obj.FilletRadius.Value)}</filletradius>\n")
        else:
            file.write(f"{' ' * (indent + 2)}<filletradius>0.0</filletradius>\n")
        file.write(f"{' ' * (indent + 2)}<rootchord>{self.toMeters(feature.getRootChord())}</rootchord>\n")
        file.write(f"{' ' * (indent + 2)}<height>{self.toMeters(feature.getHeight())}</height>\n")
        self.writeSubcomponents(file, feature, indent + 2)
        file.write(f"{' ' * indent}</ellipticalfinset>\n\n")

    def writeFinTube(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int, suffix : str | None = None) -> None:
        file.write(f"{' ' * indent}<tubefinset>\n")
        if suffix:
            file.write(f"{' ' * (indent + 2)}<name>{feature.getName()}-{suffix}</name>\n")
        else:
            file.write(f"{' ' * (indent + 2)}<name>{feature.getName()}</name>\n")
        file.write(f"{' ' * (indent + 2)}<id>{uuid.uuid4()}</id>\n")
        if feature.isFinSet():
            fins = feature.getFinCount()
        else:
            fins = 1
        file.write(f"{' ' * (indent + 2)}<instancecount>{fins}</instancecount>\n")
        file.write(f"{' ' * (indent + 2)}<fincount>{fins}</fincount>\n")
        file.write(f"{' ' * (indent + 2)}<radiusoffset method=\"{self.getRadialMethod(feature)}\">{self.toMeters(feature._obj.RadialOffset.Value)}</radiusoffset>\n")
        file.write(f"{' ' * (indent + 2)}<angleoffset method=\"relative\">{feature._obj.AngleOffset.Value}</angleoffset>\n")
        file.write(f"{' ' * (indent + 2)}<rotation>{feature._obj.AngleOffset.Value}</rotation>\n")
        file.write(f"{' ' * (indent + 2)}<axialoffset method=\"{self.getAxialMethod(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</axialoffset>\n")
        file.write(f"{' ' * (indent + 2)}<position type=\"{self.getPositionType(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</position>\n")
        if feature.isTubeOuterRadiusAutomatic():
            file.write(f"{' ' * (indent + 2)}<radius>auto</radius>\n")
        else:
            file.write(f"{' ' * (indent + 2)}<radius>{feature.getTubeOuterRadius()}</radius>\n")
        file.write(f"{' ' * (indent + 2)}<length>{self.toMeters(float(feature.getLength()))}</length>\n")
        file.write(f"{' ' * (indent + 2)}<thickness>{self.toMeters(feature._obj.TubeThickness.Value)}</thickness>\n")
        self.writeSubcomponents(file, feature, indent + 2)
        file.write(f"{' ' * indent}</tubefinset>\n\n")

    def writeFinSketch(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int, suffix : str | None = None) -> None:
        file.write(f"{' ' * indent}<freeformfinset>\n")
        if suffix:
            file.write(f"{' ' * (indent + 2)}<name>{feature.getName()}-{suffix}</name>\n")
        else:
            file.write(f"{' ' * (indent + 2)}<name>{feature.getName()}</name>\n")
        file.write(f"{' ' * (indent + 2)}<id>{uuid.uuid4()}</id>\n")
        if feature.isFinSet():
            fins = feature.getFinCount()
        else:
            fins = 1
        file.write(f"{' ' * (indent + 2)}<instancecount>{fins}</instancecount>\n")
        file.write(f"{' ' * (indent + 2)}<fincount>{fins}</fincount>\n")
        file.write(f"{' ' * (indent + 2)}<radiusoffset method=\"{self.getRadialMethod(feature)}\">{self.toMeters(feature._obj.RadialOffset.Value)}</radiusoffset>\n")
        file.write(f"{' ' * (indent + 2)}<angleoffset method=\"relative\">{feature._obj.AngleOffset.Value}</angleoffset>\n")
        file.write(f"{' ' * (indent + 2)}<rotation>{feature._obj.AngleOffset.Value}</rotation>\n")
        file.write(f"{' ' * (indent + 2)}<axialoffset method=\"{self.getAxialMethod(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</axialoffset>\n")
        file.write(f"{' ' * (indent + 2)}<position type=\"{self.getPositionType(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</position>\n")
        file.write(f"{' ' * (indent + 2)}<thickness>{self.toMeters(feature.getRootThickness())}</thickness>\n")
        file.write(f"{' ' * (indent + 2)}<crosssection>{self.getCrossSection(feature)}</crosssection>\n")
        file.write(f"{' ' * (indent + 2)}<cant>{feature._obj.Cant.Value}</cant>\n")
        self.writeFinTab(file, feature, indent + 2)
        if feature._obj.Fillets:
            file.write(f"{' ' * (indent + 2)}<filletradius>{self.toMeters(feature._obj.FilletRadius.Value)}</filletradius>\n")
        else:
            file.write(f"{' ' * (indent + 2)}<filletradius>0.0</filletradius>\n")
        file.write(f"{' ' * (indent + 2)}<finpoints>\n")
        for point in self.getVertexes(feature):
            file.write(f"{' ' * (indent + 4)}<point x=\"{self.toMeters(point.Point.x)}\" y=\"{self.toMeters(point.Point.z)}\"/>\n")
        file.write(f"{' ' * (indent + 2)}</finpoints>\n")
        self.writeSubcomponents(file, feature, indent + 2)
        file.write(f"{' ' * indent}</freeformfinset>\n\n")

    def writeFinTab(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        if feature._obj.Ttw:
            file.write(f"{' ' * indent}<tabheight>{self.toMeters(feature._obj.TtwHeight.Value)}</tabheight>\n")
            file.write(f"{' ' * indent}<tablength>{self.toMeters(feature._obj.TtwLength.Value)}</tablength>\n")
            file.write(f"{' ' * indent}<tabposition relativeto=\"top\">{self.toMeters(feature._obj.TtwOffset.Value)}</tabposition>\n")

    def getVertexes(self, feature : RocketComponentShapeless) -> list:
        """Get the vertexes starting at the origin.

        Getting the vertexes from a shape can start at any point along the edge. This function ensures the
        first point is at the origin"""

        profile = feature._obj.Profile
        vertexes = profile.Shape.Vertexes
        origin = -1
        for index, point in enumerate(vertexes):
            if point.Point.x == 0 and point.Point.z == 0:
                origin = index
                break
        if origin > 0:
            vertexes = vertexes[origin:] + vertexes[:origin]
        return vertexes


    def getRadialMethod(self, feature : RocketComponentShapeless) -> str:
        method = feature._obj.RadialReference
        if method in self._locations:
            return self._locations[method]
        return "surface"

    def getAxialMethod(self, feature : RocketComponentShapeless) -> str:
        method = feature._obj.AxialMethod.getMethodName()
        if method in self._locations:
            return self._locations[method]
        return "bottom"

    def getPositionType(self, feature : RocketComponentShapeless) -> str:
        method = feature._obj.LocationReference
        if method in self._locations:
            return self._locations[method]
        return "bottom"

    def getCrossSection(self, feature : RocketComponentShapeless) -> str:
        cross = feature._obj.RootCrossSection
        if cross in self._finCrossSection:
            return self._finCrossSection[cross]
        return "rounded"
