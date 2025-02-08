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
"""Class for CFD Reports"""

__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import os
import csv
import math

from docx import Document
from docx.shared import Inches
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

from CfdOF import CfdTools

from Rocket.Utilities import _msg
from Rocket.cfd.FeatureCFDRocket import applyTranslations, calcFrontalArea

class CFDReport:

    def __init__(self, analysis):
        # Import here to prevent circular imports
        from Rocket.cfd.CFDUtil import caliber, finThickness
        from Rocket.cfd.FeatureCFDRocket import calcFrontalArea

        self._analysis = analysis
        self._path = os.path.join(CfdTools.getOutputPath(self._analysis), 'CFD Report.docx')

        self._CP = False

        self._frontalArea = calcFrontalArea(self._analysis.Shape)
        self._diameter = caliber(self._analysis.Rocket)
        self._thickness = finThickness(self._analysis.Rocket)
        box = self._analysis.Shape.BoundBox
        self._length = box.XLength
        self._x0 = self._length / 2.0
        self._rotation = self._analysis.CFDRocket.AngleOfRotation.Value

        self._forces = {}
        self._moments = {}
        self._coefficients = {}

    def getPath(self):
        return self._path

    def collectStats(self):
        for angle in self._analysis.AOAList:
            dirname = "case_aoa_{}".format(angle)

            path = os.path.join(CfdTools.getOutputPath(self._analysis), dirname,
                                "postProcessing", "ForceReportingFunction", "0", "force.dat")
            self.collectForceInformation(path, angle)

            path = os.path.join(CfdTools.getOutputPath(self._analysis), dirname,
                                "postProcessing", "ForceReportingFunction", "0", "moment.dat")
            self.collectMomentInformation(path, angle)

            path = os.path.join(CfdTools.getOutputPath(self._analysis), dirname,
                                "postProcessing", "ForceCoefficientReportingFunction", "0", "coefficient.dat")
            self.collectCoefficientInformation(path, angle)

    def collectForceInformation(self, path, angle):
        with open(path, "r") as csvfile:
            csvreader = csv.reader(csvfile, delimiter=' ', skipinitialspace=True)
            for row in csvreader:
                if len(row) == 10:
                    self._forces[str(angle)] = row

    def collectMomentInformation(self, path, angle):
        with open(path, "r") as csvfile:
            csvreader = csv.reader(csvfile, delimiter=' ', skipinitialspace=True)
            for row in csvreader:
                # Read all and save the last row
                if len(row) == 10:
                    self._moments[str(angle)] = row

    def collectCoefficientInformation(self, path, angle):
        with open(path, "r") as csvfile:
            csvreader = csv.reader(csvfile, delimiter='\t', skipinitialspace=True)
            for row in csvreader:
                # Read all and save the last row
                if len(row) == 13:
                    self._coefficients[str(angle)] = row

    def generate(self):
        self.collectStats()

        self._document = Document()
        self.addStyles()

        self.generateIntro()
        if self._CP:
            self.generateCP()
        self.generateCD()
        self.generateCL()
        self._document.save(self._path)

    def addStyles(self):
        """ Add some LibreOffice styles """
        styles = self._document.styles
        styles.add_style('Block Quotation', WD_STYLE_TYPE.PARAGRAPH, builtin = True)
        styles.add_style('Simple Grid Columns', WD_STYLE_TYPE.TABLE, builtin = True)

    def generateIntro(self):
        self._document.add_heading('CFD Report', 0)

        p = self._document.add_paragraph("This is an automated report generated by the Rocket Workbench. "\
                                         "It was created by running a CFD analysis on the document '{}'."\
                                            .format(FreeCAD.ActiveDocument.Label))

        self._document.add_paragraph("Details about the study, including the rocket")

        table = self._document.add_table(rows=4, cols=2, style='Table Grid')
        hdr_cells = table.columns[0].cells
        hdr_cells[0].text = 'Length'
        hdr_cells[1].text = 'Diameter'
        hdr_cells[2].text = 'Minimum Fin Thickness'
        hdr_cells[3].text = 'Frontal Area'
        data_cells = table.columns[1].cells
        data_cells[0].text = FreeCAD.Units.Quantity("{} mm".format(self._length)).UserString
        data_cells[1].text = FreeCAD.Units.Quantity("{} mm".format(self._diameter)).UserString
        data_cells[2].text = FreeCAD.Units.Quantity("{} mm".format(self._thickness)).UserString
        data_cells[3].text = FreeCAD.Units.Quantity("{} mm^2".format(self._frontalArea)).UserString

        self._document.add_heading('Study Parameters', level=1)

        self._document.add_paragraph("This study varied the following parameters:")
        table = self._document.add_table(rows=1, cols=1, style='Table Grid')
        table.autofit = True
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Angle of Attack'
        for angle in self._analysis.AOAList:
            row_cells = table.add_row().cells
            row_cells[0].text = str(angle)

        non_zero = 0
        for angle in self._analysis.AOAList:
            if angle != 0:
                non_zero += 1
        if non_zero < 2:
            self._CP = False
            p = self._document.add_paragraph()
            p.add_run("NOTE: It is not possible to calculate the center of pressure at an "\
                                        "angle of attack of 0. It must be calculated at multiple points close "\
                                        "to 0 and inferred using l'Hôpital's rule.").bold = True
            p = self._document.add_paragraph()
            p.add_run('This study is unable to determine Center of Pressure.').italic = True
        else:
            self._CP = True

        self._document.add_heading('Configuration', level=1)

        self.physicsModelConfig()
        self.fluidPropertiesConfig()
        self.initializeFlowConfig()
        self.solverConfig()
        self.mesherConfig()
        self.boundaryConditionsConfig()

        self._document.add_page_break()

    def physicsModelConfig(self):
        self._document.add_heading('Physics Model', level=2)

        physicsModel = CfdTools.getPhysicsModel(self._analysis)
        table = self._document.add_table(rows=1, cols=2, style='Table Grid')
        table.autofit = True

        row_cells = table.rows[0].cells
        row_cells[0].text = "Time"
        row_cells[1].text = physicsModel.Time

        row_cells = table.add_row().cells
        row_cells[0].text = "Flow"
        row_cells[1].text = physicsModel.Phase

        row_cells = table.add_row().cells
        row_cells[0].text = "Isothermal"
        row_cells[1].text = self.configState(physicsModel.Flow == "Isothermal")

        row_cells = table.add_row().cells
        row_cells[0].text = "High Mach number"
        row_cells[1].text = self.configState(physicsModel.Flow == "HighMachCompressible")

        row_cells = table.add_row().cells
        row_cells[0].text = "Viscous"
        row_cells[1].text = self.configState(physicsModel.Turbulence == "Inviscid")

        row_cells = table.add_row().cells
        row_cells[0].text = "Rotating frame (SRF)"
        row_cells[1].text = self.configState(physicsModel.SRFModelEnabled)

        if physicsModel.Turbulence != "Inviscid":
            row_cells = table.add_row().cells
            row_cells[0].text = "Turbulence"
            row_cells[1].text = physicsModel.Turbulence
            if physicsModel.Turbulence != "Laminar":
                row_cells = table.add_row().cells
                row_cells[0].text = "Turbulence Model"
                row_cells[1].text = physicsModel.TurbulenceModel

        if physicsModel.Flow != "Isothermal" or physicsModel.Phase == "FreeSurface":
            row_cells = table.add_row().cells
            row_cells[0].text = "Gravity (x, y, z)"
            row_cells[1].text = "({}, {}, {})".format(
                physicsModel.gx.UserString,
                physicsModel.gy.UserString,
                physicsModel.gz.UserString,
            )

        if physicsModel.SRFModelEnabled and physicsModel.Phase != "FreeSurface":
            row_cells = table.add_row().cells
            row_cells[0].merge(row_cells[1])
            row_cells[0].text = "Moving Reference Frame (SRF)"

            row_cells = table.add_row().cells
            row_cells[0].text = "RPM"
            row_cells[1].text = physicsModel.SRFModelRPM.UserString

            row_cells = table.add_row().cells
            row_cells[0].text = "Center of Rotation"
            row_cells[1].text = "({} mm, {} mm, {} mm)".format(
                physicsModel.SRFModelCoR.x,
                physicsModel.SRFModelCoR.y,
                physicsModel.SRFModelCoR.z,
            )

            row_cells = table.add_row().cells
            row_cells[0].text = "Rotational Axis"
            row_cells[1].text = "({}, {}, {})".format(
                physicsModel.SRFModelAxis.x,
                physicsModel.SRFModelAxis.y,
                physicsModel.SRFModelAxis.z,
            )

    def fluidPropertiesConfig(self):
        self._document.add_heading('Fluid Properties', level=2)

    def initializeFlowConfig(self):
        self._document.add_heading('Initialize Flow Field', level=2)

    def solverConfig(self):
        self._document.add_heading('Solver', level=2)

    def mesherConfig(self):
        self._document.add_heading('Mesher', level=2)

    def boundaryConditionsConfig(self):
        self._document.add_heading('Boundary Conditions', level=2)

    def configState(self, condition):
        if condition:
            return "True"
        else:
            return "False"

    def generateCP(self):
        self._document.add_heading('Center of Pressure', level=1)
        p = self._document.add_paragraph("")
        p.add_run("NOTE: It is not possible to calculate the center of pressure at an "\
                                    "angle of attack of 0. It must be calculated at multiple points close "\
                                    "to 0 and inferred using l'Hôpital's rule.").bold = True
        self._document.add_paragraph("Center of Pressure at multiple angles of attack with the rocket rotated "\
                                     "around the center point.")

        p = self._document.add_paragraph("CP = X0 - My / (Fz * cos(AOA) + Fx * sin(AOA))", style="Block Quotation")
        p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        p = self._document.add_paragraph("X0 = {} mm".format(int(self._x0)), style="Block Quotation")
        p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

        count = len(self._analysis.AOAList)
        table = self._document.add_table(rows=5, cols=count+1, style='Simple Grid Columns')
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Angle of Attack'
        for i in range(count):
            hdr_cells[i + 1].text = str(self._analysis.AOAList[i])
        data_cells = table.columns[0].cells
        data_cells[1].text = "My"
        data_cells[2].text = "Fx"
        data_cells[3].text = "Fz"
        data_cells[4].text = "CP"
        for i in range(count):
            data_cells = table.columns[i+1].cells
            angle = str(self._analysis.AOAList[i])
            My = float(self._moments[angle][2])
            Fx = float(self._forces[angle][1])
            Fz = float(self._forces[angle][3])
            aoa = math.radians(float(self._analysis.AOAList[i]))
            # X = X0 - My / (Fz * cos(AOA) + Fx * sin(AOA))
            x = (My / (Fz * math.cos(aoa) + Fx * math.sin(aoa)))
            x = self._x0 - (x * 1000.0) # Meters to mm
            data_cells[1].text = "{:#.3g}".format(My)
            data_cells[2].text = "{:#.3g}".format(Fx)
            data_cells[3].text = "{:#.3g}".format(Fz)
            data_cells[4].text = "{} mm".format(int(x))

        self._document.add_page_break()

    def generateCD(self):
        self._document.add_heading('Lift and Drag', level=1)
        p = self._document.add_paragraph("Lift and Drag coefficients at multiple angles of attack with the rocket rotated "\
                                     "around the center point.")
        p.add_run(" The frontal reference area is adjusted for each angle of attack.")

        count = len(self._analysis.AOAList)
        table = self._document.add_table(rows=4, cols=count+1, style='Simple Grid Columns')
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Angle of Attack'
        for i in range(count):
            hdr_cells[i + 1].text = str(self._analysis.AOAList[i])
        data_cells = table.columns[0].cells
        data_cells[1].text = "Frontal Area"
        data_cells[2].text = "Cd"
        data_cells[3].text = "Cl"
        for i in range(count):
            data_cells = table.columns[i+1].cells
            angle = str(self._analysis.AOAList[i])
            aoa = float(self._analysis.AOAList[i])
            Cd = float(self._coefficients[angle][1])
            Cl = float(self._coefficients[angle][4])
            solid = applyTranslations(self._analysis.Shape, self._x0, aoa, self._rotation)
            area = calcFrontalArea(solid)
            data_cells[1].text = FreeCAD.Units.Quantity("{} mm^2".format(area)).UserString
            data_cells[2].text = "{:#.3g}".format(Cd)
            data_cells[3].text = "{:#.3g}".format(Cl)

        # self._document.add_page_break()

    def generateCL(self):
        # self._document.add_heading('Lift', level=1)
        # self._document.add_paragraph("Lift coefficient at multiple angles of attach")
        pass
