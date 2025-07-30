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
from Rocket.Constants import STYLE_SOLID, STYLE_HOLLOW
from Rocket.Constants import LOCATION_PARENT_TOP, LOCATION_PARENT_MIDDLE, LOCATION_PARENT_BOTTOM, LOCATION_BASE, \
    LOCATION_AFTER, LOCATION_SURFACE, LOCATION_CENTER
from Rocket.Constants import FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_ELLIPSE, FIN_CROSS_BICONVEX, \
    FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE
from Rocket.Constants import FIN_TYPE_TRAPEZOID, FIN_TYPE_TRIANGLE, FIN_TYPE_ELLIPSE, FIN_TYPE_TUBE, FIN_TYPE_SKETCH


class OpenRocketExporter:

    def __init__(self, exportList: list[FreeCAD.DocumentObject], filename: str) -> None:
        self._exportList = exportList
        self._filename = filename

        self._feature = {
            FEATURE_ROCKET : self.writeNull,
            FEATURE_STAGE : self.writeNull,
            FEATURE_PARALLEL_STAGE : self.writeNull,
            FEATURE_BULKHEAD : self.writeNull,
            FEATURE_POD : self.writeNull,
            FEATURE_BODY_TUBE : self.writeBodytube,
            FEATURE_INNER_TUBE : self.writeNull,
            FEATURE_TUBE_COUPLER : self.writeNull,
            FEATURE_ENGINE_BLOCK : self.writeNull,
            FEATURE_CENTERING_RING : self.writeNull,
            FEATURE_FIN : self.writeFin,
            FEATURE_FINCAN : self.writeNull,
            FEATURE_NOSE_CONE : self.writeNosecone,
            FEATURE_TRANSITION : self.writeNull,
            FEATURE_LAUNCH_LUG : self.writeNull,
            FEATURE_RAIL_BUTTON : self.writeNull,
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

    def writeSubcomponents(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        if feature.hasChildren():
            file.write(f"{' ' * indent}<subcomponents>\n")
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
            print(f"Unknwon nose type {noseType}")
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
            file.write(f"{' ' * (indent)}<aftshoulderthickness>{self.toMeters(feature._obj.ShoulderLength.Value)}</aftshoulderthickness>\n")
            if feature._obj.NoseStyle != STYLE_HOLLOW:
                file.write(f"{' ' * (indent)}<aftshouldercapped>true</aftshouldercapped>\n")
            else:
                file.write(f"{' ' * (indent)}<aftshouldercapped>false</aftshouldercapped>\n")

    def writeBodytube(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        file.write(f"{' ' * indent}<bodytube>\n")
        file.write(f"{' ' * (indent + 2)}<name>{feature.getName()}</name>\n")
        file.write(f"{' ' * (indent + 2)}<id>{uuid.uuid4()}</id>\n")
        file.write(f"{' ' * (indent + 2)}<length>{self.toMeters(float(feature.getLength()))}</length>\n")
        file.write(f"{' ' * (indent + 2)}<thickness>{self.toMeters(feature._obj.Thickness.Value)}</thickness>\n")
        if feature.isOuterRadiusAutomatic():
            file.write(f"{' ' * (indent + 2)}<radius>auto {self.toMeters(float(feature.getForeRadius()))}</radius>\n")
        else:
            file.write(f"{' ' * (indent + 2)}<radius>{self.toMeters(float(feature.getForeRadius()))}</radius>\n")
        self.writeSubcomponents(file, feature, indent + 2)
        file.write(f"{' ' * indent}</bodytube>\n\n")

    def writeFin(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        if feature._obj.FinType == FIN_TYPE_TRAPEZOID:
            self.writeFinTrapezoid(file, feature, indent)
        elif feature._obj.FinType == FIN_TYPE_TRIANGLE:
            self.writeFinTrapezoid(file, feature, indent)
        elif feature._obj.FinType == FIN_TYPE_ELLIPSE:
            pass
        elif feature._obj.FinType == FIN_TYPE_TUBE:
            pass
        elif feature._obj.FinType == FIN_TYPE_SKETCH:
            pass

    def writeFinTrapezoid(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        file.write(f"{' ' * indent}<trapezoidfinset>\n")
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
        file.write(f"{' ' * (indent + 2)}<position type=\"{self.getPositionType(feature)}\">{self.toMeters(feature._obj.Position._x)}</position>\n")
        # file.write(f"{' ' * (indent + 2)}<length>{self.toMeters(float(feature.getLength()))}</length>\n")
        file.write(f"{' ' * (indent + 2)}<thickness>{self.toMeters(feature.getRootThickness())}</thickness>\n")
        file.write(f"{' ' * (indent + 2)}<crosssection>{self.getCrossSection(feature)}</crosssection>\n")
        file.write(f"{' ' * (indent + 2)}<cant>{feature._obj.Cant.Value}</cant>\n")
        file.write(f"{' ' * (indent + 2)}<filletradius>{self.toMeters(feature._obj.FilletRadius.Value)}</filletradius>\n")
        file.write(f"{' ' * (indent + 2)}<rootchord>{self.toMeters(feature.getRootChord())}</rootchord>\n")
        file.write(f"{' ' * (indent + 2)}<tipchord>{self.toMeters(feature.getTipChord())}</tipchord>\n")
        file.write(f"{' ' * (indent + 2)}<sweeplength>{self.toMeters(feature.getSweepLength())}</sweeplength>\n")
        file.write(f"{' ' * (indent + 2)}<height>{self.toMeters(feature.getHeight())}</height>\n")
        self.writeSubcomponents(file, feature, indent + 2)
        file.write(f"{' ' * indent}</trapezoidfinset>\n\n")

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

"""
              <trapezoidfinset>
                <name>Trapezoidal fin set</name>
                <id>9acd3480-76fb-4d48-b203-ce394d8c3d8e</id>
                <instancecount>3</instancecount>
                <fincount>3</fincount>
                <radiusoffset method="surface">0.0</radiusoffset>
                <angleoffset method="relative">0.0</angleoffset>
                <rotation>0.0</rotation>
                <axialoffset method="bottom">0.0</axialoffset>
                <position type="bottom">0.0</position>
                <finish>normal</finish>
                <material type="bulk" density="680.0" group="PaperProducts">Cardboard</material>
                <thickness>0.002</thickness>
                <crosssection>rounded</crosssection>
                <cant>0.0</cant>
                <filletradius>0.0</filletradius>
                <filletmaterial type="bulk" density="680.0" group="PaperProducts">Cardboard</filletmaterial>
                <rootchord>0.0508</rootchord>
                <tipchord>0.0508</tipchord>
                <sweeplength>0.0254</sweeplength>
                <height>0.03</height>
              </trapezoidfinset>
"""
