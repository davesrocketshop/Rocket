# ***************************************************************************
# *   Copyright (c) 2022-2025 David Carter <dcarter@davidcarter.ca>         *
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
"""Class for building test rockets"""

__title__ = "FreeCAD Body Tube Tests"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD

from Rocket.Constants import TYPE_CONE, TYPE_BLUNTED_CONE, TYPE_SPHERICAL, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_BLUNTED_OGIVE, TYPE_SECANT_OGIVE, TYPE_VON_KARMAN, TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_POWER

from Ui.Commands.CmdBodyTube import makeBodyTube, makeEngineBlock, makeInnerTube
from Ui.Commands.CmdRocket import makeRocket
from Ui.Commands.CmdStage import makeStage
from Ui.Commands.CmdNoseCone import makeNoseCone
from Ui.Commands.CmdFin import makeFin
from Ui.Commands.CmdFinCan import makeFinCan
from Ui.Commands.CmdLaunchGuides import makeLaunchLug
from Ui.Commands.CmdCenteringRing import makeCenteringRing
from Rocket.position import AxialMethod

class TestRockets:

    """
        This is a Estes Alpha III
        http://www.rocketreviews.com/alpha-iii---estes-221256.html
        It is picked as a standard, simple, validation rocket.
        This function is used for unit, integration tests, DO NOT CHANGE (without updating tests).
    """
    @classmethod
    def makeEstesAlphaIII(cls):
        rocket = makeRocket('Alpha III', False)
        # rocket.enableEvents(False)
        rocket.setName("Estes Alpha III / Code Verification Rocket")

        stage = makeStage()
        stage.setName("Stage")
        rocket.addChild(stage)

        noseconeLength = 70.0
        noseconeRadius = 12.0
        nosecone = makeNoseCone()
        nosecone.setNoseType(TYPE_OGIVE)
        nosecone.setLength(noseconeLength)
        nosecone.setAftRadius(noseconeRadius)

        nosecone.setShoulderLength(29.0)
        nosecone.setShoulderRadius(11.0)
        nosecone.setName("Nose Cone")
        stage.addChild(nosecone)

        bodytubeLength = 200.0
        bodytubeRadius = 12.0
        bodytubeThickness = 0.3
        bodytube = makeBodyTube()
        bodytube.setLength(bodytubeLength)
        bodytube.setOuterRadius(bodytubeRadius)
        bodytube.setThickness(bodytubeThickness)
        bodytube.setName("Body Tube")
        stage.addChild(bodytube)

        finCount = 3
        finRootChord = 50.0
        finTipChord = 30.0
        finSweep = 20.0
        finHeight = 50.0
        finset = makeFin()
        finset.setFinCount(finCount)
        finset.setRootChord(finRootChord)
        finset.setTipChord(finTipChord)
        finset.setSweepLength(finSweep)
        finset.setHeight(finHeight)
        finset.setThickness(3.2)
        finset.setAxialMethod(AxialMethod.BOTTOM)
        finset.setName("3 Fin Set")
        bodytube.addChild(finset)

        lug = makeLaunchLug()
        lug.setName("Launch Lugs")
        lug.setAxialMethod(AxialMethod.TOP)
        lug.setAxialOffset(111.0)
        lug.setLength(50.0)
        lug.setOuterRadius(2.2)
        lug.setInnerRadius(2.0)
        bodytube.addChild(lug)

        inner = makeInnerTube() # InnerTube?
        inner.setAxialMethod(AxialMethod.TOP)
        inner.setAxialOffset(133.0)
        inner.setLength(70.0)
        inner.setOuterRadius(9.0)
        inner.setThickness(0.3)
        inner.setMotorMount(True)
        inner.setName("Motor Mount Tube")
        bodytube.addChild(inner)

        # MotorBlock
        thrustBlock= makeEngineBlock()
        thrustBlock.setAxialMethod(AxialMethod.TOP)
        thrustBlock.setAxialOffset(0.0)
        thrustBlock.setLength(5.0)
        thrustBlock.setOuterRadius(9.0)
        thrustBlock.setThickness(0.8)
        thrustBlock.setName("Engine Block")
        inner.addChild(thrustBlock)

        # bulkhead x2
        centerings = makeCenteringRing()
        centerings.setName("Centering Rings")
        centerings.setAxialMethod(AxialMethod.TOP)
        centerings.setAxialOffset(140.0)
        centerings.setLength(6.0)
        centerings.setInstanceCount(2)
        centerings.setInstanceSeparation(35.0)
        bodytube.addChild(centerings)

        # Material material = Application.getPreferences().getDefaultComponentMaterial(null, Material.Type.BULK);
        # nosecone.setMaterial(material);
        # bodytube.setMaterial(material);
        # finset.setMaterial(material);

        rocket.enableEvents()
        FreeCAD.activeDocument().recompute(None,True,True)
        return rocket
    
    @classmethod
    def make3stage(cls):
        rocket = makeRocket('3Stage', False)
        # rocket.enableEvents(False)
        rocket.setName("3Stage / Code Verification Rocket")

        stage = makeStage()
        stage.setName("Stage")
        rocket.addChild(stage)

        noseconeLength = 100.0
        noseconeRadius = 24.79 / 2.0
        nosecone = makeNoseCone()
        nosecone.setNoseType(TYPE_OGIVE)
        nosecone.setLength(noseconeLength)
        nosecone.setAftRadius(noseconeRadius)

        nosecone.setShoulderLength(24.79)
        nosecone.setShoulderRadius(23.62 / 2.0)
        nosecone.setName("Nose Cone")
        stage.addChild(nosecone)

        bodytubeLength = 457.0
        bodytubeRadius = noseconeRadius
        bodytubeThickness = 0.33
        bodytube = makeBodyTube()
        bodytube.setLength(bodytubeLength)
        bodytube.setOuterRadius(bodytubeRadius)
        bodytube.setThickness(bodytubeThickness)
        bodytube.setName("Body Tube")
        stage.addChild(bodytube)

        finCount = 3
        finRootChord = 57.15
        finTipChord = 30.48
        finSweep = 69.86
        finHeight = 40.64
        finset = makeFin()
        finset.setFinCount(finCount)
        finset.setRootChord(finRootChord)
        finset.setTipChord(finTipChord)
        finset.setSweepLength(finSweep)
        finset.setHeight(finHeight)
        finset.setThickness(1.4)
        finset.setAxialMethod(AxialMethod.BOTTOM)
        finset.setName("Fin")
        bodytube.addChild(finset)

        lug = makeLaunchLug()
        lug.setName("Launch Lugs")
        lug.setAxialMethod(AxialMethod.MIDDLE)
        lug.setAxialOffset(0.0)
        lug.setAngleOffset(60.0)
        lug.setLength(50.0)
        lug.setOuterRadius(2.2)
        lug.setInnerRadius(2.0)
        bodytube.addChild(lug)

        inner = makeInnerTube() # InnerTube?
        inner.setAxialMethod(AxialMethod.BOTTOM)
        inner.setAxialOffset(5.0)
        inner.setLength(70.0)
        inner.setOuterRadius(9.0)
        inner.setThickness(0.3)
        inner.setMotorMount(True)
        inner.setName("Motor Mount Tube")
        bodytube.addChild(inner)

        # MotorBlock
        thrustBlock= makeEngineBlock()
        thrustBlock.setAxialMethod(AxialMethod.TOP)
        thrustBlock.setAxialOffset(0.0)
        thrustBlock.setLength(5.0)
        thrustBlock.setOuterRadius(9.0)
        thrustBlock.setThickness(0.8)
        thrustBlock.setName("Engine Block")
        inner.addChild(thrustBlock)

        # bulkhead x2
        centerings = makeCenteringRing()
        centerings.setName("Centering Rings")
        centerings.setAxialMethod(AxialMethod.BOTTOM)
        centerings.setAxialOffset(-50.0)
        centerings.setLength(6.0)
        centerings.setInstanceCount(2)
        centerings.setInstanceSeparation(35.0)
        bodytube.addChild(centerings)

        # 2nd stage
        stage = makeStage()
        stage.setName("Stage")
        rocket.addChild(stage)

        bodytubeLength = 70.0
        bodytubeRadius = noseconeRadius
        bodytubeThickness = 0.33
        bodytube = makeBodyTube()
        bodytube.setLength(bodytubeLength)
        bodytube.setOuterRadius(bodytubeRadius)
        bodytube.setThickness(bodytubeThickness)
        bodytube.setName("Body Tube")
        stage.addChild(bodytube)

        finCount = 3
        finRootChord = 57.15
        finTipChord = 30.48
        finSweep = 69.86
        finHeight = 40.64
        finset = makeFin()
        finset.setFinCount(finCount)
        finset.setRootChord(finRootChord)
        finset.setTipChord(finTipChord)
        finset.setSweepLength(finSweep)
        finset.setHeight(finHeight)
        finset.setThickness(1.4)
        finset.setAxialMethod(AxialMethod.BOTTOM)
        finset.setName("Fin")
        bodytube.addChild(finset)

        # 3rd stage
        stage = makeStage()
        stage.setName("Stage")
        rocket.addChild(stage)

        fincan = makeFinCan()
        stage.addChild(fincan)

        rocket.enableEvents()
        FreeCAD.activeDocument().recompute(None,True,True)
        return rocket
