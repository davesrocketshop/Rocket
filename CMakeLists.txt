
IF (BUILD_GUI)
    PYSIDE_WRAP_RC(Rocket_QRC_SRCS Resources/Rocket.qrc)
ENDIF (BUILD_GUI)

SET(Rocket_SRCS
    Init.py
    InitGui.py
    Rocket.py
    RocketGui.py
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
    Resources/icons/RocketWorkbench.svg
)

fc_copy_sources(Rocket "${CMAKE_BINARY_DIR}/Mod/Rocket" ${RocketGuiIcon_SVG})
INSTALL(FILES ${RocketGuiIcon_SVG} DESTINATION "Mod/Rocket/Resources/icons")
