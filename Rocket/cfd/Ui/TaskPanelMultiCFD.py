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
"""Class for controlling multiple CFDs"""

__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"


import FreeCAD
import FreeCADGui
import time
import os

from DraftTools import translate

from PySide import QtGui, QtCore
# from PySide.QtWidgets import QDialog, QGridLayout, QVBoxLayout, QSizePolicy
from PySide.QtGui import QApplication
from PySide.QtCore import Qt

from CfdOF import CfdTools
from CfdOF.CfdConsoleProcess import CfdConsoleProcess
from CfdOF.PostProcess.CfdReportingFunction import CfdReportingFunction
from CfdOF.Mesh import CfdMeshTools
from CfdOF.Mesh.CfdMesh import MESHERS
from CfdOF.CfdTools import setQuantity, getQuantity, storeIfChanged
from CfdOF.Solve import CfdCaseWriterFoam
from CfdOF.Solve.CfdRunnableFoam import CfdRunnableFoam

from Ui.UIPaths import getUIPath

from Rocket.cfd.FeatureCFDRocket import FeatureCFDRocket
from Rocket.cfd.Reports.CFDReport import CFDReport

SUBPROCESS_NONE = 0
SUBPROCESS_MESH = 1
SUBPROCESS_CFD = 2

class FoamRunner(CfdRunnableFoam):

    def __init__(self, analysis=None, solver=None):
        super().__init__(analysis, solver)

    def constructReportingFunctionPlotters(self):
        # No graphs for reporting functions
        pass

    def initMonitors(self):
        pass

class TaskPanelMultiCFD:

    def __init__(self,obj,mode):
        self._obj = obj

        self.form = FreeCADGui.PySideUic.loadUi(os.path.join(getUIPath(), 'Resources', 'ui', "DialogMultiCFD.ui"))
        # self.form.setWindowIcon(QtGui.QIcon(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_CFDRocket.svg"))

        self._consoleMessageCart = ''
        self._meshTools = None

        self._solver = CfdTools.getSolver(self._obj)
        # self._foamRunnable = CfdRunnableFoam.CfdRunnableFoam(CfdTools.getActiveAnalysis(), self._solver)
        self._foamRunnable = FoamRunner(CfdTools.getActiveAnalysis(), self._solver)

        self._subProcess = SUBPROCESS_NONE # Current active subprocess
        self._processing = False
        self._obj.Proxy._cfdProcess = CfdConsoleProcess(finished_hook=self.cfdProcessFinished,
                                                             stdout_hook=self.gotOutputLines,
                                                             stderr_hook=self.gotErrorLines)


        self._timer = QtCore.QTimer()
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self.updateTimerText)

        self.form.editAOA.textChanged.connect(self.onAOAChanged)
        self.form.buttonStart.clicked.connect(self.onStart)
        self.form.buttonStop.clicked.connect(self.onStop)
        self.form.buttonStop.setEnabled(False)

        self.update()

        self._start = time.time()
        self._timer.start()

    def transferTo(self):
        "Transfer from the dialog to the object"
        self._obj.AOAList = self.getAOAList()

    def transferFrom(self):
        "Transfer from the object to the dialog"
        self.form.editAOA.setPlainText(self.getAOAText())

    def onAOAChanged(self):
        self.transferTo()
        # _ = self.getAOAList()

    def getAOAList(self):
        listText = self.form.editAOA.toPlainText()
        textList = listText.split('\n')
        angles = []
        for angle in textList:
            if len(angle) > 0:
                try:
                    angles.append(float(angle))
                except ValueError:
                    print("Illegal float value '{}'".format(angle))
        return angles

    def getAOAText(self):
        listText = ""
        for angle in self._obj.AOAList:
            if len(listText) > 0:
                listText += "\n"
            listText += str(angle)
        return listText

    def setEdited(self):
        # try:
        #     self._obj.Proxy.setEdited()
        # except ReferenceError:
        #     # Object may be deleted
        #     pass
        pass

    def getStandardButtons(self):
        return QtGui.QDialogButtonBox.Close

    # def clicked(self,button):
    #     if button == QtGui.QDialogButtonBox.Apply:
    #         self.transferTo()
    #         self._obj.Proxy.execute(self._obj)

    def update(self):
        'fills the widgets'
        self.transferFrom()

    def reject(self):
        FreeCADGui.ActiveDocument.resetEdit()
        return True

    def closed(self):
        # We call this from unsetEdit to ensure cleanup
        self._obj.Proxy._cfdProcess.terminate()
        self._obj.Proxy._cfdProcess.waitForFinished()
        self._timer.stop()
        FreeCAD.ActiveDocument.recompute()

    def updateTimerText(self):
        if self._processing:
            self.form.labelTime.setText(translate('Rocket', 'Time: ') + CfdTools.formatTimer(time.time() - self._start))
        pass

    def cfdProcessFinished(self, exit_code):
        if exit_code == 0:
            if self._subProcess == SUBPROCESS_MESH:
                self.consoleMessage('Meshing completed')
            elif self._subProcess == SUBPROCESS_CFD:
                self.consoleMessage("Simulation finished successfully")
            # self.analysis_obj.NeedsMeshRerun = False
            # self.form.pb_run_mesh.setEnabled(True)
            # self.form.pb_stop_mesh.setEnabled(False)
            # self.form.pb_paraview.setEnabled(True)
            # self.form.pb_write_mesh.setEnabled(True)
            # self.form.pb_check_mesh.setEnabled(True)
            # self.form.pb_load_mesh.setEnabled(True)
        else:
            if self._subProcess == SUBPROCESS_MESH:
                self.consoleMessage("Meshing exited with error", 'Error')
            elif self._subProcess == SUBPROCESS_CFD:
                self.consoleMessage("Simulation exited with error", 'Error')
            self.stopProcessing()
            # self.form.pb_run_mesh.setEnabled(True)
            # self.form.pb_stop_mesh.setEnabled(False)
            # self.form.pb_write_mesh.setEnabled(True)
            # self.form.pb_check_mesh.setEnabled(False)
            # self.form.pb_paraview.setEnabled(False)

        self.error_message = ''
        # Get rid of any existing loaded mesh
        # self.pbClearMeshClicked()
        # self.updateUI()
        pass

    def gotOutputLines(self, lines):
        if self._subProcess == SUBPROCESS_CFD:
            self._foamRunnable.processOutput(lines)
        else:
            for l in lines.split('\n'):
                if l.endswith("faces in error to set meshQualityFaces"):
                    self.check_mesh_error = True

    def gotErrorLines(self, lines):
        print_err = self._obj.Proxy._cfdProcess.processErrorOutput(lines)
        if print_err is not None:
            self.consoleMessage(print_err, 'Error')
            self.check_mesh_error = True

    def onStart(self):
        self.startProcessing()

        for angle in self._obj.AOAList:
            self.doCFD(angle)

        self.createReport()

        self.stopProcessing()

    def createReport(self):
        self.consoleMessage(translate('Rocket', 'Preparing report...'))

        report = CFDReport(self._obj)
        report.generate()
        CfdTools.openFileManager(report.getPath())

        self.consoleMessage(translate('Rocket', 'Report complete'))

    def startProcessing(self):
        self._start = time.time()
        self._processing = True
        self.form.buttonStop.setEnabled(True)

    def stopProcessing(self):
        self.form.buttonStop.setEnabled(False)
        self._processing = False

    def onStop(self):
        self.stopProcessing()
        self._obj.Proxy._cfdProcess.terminate()
        self._obj.Proxy._cfdProcess.waitForFinished()
        self._timer.stop()

    def doCFD(self, aoa):
        self.setupCFD(aoa)
        if self._processing:
            self.mesh()
        if self._processing:
            self.solve()

    def setupCFD(self, aoa):
        """ Ensures the objects are set for the required AOA """
        self.consoleMessage(translate('Rocket', 'Preparing for AOA={}...').format(aoa))
        area = self.setupRocket(aoa)
        if area == 0:
            self.stopProcessing()
            return
        self.setupReferenceArea(area)
        self.setupCaseName(aoa)

    def setupRocket(self, aoa):
        rocket = self.getCFDRocket(self._obj)
        if rocket is None:
            self.consoleMessage(translate('Rocket', 'No rocket found'), 'Error')
            return 0
        rocket._obj.AngleOfAttack = aoa
        # rocket.execute(rocket)
        FreeCAD.ActiveDocument.recompute()
        return rocket.calcFrontalArea()

    def setupReferenceArea(self, area):
        for child in self._obj.Group:
            if hasattr(child, "Proxy") and isinstance(child.Proxy, CfdReportingFunction):
                if child.ReportingFunctionType == "ForceCoefficients":
                    child.AreaRef = area
        FreeCAD.ActiveDocument.recompute()

    def setupCaseName(self, aoa):
        caseName = "case_aoa_{}".format(aoa)
        print("Case name '{}'".format(caseName))
        self._solver.InputCaseName = caseName
        FreeCAD.ActiveDocument.recompute()

    def mesh(self):
        self.writeMesh()
        if self._processing:
            self.runMesher()
            self._obj.Proxy._cfdProcess.waitForFinished()

    def writeMesh(self):
        self.setupMeshtools()

        # FreeCADGui.doCommand("from CfdOF.Mesh import CfdMeshTools")
        # FreeCADGui.doCommand("from CfdOF import CfdTools")
        # FreeCADGui.doCommand("cart_mesh = "
        #                      "CfdMeshTools.CfdMeshTools(FreeCAD.ActiveDocument." + self.mesh_obj.Name + ")")
        # FreeCADGui.doCommand("FreeCAD.ActiveDocument." + self.mesh_obj.Name + ".Proxy.cart_mesh = cart_mesh")
        cart_mesh = self._meshTools
        cart_mesh.progressCallback = self.progressCallback

        # Start writing the mesh files
        self.consoleMessage("Preparing meshing ...")
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            # setQuantity(self.form.if_max, str(cart_mesh.getClmax()))
            # Re-update the data in case ClMax was auto-set to avoid spurious update detection on next write
            # self.store()
            print('Part to mesh:\n  Name: '
                  + cart_mesh.part_obj.Name + ', Label: '
                  + cart_mesh.part_obj.Label + ', ShapeType: '
                  + cart_mesh.part_obj.Shape.ShapeType)
            print('  CharacteristicLengthMax: ' + str(cart_mesh.clmax))
            cart_mesh.writeMesh()
            # FreeCADGui.doCommand("cart_mesh.writeMesh()")
        except Exception as ex:
            self.consoleMessage("Error " + type(ex).__name__ + ": " + str(ex), 'Error')
            raise
        else:
            self._obj.NeedsMeshRerun = True
        finally:
            QApplication.restoreOverrideCursor()

        # Update the UI
        # self.updateUI()

    def runMesher(self):
        cart_mesh = self._meshTools
        cart_mesh.progressCallback = self.progressCallback
        cart_mesh.Error = False

        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            self._subProcess = SUBPROCESS_MESH
            mesher = CfdTools.getMeshObject(self._obj)
            self.consoleMessage("Initializing {} ...".format(mesher.MeshUtility))
            mesher.Proxy.cart_mesh = cart_mesh
            # FreeCADGui.doCommand("from CfdOF.Mesh import CfdMeshTools")
            # FreeCADGui.doCommand("from CfdOF import CfdTools")
            # FreeCADGui.doCommand("from CfdOF import CfdConsoleProcess")
            # FreeCADGui.doCommand("cart_mesh = "
            #                      "    CfdMeshTools.CfdMeshTools(FreeCAD.ActiveDocument." + self.mesh_obj.Name + ")")
            # FreeCADGui.doCommand("proxy = FreeCAD.ActiveDocument." + self.mesh_obj.Name + ".Proxy")
            # FreeCADGui.doCommand("proxy.cart_mesh = cart_mesh")
            # FreeCADGui.doCommand("cart_mesh.error = False")
            if CfdTools.getFoamRuntime() == "MinGW":
                # FreeCADGui.doCommand("cmd = CfdTools.makeRunCommand('Allmesh.bat', source_env=False)")
                cmd = CfdTools.makeRunCommand('Allmesh.bat', source_env=False)
            else:
                # FreeCADGui.doCommand("cmd = CfdTools.makeRunCommand('./Allmesh', cart_mesh.meshCaseDir, source_env=False)")
                cmd = CfdTools.makeRunCommand('./Allmesh', cart_mesh.meshCaseDir, source_env=False)
            # FreeCADGui.doCommand("env_vars = CfdTools.getRunEnvironment()")
            env_vars = CfdTools.getRunEnvironment()
            # FreeCADGui.doCommand("proxy.running_from_macro = True")
            # self.mesh_obj.Proxy.running_from_macro = False
            # FreeCADGui.doCommand("if proxy.running_from_macro:\n" +
            #                      "  mesh_process = CfdConsoleProcess.CfdConsoleProcess()\n" +
            #                      "  mesh_process.start(cmd, env_vars=env_vars, working_dir=cart_mesh.meshCaseDir)\n" +
            #                      "  mesh_process.waitForFinished()\n" +
            #                      "else:\n" +
            #                      "  proxy.mesh_process.start(cmd, env_vars=env_vars, working_dir=cart_mesh.meshCaseDir)")
            self._obj.Proxy._cfdProcess.start(cmd, env_vars=env_vars, working_dir=cart_mesh.meshCaseDir)
            if self._obj.Proxy._cfdProcess.waitForStarted():
                # self.form.pb_run_mesh.setEnabled(False)  # Prevent user running a second instance
                # self.form.pb_stop_mesh.setEnabled(True)
                # self.form.pb_write_mesh.setEnabled(False)
                # self.form.pb_check_mesh.setEnabled(False)
                # self.form.pb_paraview.setEnabled(False)
                # self.form.pb_load_mesh.setEnabled(False)
                self.consoleMessage("Mesher started ...")
            else:
                self.consoleMessage("Error starting meshing process", 'Error')
                # self.mesh_obj.Proxy.cart_mesh.error = True
        except Exception as ex:
            self.consoleMessage("Error " + type(ex).__name__ + ": " + str(ex), 'Error')
            raise
        finally:
            QApplication.restoreOverrideCursor()

    def solve(self):
        self.writeOpenFOAM()
        if self._processing:
            self.runOpenFOAM()
            self._obj.Proxy._cfdProcess.waitForFinished()

    def writeOpenFOAM(self):
        # FreeCADGui.doCommand("from CfdOF.Solve import CfdCaseWriterFoam")
        # from CfdOF.Solve import CfdCaseWriterFoam
        # import importlib
        # importlib.reload(CfdCaseWriterFoam)
        self.consoleMessage("Case writer called")
        # self.form.pb_paraview.setEnabled(False)
        # self.form.pb_edit_inp.setEnabled(False)
        # self.form.pb_run_solver.setEnabled(False)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            self._solver.Proxy.case_writer = CfdCaseWriterFoam.CfdCaseWriterFoam(self._obj)
            writer = self._solver.Proxy.case_writer
            # FreeCADGui.doCommand("FreeCAD.ActiveDocument." + self.solver_object.Name + ".Proxy.case_writer = "
            #                         "CfdCaseWriterFoam.CfdCaseWriterFoam(FreeCAD.ActiveDocument." +
            #                         self.solver_runner.analysis.Name + ")")
            # FreeCADGui.doCommand("writer = FreeCAD.ActiveDocument." +
            #                         self.solver_object.Name + ".Proxy.case_writer")
            # writer = self.solver_object.Proxy.case_writer
            writer.progressCallback = self.consoleMessage
            writer.writeCase()
            # FreeCADGui.doCommand("writer.writeCase()")
        except Exception as e:
            self.consoleMessage("Error writing case:", 'Error')
            self.consoleMessage(type(e).__name__ + ": " + str(e), 'Error')
            self.consoleMessage("Write case setup file failed", 'Error')
            raise
        else:
            self._obj.NeedsCaseRewrite = False
        finally:
            QApplication.restoreOverrideCursor()
        # self.updateUI()
        # self.form.pb_run_solver.setEnabled(True)

    def runOpenFOAM(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self._subProcess = SUBPROCESS_CFD
        # FreeCADGui.doCommand("from CfdOF import CfdTools")
        # FreeCADGui.doCommand("from CfdOF import CfdConsoleProcess")
        # solver = CfdTools.getSolver(self._obj)
        # foam_runnable = CfdRunnableFoam.CfdRunnableFoam(CfdTools.getActiveAnalysis(), self._solver)
        self._solver.Proxy.solver_runner = self._foamRunnable #self.solver_runner
        # FreeCADGui.doCommand("proxy = FreeCAD.ActiveDocument." + self.solver_object.Name + ".Proxy")
        # # This is a workaround to emit code into macro without actually running it
        # FreeCADGui.doCommand("proxy.running_from_macro = True")
        # self.solver_object.Proxy.running_from_macro = False
        # FreeCADGui.doCommand(
        #     "if proxy.running_from_macro:\n" +
        #     "  analysis_object = FreeCAD.ActiveDocument." + self.analysis_object.Name + "\n" +
        #     "  solver_object = FreeCAD.ActiveDocument." + self.solver_object.Name + "\n" +
        #     "  working_dir = CfdTools.getOutputPath(analysis_object)\n" +
        #     "  case_name = solver_object.InputCaseName\n" +
        #     "  solver_directory = os.path.abspath(os.path.join(working_dir, case_name))\n" +
        #     "  from CfdOF.Solve import CfdRunnableFoam\n" +
        #     "  solver_runner = CfdRunnableFoam.CfdRunnableFoam(analysis_object, solver_object)\n" +
        #     "  cmd = solver_runner.getSolverCmd(solver_directory)\n" +
        #     "  if cmd is not None:\n" +
        #     "    env_vars = solver_runner.getRunEnvironment()\n" +
        #     "    solver_process = CfdConsoleProcess.CfdConsoleProcess(stdout_hook=solver_runner.processOutput)\n" +
        #     "    solver_process.start(cmd, env_vars=env_vars, working_dir=solver_directory)\n" +
        #     "    solver_process.waitForFinished()\n")
        working_dir = CfdTools.getOutputPath(self._obj)
        case_name = self._solver.InputCaseName
        solver_directory = os.path.abspath(os.path.join(working_dir, case_name))
        cmd = self._foamRunnable.getSolverCmd(solver_directory)
        if cmd is None:
            return
        env_vars = self._foamRunnable.getRunEnvironment()
        # self.solver_object.Proxy.solver_process = CfdConsoleProcess(finished_hook=self.cfdProcessFinished,
        #                                                             stdout_hook=self.gotOutputLines,
        #                                                             stderr_hook=self.gotErrorLines)
        self._obj.Proxy._cfdProcess.start(cmd, env_vars=env_vars, working_dir=solver_directory)
        # self.solver_object.Proxy.solver_process.start(cmd, env_vars=env_vars, working_dir=solver_directory)
        if self._obj.Proxy._cfdProcess.waitForStarted():
            # Setting solve button to inactive to ensure that two instances of the same simulation aren't started
            # simultaneously
            # self.form.pb_write_inp.setEnabled(False)
            # self.form.pb_run_solver.setEnabled(False)
            # self.form.terminateSolver.setEnabled(True)
            # self.form.pb_paraview.setEnabled(True)
            self.consoleMessage("Solver started")
        else:
            self.consoleMessage("Error starting solver", 'Error')
        QApplication.restoreOverrideCursor()

    def getCFDRocket(self, obj):
        return self._obj.CFDRocket.Proxy

    def progressCallback(self, message):
        self.consoleMessage(message)

    def consoleMessage(self, message="", colourType=None, timed=True):
        if timed:
            self._consoleMessageCart += \
                '<font color="{}">{:4.1f}:</font> '.format(CfdTools.getColour('Logging'), time.time() - self._start)
        if colourType:
            self._consoleMessageCart += \
                '<font color="{}">{}</font><br>'.format(CfdTools.getColour(colourType), message)
        else:
            self._consoleMessageCart += message + '<br>'
        self.form.editStatus.setText(self._consoleMessageCart)
        self.form.editStatus.moveCursor(QtGui.QTextCursor.End)
        if FreeCAD.GuiUp:
            FreeCAD.Gui.updateGui()

    def setupMeshtools(self):
        mesher = CfdTools.getMeshObject(self._obj)
        if mesher is None:
            self.stopProcessing()
            return
        # mesher = mesher[0]
        self._meshTools = CfdMeshTools.CfdMeshTools(mesher)
