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

import FreeCAD
import sqlite3
from os import walk

import xml.sax

from App.Parts.PartDatabaseOrcImporter import PartDatabaseOrcImporter
from App.Utilities import _msg

class PartDatabase:

    def __init__(self):
        pass

    def getConnection(self, ro=True):
        # By default get a read only connection
        if ro:
            connection = sqlite3.connect("file:" + FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/parts/Parts.db?mode=ro", uri=True)
        else:
            connection = sqlite3.connect(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/parts/Parts.db")
        return connection

    def updateDatabase(self):
        connection = sqlite3.connect(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/parts/Parts.db")

        self._createTables(connection)
        self._importFiles(connection)

        connection.close()

    def _createTables(self, connection):
        cursor = connection.cursor()

        cursor.execute("DROP TABLE IF EXISTS material")
        cursor.execute("CREATE TABLE material (material_index INTEGER PRIMARY KEY ASC, manufacturer, name, type, density, units)")

        cursor.execute("DROP TABLE IF EXISTS component")
        cursor.execute("CREATE TABLE component (component_index INTEGER PRIMARY KEY ASC, manufacturer, part_number, description, material_index, mass, mass_units)")

        cursor.execute("DROP TABLE IF EXISTS tube_type")
        cursor.execute("CREATE TABLE tube_type (tube_type_index INTEGER PRIMARY KEY ASC, type)")
        cursor.execute("INSERT INTO tube_type(type) VALUES ('body tube'), ('centering ring'), ('coupler'), ('engine block'), ('launch lug')")

        cursor.execute("DROP TABLE IF EXISTS body_tube")
        cursor.execute("CREATE TABLE body_tube (body_tube_index INTEGER PRIMARY KEY ASC, component_index, tube_type_index, inner_diameter, inner_diameter_units, outer_diameter, outer_diameter_units, length, length_units)")

        connection.commit()

    def _importFiles(self, connection):
        for (dirpath, dirnames, filenames) in walk(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/parts/openrocket_components/"):
            # _msg("dirpath = %s, dirname = %s, filename = %s" % (dirpath, dirnames, filenames))
            for file in filenames:
                self._importOrcPartFile(connection, dirpath + file)

    def _importOrcPartFile(self, connection, filename):
        _msg("Importing %s..." % filename)

        # create an XMLReader
        parser = xml.sax.make_parser()

        # turn off namepsaces
        parser.setFeature(xml.sax.handler.feature_namespaces, 0)

        # override the default ContextHandler
        handler = PartDatabaseOrcImporter(connection)
        parser.setContentHandler(handler)
        parser.parse(filename)

    def _importRktPartFile(self, connection, filename):
        pass
