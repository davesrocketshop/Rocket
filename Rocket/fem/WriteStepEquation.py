# ***************************************************************************
# *   Copyright (c) 2021 Bernd Hahnebach <bernd@bimstatik.org>              *
# *                                                                         *
# *   This file is part of the FreeCAD CAx development system.              *
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

__title__ = "FreeCAD FEM calculix write inpfile step equation"
__author__ = "Bernd Hahnebach"
__url__ = "https://www.freecad.org"


import FreeCAD


def write_step_equation(f, ccxwriter):

    f.write("\n{}\n".format(59 * "*"))
    f.write("** At least one step is needed to run an CalculiX analysis of FreeCAD\n")

    # build STEP line
    step = "*STEP"
    # write STEP line
    f.write(step + "\n")

    # ANALYSIS parameter line
    analysis_parameter = ""
    if ccxwriter.solver_obj.EigenmodeLowLimit == 0.0 \
            and ccxwriter.solver_obj.EigenmodeHighLimit == 0.0:
        analysis_parameter = "{}\n".format(ccxwriter.solver_obj.EigenmodesCount)
    else:
        analysis_parameter = "{},{},{}\n".format(
            ccxwriter.solver_obj.EigenmodesCount,
            ccxwriter.solver_obj.EigenmodeLowLimit,
            ccxwriter.solver_obj.EigenmodeHighLimit
        )

    # write analysis type line, analysis parameter line
    f.write("*STATIC\n")
    f.write("*FREQUENCY, SOLVER=MATRIXSTORAGE\n")
    f.write(analysis_parameter + "\n")


def write_step_end(f, ccxwriter):
    f.write("\n{}\n".format(59 * "*"))
    f.write("*END STEP \n")
