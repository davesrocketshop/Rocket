# ***************************************************************************
# *   Copyright (c) 2022 David Carter <dcarter@davidcarter.ca>              *
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
import unittest

from App.Constants import TYPE_CONE, TYPE_BLUNTED_CONE, TYPE_SPHERICAL, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_BLUNTED_OGIVE, TYPE_SECANT_OGIVE, TYPE_VON_KARMAN, TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_POWER

from Ui.Commands.CmdBodyTube import makeBodyTube
from Ui.Commands.CmdRocket import makeRocket
from Ui.Commands.CmdStage import makeStage
from Ui.Commands.CmdNoseCone import makeNoseCone
from Ui.Commands.CmdFin import makeFin
from Ui.Commands.CmdLaunchGuides import makeLaunchLug
from App.position import AxialMethod

class TestRockets:

    """ 
        This is a Estes Alpha III 
        http://www.rocketreviews.com/alpha-iii---estes-221256.html
        It is picked as a standard, simple, validation rocket. 
        This function is used for unit, integration tests, DO NOT CHANGE (without updating tests).
    """
    def makeEstesAlphaIII():
        rocket = makeRocket('Alpha III', False).Proxy
        rocket.enableEvents(False)
        rocket.setName("Estes Alpha III / Code Verification Rocket")

        stage = makeStage().Proxy
        stage.setName("Stage")
        rocket.addChild(stage)
                
        noseconeLength = 70.0
        noseconeRadius = 12.0
        nosecone = makeNoseCone().Proxy
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
        bodytube = makeBodyTube().Proxy
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
        finset = makeFin().Proxy
        finset.setFinCount(finCount)
        finset.setRootChord(finRootChord)
        finset.setTipChord(finTipChord)
        finset.setSweepLength(finSweep)
        finset.setHeight(finHeight)
        finset.setThickness(3.2)
        # finset.setAxialMethod(AxialMethod.BOTTOM)
        finset.setName("3 Fin Set")
        bodytube.addChild(finset)
            
        lug = makeLaunchLug().Proxy
        lug.setName("Launch Lugs")
        lug.setAxialMethod(AxialMethod.TOP)
        lug.setAxialOffset(111.0)
        lug.setLength(50.0)
        lug.setOuterRadius(2.2)
        lug.setInnerRadius(2.0)
        bodytube.addChild(lug)
            
        inner = makeBodyTube().Proxy # InnerTube?
        inner.setAxialMethod(AxialMethod.TOP)
        inner.setAxialOffset(133.0)
        inner.setLength(70.0)
        inner.setOuterRadius(9.0)
        inner.setThickness(0.3)
        inner.setMotorMount(True)
        inner.setName("Motor Mount Tube")
        bodytube.addChild(inner)
            
        #     {
        #         // MotorBlock 
        #         EngineBlock thrustBlock= new EngineBlock();
        #         thrustBlock.setAxialMethod(AxialMethod.TOP);
        #         thrustBlock.setAxialOffset(0.0);
        #         thrustBlock.setLength(0.005);
        #         thrustBlock.setOuterRadius(0.009);
        #         thrustBlock.setThickness(0.0008);
        #         thrustBlock.setName("Engine Block");
        #         inner.addChild(thrustBlock);
        #         inner.setMotorMount( true);
            
        #         {
        #             MotorConfiguration motorConfig = new MotorConfiguration(inner, TEST_FCID_0);
        #             Motor mtr =	TestRockets.generateMotor_A8_18mm();
        #             motorConfig.setMotor( mtr);
        #             motorConfig.setEjectionDelay(0.0);
        #             inner.setMotorConfig( motorConfig, TEST_FCID_0);
        #         }
        #         {
        #             MotorConfiguration motorConfig = new MotorConfiguration(inner,TEST_FCID_1);
        #             Motor mtr =	TestRockets.generateMotor_B4_18mm();
        #             motorConfig.setMotor( mtr);
        #             motorConfig.setEjectionDelay(3.0);
        #             inner.setMotorConfig( motorConfig, TEST_FCID_1);
        #         }
        #         {
        #             MotorConfiguration motorConfig = new MotorConfiguration(inner, TEST_FCID_2);
        #             Motor mtr =	TestRockets.generateMotor_C6_18mm();
        #             motorConfig.setEjectionDelay(3.0);
        #             motorConfig.setMotor( mtr);
        #             inner.setMotorConfig( motorConfig, TEST_FCID_2);
        #         }
        #         {
        #             MotorConfiguration motorConfig = new MotorConfiguration(inner,TEST_FCID_3);
        #             Motor mtr =	TestRockets.generateMotor_C6_18mm();
        #             motorConfig.setEjectionDelay(5.0);
        #             motorConfig.setMotor( mtr);
        #             inner.setMotorConfig( motorConfig, TEST_FCID_3);
        #         }
        #         {
        #             MotorConfiguration motorConfig = new MotorConfiguration(inner,TEST_FCID_4);
        #             Motor mtr =	TestRockets.generateMotor_C6_18mm();
        #             motorConfig.setEjectionDelay(7.0);
        #             motorConfig.setMotor( mtr);
        #             inner.setMotorConfig( motorConfig, TEST_FCID_4);
        #         }
        #     }
        
        #     // parachute
        #     Parachute chute = new Parachute();
        #     chute.setAxialMethod(AxialMethod.TOP);
        #     chute.setName("Parachute");
        #     chute.setAxialOffset(0.028);
        #     chute.setOverrideMass(0.002);
        #     chute.setMassOverridden(true);
        #     bodytube.addChild(chute);
            
        #     // bulkhead x2
        #     CenteringRing centerings = new CenteringRing();
        #     centerings.setName("Centering Rings");
        #     centerings.setAxialMethod(AxialMethod.TOP);
        #     centerings.setAxialOffset(0.14);
        #     centerings.setLength(0.006);
        #     centerings.setInstanceCount(2);
        #     centerings.setInstanceSeparation(0.035);
        #     bodytube.addChild(centerings);
        # }
        
        # Material material = Application.getPreferences().getDefaultComponentMaterial(null, Material.Type.BULK);
        # nosecone.setMaterial(material);
        # bodytube.setMaterial(material);
        # finset.setMaterial(material);
        
        # // preserve default default configuration of rocket -- to test what the default is set to upon initialization.
        
        rocket.enableEvents()
        return rocket

