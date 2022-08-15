# ***************************************************************************
# *   Copyright (c) 2021 David Carter <dcarter@davidcarter.ca>              *
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
"""Class for rocket part Database"""

__title__ = "FreeCAD Open Rocket Part Component Database"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import sqlite3
from os import walk

import xml.sax

from App.Parts.PartDatabaseOrcImporter import PartDatabaseOrcImporter
from App.Parts.Component import Component
from App.Parts.Exceptions import NotFoundError
from App.Parts.Utilities import _msg

class PartDatabase:

    def __init__(self, rootFolder):
        self._rootFolder = rootFolder

    def getConnection(self, ro=True):
        # By default get a read only connection
        if ro:
            connection = sqlite3.connect("file:" + self._rootFolder + "/Resources/parts/Parts.db?mode=ro", uri=True)
        else:
            connection = sqlite3.connect(self._rootFolder + "/Resources/parts/Parts.db")
        return connection

    def getManufacturers(self):
        connection = self.getConnection()
        
        try:
            manufacturers = Component.getManufacturers(connection)
        except NotFoundError:
            manufacturers = []

        connection.close()
        return manufacturers

    def updateDatabase(self):
        connection = sqlite3.connect(self._rootFolder + "/Resources/parts/Parts.db")
        connection.row_factory = sqlite3.Row

        self._createTables(connection)
        self._importFiles(connection)

        with open('dump.sql', 'w') as f:
            for line in connection.iterdump():
                f.write("%s\n" % line)

        connection.close()

    def _createTables(self, connection):
        cursor = connection.cursor()

        cursor.execute("DROP TABLE IF EXISTS alias")
        cursor.execute("CREATE TABLE alias (alias_index INTEGER PRIMARY KEY ASC, alias_type, name, alias_name)")

        cursor.execute("DROP TABLE IF EXISTS material")
        cursor.execute("CREATE TABLE material (material_index INTEGER PRIMARY KEY ASC, manufacturer, material_name, type, density, units)")
        cursor.execute("CREATE INDEX idx_material ON material(manufacturer, material_name, type)")

        cursor.execute("DROP TABLE IF EXISTS component")
        cursor.execute("CREATE TABLE component (component_index INTEGER PRIMARY KEY ASC, manufacturer, part_number, description, material_index, mass, mass_units)")
        cursor.execute("CREATE INDEX idx_component_manufacturer ON component(manufacturer)")

        cursor.execute("DROP TABLE IF EXISTS tube_type")
        cursor.execute("CREATE TABLE tube_type (tube_type_index INTEGER PRIMARY KEY ASC, type)")
        cursor.execute("CREATE INDEX idx_tube_type_type ON tube_type(type)")
        cursor.execute("INSERT INTO tube_type(type) VALUES ('Body Tube'), ('Centering Ring'), ('Tube Coupler'), ('Engine Block'), ('Launch Lug'), ('Bulkhead')")

        cursor.execute("DROP TABLE IF EXISTS body_tube")
        cursor.execute("CREATE TABLE body_tube (body_tube_index INTEGER PRIMARY KEY ASC, component_index, tube_type_index, inner_diameter, inner_diameter_units, outer_diameter, outer_diameter_units, length, length_units)")
        cursor.execute("CREATE INDEX idx_body_tube ON body_tube(component_index, tube_type_index)")
 
        cursor.execute("DROP TABLE IF EXISTS nose")
        cursor.execute("""CREATE TABLE nose (nose_index INTEGER PRIMARY KEY ASC, component_index, shape, style, diameter, diameter_units,
            length, length_units, thickness, thickness_units, shoulder_diameter, shoulder_diameter_units, shoulder_length, shoulder_length_units)""")

        cursor.execute("DROP TABLE IF EXISTS transition")
        cursor.execute("""CREATE TABLE transition (transition_index INTEGER PRIMARY KEY ASC, component_index, shape, style, 
            fore_outside_diameter, fore_outside_diameter_units, fore_shoulder_diameter, fore_shoulder_diameter_units, fore_shoulder_length, fore_shoulder_length_units,
            aft_outside_diameter, aft_outside_diameter_units, aft_shoulder_diameter, aft_shoulder_diameter_units, aft_shoulder_length, aft_shoulder_length_units,
            length, length_units, thickness, thickness_units)""")

        cursor.execute("DROP TABLE IF EXISTS parachute")
        cursor.execute("CREATE TABLE parachute (parachute_index INTEGER PRIMARY KEY ASC, component_index, line_material_index, sides, lines, diameter, diameter_units, line_length, line_length_units)")
            
        cursor.execute("DROP TABLE IF EXISTS streamer")
        cursor.execute("CREATE TABLE streamer (streamer_index INTEGER PRIMARY KEY ASC, component_index, length, length_units, width, width_units, thickness, thickness_units)")

        connection.commit()

    def _importFiles(self, connection):
        # Import files with initial definitions, or corrections to incomplete definitions
        for (dirpath, dirnames, filenames) in walk(self._rootFolder + "/Resources/parts/workbench/"):
            for file in filenames:
                self._importOrcPartFile(connection, dirpath + file)

        for (dirpath, dirnames, filenames) in walk(self._rootFolder + "/Resources/parts/openrocket-database/orc/"):
            self._importOrcPartFile(connection, dirpath + 'generic_materials.orc')
            for file in filenames:
                self._importOrcPartFile(connection, dirpath + file)

    def _importOrcPartFile(self, connection, filename):
        _msg("Importing %s..." % filename)

        # create an XMLReader
        parser = xml.sax.make_parser()

        # turn off namespaces
        parser.setFeature(xml.sax.handler.feature_namespaces, 0)

        # override the default ContextHandler
        handler = PartDatabaseOrcImporter(connection, filename)
        parser.setContentHandler(handler)
        parser.parse(filename)

    def _importRktPartFile(self, connection, filename):
        pass
