# ***************************************************************************
# *   Copyright (c) 2021-2025 David Carter <dcarter@davidcarter.ca>         *
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
"""Rocket Workbench Constants"""

__title__ = "FreeCAD Rocket Workbench Constants"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD

translate = FreeCAD.Qt.translate

#  Default values
DEFAULT_REFERENCE_LENGTH = 0.01

# Feature types
FEATURE_ROCKET = "Rocket"
FEATURE_STAGE = "RocketStage"
FEATURE_PARALLEL_STAGE = "RocketParallelStage"
FEATURE_BULKHEAD = "RocketBulkhead"
FEATURE_POD = "RocketPod"
FEATURE_BODY_TUBE = "RocketBodyTube"
FEATURE_INNER_TUBE = "RocketInnerTube"
FEATURE_TUBE_COUPLER = "RocketTubeCoupler"
FEATURE_ENGINE_BLOCK = "RocketEngineBlock"
FEATURE_CENTERING_RING = "RocketCenteringRing"
FEATURE_FIN = "RocketFin"
FEATURE_FINCAN = "RocketFinCan"
FEATURE_NOSE_CONE = "RocketNoseCone"
FEATURE_TRANSITION = "RocketTransition"
FEATURE_LAUNCH_LUG = "RocketLaunchLug"
FEATURE_RAIL_BUTTON = "RocketRailButton"
FEATURE_RAIL_GUIDE = "RocketRailGuide"
FEATURE_OFFSET = "RocketOffset"
FEATURE_RINGTAIL = "RocketRingtail"

FEATURE_WIND_TUNNEL = "RocketWindTunnel"
FEATURE_CFD_ROCKET = "RocketCFDRocket"
FEATURE_CFD_ANALYSIS = "RocketMultiCFDAnalysis"

# Part styles
STYLE_SOLID = "solid"
STYLE_SOLID_CORE = "solid core" # Used by transitions, not nose cones
STYLE_HOLLOW = "hollow"
STYLE_CAPPED = "capped"

# Cap styles
STYLE_CAP_SOLID = "solid"
STYLE_CAP_BAR = "bar"
STYLE_CAP_CROSS = "cross"

# Part shapes
TYPE_CONE = "cone"
TYPE_BLUNTED_CONE = "blunted cone"
TYPE_SPHERICAL = "spherical"
TYPE_ELLIPTICAL = "elliptical"
TYPE_OGIVE = "ogive"
TYPE_BLUNTED_OGIVE = "blunted ogive"
TYPE_SECANT_OGIVE = "secant ogive"
TYPE_PARABOLA = "parabola"
TYPE_VON_KARMAN = "Von Karman"
TYPE_PARABOLIC = "parabolic series"
TYPE_POWER = "power series"
TYPE_HAACK = "Haack series"
TYPE_NIKE_SMOKE = "Nike Smoke"
TYPE_PROXY = "proxy"

# Fin types
FIN_TYPE_TRAPEZOID = "trapezoid"
FIN_TYPE_TRIANGLE = "triangular"
FIN_TYPE_ELLIPSE = "elliptical"
FIN_TYPE_TUBE = "tube"
FIN_TYPE_SKETCH = "custom"
FIN_TYPE_PROXY = "proxy"

# Fin cross sections
FIN_CROSS_SAME = "Same as root"
FIN_CROSS_SQUARE = "square"
FIN_CROSS_ROUND = "round"
FIN_CROSS_ELLIPSE = "ellipse"
FIN_CROSS_BICONVEX = "biconvex"
FIN_CROSS_AIRFOIL = "airfoil"
FIN_CROSS_WEDGE = "wedge"
FIN_CROSS_DIAMOND = "diamond"
FIN_CROSS_TAPER_LE = "LE taper"
FIN_CROSS_TAPER_TE = "TE taper"
FIN_CROSS_TAPER_LETE = "taper"

FIN_DEBUG_FULL = "Full"
FIN_DEBUG_PROFILE_ONLY = "Profile"
FIN_DEBUG_MASK_ONLY = "Mask"

FINCAN_STYLE_SLEEVE = "Sleeve"
FINCAN_STYLE_BODYTUBE = "Body Tube"

# Fin can edges
FINCAN_EDGE_SQUARE = "square"
FINCAN_EDGE_ROUND = "round"
FINCAN_EDGE_TAPER = "taper"

FINCAN_PRESET_CUSTOM = 'Custom'
FINCAN_PRESET_1_8 = '1/8"'
FINCAN_PRESET_3_16 = '3/16"'
FINCAN_PRESET_1_4 = '1/4"'

FINCAN_COUPLER_MATCH_ID = "Flush with fin can"
FINCAN_COUPLER_STEPPED = "Stepped"

FIN_DEBUG_FULL = "Full"
FIN_DEBUG_PROFILE_ONLY = "Profile"
FIN_DEBUG_MASK_ONLY = "Mask"

FIN_EDGE_SQUARE = "Square"
FIN_EDGE_ROUNDED = "Rounded"

# Part material types
MATERIAL_TYPE_BULK = "BULK"
MATERIAL_TYPE_SURFACE = "SURFACE"
MATERIAL_TYPE_LINE = "LINE"

# Rail button types
RAIL_BUTTON_ROUND = "Round"
RAIL_BUTTON_AIRFOIL = "Airfoil"

# Rail guide base types
RAIL_GUIDE_BASE_FLAT = "Flat"
RAIL_GUIDE_BASE_CONFORMAL = "Conformal"
RAIL_GUIDE_BASE_V = "V Shaped"

# Retainer styles
RETAINER_TUBE_MOUNT = "Tube mount"
RETAINER_FLANGE_MOUNT = "Flange mount"
RETAINER_TAILCONE = "Tailcone"

# Components in the database
COMPONENT_TYPE_ANY = "Any"
COMPONENT_TYPE_BODYTUBE = "Body Tube"
COMPONENT_TYPE_BULKHEAD = "Bulkhead"
COMPONENT_TYPE_CENTERINGRING = "Centering Ring"
COMPONENT_TYPE_COUPLER = "Tube Coupler"
COMPONENT_TYPE_ENGINEBLOCK = "Engine Block"
COMPONENT_TYPE_LAUNCHLUG = "Launch Lug"
COMPONENT_TYPE_NOSECONE = "Nose Cone"
COMPONENT_TYPE_PARACHUTE = "Parachute"
COMPONENT_TYPE_STREAMER = "Streamer"
COMPONENT_TYPE_TRANSITION = "Transition"
COMPONENT_TYPE_RAILBUTTON = "Rail Button"
COMPONENT_TYPE_RETAINER = "Retainer"

# Location Reference
LOCATION_PARENT_TOP = translate('Rocket', "Top of the parent component")
LOCATION_PARENT_MIDDLE = translate('Rocket', "Middle of the parent component")
LOCATION_PARENT_BOTTOM = translate('Rocket', "Bottom of the parent component")
LOCATION_BASE = translate('Rocket', "Base of the rocket")
LOCATION_AFTER = translate('Rocket', "After the target component")
LOCATION_SURFACE = translate('Rocket', "Surface of the parent component")
LOCATION_CENTER = translate('Rocket', "Center of the parent component")

# Part properties, defined in /App/PropertyContainer.h for cpp
# These can be bitwise or'ed to combine properties, when calling addProperty
PROP_NONE = 0           # No special property type
PROP_READONLY = 1       # Property is read-only in the editor
PROP_TRANSIENT = 2      # Property won't be saved to file
PROP_HIDDEN = 4         # Property won't appear in the editor
PROP_OUTPUT = 8         # Modified property doesn't touch its parent container
PROP_NORECOMPUTE = 16   # Modified property doesn't touch its container for recompute

# A subset for use with setEditorMode calls
EDITOR_NONE = 0
EDITOR_READONLY = 1
EDITOR_HIDDEN = 2

# Fastener properties
COUNTERSINK_ANGLE_NONE = "None"
COUNTERSINK_ANGLE_60 = "60"
COUNTERSINK_ANGLE_82 = "82 (American inch screws)"
COUNTERSINK_ANGLE_90 = "90 (Metric)"
COUNTERSINK_ANGLE_100 = "100 (British Imperial inch screws"
COUNTERSINK_ANGLE_110 = "110"
COUNTERSINK_ANGLE_120 = "120"

FASTENER_PRESET_6 = '#6'
FASTENER_PRESET_8 = '#8'
FASTENER_PRESET_10 = '#10'
FASTENER_PRESET_1_4 = '1/4"'

FASTENER_PRESET_6_HEAD = '0.307"'
FASTENER_PRESET_6_SHANK = '0.1380"'

FASTENER_PRESET_8_HEAD = '0.359"'
FASTENER_PRESET_8_SHANK = '0.1640"'

FASTENER_PRESET_10_HEAD = '0.411"'
FASTENER_PRESET_10_SHANK = '0.1900"'

FASTENER_PRESET_1_4_HEAD = '0.531"'
FASTENER_PRESET_1_4_SHANK = '0.2500"'
