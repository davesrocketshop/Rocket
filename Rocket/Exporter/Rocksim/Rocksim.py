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
"""Provides support for exporting Rocksim files."""

__title__ = "FreeCAD Rocksim Exporter"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import io
import uuid
from typing import Any
import zipfile

import FreeCAD

translate = FreeCAD.Qt.translate

from Rocket.RocketComponentShapeless import RocketComponentShapeless
from Rocket.FeatureRocket import FeatureRocket
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

from Rocket.Utilities import _err

class RocksimExporter:

    def __init__(self, exportList: list[FreeCAD.DocumentObject], filename: str) -> None:
        self._exportList = exportList
        self._filename = filename

        self._feature = {
            FEATURE_ROCKET : self.writeNull,
            FEATURE_STAGE : self.writeNull,
            FEATURE_PARALLEL_STAGE : self.writeNull,
            FEATURE_BULKHEAD : self.writeNull,
            FEATURE_POD : self.writeNull,
            FEATURE_BODY_TUBE : self.writeNull,
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
        # self._feature = {
        #     FEATURE_ROCKET : self.writeNull,
        #     FEATURE_STAGE : self.writeNull,
        #     FEATURE_PARALLEL_STAGE : self.writeNull,
        #     FEATURE_BULKHEAD : self.writeBulkhead,
        #     FEATURE_POD : self.writeNull,
        #     FEATURE_BODY_TUBE : self.writeBodytube,
        #     FEATURE_INNER_TUBE : self.writeInnerTube,
        #     FEATURE_TUBE_COUPLER : self.writeTubeCoupler,
        #     FEATURE_ENGINE_BLOCK : self.writeEngineBlock,
        #     FEATURE_CENTERING_RING : self.writeCenteringRing,
        #     FEATURE_FIN : self.writeFin,
        #     FEATURE_FINCAN : self.writeFinCan,
        #     FEATURE_NOSE_CONE : self.writeNosecone,
        #     FEATURE_TRANSITION : self.writeTransition,
        #     FEATURE_LAUNCH_LUG : self.writeLaunchLug,
        #     FEATURE_RAIL_BUTTON : self.writeRailButton,
        #     FEATURE_RAIL_GUIDE : self.writeNull,
        #     FEATURE_OFFSET : self.writeNull,
        #     FEATURE_RINGTAIL : self.writeNull,
        # }

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

    def _getRocket(self, obj : FreeCAD.DocumentObject) -> FeatureRocket:
        proxy = self.getProxy(obj)
        if not hasattr(proxy, "Type"):
            return None
        if proxy.Type == FEATURE_ROCKET:
            return proxy
        rocket = None
        if hasattr(proxy, "getRocket"):
            rocket = proxy.getRocket()
        return rocket

    def export(self) -> None:
        entry = self._exportList[0]

        # Ensure we have a rocket selected
        rocket = self._getRocket(entry)
        if not rocket:
            _err(translate("Rocket", "Please select a rocket object"))
            if FreeCAD.GuiUp:
                from PySide import QtGui
                QtGui.QMessageBox.information(None, "", translate("Rocket", "Please select a rocket object"))
            return

        name=entry.Document.Name
        with open(self._filename, "w") as file:
            self.write(file, f"""<RockSimDocument>
  <FileVersion>4</FileVersion>
  <DesignInformation>
    <RocketDesign>
      <CalculateCD>1</CalculateCD>
      <ProCalculateCD>1</ProCalculateCD>
      <ProCalculateCN>1</ProCalculateCN>
      <FixedCd>0.75</FixedCd>
      <FixedCd2>0.8</FixedCd2>
      <FixedCd3>0.81</FixedCd3>
      <FixedCd2Alone>0.95</FixedCd2Alone>
      <FixedCd3Alone>0.95</FixedCd3Alone>
""")
            self.writeStages(file, rocket)
            self.write(file, """<SideViewDims>
</SideViewDims>
<BaseViewDims>
</BaseViewDims>
<VertViewDims>
</VertViewDims>
</RocketDesign>
</DesignInformation>
<SimulationResultsList>
</SimulationResultsList>
</RockSimDocument>
""")

    def writeStages(self, file : io.TextIOBase, rocket : FeatureRocket) -> None:
        stages = rocket.getStageCount()
        self.write(file, f"      <StageCount>{stages}</StageCount>")
        self.write(file, """<Stage3Mass>0.</Stage3Mass>
      <Stage2Mass>0.</Stage2Mass>
      <Stage1Mass>0.</Stage1Mass>
      <Stage321CG>0.</Stage321CG>
      <Stage32CG>0.</Stage32CG>
      <Stage3CG>0.</Stage3CG>
      <Stage2CGAlone>0.</Stage2CGAlone>
      <Stage1CGAlone>0.</Stage1CGAlone>
      <CPCalcFlags>4</CPCalcFlags>
      <LaunchGuideLength>914.4</LaunchGuideLength>
      <UseKnownMass>0</UseKnownMass>
      <DefaultFinish>0</DefaultFinish>
      <FinishMedium>0</FinishMedium>
      <FinishCoatCount>1</FinishCoatCount>
      <GlueType>0</GlueType>
      <CPSimFlags>4</CPSimFlags>
      <LastSerialNumber>1</LastSerialNumber>
      <DisplayFlags>1</DisplayFlags>
      <MetricsFlags>0</MetricsFlags>
      <BarromanXN>0,23.2573,0,0</BarromanXN>
      <BarrowmanCNa>0,2,0,0</BarrowmanCNa>
      <RockSimXN>0,23.2573,0,0</RockSimXN>
      <RockSimCNa>0,2,0,0</RockSimCNa>
      <RockSimCNa90>0,0,0,0</RockSimCNa90>
      <RockSimXN90>0,0,0,0</RockSimXN90>
      <ViewType>0</ViewType>
      <ViewStageCount>1</ViewStageCount>
      <ViewTypeEdit>0</ViewTypeEdit>
      <ViewStageCountEdit>1</ViewStageCountEdit>
      <ZoomFactor>0.</ZoomFactor>
      <ZoomFactorEdit>0.</ZoomFactorEdit>
      <ScrollPosX>0</ScrollPosX>
      <ScrollPosY>0</ScrollPosY>
      <ScrollPosXEdit>0</ScrollPosXEdit>
      <ScrollPosYEdit>0</ScrollPosYEdit>
      <ThreeDFlags>0</ThreeDFlags>
      <ThreeDFlagsEdit>0</ThreeDFlagsEdit>
      <UseModelSprite>0</UseModelSprite>
      <StaticMarginRef>0</StaticMarginRef>
      <UserRefDiameter>0.</UserRefDiameter>
      <SideMarkerHeight>10.</SideMarkerHeight>
      <SideDimensionHeight>10.</SideDimensionHeight>
      <BaseMarkerHeight>10.</BaseMarkerHeight>
      <BaseDimensionHeight>10.</BaseDimensionHeight>
      <ShowGlideCP>0</ShowGlideCP>
      <ShowGridTypeSide>0</ShowGridTypeSide>
      <ShowGridTypeBase>0</ShowGridTypeBase>
      <GridSpacing>10.</GridSpacing>
      <GridOpacity>0.15</GridOpacity>
      <GridColor>black</GridColor>
      <MaxDiaWithFins>10.</MaxDiaWithFins>
      <MaxDiaWithoutFins>10.</MaxDiaWithoutFins>
      <MaxLenWithFins>50.</MaxLenWithFins>
      <MaxLenWithoutFins>50.</MaxLenWithoutFins>
      <MinXExtent>0.</MinXExtent>
      <MaxXExtent>50.</MaxXExtent>
      <CalculatedMaxStageDia>0,10,0,0</CalculatedMaxStageDia>
      <CalculatedStageLen>0,50,0,0</CalculatedStageLen>
      <Cd3>
        <PolyData  useXYOnly="0" useSmoothCurveEvaluation="0" count="0">
        <X-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</X-data>
        <A-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</A-data>
        <B-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</B-data>
        <C-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</C-data>
      </PolyData>
    </Cd3>
    <Cd32>
      <PolyData  useXYOnly="0" useSmoothCurveEvaluation="0" count="0">
      <X-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</X-data>
      <A-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</A-data>
      <B-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</B-data>
      <C-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</C-data>
    </PolyData>
  </Cd32>
  <Cd321>
    <PolyData  useXYOnly="0" useSmoothCurveEvaluation="0" count="0">
    <X-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</X-data>
    <A-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</A-data>
    <B-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</B-data>
    <C-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</C-data>
  </PolyData>
</Cd321>
<Cb3>
  <PolyData  useXYOnly="1" useSmoothCurveEvaluation="0" count="0">
  <X-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</X-data>
  <A-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</A-data>
  <B-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</B-data>
  <C-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</C-data>
</PolyData>
</Cb3>
<Cb32>
<PolyData  useXYOnly="1" useSmoothCurveEvaluation="0" count="0">
<X-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</X-data>
<A-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</A-data>
<B-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</B-data>
<C-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</C-data>
</PolyData>
</Cb32>
<Cb321>
<PolyData  useXYOnly="1" useSmoothCurveEvaluation="0" count="0">
<X-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</X-data>
<A-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</A-data>
<B-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</B-data>
<C-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</C-data>
</PolyData>
</Cb321>
<CNa3>
<PolyData  useXYOnly="0" useSmoothCurveEvaluation="0" count="0">
<X-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</X-data>
<A-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</A-data>
<B-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</B-data>
<C-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</C-data>
</PolyData>
</CNa3>
<CNa32>
<PolyData  useXYOnly="0" useSmoothCurveEvaluation="0" count="0">
<X-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</X-data>
<A-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</A-data>
<B-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</B-data>
<C-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</C-data>
</PolyData>
</CNa32>
<CNa321>
<PolyData  useXYOnly="0" useSmoothCurveEvaluation="0" count="0">
<X-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</X-data>
<A-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</A-data>
<B-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</B-data>
<C-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</C-data>
</PolyData>
</CNa321>
<CP3>
<PolyData  useXYOnly="0" useSmoothCurveEvaluation="0" count="0">
<X-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</X-data>
<A-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</A-data>
<B-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</B-data>
<C-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</C-data>
</PolyData>
</CP3>
<CP32>
<PolyData  useXYOnly="0" useSmoothCurveEvaluation="0" count="0">
<X-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</X-data>
<A-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</A-data>
<B-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</B-data>
<C-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</C-data>
</PolyData>
</CP32>
<CP321>
<PolyData  useXYOnly="0" useSmoothCurveEvaluation="0" count="0">
<X-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</X-data>
<A-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</A-data>
<B-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</B-data>
<C-data>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</C-data>
</PolyData>
</CP321>
<SimulationEventList>
</SimulationEventList>
""")
        for child in rocket.getChildren():
            childProxy = self.getProxy(child)
            if isinstance(childProxy, FeatureStage):
                self.writeStage(file, childProxy)
        if stages < 3:
            for i in range(1, 4 - stages):
                self.write(file, f"<Stage{i}Parts>\n")
                self.write(file, f"</Stage{i}Parts>\n")

    def write(self, file : io.TextIOBase, string : str) -> None:
        # file.write(string.encode('utf-8'))
        file.write(string)

    def writeStage(self, file : io.TextIOBase, feature : RocketComponentShapeless):
        stageNumber = 3 - feature.getStageNumber()
        if stageNumber <= 3 and stageNumber > 0:
            # stageName = feature.getName()
            self.write(file, f"<Stage{stageNumber}Parts>\n")
            indent = 0
            self.writeSubcomponents(file, feature, indent)
            self.write(file, f"</Stage{stageNumber}Parts>\n")

    def getProxy(self, obj : Any) -> RocketComponentShapeless:
        if hasattr(obj, "Proxy"):
            return obj.Proxy
        return obj

    def toMeters(self, mm : float) -> float:
        return mm / 1000.0

    def writeSubcomponents(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int, extra : RocketComponentShapeless | None = None) -> None:
        if feature.hasChildren() or extra:
            # self.write(file, f"{' ' * indent}<subcomponents>\n")
            # if extra:
            #     type = extra.getType()
            #     if type == FEATURE_FINCAN:
            #         type = FEATURE_FIN # Avoid recursion
            #         if type in self._feature:
            #             self._feature[type](file, extra, indent + 2, "fin")
            #         if extra._obj.LaunchLug:
            #             type = FEATURE_LAUNCH_LUG
            #         if type in self._feature:
            #             self._feature[type](file, extra, indent + 2, "lug")
            for child in feature.getChildren():
                childProxy = self.getProxy(child)
                type = childProxy.getType()
                if type in self._feature:
                    self._feature[type](file, childProxy, indent)
                else:
                    print(f"Unknown feature {type}")
            # self.write(file, f"{' ' * indent}</subcomponents>\n")

    def writeAppearance(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int, finish : bool = True) -> None:
        appearance = None
        try:
            appearance = feature._obj.ViewObject.ShapeAppearance[0]
        except Exception:
            # No appearance available
            return

        self.write(file, f"{' ' * indent}<appearance>\n")
        color = appearance.DiffuseColor
        red = round(color[0] * 255.0)
        green = round(color[1] * 255.0)
        blue = round(color[2] * 255.0)
        alpha = round(color[3] * 255.0)
        self.write(file, f"{' ' * (indent + 2)}<paint red=\"{red}\" green=\"{green}\" blue=\"{blue}\" alpha=\"{alpha}\"/>\n")
        self.write(file, f"{' ' * (indent + 2)}<shine>{appearance.Shininess}</shine>\n")
        self.write(file, f"{' ' * indent}</appearance>\n\n")
        if finish:
            self.write(file, f"{' ' * indent}<finish>polished</finish>\n\n")

    def writeNull(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        pass

    def isEmpty(self, string : str) -> bool:
        """
        Checks if a string is empty or contains only whitespace characters.
        """
        return not string or string.isspace()

    def writeNosecone(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        manufacturer = feature._obj.Manufacturer
        if self.isEmpty(manufacturer):
            manufacturer = "Custom"
        self.write(file, "<NoseCone>\n")
        self.write(file, f"<PartMfg>{manufacturer}</PartMfg>\n")
        self.write(file, "<KnownMass>0.</KnownMass>\n")
        self.write(file, "<Density>128.148</Density>\n")
        self.write(file, "<Material>Balsa</Material>\n")
        self.write(file, f"<Name>{feature.getName()}</Name>\n")
        self.write(file, """<KnownCG>0.</KnownCG>
<UseKnownCG>0</UseKnownCG>
<Xb>0.</Xb>
""")
        self.write(file, """<RadialLoc>0.</RadialLoc>
<RadialAngle>0.</RadialAngle>
<Texture>file=()|position=(0,0,0)|origin=(0.5,0.5,0.5)|scale=(1,1,1)|repeat=(1)|interpolate=(0)|flipr=(0)|flips=(0)|flipt=(0)|preventseam=(1)|rotate=(0)</Texture>
<Opacity>1.</Opacity>
<Specular>0.</Specular>
<SpecularPower>1.</SpecularPower>
<Ambient>0.</Ambient>
<Diffuse>1.</Diffuse>
<AbientColor>blue</AbientColor>
<DiffuseColor>blue</DiffuseColor>
<SpecularColor>white</SpecularColor>
<UseSingleColor>1</UseSingleColor>
<SerialNo>1</SerialNo>
<DisplayFlags>0</DisplayFlags>
<MetricsFlags>0</MetricsFlags>
<LocationMode>0</LocationMode>
<Color>blue</Color>
<BarrowmanCNa>2.</BarrowmanCNa>
<BarrowmanXN>0.0232573</BarrowmanXN>
<RockSimCNa>2.</RockSimCNa>
<RockSimXN>0.0232573</RockSimXN>
<SimpleColorModel>1</SimpleColorModel>
<ProduceTemplate>0</ProduceTemplate>
<TemplateUnits>8</TemplateUnits>
<Removed>0</Removed>
<Station>0.</Station>
<Len>50.</Len>
<BaseDia>10.</BaseDia>
<FinishCode>0</FinishCode>
<ShapeCode>1</ShapeCode>
<ConstructionType>0</ConstructionType>
<ShoulderLen>0.</ShoulderLen>
<WallThickness>0.</WallThickness>
<ShapeParameter>0.</ShapeParameter>
<ShoulderOD>0.</ShoulderOD>
<BaseExtensionLen>0.</BaseExtensionLen>
<CoreDia>0.</CoreDia>
<CoreLen>0.</CoreLen>
<AttachedParts>
</AttachedParts>
</NoseCone>
""")
        # self.write(file, f"{' ' * indent}<nosecone>\n")
        # self.write(file, f"{' ' * (indent + 2)}<name>{feature.getName()}</name>\n")
        # self.write(file, f"{' ' * (indent + 2)}<id>{uuid.uuid4()}</id>\n")
        # self.writeAppearance(file, feature, indent+2)
        # if len(feature._obj.Comment) > 0:
        #     self.write(file, f"{' ' * (indent + 2)}<comment>{feature._obj.Comment}</comment>\n")
        # noseType = feature._obj.NoseType
        # if noseType in self._noseTypes:
        #     self._noseTypes[noseType](file, feature, indent + 2)
        # else:
        #     print(f"Unknown nose type {noseType}")
        # self.write(file, f"{' ' * indent}</nosecone>\n\n")

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
        self.write(file, f"{' ' * (indent)}<length>{self.toMeters(float(feature.getLength()))}</length>\n")
        if feature._obj.NoseStyle == STYLE_SOLID:
            self.write(file, f"{' ' * (indent)}<thickness>filled</thickness>\n")
        else:
            self.write(file, f"{' ' * (indent)}<thickness>{self.toMeters(feature._obj.Thickness.Value)}</thickness>\n")
        if feature._obj.NoseType in [TYPE_SECANT_OGIVE, TYPE_POWER, TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_HAACK, TYPE_VON_KARMAN]:
            self.write(file, f"{' ' * (indent)}<shapeparameter>{feature._obj.Coefficient}</shapeparameter>\n")
        else:
            self.write(file, f"{' ' * (indent)}<shapeparameter>1.0</shapeparameter>\n")
        self.write(file, f"{' ' * (indent)}<shape>{shape}</shape>\n")
        # <shapeclipped>false</shapeclipped>
        self.write(file, f"{' ' * (indent)}<aftradius>{self.toMeters(float(feature.getAftRadius()))}</aftradius>\n")
        self.writeNoseShoulder(file, feature, indent)
        self.write(file, f"{' ' * (indent)}<isflipped>false</isflipped>\n")

    def writeNoseShoulder(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        if feature._obj.Shoulder:
            self.write(file, f"{' ' * (indent)}<aftshoulderradius>{self.toMeters(float(feature.getAftShoulderRadius()))}</aftshoulderradius>\n")
            self.write(file, f"{' ' * (indent)}<aftshoulderlength>{self.toMeters(feature._obj.ShoulderLength.Value)}</aftshoulderlength>\n")
            self.write(file, f"{' ' * (indent)}<aftshoulderthickness>{self.toMeters(feature._obj.ShoulderThickness.Value)}</aftshoulderthickness>\n")
            if feature._obj.NoseStyle != STYLE_HOLLOW:
                self.write(file, f"{' ' * (indent)}<aftshouldercapped>true</aftshouldercapped>\n")
            else:
                self.write(file, f"{' ' * (indent)}<aftshouldercapped>false</aftshouldercapped>\n")

    def writeTransition(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        self.write(file, f"{' ' * indent}<transition>\n")
        self.write(file, f"{' ' * (indent + 2)}<name>{feature.getName()}</name>\n")
        self.write(file, f"{' ' * (indent + 2)}<id>{uuid.uuid4()}</id>\n")
        self.writeAppearance(file, feature, indent+2)
        if len(feature._obj.Comment) > 0:
            self.write(file, f"{' ' * (indent + 2)}<comment>{feature._obj.Comment}</comment>\n")
        transitionType = feature._obj.TransitionType
        if transitionType in self._transitionTypes:
            self._transitionTypes[transitionType](file, feature, indent + 2)
        else:
            print(f"Unknown nose type {transitionType}")
        self.write(file, f"{' ' * indent}</transition>\n\n")

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
        self.write(file, f"{' ' * (indent)}<length>{self.toMeters(float(feature.getLength()))}</length>\n")
        if feature._obj.TransitionStyle == STYLE_SOLID:
            self.write(file, f"{' ' * (indent)}<thickness>filled</thickness>\n")
        else:
            self.write(file, f"{' ' * (indent)}<thickness>{self.toMeters(feature._obj.Thickness.Value)}</thickness>\n")
        self.write(file, f"{' ' * (indent)}<shape>{shape}</shape>\n")
        if feature._obj.TransitionType in [TYPE_ELLIPTICAL, TYPE_POWER, TYPE_PARABOLA, TYPE_HAACK, TYPE_VON_KARMAN]:
            if feature._obj.Clipped:
                self.write(file, f"{' ' * (indent)}<shapeclipped>true</shapeclipped>\n")
            else:
                self.write(file, f"{' ' * (indent)}<shapeclipped>false</shapeclipped>\n")
        if feature._obj.TransitionType in [TYPE_SECANT_OGIVE, TYPE_POWER, TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_HAACK, TYPE_VON_KARMAN]:
            self.write(file, f"{' ' * (indent)}<shapeparameter>{feature._obj.Coefficient}</shapeparameter>\n")
        elif feature._obj.TransitionType in [TYPE_OGIVE, TYPE_BLUNTED_OGIVE]:
            self.write(file, f"{' ' * (indent)}<shapeparameter>1.0</shapeparameter>\n")
        if feature.isForeRadiusAutomatic():
            self.write(file, f"{' ' * (indent)}<foreradius>auto {self.toMeters(float(feature.getForeRadius()))}</foreradius>\n")
        else:
            self.write(file, f"{' ' * (indent)}<foreradius>{self.toMeters(float(feature.getForeRadius()))}</foreradius>\n")
        if feature.isAftRadiusAutomatic():
            self.write(file, f"{' ' * (indent)}<aftradius>auto {self.toMeters(float(feature.getAftRadius()))}</aftradius>\n")
        else:
            self.write(file, f"{' ' * (indent)}<aftradius>{self.toMeters(float(feature.getAftRadius()))}</aftradius>\n")
        self.writeTransitionForeShoulder(file, feature, indent)
        self.writeTransitionAftShoulder(file, feature, indent)

    def writeTransitionForeShoulder(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        if feature._obj.ForeShoulder:
            self.write(file, f"{' ' * (indent)}<foreshoulderradius>{self.toMeters(feature.getForeShoulderRadius())}</foreshoulderradius>\n")
            self.write(file, f"{' ' * (indent)}<foreshoulderlength>{self.toMeters(feature._obj.ForeShoulderLength.Value)}</foreshoulderlength>\n")
            self.write(file, f"{' ' * (indent)}<foreshoulderthickness>{self.toMeters(feature._obj.ForeShoulderThickness.Value)}</foreshoulderthickness>\n")
            if feature._obj.TransitionStyle not in [STYLE_HOLLOW, STYLE_SOLID_CORE]:
                self.write(file, f"{' ' * (indent)}<foreshouldercapped>true</foreshouldercapped>\n")
            else:
                self.write(file, f"{' ' * (indent)}<foreshouldercapped>false</foreshouldercapped>\n")
        else:
            self.write(file, f"{' ' * (indent)}<foreshoulderradius>0.0</foreshoulderradius>\n")
            self.write(file, f"{' ' * (indent)}<foreshoulderlength>0.0</foreshoulderlength>\n")
            self.write(file, f"{' ' * (indent)}<foreshoulderthickness>0.0</foreshoulderthickness>\n")
            self.write(file, f"{' ' * (indent)}<foreshouldercapped>false</foreshouldercapped>\n")

    def writeTransitionAftShoulder(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        if feature._obj.AftShoulder:
            self.write(file, f"{' ' * (indent)}<aftshoulderradius>{self.toMeters(float(feature.getAftShoulderRadius()))}</aftshoulderradius>\n")
            self.write(file, f"{' ' * (indent)}<aftshoulderlength>{self.toMeters(feature._obj.AftShoulderLength.Value)}</aftshoulderlength>\n")
            self.write(file, f"{' ' * (indent)}<aftshoulderthickness>{self.toMeters(feature._obj.AftShoulderThickness.Value)}</aftshoulderthickness>\n")
            if feature._obj.TransitionStyle not in [STYLE_HOLLOW, STYLE_SOLID_CORE]:
                self.write(file, f"{' ' * (indent)}<aftshouldercapped>true</aftshouldercapped>\n")
            else:
                self.write(file, f"{' ' * (indent)}<aftshouldercapped>false</aftshouldercapped>\n")
        else:
            self.write(file, f"{' ' * (indent)}<aftshoulderradius>0.0</aftshoulderradius>\n")
            self.write(file, f"{' ' * (indent)}<aftshoulderlength>0.0</aftshoulderlength>\n")
            self.write(file, f"{' ' * (indent)}<aftshoulderthickness>0.0</aftshoulderthickness>\n")
            self.write(file, f"{' ' * (indent)}<aftshouldercapped>false</aftshouldercapped>\n")

    def writeBodytube(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int, finCan : RocketComponentShapeless | None = None) -> None:
        self.write(file, f"{' ' * indent}<bodytube>\n")
        self.write(file, f"{' ' * (indent + 2)}<name>{feature.getName()}</name>\n")
        self.write(file, f"{' ' * (indent + 2)}<id>{uuid.uuid4()}</id>\n")
        self.writeAppearance(file, feature, indent+2)
        self.write(file, f"{' ' * (indent + 2)}<length>{self.toMeters(float(feature.getLength()))}</length>\n")
        self.write(file, f"{' ' * (indent + 2)}<thickness>{self.toMeters(feature._obj.Thickness.Value)}</thickness>\n")
        if hasattr(feature, "isOuterRadiusAutomatic") and feature.isOuterRadiusAutomatic():
            self.write(file, f"{' ' * (indent + 2)}<radius>auto {self.toMeters(float(feature.getForeRadius()))}</radius>\n")
        else:
            self.write(file, f"{' ' * (indent + 2)}<radius>{self.toMeters(float(feature.getForeRadius()))}</radius>\n")
        self.writeMotorMount(file, feature, indent + 2)
        # if finCan:
        #     # Fincans aren't directly supported by OpenRocket. This is a kludge
        #     self.writeFin(file, finCan, indent + 2)
        self.writeSubcomponents(file, feature, indent + 2, finCan)
        self.write(file, f"{' ' * indent}</bodytube>\n\n")

    def writeTubeCoupler(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        self.write(file, f"{' ' * indent}<tubecoupler>\n")
        self.write(file, f"{' ' * (indent + 2)}<name>{feature.getName()}</name>\n")
        self.write(file, f"{' ' * (indent + 2)}<id>{uuid.uuid4()}</id>\n")
        self.writeAppearance(file, feature, indent+2, False)
        self.write(file, f"{' ' * (indent + 2)}<axialoffset method=\"{self.getAxialMethod(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</axialoffset>\n")
        self.write(file, f"{' ' * (indent + 2)}<position type=\"{self.getPositionType(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</position>\n")
        self.write(file, f"{' ' * (indent + 2)}<length>{self.toMeters(float(feature.getLength()))}</length>\n")
        # <radialposition>0.0</radialposition>
        # <radialdirection>0.0</radialdirection>
        if feature.isOuterRadiusAutomatic():
            self.write(file, f"{' ' * (indent + 2)}<outerradius>auto {self.toMeters(float(feature.getOuterRadius(0)))}</outerradius>\n")
        else:
            self.write(file, f"{' ' * (indent + 2)}<outerradius>{self.toMeters(float(feature.getOuterRadius(0)))}</outerradius>\n")
        self.write(file, f"{' ' * (indent + 2)}<thickness>{self.toMeters(feature._obj.Thickness.Value)}</thickness>\n")
        self.writeSubcomponents(file, feature, indent + 2)
        self.write(file, f"{' ' * indent}</tubecoupler>\n\n")

    def writeInnerTube(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        self.write(file, f"{' ' * indent}<innertube>\n")
        self.write(file, f"{' ' * (indent + 2)}<name>{feature.getName()}</name>\n")
        self.write(file, f"{' ' * (indent + 2)}<id>{uuid.uuid4()}</id>\n")
        self.writeAppearance(file, feature, indent+2, False)
        self.write(file, f"{' ' * (indent + 2)}<axialoffset method=\"{self.getAxialMethod(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</axialoffset>\n")
        self.write(file, f"{' ' * (indent + 2)}<position type=\"{self.getPositionType(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</position>\n")
        self.write(file, f"{' ' * (indent + 2)}<length>{self.toMeters(float(feature.getLength()))}</length>\n")
        # <radialposition>0.0</radialposition>
        # <radialdirection>0.0</radialdirection>
        if feature.isOuterRadiusAutomatic():
            self.write(file, f"{' ' * (indent + 2)}<outerradius>auto {self.toMeters(float(feature.getOuterRadius(0)))}</outerradius>\n")
        else:
            self.write(file, f"{' ' * (indent + 2)}<outerradius>{self.toMeters(float(feature.getOuterRadius(0)))}</outerradius>\n")
        self.write(file, f"{' ' * (indent + 2)}<thickness>{self.toMeters(feature._obj.Thickness.Value)}</thickness>\n")
        self.writeMotorMount(file, feature, indent + 2)
        self.writeSubcomponents(file, feature, indent + 2)
        self.write(file, f"{' ' * indent}</innertube>\n\n")

    def writeMotorMount(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        if feature.isMotorMount():
            self.write(file, f"{' ' * indent}<motormount>\n")
            self.write(file, f"{' ' * (indent + 2)}<ignitionevent>automatic</ignitionevent>\n")
            self.write(file, f"{' ' * (indent + 2)}<ignitiondelay>0.0</ignitiondelay>\n")
            self.write(file, f"{' ' * (indent + 2)}<overhang>{self.toMeters(feature._obj.Overhang.Value)}</overhang>\n")
            self.write(file, f"{' ' * indent}</motormount>\n\n")

    def writeBulkhead(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        self.write(file, f"{' ' * indent}<bulkhead>\n")
        self.write(file, f"{' ' * (indent + 2)}<name>{feature.getName()}</name>\n")
        self.write(file, f"{' ' * (indent + 2)}<id>{uuid.uuid4()}</id>\n")
        self.writeAppearance(file, feature, indent+2, False)
        self.write(file, f"{' ' * (indent + 2)}<instancecount>1</instancecount>\n")
        self.write(file, f"{' ' * (indent + 2)}<instanceseparation>0</instanceseparation>\n")
        self.write(file, f"{' ' * (indent + 2)}<axialoffset method=\"{self.getAxialMethod(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</axialoffset>\n")
        self.write(file, f"{' ' * (indent + 2)}<position type=\"{self.getPositionType(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</position>\n")
        self.write(file, f"{' ' * (indent + 2)}<length>{self.toMeters(float(feature.getLength()))}</length>\n")
        # <radialposition>0.0</radialposition>
        # <radialdirection>0.0</radialdirection>
        if feature.isOuterRadiusAutomatic():
            self.write(file, f"{' ' * (indent + 2)}<outerradius>auto {self.toMeters(float(feature.getOuterRadius(0)))}</outerradius>\n")
        else:
            self.write(file, f"{' ' * (indent + 2)}<outerradius>{self.toMeters(float(feature.getOuterRadius(0)))}</outerradius>\n")
        self.write(file, f"{' ' * indent}</bulkhead>\n\n")

    def writeCenteringRing(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        self.write(file, f"{' ' * indent}<centeringring>\n")
        self.write(file, f"{' ' * (indent + 2)}<name>{feature.getName()}</name>\n")
        self.write(file, f"{' ' * (indent + 2)}<id>{uuid.uuid4()}</id>\n")
        self.writeAppearance(file, feature, indent+2, False)
        self.write(file, f"{' ' * (indent + 2)}<instancecount>1</instancecount>\n")
        self.write(file, f"{' ' * (indent + 2)}<instanceseparation>0</instanceseparation>\n")
        self.write(file, f"{' ' * (indent + 2)}<axialoffset method=\"{self.getAxialMethod(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</axialoffset>\n")
        self.write(file, f"{' ' * (indent + 2)}<position type=\"{self.getPositionType(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</position>\n")
        self.write(file, f"{' ' * (indent + 2)}<length>{self.toMeters(float(feature.getLength()))}</length>\n")
        # <radialposition>0.0</radialposition>
        # <radialdirection>0.0</radialdirection>
        if feature.isOuterRadiusAutomatic():
            self.write(file, f"{' ' * (indent + 2)}<outerradius>auto</outerradius>\n")
        else:
            self.write(file, f"{' ' * (indent + 2)}<outerradius>{self.toMeters(float(feature.getOuterRadius(0)))}</outerradius>\n")
        if feature.isInnerRadiusAutomatic():
            self.write(file, f"{' ' * (indent + 2)}<innerradius>auto</innerradius>\n")
        else:
            self.write(file, f"{' ' * (indent + 2)}<innerradius>{self.toMeters(float(feature.getInnerRadius(0)))}</innerradius>\n")
        self.write(file, f"{' ' * indent}</centeringring>\n\n")

    def writeEngineBlock(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        self.write(file, f"{' ' * indent}<engineblock>\n")
        self.write(file, f"{' ' * (indent + 2)}<name>{feature.getName()}</name>\n")
        self.write(file, f"{' ' * (indent + 2)}<id>{uuid.uuid4()}</id>\n")
        self.writeAppearance(file, feature, indent+2, False)
        self.write(file, f"{' ' * (indent + 2)}<axialoffset method=\"{self.getAxialMethod(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</axialoffset>\n")
        self.write(file, f"{' ' * (indent + 2)}<position type=\"{self.getPositionType(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</position>\n")
        self.write(file, f"{' ' * (indent + 2)}<length>{self.toMeters(float(feature.getLength()))}</length>\n")
        if feature.isOuterRadiusAutomatic():
            self.write(file, f"{' ' * (indent + 2)}<outerradius>auto</outerradius>\n")
        else:
            self.write(file, f"{' ' * (indent + 2)}<outerradius>{self.toMeters(float(feature.getOuterRadius(0)))}</outerradius>\n")
        self.write(file, f"{' ' * (indent + 2)}<thickness>{self.toMeters(float(feature.getThickness()))}</thickness>\n")
        self.write(file, f"{' ' * indent}</engineblock>\n\n")

    def writeLaunchLug(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int, suffix : str | None = None) -> None:
        self.write(file, f"{' ' * indent}<launchlug>\n")
        if suffix:
            self.write(file, f"{' ' * (indent + 2)}<name>{feature.getName()}-{suffix}</name>\n")
        else:
            self.write(file, f"{' ' * (indent + 2)}<name>{feature.getName()}</name>\n")
        self.write(file, f"{' ' * (indent + 2)}<id>{uuid.uuid4()}</id>\n")
        self.writeAppearance(file, feature, indent+2, False)
        if hasattr(feature, "getInstanceCount"):
            self.write(file, f"{' ' * (indent + 2)}<instancecount>{feature.getInstanceCount()}</instancecount>\n")
            self.write(file, f"{' ' * (indent + 2)}<instanceseparation>{feature.getInstanceSeparation()}</instanceseparation>\n")
        if feature.getType() == FEATURE_FINCAN:
            offset = float(feature._obj.FinSpacing) / 2.0
            self.write(file, f"{' ' * (indent + 2)}<angleoffset method=\"relative\">{-offset}</angleoffset>\n")
            self.write(file, f"{' ' * (indent + 2)}<radialdirection>{-offset}</radialdirection>\n")
            self.write(file, f"{' ' * (indent + 2)}<axialoffset method=\"{self.getAxialMethod(feature)}\">{self.toMeters(feature._obj.LugLeadingEdgeOffset.Value)}</axialoffset>\n")
            self.write(file, f"{' ' * (indent + 2)}<position type=\"top\">{self.toMeters(feature._obj.LugLeadingEdgeOffset.Value)}</position>\n")
            self.write(file, f"{' ' * (indent + 2)}<radius>{self.toMeters(float(feature._obj.LugInnerDiameter) / 2.0 + float(feature._obj.LugThickness))}</radius>\n")
            self.write(file, f"{' ' * (indent + 2)}<length>{self.toMeters(float(feature._obj.LugLength))}</length>\n")
            self.write(file, f"{' ' * (indent + 2)}<thickness>{self.toMeters(float(feature._obj.LugThickness))}</thickness>\n")
        else:
            self.write(file, f"{' ' * (indent + 2)}<angleoffset method=\"relative\">{feature._obj.AngleOffset.Value}</angleoffset>\n")
            self.write(file, f"{' ' * (indent + 2)}<radialdirection>{feature._obj.AngleOffset.Value}</radialdirection>\n")
            self.write(file, f"{' ' * (indent + 2)}<axialoffset method=\"{self.getAxialMethod(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</axialoffset>\n")
            self.write(file, f"{' ' * (indent + 2)}<position type=\"{self.getPositionType(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</position>\n")
            self.write(file, f"{' ' * (indent + 2)}<radius>{self.toMeters(float(feature.getOuterRadius(0)))}</radius>\n")
            self.write(file, f"{' ' * (indent + 2)}<length>{self.toMeters(float(feature.getLength()))}</length>\n")
            self.write(file, f"{' ' * (indent + 2)}<thickness>{self.toMeters(feature._obj.Thickness.Value)}</thickness>\n")
        self.write(file, f"{' ' * indent}</launchlug>\n\n")

    def writeRailButton(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        self.write(file, f"{' ' * indent}<railbutton>\n")
        self.write(file, f"{' ' * (indent + 2)}<name>{feature.getName()}</name>\n")
        self.write(file, f"{' ' * (indent + 2)}<id>{uuid.uuid4()}</id>\n")
        self.writeAppearance(file, feature, indent+2, False)
        self.write(file, f"{' ' * (indent + 2)}<instancecount>{feature.getInstanceCount()}</instancecount>\n")
        self.write(file, f"{' ' * (indent + 2)}<instanceseparation>{feature.getInstanceSeparation()}</instanceseparation>\n")
        self.write(file, f"{' ' * (indent + 2)}<angleoffset method=\"relative\">{feature._obj.AngleOffset.Value}</angleoffset>\n")
        self.write(file, f"{' ' * (indent + 2)}<axialoffset method=\"{self.getAxialMethod(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</axialoffset>\n")
        self.write(file, f"{' ' * (indent + 2)}<position type=\"{self.getPositionType(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</position>\n")
        self.write(file, f"{' ' * (indent + 2)}<outerdiameter>{self.toMeters(feature._obj.Diameter.Value)}</outerdiameter>\n")
        self.write(file, f"{' ' * (indent + 2)}<innerdiameter>{self.toMeters(feature._obj.InnerDiameter.Value)}</innerdiameter>\n")
        self.write(file, f"{' ' * (indent + 2)}<height>{self.toMeters(feature._obj.Height.Value)}</height>\n")
        self.write(file, f"{' ' * (indent + 2)}<baseheight>{self.toMeters(feature._obj.BaseHeight.Value)}</baseheight>\n")
        self.write(file, f"{' ' * (indent + 2)}<flangeheight>{self.toMeters(feature._obj.FlangeHeight.Value)}</flangeheight>\n")
        self.write(file, f"{' ' * (indent + 2)}<screwheight>0.0</screwheight>\n")
        self.write(file, f"{' ' * indent}</railbutton>\n\n")

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
        self.write(file, f"{' ' * indent}<trapezoidfinset>\n")
        if suffix:
            self.write(file, f"{' ' * (indent + 2)}<name>{feature.getName()}-{suffix}</name>\n")
        else:
            self.write(file, f"{' ' * (indent + 2)}<name>{feature.getName()}</name>\n")
        self.write(file, f"{' ' * (indent + 2)}<id>{uuid.uuid4()}</id>\n")
        self.writeAppearance(file, feature, indent+2)
        if feature.isFinSet():
            fins = feature.getFinCount()
        else:
            fins = 1
        self.write(file, f"{' ' * (indent + 2)}<instancecount>{fins}</instancecount>\n")
        self.write(file, f"{' ' * (indent + 2)}<fincount>{fins}</fincount>\n")
        self.write(file, f"{' ' * (indent + 2)}<radiusoffset method=\"{self.getRadialMethod(feature)}\">{self.toMeters(feature._obj.RadialOffset.Value)}</radiusoffset>\n")
        self.write(file, f"{' ' * (indent + 2)}<angleoffset method=\"relative\">{feature._obj.AngleOffset.Value}</angleoffset>\n")
        self.write(file, f"{' ' * (indent + 2)}<rotation>{feature._obj.AngleOffset.Value}</rotation>\n")
        self.write(file, f"{' ' * (indent + 2)}<axialoffset method=\"{self.getAxialMethod(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</axialoffset>\n")
        self.write(file, f"{' ' * (indent + 2)}<position type=\"{self.getPositionType(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</position>\n")
        # self.write(file, f"{' ' * (indent + 2)}<length>{self.toMeters(float(feature.getLength()))}</length>\n")
        self.write(file, f"{' ' * (indent + 2)}<thickness>{self.toMeters(feature.getRootThickness())}</thickness>\n")
        self.write(file, f"{' ' * (indent + 2)}<crosssection>{self.getCrossSection(feature)}</crosssection>\n")
        self.write(file, f"{' ' * (indent + 2)}<cant>{feature._obj.Cant.Value}</cant>\n")
        self.writeFinTab(file, feature, indent + 2)
        if feature._obj.Fillets:
            self.write(file, f"{' ' * (indent + 2)}<filletradius>{self.toMeters(feature._obj.FilletRadius.Value)}</filletradius>\n")
        else:
            self.write(file, f"{' ' * (indent + 2)}<filletradius>0.0</filletradius>\n")
        self.write(file, f"{' ' * (indent + 2)}<rootchord>{self.toMeters(feature.getRootChord())}</rootchord>\n")
        if feature._obj.FinType == FIN_TYPE_TRIANGLE:
            self.write(file, f"{' ' * (indent + 2)}<tipchord>0.0</tipchord>\n")
        else:
            self.write(file, f"{' ' * (indent + 2)}<tipchord>{self.toMeters(feature.getTipChord())}</tipchord>\n")
        self.write(file, f"{' ' * (indent + 2)}<sweeplength>{self.toMeters(feature.getSweepLength())}</sweeplength>\n")
        self.write(file, f"{' ' * (indent + 2)}<height>{self.toMeters(feature.getHeight())}</height>\n")
        self.writeSubcomponents(file, feature, indent + 2)
        self.write(file, f"{' ' * indent}</trapezoidfinset>\n\n")

    def writeFinEllipse(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int, suffix : str | None = None) -> None:
        self.write(file, f"{' ' * indent}<ellipticalfinset>\n")
        if suffix:
            self.write(file, f"{' ' * (indent + 2)}<name>{feature.getName()}-{suffix}</name>\n")
        else:
            self.write(file, f"{' ' * (indent + 2)}<name>{feature.getName()}</name>\n")
        self.write(file, f"{' ' * (indent + 2)}<id>{uuid.uuid4()}</id>\n")
        self.writeAppearance(file, feature, indent+2)
        if feature.isFinSet():
            fins = feature.getFinCount()
        else:
            fins = 1
        self.write(file, f"{' ' * (indent + 2)}<instancecount>{fins}</instancecount>\n")
        self.write(file, f"{' ' * (indent + 2)}<fincount>{fins}</fincount>\n")
        self.write(file, f"{' ' * (indent + 2)}<radiusoffset method=\"{self.getRadialMethod(feature)}\">{self.toMeters(feature._obj.RadialOffset.Value)}</radiusoffset>\n")
        self.write(file, f"{' ' * (indent + 2)}<angleoffset method=\"relative\">{feature._obj.AngleOffset.Value}</angleoffset>\n")
        self.write(file, f"{' ' * (indent + 2)}<rotation>{feature._obj.AngleOffset.Value}</rotation>\n")
        self.write(file, f"{' ' * (indent + 2)}<axialoffset method=\"{self.getAxialMethod(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</axialoffset>\n")
        self.write(file, f"{' ' * (indent + 2)}<position type=\"{self.getPositionType(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</position>\n")
        # self.write(file, f"{' ' * (indent + 2)}<length>{self.toMeters(float(feature.getLength()))}</length>\n")
        self.write(file, f"{' ' * (indent + 2)}<thickness>{self.toMeters(feature.getRootThickness())}</thickness>\n")
        self.write(file, f"{' ' * (indent + 2)}<crosssection>{self.getCrossSection(feature)}</crosssection>\n")
        self.write(file, f"{' ' * (indent + 2)}<cant>{feature._obj.Cant.Value}</cant>\n")
        self.writeFinTab(file, feature, indent + 2)
        if feature._obj.Fillets:
            self.write(file, f"{' ' * (indent + 2)}<filletradius>{self.toMeters(feature._obj.FilletRadius.Value)}</filletradius>\n")
        else:
            self.write(file, f"{' ' * (indent + 2)}<filletradius>0.0</filletradius>\n")
        self.write(file, f"{' ' * (indent + 2)}<rootchord>{self.toMeters(feature.getRootChord())}</rootchord>\n")
        self.write(file, f"{' ' * (indent + 2)}<height>{self.toMeters(feature.getHeight())}</height>\n")
        self.writeSubcomponents(file, feature, indent + 2)
        self.write(file, f"{' ' * indent}</ellipticalfinset>\n\n")

    def writeFinTube(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int, suffix : str | None = None) -> None:
        self.write(file, f"{' ' * indent}<tubefinset>\n")
        if suffix:
            self.write(file, f"{' ' * (indent + 2)}<name>{feature.getName()}-{suffix}</name>\n")
        else:
            self.write(file, f"{' ' * (indent + 2)}<name>{feature.getName()}</name>\n")
        self.write(file, f"{' ' * (indent + 2)}<id>{uuid.uuid4()}</id>\n")
        self.writeAppearance(file, feature, indent+2)
        if feature.isFinSet():
            fins = feature.getFinCount()
        else:
            fins = 1
        self.write(file, f"{' ' * (indent + 2)}<instancecount>{fins}</instancecount>\n")
        self.write(file, f"{' ' * (indent + 2)}<fincount>{fins}</fincount>\n")
        self.write(file, f"{' ' * (indent + 2)}<radiusoffset method=\"{self.getRadialMethod(feature)}\">{self.toMeters(feature._obj.RadialOffset.Value)}</radiusoffset>\n")
        self.write(file, f"{' ' * (indent + 2)}<angleoffset method=\"relative\">{feature._obj.AngleOffset.Value}</angleoffset>\n")
        self.write(file, f"{' ' * (indent + 2)}<rotation>{feature._obj.AngleOffset.Value}</rotation>\n")
        self.write(file, f"{' ' * (indent + 2)}<axialoffset method=\"{self.getAxialMethod(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</axialoffset>\n")
        self.write(file, f"{' ' * (indent + 2)}<position type=\"{self.getPositionType(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</position>\n")
        if feature.isTubeOuterRadiusAutomatic():
            self.write(file, f"{' ' * (indent + 2)}<radius>auto</radius>\n")
        else:
            self.write(file, f"{' ' * (indent + 2)}<radius>{feature.getTubeOuterRadius()}</radius>\n")
        self.write(file, f"{' ' * (indent + 2)}<length>{self.toMeters(float(feature.getLength()))}</length>\n")
        self.write(file, f"{' ' * (indent + 2)}<thickness>{self.toMeters(feature._obj.TubeThickness.Value)}</thickness>\n")
        self.writeSubcomponents(file, feature, indent + 2)
        self.write(file, f"{' ' * indent}</tubefinset>\n\n")

    def writeFinSketch(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int, suffix : str | None = None) -> None:
        self.write(file, f"{' ' * indent}<freeformfinset>\n")
        if suffix:
            self.write(file, f"{' ' * (indent + 2)}<name>{feature.getName()}-{suffix}</name>\n")
        else:
            self.write(file, f"{' ' * (indent + 2)}<name>{feature.getName()}</name>\n")
        self.write(file, f"{' ' * (indent + 2)}<id>{uuid.uuid4()}</id>\n")
        self.writeAppearance(file, feature, indent+2)
        if feature.isFinSet():
            fins = feature.getFinCount()
        else:
            fins = 1
        self.write(file, f"{' ' * (indent + 2)}<instancecount>{fins}</instancecount>\n")
        self.write(file, f"{' ' * (indent + 2)}<fincount>{fins}</fincount>\n")
        self.write(file, f"{' ' * (indent + 2)}<radiusoffset method=\"{self.getRadialMethod(feature)}\">{self.toMeters(feature._obj.RadialOffset.Value)}</radiusoffset>\n")
        self.write(file, f"{' ' * (indent + 2)}<angleoffset method=\"relative\">{feature._obj.AngleOffset.Value}</angleoffset>\n")
        self.write(file, f"{' ' * (indent + 2)}<rotation>{feature._obj.AngleOffset.Value}</rotation>\n")
        self.write(file, f"{' ' * (indent + 2)}<axialoffset method=\"{self.getAxialMethod(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</axialoffset>\n")
        self.write(file, f"{' ' * (indent + 2)}<position type=\"{self.getPositionType(feature)}\">{self.toMeters(feature._obj.AxialOffset.Value)}</position>\n")
        self.write(file, f"{' ' * (indent + 2)}<thickness>{self.toMeters(feature.getRootThickness())}</thickness>\n")
        self.write(file, f"{' ' * (indent + 2)}<crosssection>{self.getCrossSection(feature)}</crosssection>\n")
        self.write(file, f"{' ' * (indent + 2)}<cant>{feature._obj.Cant.Value}</cant>\n")
        self.writeFinTab(file, feature, indent + 2)
        if feature._obj.Fillets:
            self.write(file, f"{' ' * (indent + 2)}<filletradius>{self.toMeters(feature._obj.FilletRadius.Value)}</filletradius>\n")
        else:
            self.write(file, f"{' ' * (indent + 2)}<filletradius>0.0</filletradius>\n")
        self.write(file, f"{' ' * (indent + 2)}<finpoints>\n")
        for point in self.getVertexes(feature):
            self.write(file, f"{' ' * (indent + 4)}<point x=\"{self.toMeters(point.Point.x)}\" y=\"{self.toMeters(point.Point.z)}\"/>\n")
        self.write(file, f"{' ' * (indent + 2)}</finpoints>\n")
        self.writeSubcomponents(file, feature, indent + 2)
        self.write(file, f"{' ' * indent}</freeformfinset>\n\n")

    def writeFinTab(self, file : io.TextIOBase, feature : RocketComponentShapeless, indent : int) -> None:
        if feature._obj.Ttw:
            self.write(file, f"{' ' * indent}<tabheight>{self.toMeters(feature._obj.TtwHeight.Value)}</tabheight>\n")
            self.write(file, f"{' ' * indent}<tablength>{self.toMeters(feature._obj.TtwLength.Value)}</tablength>\n")
            self.write(file, f"{' ' * indent}<tabposition relativeto=\"top\">{self.toMeters(feature._obj.TtwOffset.Value)}</tabposition>\n")

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
