# SPDX-License-Identifier: LGPL-2.1-or-later


IF (BUILD_GUI)
    PYSIDE_WRAP_RC(Rocket_QRC_SRCS Resources/Rocket.qrc)
ENDIF (BUILD_GUI)

SET(Rocket_SRCS
    Init.py
    InitGui.py
    Rocket.py
    RocketGui.py
    importORK.py
    importRKT.py
    App/Component/__init__.py
    App/Component/AxialStageComponent.py
    App/Component/BodyTubeComponent.py
    App/Component/Component.py
    App/Component/NoseConeComponent.py
    App/Component/RocketComponent.py
    App/__init__.py
    App/BodyTubeShapeHandler.py
    App/BulkheadShapeHandler.py
    App/CenteringRingShapeHandler.py
    App/Constants.py
    App/FinTrapezoidShapeHandler.py
    App/NoseConeShapeHandler.py
    App/NoseEllipseShapeHandler.py
    App/NoseHaackShapeHandler.py
    App/NoseOgiveShapeHandler.py
    App/NoseParabolicShapeHandler.py
    App/NosePowerShapeHandler.py
    App/NoseShapeHandler.py
    App/OpenRocket.py
    App/ShapeBodyTube.py
    App/ShapeBulkhead.py
    App/ShapeCenteringRing.py
    App/ShapeComponent.py
    App/ShapeFin.py
    App/ShapeNoseCone.py
    App/ShapeTransition.py
    App/TransitionConeShapeHandler.py
    App/TransitionEllipseShapeHandler.py
    App/TransitionHaackShapeHandler.py
    App/TransitionOgiveShapeHandler.py
    App/TransitionParabolicShapeHandler.py
    App/TransitionPowerShapeHandler.py
    App/TransitionShapeHandler.py
    App/Utilities.py
    Ui/__init__.py
    Ui/CmdBodyTube.py
    Ui/CmdBulkhead.py
    Ui/CmdCenteringRing.py
    Ui/CmdFin.py
    Ui/CmdFinCan.py
    Ui/CmdNoseCone.py
    Ui/CmdTransition.py
    Ui/TaskPanelBodyTube.py
    Ui/TaskPanelBulkhead.py
    Ui/TaskPanelFin.py
    Ui/TaskPanelNoseCone.py
    Ui/TaskPanelTransition.py
    Ui/ViewBodyTube.py
    Ui/ViewBulkhead.py
    Ui/ViewCenteringRing.py
    Ui/ViewFin.py
    Ui/ViewNoseCone.py
    Ui/ViewTransition.py
)
SOURCE_GROUP("" FILES ${Rocket_SRCS})

ADD_CUSTOM_TARGET(Rocket ALL
    SOURCES ${Rocket_SRCS} ${Rocket_QRC_SRCS}
)

fc_copy_sources(Rocket "${CMAKE_BINARY_DIR}/Mod/Rocket" ${Rocket_SRCS})

IF (BUILD_GUI)
    fc_target_copy_resource(Rocket
        ${CMAKE_CURRENT_BINARY_DIR}
        ${CMAKE_BINARY_DIR}/Mod/Rocket
        Rocket_rc.py)
ENDIF (BUILD_GUI)

INSTALL(
    FILES
        ${Rocket_SRCS}
        ${Rocket_QRC_SRCS}
    DESTINATION
        Mod/Rocket
)

SET(RocketGuiIcon_SVG
    Resources/icons/Rocket_BodyTube.svg
    Resources/icons/Rocket_Bulkhead.svg
    Resources/icons/Rocket_CenteringRing.svg
    Resources/icons/Rocket_Fin.svg
    Resources/icons/Rocket_FinCan.svg
    Resources/icons/Rocket_NoseCone.svg
    Resources/icons/Rocket_Transition.svg
    Resources/icons/RocketWorkbench.svg
)

fc_copy_sources(Rocket "${CMAKE_BINARY_DIR}/Mod/Rocket" ${RocketGuiIcon_SVG})
INSTALL(FILES ${RocketGuiIcon_SVG} DESTINATION "Mod/Rocket/Resources/icons")
