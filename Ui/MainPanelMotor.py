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
"""Class for motor analysis """

__title__ = "FreeCAD Motor"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    

import FreeCAD
import FreeCADGui

from DraftTools import translate

from PySide import QtGui, QtCore
from PySide2.QtWidgets import QGridLayout, QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy

def hLine():
    # Create a horizontal line by creating a frame and setting its shape to QFrame::HLine:
    hFrame =  QFrame()
    hFrame.setFrameShape(QFrame.HLine)
    return hFrame

def vLine():
    # Create a vertical line by creating a frame and setting its shape to QFrame::VLine:
    vFrame =  QFrame()
    vFrame.setFrameShape(QFrame.VLine)
    return vFrame

class MainPanelDialog(QtGui.QWidget):

    def __init__(self,obj,mode):
        super().__init__()

        self._obj = obj

        ui = FreeCADGui.UiLoader()

        # define our window
        self.setGeometry(0, 0, 600, 0)
        self.setWindowTitle(translate('Rocket', "Motor"))
        self.setObjectName("Motor viewer")
        self.horizontalLayout = QHBoxLayout(self)

        vbox = QVBoxLayout(self)
        self.resultsWidget = FreeCADGui.PySideUic.loadUi(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/ui/Motor/ResultsWidget.ui", self)
        self.resultsWidget.setParent(self)
        vbox.addWidget(self.resultsWidget)

        self.group = QtGui.QGroupBox(translate('Rocket', "Motor Statistics"), self)
        self.group.setCheckable(False)
        self.group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.labelMotorDesignationText = QtGui.QLabel(translate('Rocket', "Motor Designation:"), self)
        self.labelMotorDesignation = QtGui.QLabel(translate('Rocket', "-"), self)

        self.labelImpulseText = QtGui.QLabel(translate('Rocket', "Impulse:"), self)
        self.labelImpulse = QtGui.QLabel(translate('Rocket', "-"), self)

        self.labelDeliveredISPText = QtGui.QLabel(translate('Rocket', "Delivered ISP:"), self)
        self.labelDeliveredISP = QtGui.QLabel(translate('Rocket', "-"), self)

        self.labelBurnTimeText = QtGui.QLabel(translate('Rocket', "Burn Time:"), self)
        self.labelBurnTime = QtGui.QLabel(translate('Rocket', "-"), self)

        self.labelVolumeLoadingText = QtGui.QLabel(translate('Rocket', "Volume Loading:"), self)
        self.labelVolumeLoading = QtGui.QLabel(translate('Rocket', "-"), self)

        self.labelAveragePressureText = QtGui.QLabel(translate('Rocket', "Average Pressure:"), self)
        self.labelAveragePressure = QtGui.QLabel(translate('Rocket', "-"), self)

        self.labelPeakPressureText = QtGui.QLabel(translate('Rocket', "Peak Pressure:"), self)
        self.labelPeakPressure = QtGui.QLabel(translate('Rocket', "-"), self)

        self.labelInitialKNText = QtGui.QLabel(translate('Rocket', "Initial Kn:"), self)
        self.labelInitialKN = QtGui.QLabel(translate('Rocket', "-"), self)

        self.labelPeakKNText = QtGui.QLabel(translate('Rocket', "Peak Kn:"), self)
        self.labelPeakKN = QtGui.QLabel(translate('Rocket', "-"), self)

        self.labelIdealThrustCoefficientText = QtGui.QLabel(translate('Rocket', "Ideal Thrust Coefficient:"), self)
        self.labelIdealThrustCoefficient = QtGui.QLabel(translate('Rocket', "-"), self)

        self.labelPropellantMassText = QtGui.QLabel(translate('Rocket', "Propellant Mass:"), self)
        self.labelPropellantMass = QtGui.QLabel(translate('Rocket', "-"), self)

        self.labelPropellantLengthText = QtGui.QLabel(translate('Rocket', "Propellant Length:"), self)
        self.labelPropellantLength = QtGui.QLabel(translate('Rocket', "-"), self)

        self.labelPortThroatRatioText = QtGui.QLabel(translate('Rocket', "Port/Throat Ratio:"), self)
        self.labelPortThroatRatio = QtGui.QLabel(translate('Rocket', "-"), self)

        self.labelPeakMassFluxText = QtGui.QLabel(translate('Rocket', "Peak Mass Flux:"), self)
        self.labelPeakMassFlux = QtGui.QLabel(translate('Rocket', "-"), self)

        self.labelDeliveredThrustCoefficientText = QtGui.QLabel(translate('Rocket', "Delivered Thrust Coefficient:"), self)
        self.labelDeliveredThrustCoefficient = QtGui.QLabel(translate('Rocket', "-"), self)

        col = 0
        grid = QGridLayout()

        row = 0
        grid.addItem(self.hbox(self.labelMotorDesignationText, self.labelMotorDesignation), row, col)
        row += 1
        grid.addItem(self.hbox(self.labelImpulseText, self.labelImpulse), row, col)
        row += 1
        grid.addItem(self.hbox(self.labelDeliveredISPText, self.labelDeliveredISP), row, col)
        row += 1
        grid.addItem(self.hbox(self.labelBurnTimeText, self.labelBurnTime), row, col)
        row += 1
        grid.addItem(self.hbox(self.labelVolumeLoadingText, self.labelVolumeLoading), row, col)

        col += 1
        row = 0
        grid.addItem(self.hbox(self.labelAveragePressureText, self.labelAveragePressure), row, col)
        row += 1
        grid.addItem(self.hbox(self.labelPeakPressureText, self.labelPeakPressure), row, col)
        row += 1
        grid.addItem(self.hbox(self.labelInitialKNText, self.labelInitialKN), row, col)
        row += 1
        grid.addItem(self.hbox(self.labelPeakKNText, self.labelPeakKN), row, col)
        row += 1
        grid.addItem(self.hbox(self.labelIdealThrustCoefficientText, self.labelIdealThrustCoefficient), row, col)

        col += 1
        row = 0
        grid.addItem(self.hbox(self.labelPropellantMassText, self.labelPropellantMass), row, col)
        row += 1
        grid.addItem(self.hbox(self.labelPropellantLengthText, self.labelPropellantLength), row, col)
        row += 1
        grid.addItem(self.hbox(self.labelPortThroatRatioText, self.labelPortThroatRatio), row, col)
        row += 1
        grid.addItem(self.hbox(self.labelPeakMassFluxText, self.labelPeakMassFlux), row, col)
        row += 1
        grid.addItem(self.hbox(self.labelDeliveredThrustCoefficientText, self.labelDeliveredThrustCoefficient), row, col)

        self.group.setLayout(grid)
        vbox.addWidget(self.group)
        self.horizontalLayout.addItem(vbox)

        self.setLayout(self.horizontalLayout)

        self.update()

    def hbox(self, label1, label2):
        hb = QHBoxLayout(self)
        hb.addWidget(label1)
        hb.addWidget(label2)
        return hb

    def closeEvent(self, event):
        if self._obj:
            # before deleting this view, we remove the reference to it in the object
            if hasattr(self._obj,"ViewObject"):
                if self._obj.ViewObject:
                    if hasattr(self._obj.ViewObject.Proxy,"editor"):
                        del self._obj.ViewObject.Proxy.editor
        if FreeCADGui:
            if FreeCADGui.ActiveDocument:
                FreeCADGui.ActiveDocument.resetEdit()

        
    def transferTo(self):
        "Transfer from the dialog to the object" 
        pass

    def transferFrom(self):
        "Transfer from the object to the dialog"
        pass

    def onProperty(self, value):
        print("Property button pushed '%s'", value)
        
    def update(self):
        'fills the widgets'
        self.transferFrom()
                
    def accept(self):
        self.transferTo()
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.resetEdit()
        
                    
    def reject(self):
        FreeCAD.ActiveDocument.abortTransaction()
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.resetEdit()
