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
            FEATURE_FIN : self.writeNull,
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
            TYPE_SPHERICAL : self.writeNoseTypeCone,
            TYPE_ELLIPTICAL : self.writeNoseTypeCone,
            TYPE_OGIVE : self.writeNoseTypeOgive,
            TYPE_BLUNTED_OGIVE : self.writeNoseTypeOgive,
            TYPE_SECANT_OGIVE : self.writeNoseTypeOgive,
            TYPE_PARABOLA : self.writeNoseTypeCone,
            TYPE_VON_KARMAN : self.writeNoseTypeCone,
            TYPE_PARABOLIC : self.writeNoseTypeCone,
            TYPE_POWER : self.writeNoseTypeCone,
            TYPE_HAACK : self.writeNoseTypeCone,
            TYPE_NIKE_SMOKE : self.writeNoseTypeCone,
            TYPE_PROXY : self.writeNoseTypeCone,
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
        file.write(f"{' ' * (indent + 2)}<shape>{feature._obj.NoseType}</shape>\n")

    def writeNoseTypeOgive(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        file.write(f"{' ' * (indent)}<length>{self.toMeters(float(feature.getLength()))}</length>\n")
        if feature._obj.NoseStyle == STYLE_SOLID:
            file.write(f"{' ' * (indent)}<thickness>filled</thickness>\n")
        else:
            file.write(f"{' ' * (indent)}<thickness>{self.toMeters(feature._obj.Thickness.Value)}</thickness>\n")
        if feature._obj.NoseType == TYPE_SECANT_OGIVE:
            file.write(f"{' ' * (indent)}<shapeparameter>{feature._obj.Coefficient}</shapeparameter>\n")
        else:
            file.write(f"{' ' * (indent)}<shapeparameter>1.0</shapeparameter>\n")
        file.write(f"{' ' * (indent)}<shape>{feature._obj.NoseType}</shape>\n")
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
        file.write(f"{' ' * indent}</bodytube>\n\n")
