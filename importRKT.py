# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Provides support for importing Rocksim files."""

__title__ = "FreeCAD Rocksim Importer"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"


import os

import FreeCAD

from Rocket.Importer.Rocksim.Rocksim import RocksimImporter

def open(filename):
    """Open filename and parse using the orkHandler().

    Parameters
    ----------
    filename : str
        The path to the filename to be opened.

    Returns
    -------
    App::Document
        The new FreeCAD document object created, with the parsed information.
    """
    docname = os.path.split(filename)[1]
    doc = FreeCAD.newDocument(docname)
    doc.Label = docname[:-4]

    RocksimImporter.importFile(doc, filename)

    doc.recompute()
    return doc


def insert(filename, docname):
    """Get an active document and parse using the orkHandler().

    If no document exist, it is created.

    Parameters
    ----------
    filename : str
        The path to the filename to be opened.
    docname : str
        The name of the active App::Document if one exists, or
        of the new one created.

    Returns
    -------
    App::Document
        The active FreeCAD document, or the document created if none exists,
        with the parsed information.
    """
    try:
        doc = FreeCAD.getDocument(docname)
    except NameError:
        doc = FreeCAD.newDocument(docname)
    FreeCAD.ActiveDocument = doc

    RocksimImporter.importFile(doc, filename)

    doc.recompute()
